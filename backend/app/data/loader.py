import logging
from pathlib import Path
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
from backend.app.core.config import settings
from backend.app.data.cleaner import normalize_portuguese_text, clean_categories

logger = logging.getLogger(__name__)

def build_analytical_dataset(raw_dir: Path, output_dir: Path) -> pd.DataFrame:
    """
    Ingests raw Olist CSVs, performs grain-safe aggregations,
    cleans categories and text, computes operational KPIs,
    and exports orders_analytical.parquet.
    """
    logger.info("Loading raw Olist datasets...")
    orders = pd.read_csv(raw_dir / "olist_orders_dataset.csv")
    items = pd.read_csv(raw_dir / "olist_order_items_dataset.csv")
    reviews = pd.read_csv(raw_dir / "olist_order_reviews_dataset.csv")
    products = pd.read_csv(raw_dir / "olist_products_dataset.csv")
    translations = pd.read_csv(raw_dir / "product_category_name_translation.csv")
    customers = pd.read_csv(raw_dir / "olist_customers_dataset.csv")
    sellers = pd.read_csv(raw_dir / "olist_sellers_dataset.csv")

    # 1. Clean Products with Category Translations
    products_clean = clean_categories(products, translations)
    products_clean["product_volume_cm3"] = (
        products_clean["product_length_cm"].fillna(0)
        * products_clean["product_height_cm"].fillna(0)
        * products_clean["product_width_cm"].fillna(0)
    )

    # 2. Pre-aggregate Items to Order Grain
    logger.info("Aggregating order items to single order grain...")
    items_agg = items.groupby("order_id").agg(
        total_price=("price", "sum"),
        total_freight=("freight_value", "sum"),
        item_count=("order_item_id", "count"),
        product_id=("product_id", "first"),
        seller_id=("seller_id", "first"),
        unique_sellers=("seller_id", "nunique")
    ).reset_index()

    # 3. Clean and Deduplicate Reviews to Single Order Grain
    logger.info("Cleaning reviews and handling order grain deduplication...")
    reviews_sorted = reviews.sort_values("review_score", ascending=True)
    reviews_agg = reviews_sorted.groupby("order_id").agg(
        review_score=("review_score", "first"), # Conservative: capture customer dissatisfaction
        review_title=("review_comment_title", lambda s: next((x for x in s if isinstance(x, str) and x.strip()), "")),
        review_comment=("review_comment_message", lambda s: next((x for x in s if isinstance(x, str) and x.strip()), "")),
        review_creation_date=("review_creation_date", "first")
    ).reset_index()

    # Normalize Portuguese review comments
    reviews_agg["cleaned_comment"] = reviews_agg["review_comment"].apply(normalize_portuguese_text)
    reviews_agg["has_comment"] = reviews_agg["cleaned_comment"].apply(lambda x: 1 if len(x) > 0 else 0)

    # 4. Safe Grain Merging
    logger.info("Merging datasets onto unique orders...")
    df = orders.merge(items_agg, on="order_id", how="inner")
    df = df.merge(reviews_agg, on="order_id", how="left")
    df = df.merge(customers[["customer_id", "customer_unique_id", "customer_state", "customer_city"]], on="customer_id", how="left")
    df = df.merge(sellers[["seller_id", "seller_state", "seller_city"]], on="seller_id", how="left")
    df = df.merge(
        products_clean[[
            "product_id", 
            "product_category_name_english", 
            "product_weight_g", 
            "product_volume_cm3"
        ]], 
        on="product_id", 
        how="left"
    )

    # 5. Timestamp Parsing & Operational Metrics Computation
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Filter to delivered orders with valid delivery and estimate dates
    delivered_mask = (
        (df["order_status"] == "delivered") &
        df["order_delivered_customer_date"].notnull() &
        df["order_estimated_delivery_date"].notnull()
    )
    df["is_delivered"] = delivered_mask.astype(int)

    # Delivery delay in days: actual delivery - estimated delivery
    delay_delta = (df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]).dt.total_seconds() / 86400.0
    df["delay_days"] = np.where(delivered_mask, np.maximum(0.0, delay_delta), 0.0)
    df["is_late"] = np.where(delivered_mask & (delay_delta > 0), 1, 0)

    # Transit days: actual delivery - purchase timestamp
    transit_delta = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.total_seconds() / 86400.0
    df["transit_days"] = np.where(delivered_mask, np.maximum(0.0, transit_delta), np.nan)

    # Cost ratios & geography
    df["freight_ratio"] = df["total_freight"] / (df["total_price"] + df["total_freight"]).replace(0, np.nan)
    df["is_interstate"] = (df["customer_state"] != df["seller_state"]).astype(int)
    
    # Target variable: low rating (score <= 2)
    df["is_low_score"] = (df["review_score"] <= 2).astype(int)
    df["has_comment"] = df["has_comment"].fillna(0).astype(int)

    # Fill category nulls
    df["product_category_name_english"] = df["product_category_name_english"].fillna("other_unclassified")

    # Export analytical dataset
    output_dir.mkdir(parents=True, exist_ok=True)
    output_parquet = output_dir / "orders_analytical.parquet"
    df.to_parquet(output_parquet, index=False)
    logger.info(f"Successfully created analytical dataset: {output_parquet} ({len(df):,d} records)")

    return df
