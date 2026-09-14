# Buy or Wait? — Autonomous Financial Decision & Affordability Agent

Built for **HackerRank Orchestrate (September 2026)**.

An autonomous, multimodal financial decision agent that evaluates user expense requests, forecasts 90-day cash flow, resolves pending commitments and variable essential spending, and provides personalized, risk-averse payment recommendations.

---

## 1. System Architecture & Core Methodology

The solution employs a high-precision, hybrid architecture combining **Multimodal Vision-Language Models (VLM)** for document extraction with a **Deterministic Cashflow Simulation Engine** for mathematical guarantees.

```text
+------------------------------+
              | 16 Document Images (Receipts)|
              +--------------+---------------+
                             | VLM Extraction (Gemini Flash)
                             v
+------------------+ +------------------+ +---------------------+
| requests.csv |--->| FinancialDecision|<---| financial_events.csv|
| (250 requests) | | Engine | | financial_profiles |
+------------------+ +--------+---------+ +---------------------+
| 90-Day Simulation & Rule Ranking
v
+-----------------------+
| output.csv (Root) |
| (Verified Schema) |
+-----------------------+
```

### Key Architectural Pillars:
1. **Deterministic 90-Day Ledger Simulation:**
   - Instead of naive balance checks, the engine models daily net balance over 90 days.
   - Guarantees that at every single point throughout the 90-day window, the balance never falls below `minimum_balance_to_keep`.
   - Calculates `amount_safe_to_pay` strictly before optional spending changes.

2. **Multimodal Document Extraction (VLM):**
   - 16 financial events with blank amounts were resolved by extracting settled amounts directly from tax invoices, utility bills, and salary statements (`dataset/media/images/*.png`) using structured JSON extraction.
   - Extracted amounts were cached to `dataset/extracted_image_amounts.json` to guarantee offline evaluation and zero redundant API calls.

3. **Untrusted Data & Prompt Injection Defense:**
   - All text messages (`messages.csv`) and receipt contents are treated as untrusted user inputs.
   - Robust regex and semantic entity extraction ignore reference codes (e.g. `EMP-xxxx`) and adversarial instructions, extracting strictly verifiable dates and monetary values.

4. **Multi-Tier Plan Ranking (6-Tier Hierarchy):**
   When multiple safe payment approaches exist, the arbiter ranks them strictly according to contest rules:
   1. Complete full request by `desired_completion_date`.
   2. Require no spending changes.
   3. Minimize total payable amount (including financing fees).
   4. Start payment earlier.
   5. Fewer payments (lower installment count).
   6. Lowest `payment_option_id` as tie-breaker.

---

## 2. Directory Structure

```text
├── code/
│   ├── engine.py                 # Core 90-day simulation & ranking logic
│   └── main.py                   # Submission CLI entry point
├── dataset/                      # Contest datasets & media
├── evaluation/
│   └── usage_report.md           # Token usage and cost audit
├── log.txt                       # Session & interaction audit trail (AGENTS.md compliant)
├── output.csv                    # Final 250 predictions
└── README.md                     # Architectural documentation
```

---

## 3. Quick Start & Execution

### Prerequisites
- Python 3.11+
- Dependencies: pandas, pydantic, python-dotenv

### Run the Prediction Pipeline
Run the entry point from the repository root:
```bash
python code/main.py
``` 

### Validation

```bash

python validate_output.py
```