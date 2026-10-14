import re
import unicodedata
from typing import Optional
import pandas as pd

def normalize_portuguese_text(text: Optional[str]) -> str:
    """
    Normalizes Portuguese text by stripping diacritics/accents,
    lowercasing, and cleaning irregular punctuation and whitespace.
    Example: 'Não recebi o produto, péssimo!' -> 'nao recebi o produto pessimo'
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # Normalize unicode to NFKD (separates base characters from diacritical marks)
    nfkd = unicodedata.normalize("NFKD", text)
    # Filter out non-spacing diacritical marks (e.g. ~, ^, `, ´, ç cedilla)
    stripped = "".join([c for c in nfkd if not unicodedata.combining(c)])
    
    # Lowercase
    cleaned = stripped.lower()
    # Replace newlines, tabs, and multiple spaces with a single space
    cleaned = re.sub(r"[\r\n\t]+", " ", cleaned)
    # Remove special punctuation but keep basic alphanumeric and spaces
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    # Collapse multiple spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    
    return cleaned


def clean_categories(
    products_df: pd.DataFrame, 
    translations_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Merges products with category translations and fills missing values.
    """
    merged = products_df.merge(
        translations_df, 
        on="product_category_name", 
        how="left"
    )
    # If English translation is missing, fallback to raw name, else 'other_unclassified'
    merged["product_category_name_english"] = (
        merged["product_category_name_english"]
        .fillna(merged["product_category_name"])
        .fillna("other_unclassified")
    )
    return merged
