TRACK_ID=PS03

# RetailIQ Copilot
> **Data-Grounded Sales & Inventory Intelligence for Store Managers**

RetailIQ Copilot is a enterprise-grade decision support system built for NexusTiQ 24 (Track: Retail, `TRACK_ID=PS03`). It separates **deterministic Python analytics** from **natural-language GenAI explanations** using Google Gemini API to eliminate AI hallucinations, provide 100% evidence-grounded recommendations, and present a complete "Why?" reasoning layer.

---

## 🏛️ Core Design Philosophy

Do NOT build a generic AI chatbot. Build a **DATA-GROUNDED DECISION SUPPORT SYSTEM**.

```
                 ┌──────────────────────────────────┐
                 │          STORE MANAGER           │
                 └────────────────┬─────────────────┘
                                  │
                                  ▼
                 ┌──────────────────────────────────┐
                 │     Natural-Language Question    │
                 └────────────────┬─────────────────┘
                                  │
                                  ▼
                 ┌──────────────────────────────────┐
                 │     Intent + Entity Parser       │
                 │ (Extract products, stores, goals)│
                 └────────────────┬─────────────────┘
                                  │
                                  ▼
                 ┌──────────────────────────────────┐
                 │       DETERMINISTIC ENGINE       │
                 │ - Sales KPIs & Trends            │
                 │ - Inventory Coverage & Risks     │
                 │ - Non-Overlapping Anomaly Rules  │
                 │ - Actionable Recommendation Logic│
                 └────────────────┬─────────────────┘
                                  │
                                  ▼
                 ┌──────────────────────────────────┐
                 │         EVIDENCE PACKAGE         │
                 │ - Exact Metrics & Numbers        │
                 │ - Step-by-Step Calculations      │
                 │ - Configured Business Rules      │
                 │ - Explicit Demand Assumptions    │
                 └────────────────┬─────────────────┘
                                  │
                                  ▼
                 ┌──────────────────────────────────┐
                 │      GEMINI EXPLANATION LAYER    │
                 │ (Translates evidence to human text│
                 │  Refuses if data is insufficient)│
                 └────────────────┬─────────────────┘
                                  │
                                  ▼
                 ┌──────────────────────────────────┐
                 │  GROUNDED ANSWER & RECOMMENDATION │
                 │  + "Why?" Layer & Evidence Drawer│
                 └──────────────────────────────────┘
```

### Deterministic Python vs. GenAI Responsibilities

| Metric / Function | Python Engine | Gemini AI |
| :--- | :---: | :---: |
| Revenue, Units Sold, Stock Levels | ✅ Calculates | ❌ Does NOT calculate |
| Days of Inventory Remaining | ✅ Calculates | ❌ Does NOT calculate |
| Stock-out Risk & Overstock Status | ✅ Classifies | ❌ Does NOT classify |
| Sales Spikes & Drops (% Change) | ✅ Calculates | ❌ Does NOT calculate |
| Natural Language Intent & Entity Extraction | ✅ Parses | 🤖 Augments |
| Grounded Text Explanation | ❌ | ✅ Formats & Explains |
| Actionable Recommendation Rationale | ✅ Rules-based | ✅ Translates |
| Refusal of Non-Existent Products (e.g. iPhone) | ✅ Enforces | ❌ |

---

## ✨ Key Features

1. **Executive Dashboard & "Needs Attention Today"**:
   - Prioritized feed of critical operational risks (imminent stock-outs, demand surges, sales collapses, severe overstock).
   - Every issue displays supporting metrics, why it matters, recommended actions, confidence scores, and an **Evidence Explorer** button.

2. **AI Copilot Chat UI**:
   - Responds to natural-language queries such as *"What is running out?"*, *"Which products should I reorder first?"*, *"Which store is performing best?"*.
   - Never presents unsupported facts or invents numbers.

3. **🔎 Evidence Explorer — "Why am I seeing this?"**:
   - Deep inspection modal showing:
     - **Finding**: Product & Store state.
     - **Supporting Evidence**: Stock quantity, average daily sales velocity, coverage days.
     - **Configured Business Rule**: e.g., `Stock-out risk ≤ 3.0 days` (Source: Application business rule).
     - **Step-by-Step Calculation**: `12 ÷ 5.4 = 2.2 days`.
     - **Conclusion & Recommended Action**.
     - **Explicit Assumptions**: e.g., *"Demand estimate uses previous 14 days of sales."*

4. **Configurable Business Rules Engine**:
   - All rules are configurable via UI and attributed explicitly:
     - Low Stock Threshold: `10 units`
     - Stock-out Risk Threshold: `≤ 3.0 days of coverage`
     - Overstock Threshold: `≥ 45.0 days of coverage`
     - Slow-Moving Threshold: `≥ 14 days without sales`
     - Sales Spike Threshold: `≥ +50.0% increase`
     - Sales Drop Threshold: `≤ -40.0% decrease`

5. **Non-Overlapping Sales Anomaly Detection**:
   - Detects spikes and drops by comparing recent 7-day sales against a **prior 30-day baseline EXCLUDING the recent 7 days** to prevent baseline contamination.

6. **No-Hallucination Guardrails & Refusal**:
   - Asking about non-existent items (e.g., *"How did iPhone sales perform?"*) triggers explicit refusal:
     > *"I couldn't find 'iPhone' in the available retail dataset, so I cannot provide a performance analysis."*

7. **Transparent Gemini Offline Fallback**:
   - If `GEMINI_API_KEY` is missing or network fails, a prominent banner states:
     > *Gemini API unavailable. Displaying deterministic data-grounded analysis.*
   - The entire dashboard and copilot remain 100% functional via Python deterministic templates!

---

## 📊 Dataset Schema

Synthetic 90-day realistic dataset generated in `data/`:
- **Stores** (`stores.csv`): 4 locations (Downtown Flagship, Suburban Mall, Metro Express, Westside Center).
- **Products** (`products.csv`): 60 products across 5 categories (Electronics, Apparel, Grocery, Home Goods, Beauty & Health).
- **Sales** (`sales.csv`): 21,600 daily sales transactions (90 days × 4 stores × 60 products).
- **Inventory** (`inventory.csv`): 21,600 daily inventory stock snapshots.

---

## 🚀 Installation & Running

### Prerequisites
- Python 3.11+ (Tested on Python 3.13)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Environment Variable (Optional)
Set your Google Gemini API key:
```powershell
$env:GEMINI_API_KEY="your-gemini-api-key-here"
```
*(If no API key is provided, RetailIQ Copilot automatically runs in transparent deterministic fallback mode!)*

### Step 3: Run the Application
Start the application using the single entry point command:
```bash
python app.py
```
Open your browser and navigate to:
**`http://localhost:8000`**

---

## 🧪 Testing

Run unit tests covering inventory coverage, zero-division safety, anomaly windows, refusal logic, and recommendation rules:
```bash
pytest
```

---

## 🎬 5-Minute Demo Walkthrough

1. **Scenario 1 — Executive Dashboard**:
   - Open `http://localhost:8000`. Observe Executive KPI cards and the **Needs Attention Today** prioritized operational feed. Click **"Why am I seeing this?"** on Wireless Mouse to open the **Evidence Explorer** modal.

2. **Scenario 2 — Stock-out Risk Query**:
   - Switch to **AI Copilot Chat** tab. Click quick prompt **"What is running out?"**.
   - Review structured answer, coverage calculations, and recommended replenishment actions.

3. **Scenario 3 — Specific Product Risk & Evidence**:
   - Ask **"Why is Wireless Mouse at Store A high risk?"**.
   - Observe deterministic Python calculation breakdown: `Current Stock = 12 units ÷ 5.4 units/day = 2.2 days coverage (Below 3.0-day threshold)`.

4. **Scenario 4 — Anomaly Spikes & Drops**:
   - Ask **"Which products had unusual sales changes this month?"** or switch to the **Sales Anomalies** tab.
   - Inspect non-overlapping 30-day baseline calculations (+800% spike on Mechanical Keyboard vs -85.7% drop on Organic Coffee Beans).

5. **Scenario 5 — No-Hallucination Refusal**:
   - Ask **"How did iPhone sales perform?"**.
   - Observe immediate refusal statement stating iPhone is not present in the dataset, listing available categories.

6. **Scenario 6 — Overstocked & Slow-Moving Action**:
   - Ask **"Show me overstocked products."**.
   - Inspect recommended stock reallocation between Store A (Downtown Flagship) and Store D (Westside Center).

---

## 📄 License & Attribution
NexusTiQ 24 Hackathon Submission — Track: Retail (`TRACK_ID=PS03`). Built with Python, FastAPI, Pandas, and Google Gemini API.
