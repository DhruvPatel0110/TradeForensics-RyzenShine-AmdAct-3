# TradeForensics — Presentation Slide Deck & Submission Guide

**Hackathon:** AMD Developer Hackathon ACT III  
**Track:** Track 3: Reinvent Commerce  
**Team:** RyzenShine  
**Repository:** [github.com/DhruvPatel0110/TradeForensics-RyzenShine-AmdAct-3](https://github.com/DhruvPatel0110/TradeForensics-RyzenShine-AmdAct-3)  

---

## 7-Slide Pitch Deck Structure

### Slide 1: Title & The Mission
* **Headline:** TradeForensics
* **Sub-headline:** Statistical Root-Cause Forensics & Action Copilot for E-Commerce
* **Hook:** Connecting transaction logs, fulfillment latency, and unstructured Portuguese customer reviews into auditable root-cause drivers and actionable operational remediation plans.
* **Badges:** AMD Developer Hackathon ACT III • Track 3: Reinvent Commerce • Team RyzenShine
* **Visual:** Screenshot of the TradeForensics command center with the Baskerville Old Face typography and red-black minimalist aesthetic.

---

### Slide 2: The Problem — The "RAG for Numbers" Trap
* **The Reality:** E-commerce operators navigate three disconnected silos:
  1. Transaction logs (prices, freight ratios, item counts).
  2. Carrier fulfillment tracking (dispatch latency, transit delays).
  3. Qualitative feedback (unstructured Portuguese reviews).
* **The Industry Flaw:** Most modern AI startups attempt to embed tabular numbers into vector databases or dump CSVs into LLM prompts.
  * **Vector DBs are not calculators:** Embeddings cannot compute sums, averages, or understand mathematical thresholds ($31.4\% > 14.2\%$).
  * **Pure LLMs hallucinate calculations:** They invent metrics and deliver un-auditable advice.
* **The Result:** Operators are paralyzed by disconnected dashboards and guesswork when customer satisfaction drops.

---

### Slide 3: The Architecture — 4-Tier Hybrid Forensics
* **The Solution:** A strictly bounded hybrid pipeline that separates math from reasoning:
  1. **Deterministic Analytics Engine (Pandas / DuckDB):** Calculates exact baseline KPIs, fulfillment SLA breaches, and delta shifts across 98,666 real-world orders with mathematical precision.
  2. **NLP Portuguese Root-Cause Classifier:** Evaluates 40,162 customer reviews to categorize complaints into 4 operational failure modes (`DELIVERY_DELAY`, `DAMAGED_DEFECTIVE`, `CATALOG_MISMATCH`, `SERVICE_REFUND`) at **97.00% accuracy**.
  3. **LightGBM Tabular Risk Attribution:** Predicts dissatisfaction risk ($\le 2$ stars) with **0.9071 ROC-AUC** and computes exact feature importance gain (% attribution to delay days, freight ratio, etc.).
  4. **ChromaDB Vector Store:** Retrieves authentic customer complaint quotes to provide qualitative proof.
  5. **Action Copilot on AMD Instinct:** Synthesizes prioritized operational remediation checklists bounded strictly by the evidence packet (zero mathematical hallucination).

---

### Slide 4: Empirical Discoveries & Ground Truth
* **Dataset:** Brazilian E-Commerce Public Dataset by Olist (98,666 unique orders, 2016–2018).
* **The 5.75x Dissatisfaction Multiplier:**
  * Low-rating rate for on-time deliveries: **9.21%**
  * Low-rating rate when delivery deadline is missed: **52.98%**
  * *Missing a delivery SLA multiplies customer dissatisfaction by 5.75x.*
* **NLP Classifier Performance:**
  * **97.00% Overall Accuracy** | **0.9414 Macro F1** | **0.9703 Weighted F1** on 5,160 held-out test Portuguese comments.
* **LightGBM Model Performance:**
  * **0.9071 ROC-AUC** on held-out test split, surfacing that `delay_days` and `freight_ratio` drive over 70% of dissatisfaction variance.

---

### Slide 5: The Product Experience
* **Executive Store Health Dashboard:** Real-time visibility into overall store volume, late delivery rates, and delay-versus-dissatisfaction correlation curves.
* **Decoupled Forensic Dimensions:**
  * **Sellers View:** Dedicated forensics for marketplace merchant accounts, hub location filters (SP, PR, RJ), SLA breaches, and account remediation.
  * **Products View:** Catalog forensics categorizing 30 distinct product categories across Heavy Furniture, Electronics, Fashion, and Home Living.
* **Evidence Detail Drawer:** Side-by-side auditable view of baseline metrics, LightGBM feature gain bars, and authentic Portuguese review quotes.
* **Action Copilot:** One-click generation of structured remediation plans with `LOW`, `MEDIUM`, and `HIGH` effort badges, plus interactive grounded Q&A.

---

### Slide 6: AMD Instinct Hardware Acceleration
* **Why AMD Instinct Matters:** Synthesizing multi-seller audits across large enterprise marketplaces requires processing dense, multi-table evidence packets at high batch concurrency.
* **AMD Instinct™ MI300X Advantage:**
  * **192 GB HBM3 Memory:** Houses full 70B parameter models in a single accelerator without tensor-parallel sharding bottlenecks.
  * **5.3 TB/s Memory Bandwidth:** Delivers sub-210ms Time-to-First-Token and 68+ tokens/sec sustained generation speed on memory-bound structured decode.
* **Dual Deployment Pipeline:**
  * **Cloud:** Fireworks AI OpenAI-compatible endpoint running on AMD Instinct clusters (1-line toggle in `.env`).
  * **On-Premise:** Native AMD ROCm™ 6.2 + vLLM Docker container (`Dockerfile.rocm`) for private enterprise deployment.

---

### Slide 7: Commercial Viability & Next Horizon
* **Target Customers:** Multi-vendor marketplaces (Amazon, Mercado Libre, Shopify Plus) and high-volume merchant aggregators.
* **Business ROI:**
  * Prevents costly chargebacks and seller churn by detecting fulfillment breakdowns 2–3 weeks before review sentiment collapses.
  * Replaces manual operations audit spreadsheets with instantaneous, evidence-grounded action plans.
* **Future Roadmap:**
  * Real-time Kafka integration for live shipping webhook streaming.
  * Fine-tuned Portuguese SLM (Llama 3.2 3B) running on AMD Ryzen™ AI NPUs for client-side edge forensics.

---

## Lablab.ai Submission Template

### Project Title
**TradeForensics — Statistical Root-Cause Forensics & Action Copilot for E-Commerce**

### Tagline / Short Pitch
Connecting transaction logs, fulfillment latency, and customer reviews into deterministic root-cause drivers and actionable operational remediation plans — accelerated by AMD Instinct.

### Hackathon Track
**Track 3: Reinvent Commerce** (AMD Developer Hackathon ACT III)

### Problem Statement
In high-volume e-commerce, operators struggle with fragmented data: financial transactions in SQL, carrier delivery milestones in logistics tools, and unstructured reviews in customer service inboxes. When 1-star reviews spike, operators are left guessing. Generic AI tools fail because vector embeddings cannot perform mathematical calculations, leading to hallucinated numbers and un-auditable advice.

### The Solution
TradeForensics combines deterministic data science with generative reasoning. It mathematically computes baseline anomalies across 98,666 real-world orders, classifies Portuguese reviews with a 97.00% accurate NLP model, predicts low-score risk with a 0.9071 ROC-AUC LightGBM model, retrieves qualitative customer quotes via ChromaDB, and passes a bounded evidence packet to an AMD Instinct-accelerated Action Copilot to generate prioritized remediation checklists.

### How We Built It
- **Backend:** FastAPI, Python 3.11+, DuckDB / Pandas for baseline metrics.
- **ML & NLP:** LightGBM with tree feature attribution (gain/split), Scikit-Learn TF-IDF logistic classifier for Brazilian Portuguese reviews.
- **Vector RAG:** ChromaDB with `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- **Generative AI:** Bounded LLM inference producing validated Pydantic JSON action plans.
- **Frontend:** React 19 + Vite, custom minimalist red-black design system, Baskerville Old Face typography.

### How We Used AMD Hardware
TradeForensics is engineered for the high memory bandwidth of **AMD Instinct™ MI300X and MI250 accelerators**:
1. **Fireworks AI AMD Instinct Inference:** Zero-latency generation of validated Pydantic JSON action plans powered by Llama 3.3 70B Instruct deployed on AMD Instinct MI300X clusters (sub-210ms TTFT, 68 tokens/sec).
2. **Pluggable Architecture:** A 1-line environment switch (`LLM_PROVIDER=fireworks`) enables instant deployment to AMD hardware.
3. **Turnkey ROCm 6.2 Container:** Includes a verified `Dockerfile.rocm` blueprint utilizing AMD ROCm 6.2 and vLLM for on-premise enterprise deployments.
