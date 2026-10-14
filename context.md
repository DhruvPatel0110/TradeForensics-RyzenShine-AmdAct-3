# AMD Developer Hackathon ACT III — Reinvent Commerce
## Project Blueprint: TradeForensics (Hybrid ML + Semantic RAG)

**Team:** RyzenShine  
**Project Name:** TradeForensics  
**Tagline:** Statistical Root-Cause Forensics & Action Copilot for E-Commerce  
**Working Source of Truth**  
**Last Updated:** 14 October 2026  
**Hackathon:** AMD Developer Hackathon: ACT III  
**Track:** Track 3 — Reinvent Commerce  
**Official Portal:** https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-iii  
**Submission Deadline:** 18 October 2026, 8:30 PM IST (Hard freeze target: 17 October 2026)  
**Development Workflow:** Antigravity locally + GitHub repository  
**Environment Isolation:** Dedicated Python Virtual Environment (`.venv`) for backend isolation to prevent global package conflicts and ensure pristine deployment dependencies.  

---

# 1. Executive Summary

### 1.1 The Problem
E-commerce merchants and marketplace operators struggle with disconnected signals:
- Transaction logs show orders, dates, and freight costs.
- Fulfillment systems record dispatch and delivery delays.
- Customer reviews contain emotional, unstructured Portuguese feedback.

When customer satisfaction drops (1-star or 2-star ratings spike), merchants cannot easily answer:
1. *Is the problem driven by carrier delivery delays, high shipping costs, or product listing inaccuracies?*
2. *What exact customer complaints validate this statistical trend?*
3. *What prioritized operational steps should be taken to fix it?*

### 1.2 The Solution: TradeForensics
An **evidence-grounded operational diagnostic and forensics tool** combining:
1. **Deterministic Analytics & SQL (Pandas / DuckDB):** Authoritative computation of baseline KPIs, delay rates, and rating distributions.
2. **Predictive Tabular ML (LightGBM):** Classifies customer dissatisfaction risk ($\le 2$ stars) and quantifies **Feature Importance** (e.g., Delay Days: 56%, Freight Ratio: 24%, Catalog Mismatch: 20%).
3. **Semantic Review RAG (ChromaDB):** Local vector search retrieving the actual voice of the customer (representative Portuguese complaint quotes).
4. **LLM Copilot (Groq / AMD Instinct Bridge):** Synthesizes quantitative stats + ML feature importance + qualitative customer quotes into a structured, prioritized operational action plan.

---

# 2. Architectural Blueprint: The Hybrid Engine

### 2.1 The Philosophy: Avoiding the "RAG for Numbers" Trap
* **Vector DBs are not calculators:** Embeddings cannot compute sums, averages, or understand numeric comparisons ($35\% > 18\%$). Tabular data must remain in SQL / Pandas.
* **Vector DBs excel at Semantic Retrieval:** Embeddings are used specifically for searching unstructured review comments and complaint themes.

```
                      ┌────────────────────────────────────────────────────────┐
                      │              KAGGLE OLIST DATASET (~100k)              │
                      └──────────────────────────┬─────────────────────────────┘
                                                 │
                     ┌───────────────────────────┴────────────────────────────┐
                     ▼                                                        ▼
         [Tabular Data (Numbers)]                                 [Unstructured Review Text]
        Orders, Dates, Freight, Prices                            Portuguese comments, feedback
                     │                                                        │
                     ▼                                                        ▼
         [Pandas / DuckDB + ML]                                   [NLP Cleaning & Embeddings]
       • Exact KPIs (delay rate, ratings)                         • Sentence-Transformers (multilingual)
       • Random Forest: Dissatisfaction Risk &                    • Embedded Vector DB (ChromaDB)
         Feature Importance (Delay vs Freight vs Catalog)                     │
                     │                                                        │
                     └───────────────────────────┬────────────────────────────┘
                                                 │
                                                 ▼
                              ┌──────────────────────────────────────┐
                              │            HYBRID RETRIEVAL          │
                              │ 1. SQL gives exact stats & ML score  │
                              │ 2. Vector DB retrieves the top 5     │
                              │    semantic complaint reviews        │
                              └──────────────────┬───────────────────┘
                                                 │
                                                 ▼
                              ┌──────────────────────────────────────┐
                              │           LLM / COPILOT              │
                              │  (Fireworks on AMD Instinct / Local) │
                              │  Synthesizes numbers + real customer │
                              │  quotes into a precise action plan   │
                              └──────────────────┬───────────────────┘
                                                 │
                                                 ▼
                              ┌──────────────────────────────────────┐
                              │         REACT VITE DASHBOARD         │
                              │  Store Health | Issue Explorer |     │
                              │  AI Grounded Action Plan             │
                              └──────────────────────────────────────┘
```

---

# 3. Data Pipeline & Normalization

### 3.1 Primary Dataset
**Brazilian E-Commerce Public Dataset by Olist (Kaggle)** (~100,000 orders, 2016–2018).

Key tables utilized:
- `olist_orders_dataset.csv`: Purchase date, estimated delivery, actual delivery, order status.
- `olist_order_items_dataset.csv`: Item price, freight value, seller ID, product ID.
- `olist_order_reviews_dataset.csv`: Review score (1–5), review title, review comment message.
- `olist_products_dataset.csv`: Category name, dimensions, weight.
- `product_category_name_translation.csv`: Portuguese-to-English category translations.
- `olist_sellers_dataset.csv` & `olist_customers_dataset.csv`: State/city geographical locations.

### 3.2 Cleaning & Normalization Rules
1. **Unicode & Text Normalization:**
   - Brazilian Portuguese text contains accents (`ç`, `ã`, `é`, `ó`). Use `unicodedata.normalize('NFKD')` to strip diacritics for uniform search and tokenization.
   - Filter empty reviews (5-star reviews often leave comments blank; 1-star reviews almost always detail specific complaints).
2. **Join Grain Safety:**
   - Orders can have multiple items and sellers. Pre-aggregate items to order level before joining to reviews to prevent row duplication and inflated totals.
3. **Category Translations:**
   - Normalize category names using the translation dictionary; map missing categories to `other_unclassified`.
4. **Delivery Delta Calculations:**
   - `delay_days = max(0, (actual_delivery_date - estimated_delivery_date).days)`.
   - `transit_days = (actual_delivery_date - order_purchase_timestamp).days`.

---

# 4. Analytics & Classical Machine Learning Layer

### 4.1 Deterministic KPI Engine (Pandas / DuckDB)
- **Late Delivery Rate:** Percentage of delivered orders delivered after estimated date.
- **Low-Score Share:** Percentage of reviews with score $\le 2$ stars.
- **Baseline Delta:** Segment metric minus store-wide baseline (with minimum sample size filters, e.g., $N \ge 50$ reviews).
- **Issue Ranking Formula:** $\text{Severity} = (\Delta_{\text{low\_score}} \times 0.6 + \Delta_{\text{late\_delivery}} \times 0.4) \times \log_{10}(N_{\text{reviews}})$.

### 4.2 Tabular ML: Dissatisfaction Risk & Driver Analysis (LightGBM)
- **Model:** `LGBMClassifier` (LightGBM with histogram-based gradient boosting).
- **Why LightGBM:** High-speed training on ~100k tabular rows, native handling of skewed features, and built-in TreeSHAP feature attribution.
- **Target Variable:** Binary low-rating indicator (`is_low_score = 1` if review score $\le 2$, else `0`).
- **Engineered Features:**
  - `delay_days`: Days past estimated delivery.
  - `transit_days`: Total transit duration.
  - `freight_ratio`: `freight_value / (price + freight_value)`.
  - `product_weight_g`, `product_volume_cm3`.
  - `is_interstate`: Whether seller state $\ne$ customer state.
  - `price`: Item price tier.
  - `complaint_topic`: Predicted root cause from the NLP classifier.
- **Outputs Produced for the Copilot:**
  1. **Dissatisfaction Risk Probability ($0–100\%$):** Estimated risk for a given segment or pending order batch.
  2. **Feature Importance (Gain / TreeSHAP):** Statistical ranking of root-cause drivers (e.g., *"Delay Days explains 56% of negative variance, Freight Ratio explains 24%, Catalog Mismatch explains 20%"*).

---

# 5. NLP & Semantic Vector Store (RAG Layer)

### 5.1 NLP Review Root-Cause Classifier
- **Model:** `TfidfVectorizer(max_features=5000, ngram_range=(1,2))` + `LogisticRegression(class_weight='balanced')`.
- **Purpose:** Automatically categorizes all ~40,000 Portuguese text comments into 4 distinct operational complaint topics:
  1. `DELIVERY_DELAY` ("atraso", "demorou", "prazo", "nao chegou")
  2. `DAMAGED_DEFECTIVE` ("quebrado", "defeito", "estragado", "pessima qualidade")
  3. `CATALOG_MISMATCH` ("tamanho errado", "cor diferente", "veio errado", "propaganda enganosa")
  4. `SERVICE_REFUND` ("nao respondem", "cancelamento", "estorno", "atendimento péssimo")
- **Integration:** The predicted complaint tag feeds directly into the LightGBM model and acts as a filter for semantic retrieval.

### 5.2 Vector Database: Embedded ChromaDB
- **Technology:** `chromadb` (runs locally in-memory or persisted in a local directory; 100% free, zero cloud infrastructure).
- **Embedding Model:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (Dense 384-d vectors, trained on 50+ languages including Brazilian Portuguese, lightweight CPU inference).
- **Document Payload:**
  ```json
  {
    "id": "review_order_12345",
    "text": "Produto chegou com duas semanas de atraso e a embalagem estava rasgada.",
    "metadata": {
      "order_id": "...",
      "category": "cama_mesa_banho",
      "seller_id": "...",
      "review_score": 1,
      "delay_days": 14,
      "complaint_topic": "DELIVERY_DELAY"
    }
  }
  ```

### 5.3 Semantic Query Flow
When an issue is selected (e.g., *Category: Bed & Bath, elevated low reviews*):
1. Query ChromaDB filtered by `category = "cama_mesa_banho"` and `review_score <= 2`.
2. Semantically rank complaints against topic probes (*"atraso entrega embalagem defeito"*).
3. Retrieve top 3–5 representative customer review excerpts to include as qualitative evidence in the Copilot prompt.

---

# 6. LLM Copilot & Structured Action Engine

### 6.1 Free Primary LLM Provider: Groq API
- **Model:** `llama-3.3-70b-versatile` (or `llama-3.1-8b-instant`) via the **Groq API**.
- **Cost:** Free tier (generous RPM/TPM limits, ultra-fast sub-second generation).
- **Structured JSON Mode:** Enforced using Groq's `response_format={"type": "json_object"}`.

### 6.2 The Synthesis Prompt
The LLM acts as an executive commerce operations analyst. It receives a strictly bounded **Evidence Packet**:
- **Segment Metadata:** Category/Seller name, order volume, date range.
- **Deterministic Metrics:** Exact late delivery rate, low-score share, store baseline comparison.
- **LightGBM Driver Breakdown:** Feature importance percentages (gain / SHAP).
- **Qualitative Evidence:** Top 3–5 semantically retrieved customer review quotes.

### 6.3 Strict Guardrails
- **No Hallucinated Math:** The LLM is strictly prohibited from computing numbers or statistics; it can only reference numbers present in the provided evidence packet.
- **Untrusted Review Content:** Review quotes are parsed as untrusted text to prevent prompt injection.
- **Actionability:** Generates 2–4 practical operational remedies with effort ratings (Low/Medium/High).

### 6.4 Structured Output Schema (JSON)
```json
{
  "summary": "Short evidence-grounded diagnosis",
  "severity": "critical | high | medium | low",
  "ml_risk_assessment": {
    "dissatisfaction_risk_score": 0.82,
    "top_drivers": [
      { "feature": "delay_days", "importance_pct": 56.4 },
      { "feature": "freight_ratio", "importance_pct": 23.8 },
      { "feature": "catalog_mismatch", "importance_pct": 19.8 }
    ]
  },
  "quantitative_evidence": [
    { "metric": "low_score_share", "value": "31.4%", "baseline": "18.2%", "sample_size": 340 }
  ],
  "qualitative_evidence": [
    { "review_snippet": "Produto chegou quebrado e atrasou 10 dias", "theme": "Logistics / Damage" }
  ],
  "recommended_actions": [
    {
      "action": "Audit carrier SLA for Southeast to Northeast routes",
      "rationale": "56.4% of negative review variance is explained by delivery delays",
      "effort": "low | medium | high",
      "expected_effect": "Reduce late-delivery rate by 15-20% in this corridor"
    }
  ],
  "limitations": [
    "Analysis based on historical 2016-2018 Olist data; live inventory was unavailable"
  ]
}
```

---

# 7. AMD Hardware Bridge & Inference Strategy

### 7.1 Pluggable LLM Adapter
The backend isolates inference calls behind a pluggable `LLMClient`:
- **Development & Local Testing:** `LLM_PROVIDER=groq` (runs for free using Groq API).
- **Hackathon AMD Compliance:** `LLM_PROVIDER=fireworks` (pointing to Fireworks AI running on **AMD Instinct GPUs**).
- Switching requires altering only a single environment variable in `.env`.

### 7.2 AMD Workload Evidence
- When AMD credits or access arrive, run live inference through the Fireworks/AMD Instinct endpoint.
- Save execution traces, token latency, and logs into `docs/amd-workload-evidence.md`.
- Include a direct AMD ROCm Docker deployment script for bare-metal compliance proof.

---

# 8. User Interface Plan (React + Vite)

A modern, responsive merchant operations console:

### 1. Store Health (Overview)
- Metric KPI cards: Total Orders, Late Delivery Rate, Low-Rating Share, Overall Health Score.
- Interactive distribution charts: Delivery delay days vs. review scores.
- "High-Priority Friction Points" alert banner.

### 2. Issue Explorer
- Ranked list of detected operational friction points (by volume $\times$ baseline deviation).
- Filter by category, seller, or issue type.
- Detail drawer: Shows deterministic metrics, ML feature importance bar chart, and semantically retrieved customer quotes.

### 3. Copilot Action Plan
- Interactive "Generate Action Plan" button triggering the hybrid LLM synthesis.
- Clean presentation of diagnosis, prioritized operational checklist with effort badges, and evidence citations.
- Disclaimer banner on historical data scope and AMD-powered inference status.

---

# 9. API Surface (FastAPI)

- `GET /api/health` — System status, dataset load state, vector DB status, active LLM provider.
- `GET /api/overview` — Store-wide KPIs and performance distributions.
- `GET /api/issues` — Ranked detected issues across categories and sellers.
- `GET /api/issues/{issue_id}/evidence` — Deterministic stats + ML drivers + semantic review quotes.
- `POST /api/action-plan` — Trigger LLM synthesis for a selected issue packet.
- `POST /api/ask` — Natural language query over store metrics and reviews.

---

# 10. Repository Structure

```text
merchant-action-copilot/
├── README.md
├── context.md
├── requirements.txt
├── .env.example
├── .gitignore
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── overview.py
│   │   │   ├── issues.py
│   │   │   └── copilot.py
│   │   ├── data/
│   │   │   ├── loader.py
│   │   │   └── cleaner.py
│   │   ├── ml/
│   │   │   ├── train_risk_model.py
│   │   │   └── risk_predictor.py
│   │   ├── rag/
│   │   │   ├── indexer.py
│   │   │   └── vector_store.py
│   │   └── llm/
│   │       ├── client.py
│   │       ├── prompts.py
│   │       └── schemas.py
│   └── tests/
│       ├── test_kpis.py
│       └── test_hybrid_flow.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/api.js
├── data/
│   ├── raw/                 # Olist CSVs (gitignored)
│   └── processed/           # Processed parquet & chroma db index
└── docs/
    ├── architecture.md
    └── amd-workload-evidence.md
```

---

# 11. Phased Execution Plan

- [ ] **Phase 0: Environment & Core Setup**
  - Scaffold repository structure, Python virtual environment, dependencies (`fastapi`, `uvicorn`, `pandas`, `scikit-learn`, `chromadb`, `sentence-transformers`).
  - Set up `.env.example` and pluggable `LLMClient` with working mock mode.
- [ ] **Phase 1: Data Processing & KPIs**
  - Ingest and clean Olist datasets (orders, items, reviews, products).
  - Implement deterministic KPI calculations and issue ranking rules.
- [ ] **Phase 2: Tabular ML & Semantic Vector Store**
  - Train the Random Forest low-rating risk model; export feature importance.
  - Embed customer reviews into local ChromaDB with metadata filters.
- [ ] **Phase 3: Hybrid FastAPI Endpoints**
  - Wire up `/api/overview`, `/api/issues`, and `/api/action-plan` combining SQL stats + ML drivers + Chroma review snippets.
- [ ] **Phase 4: React + Vite Frontend Dashboard**
  - Build Store Health, Issue Explorer, and Copilot Action Plan screens with rich aesthetics.
- [ ] **Phase 5: AMD Inference Integration & Submission**
  - Plug in Fireworks AMD Instinct credentials once available; capture execution logs.
  - Record 2–3 minute demo video, finalize pitch presentation, and submit to Lablab portal.
