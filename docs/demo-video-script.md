# TradeForensics — Demo Video Script (2.5 - 3 Minutes)

**Hackathon:** AMD Developer Hackathon ACT III (Track 3: Reinvent Commerce)  
**Team:** RyzenShine  
**Target Audience:** Hackathon Judges, E-Commerce Operations Executives, Technical Evaluators  
**Tone:** Authoritative, crisp, empirical, and mission-critical.

---

## Video Overview & Timing Structure

| Section | Time | Focus | Visual Action |
|---|---|---|---|
| **1. Hook & The Dilemma** | 0:00 – 0:25 (25s) | Siloed data & "RAG for numbers" failure | Show disconnected spreadsheets vs TradeForensics UI |
| **2. Operational Ground Truth** | 0:25 – 0:55 (30s) | Deterministic baselines & the 5.75x rule | Dashboard KPIs, late delivery spikes, correlation curves |
| **3. Forensic Investigation** | 0:55 – 1:40 (45s) | Decoupled Sellers & Products views + LightGBM + ChromaDB | Navigate Sellers, click Evidence Drawer, show LightGBM SHAP + Portuguese reviews |
| **4. Copilot Action Plan** | 1:40 – 2:20 (40s) | Un-hallucinated remediation + Ask Copilot | Click "Generate Action Plan", show structured checklist with effort badges |
| **5. AMD Hardware & Wrap-Up** | 2:20 – 2:50 (30s) | AMD Instinct MI300X, ROCm, high memory bandwidth | Show Fireworks AMD toggle, architecture diagram, concluding impact |

---

## Detailed Script & Teleprompter

### 0:00 – 0:25 | Scene 1: The Problem — The Disconnected Signals Dilemma
* **Visual:** Open with the TradeForensics interface, showing the deep black & crimson command center. Cut briefly to a title slide: *TradeForensics: Operational Diagnostics & Action Copilot for E-Commerce*.
* **Voiceover:**
  > "In high-volume e-commerce, operators are drowning in siloed signals. Transaction logs track revenue, warehouse carriers log delivery times, and customers leave emotionally charged reviews. 
  > 
  > When satisfaction crashes, operators guess: Was it late freight? Product quality? Or misleading listings?
  > 
  > Most AI tools fail here because **Vector Databases are not calculators**. Throwing numbers into an LLM produces hallucinated statistics and zero accountability. 
  > 
  > Welcome to **TradeForensics** — built by Team RyzenShine for the AMD Developer Hackathon."

---

### 0:25 – 0:55 | Scene 2: Operational Ground Truth — The 5.75x Dissatisfaction Multiplier
* **Visual:** Smooth zoom into the **Hero Ground Truth Banner** and the 4 top KPI cards (98,666 Total Orders, 8.11% Late Delivery Rate, 14.23% Low Rating Share, 62.4 Health Score). Hover over the *Fulfillment Delay Distribution* chart.
* **Voiceover:**
  > "TradeForensics replaces guesswork with mathematical ground truth across 98,666 real-world orders. 
  > 
  > Our deterministic analytics engine immediately surfaces the core operational rule:
  > **Late shipments carry a 5.75x dissatisfaction multiplier.**
  > On-time deliveries carry just a 9.21% low-rating rate. The moment a delivery deadline is missed, negative reviews surge to 52.98%. 
  > 
  > Every baseline metric is deterministic SQL and DuckDB — zero hallucinations."

---

### 0:55 – 1:40 | Scene 3: Forensic Slicing — Sellers, Products & Hybrid AI
* **Visual:** 
  1. Click on the **Sellers** tab in the sidebar. Show the dedicated merchant accounts table, state filters (SP, PR, RJ), and seller-level late delivery deltas.
  2. Click on the **Products** tab. Show catalog categories mapped across Heavy Furniture, Electronics, Fashion, and Home Living.
  3. Click **Evidence** on `office_furniture` (or top problem seller `1ca7077d`). The **Evidence Detail Drawer** slides out from the right.
* **Voiceover:**
  > "In TradeForensics, Sellers and Product Catalogs are decoupled forensic dimensions — mirroring our persistent ChromaDB vector collections.
  > 
  > When we inspect `office_furniture`, our drawer reveals the hybrid ML pipeline:
  > First, our **97.00% accurate NLP classifier** tags customer complaints into concrete failure modes.
  > Second, our **0.9071 ROC-AUC LightGBM model** calculates exact feature attribution — showing that freight ratio and delay days explain over 78% of negative review variance.
  > Third, **embedded ChromaDB vector RAG** retrieves authentic Portuguese customer quotes proving the defect."

---

### 1:40 – 2:20 | Scene 4: Action Copilot — Evidence-Grounded Remediation
* **Visual:** Click **AI Plan** (or the red button in drawer). The **Action Plan Modal** appears with loading animation, then renders the executive diagnosis and prioritized checklist with `LOW`, `MEDIUM`, `HIGH` effort badges. Then type in "Ask Copilot": *"Why is freight ratio the top complaint driver?"* and hit Enter.
* **Voiceover:**
  > "Once the evidence packet is locked, we engage the **TradeForensics Action Copilot**.
  > 
  > Notice the strict guardrails: the LLM is prohibited from inventing numbers. It synthesizes an executive diagnosis and an actionable remediation checklist with assigned teams and effort badges.
  > 
  > Merchants can also ask targeted operational questions in natural language and receive instant, evidence-grounded answers with cited metrics."

---

### 2:20 – 2:50 | Scene 5: AMD Instinct Hardware & Closing Impact
* **Visual:** Transition to the architecture slide / `.env` toggle showing `LLM_PROVIDER=fireworks` pointing to AMD Instinct MI300X, and show the terminal / `docs/amd-workload-evidence.md`.
* **Voiceover:**
  > "Under the hood, TradeForensics is engineered for **AMD Instinct accelerators**.
  > 
  > Processing high-density multi-seller evidence packets requires massive memory bandwidth. On **AMD Instinct MI300X with 192GB of HBM3 memory at 5.3 terabytes per second**, TradeForensics achieves 68 tokens per second with 200 millisecond time-to-first-token.
  > 
  > With our pluggable Fireworks AI adapter and native ROCm 6.2 Docker blueprint, deployment is instantaneous.
  > 
  > TradeForensics: Turning raw transaction chaos into decisive operational execution. Powered by AMD."

---

## Recording Checklist for the Presenter
- [ ] Screen resolution set to 1920x1080 (1080p) or 4K with 100% DPI scaling.
- [ ] Browser in Fullscreen (`F11`) with clean address bar.
- [ ] Both Backend (`uvicorn`) and Frontend (`vite`) running smoothly.
- [ ] Microphone audio normalized (no background fan noise or echo).
- [ ] Cursor movements steady and deliberate; pause 1-2 seconds after opening modals/drawers.
