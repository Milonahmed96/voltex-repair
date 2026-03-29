# 🔧 Voltex Repair Triage Agent

> LangGraph-powered agentic repair routing for Voltex Retail — a fictional UK omnichannel technology and appliances retailer built as an AI engineering simulation project.

[![CI](https://github.com/Milonahmed96/voltex-repair/actions/workflows/ci.yml/badge.svg)](https://github.com/Milonahmed96/voltex-repair/actions/workflows/ci.yml)
[![Live Demo](https://img.shields.io/badge/live%20demo-streamlit-FF4B4B)](https://voltex-repair-ma.streamlit.app/)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Tests](https://img.shields.io/badge/tests-49%20passing-brightgreen)
![Evaluation](https://img.shields.io/badge/evaluation-81.0%25-brightgreen)

---

## Live Demo

🚀 **[Try Voltex Repair Triage Agent here](https://voltex-repair-ma.streamlit.app/)**

> **Suggested test scenarios:**
> - **📱 Phone liquid damage** — spill coffee on phone, VoltCare Complete → HIGH urgency, Newark, escalate
> - **❄️ Fridge BER test** — old fridge compressor failure → repair cost exceeds 65% of product value → Replace
> - **💻 Laptop screen crack** — dropped laptop, VoltCare Plus → Tech Bar, same day, excess applies
> - **🔍 Ambiguous fault** — vague description → LOW confidence → escalation triggered

---

## What This Is

Voltex Repair Triage Agent is a LangGraph ReAct agent that takes a customer fault report and routes it through a structured 5-step decision process — classifying the fault, checking parts availability, determining warranty coverage, estimating repair cost, and making a final routing decision. The agent's reasoning steps are visible in the UI, making every decision transparent and auditable.

This project simulates the agentic repair workflow being deployed at UK tech retailers like Currys through their Vyntelligence partnership — where customers video-record their faulty products and an AI agent routes the repair to the right technician with the right parts before the item even arrives at the repair centre.

**Voltex Retail is a fictional business** created specifically for this project series. All policies, products, and repair data are synthetic. The architecture reflects real-world production agentic patterns.

---

## Business Problem

Voltex's Newark Repair Centre handles 1.4 million repairs per year across six product categories. Without intelligent triage, every fault report goes through the same manual assessment process regardless of complexity:

- A laptop screen crack (30-minute Tech Bar repair) sits in the same queue as a motherboard failure (3-hour specialist job)
- Technicians receive products without knowing whether the customer has VoltCare, what parts are needed, or whether the product is even worth repairing
- Beyond economical repair decisions (where repair cost exceeds 65% of product value) are made after the product has already been shipped to Newark

The triage agent solves this by making all five decisions before the product leaves the customer's hands — routing simple repairs to the in-store Tech Bar, complex repairs to Newark, white goods faults to a home engineer, and BER cases directly to replacement without wasted shipping and assessment costs.

---

## Agent Architecture

```
Customer fault report
        │
        ▼
┌─────────────────────────┐
│  Tool 1: classify_fault  │  Identifies product type and fault component
│                          │  Detects liquid damage override
│                          │  Returns: component, confidence, skill required
└───────────┬──────────────┘
            │
            ▼
┌─────────────────────────┐
│  Tool 2: check_parts     │  Queries synthetic parts catalogue
│                          │  Returns: availability, cost, lead time
│                          │  Sorts by availability then cost
└───────────┬──────────────┘
            │
            ▼
┌─────────────────────────┐
│  Tool 3: check_warranty  │  Determines coverage from:
│                          │  - Manufacturer warranty (≤12 months)
│                          │  - VoltCare Essential/Plus/Complete
│                          │  - Consumer Rights Act (≤72 months)
│                          │  - No coverage (>72 months, no VoltCare)
└───────────┬──────────────┘
            │
            ▼
┌─────────────────────────┐
│  Tool 4: estimate_cost   │  Calculates parts + labour cost
│                          │  Checks BER threshold (65% of product value)
│                          │  Returns: total cost, BER flag, repair path
└───────────┬──────────────┘
            │
            ▼
┌─────────────────────────┐
│  Tool 5: make_decision   │  Final routing decision
│                          │  Sets urgency (VoltCare Complete = HIGH)
│                          │  Generates technician notes
│                          │  Returns: RepairBrief (Pydantic)
└─────────────────────────┘
            │
            ▼
    RepairBrief (typed output)
    repair_path · urgency · coverage_type
    customer_pays · excess · technician_notes
    escalate · reasoning_summary · confidence
```

### Key Design Decisions

**LangGraph ReAct pattern** — the agent uses a ReAct (Reasoning + Acting) loop where Claude reasons about what tool to call next based on what previous tools returned. This allows adaptive behaviour — if `classify_fault` returns LOW confidence, the agent flags this in its reasoning before calling `make_triage_decision`.

**Deterministic tools, LLM reasoning** — each tool is a pure Python function with deterministic logic. The LLM provides reasoning and synthesis, not arithmetic. BER calculations, parts costs, and warranty rules are computed in Python, not inferred by Claude.

**Structured Pydantic output** — the agent's final output is a typed `RepairBrief` model with 17 fields including Literal types for `repair_path`, `urgency`, and `confidence`. Invalid values are rejected at schema validation before reaching the UI.

**Liquid damage escalation override** — liquid damage always routes to Newark and always escalates regardless of what other tools return. This is implemented as a rule in `make_triage_decision`, not left to LLM judgement.

**VoltCare Complete 48-hour SLA** — when VoltCare Complete coverage is detected, urgency is set to HIGH regardless of repair complexity. This ensures the 48-hour contractual SLA is flagged at every stage.

---

## Knowledge Base

Three synthetic data files powering the agent's tools:

### Fault Taxonomy
6 product categories × multiple fault components:

| Product | Fault Components |
|---|---|
| Laptop | display, battery, keyboard, motherboard, storage, cooling |
| Phone | screen, battery, camera, connectivity, liquid |
| TV | display, audio, smart, power |
| Washing Machine | drum, water, electrical, motor |
| Fridge-Freezer | cooling, electrical, mechanical |
| Dishwasher | washing, water, electrical |

### Parts Catalogue
32 parts across all product categories with:
- Part name, cost, availability (in_stock / low_stock / out_of_stock)
- Lead time in days
- Compatible product categories

### Repair Complexity Matrix
Maps every product/component combination to:
- Complexity level (easy / medium / hard)
- Labour hours
- Required skill (tech_bar / newark / engineer)
- Labour rate per hour (Tech Bar £35 / Newark £45 / Engineer £55)

---

## Evaluation Results

Evaluated across 20 test scenarios covering all repair paths, product types, coverage types, and edge cases:

| Metric | Score |
|---|---|
| Overall | 81.0% (81/100) |
| Coverage type detection | 90.0% |
| BER flag accuracy | 90.0% |
| Urgency level | 90.0% |
| Escalation accuracy | 70.0% |
| Repair path routing | 65.0% |

### Scoring Methodology
Each scenario is scored across 5 dimensions (1 point each):
- Correct repair path (Tech Bar / Newark / Engineer / Replace)
- Correct coverage type identified
- Correct BER flag
- Correct escalation trigger
- Correct urgency level

### Results by Repair Path

| Path | Score |
|---|---|
| 🏪 Tech Bar | 80.0% |
| 🏭 Newark | 80.0% |
| 🔧 Engineer | 91.4% |
| 📦 Replace (BER) | 50.0% |

Engineer routing is the strongest — white goods faults with clear component identification are consistently routed correctly. BER detection is the weakest — the agent sometimes routes to Newark for specialist assessment rather than declaring BER immediately, which is a conservative but not incorrect behaviour.

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent framework | LangGraph ReAct |
| LLM | Claude Sonnet (Anthropic API) |
| LLM integration | langchain-anthropic |
| Output schema | Pydantic v2 |
| UI | Streamlit |
| Testing | pytest (49 tests) |
| CI | GitHub Actions |
| Python | 3.11 |

---

## Project Structure

```
voltex-repair/
├── knowledge_base.py            # Parts catalogue, fault taxonomy, BER thresholds
├── tools.py                     # 5 LangGraph tools (pure Python, deterministic)
├── agent.py                     # LangGraph ReAct agent + RepairBrief schema
├── app.py                       # Streamlit UI with agent reasoning steps
├── evaluate.py                  # 20-scenario evaluation pipeline
├── evaluation/
│   └── eval_results.json        # Evaluation output
├── tests/
│   └── test_repair.py           # 49 pytest tests
├── .github/workflows/ci.yml     # GitHub Actions CI
├── runtime.txt                  # Python 3.11 for Streamlit Cloud
├── requirements.txt
└── .env                         # API keys (gitignored)
```

---

## Getting Started

### Prerequisites
- Python 3.11
- Anthropic API key

### Installation

```bash
git clone https://github.com/Milonahmed96/voltex-repair.git
cd voltex-repair
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Configuration

```
ANTHROPIC_API_KEY=your_key_here
```

### Run the UI

```bash
streamlit run app.py
```

### Run the Agent Directly

```bash
python agent.py
```

Runs 3 smoke tests covering laptop screen crack, washing machine drainage, and phone liquid damage.

### Run Evaluation

```bash
python evaluate.py
```

20 scenarios, ~4 minutes, real API calls.

### Run Tests

```bash
python -m pytest tests/ -v
```

49 tests, no API calls required.

---

## Part of the Voltex AI Engineering Series

This is Project C in a three-project series simulating AI engineering for a UK omnichannel tech retailer:

| Project | Repo | Demo | Key metrics |
|---|---|---|---|
| B — Contact Centre Co-Pilot | [voltex-copilot](https://github.com/Milonahmed96/voltex-copilot) | [Live](https://voltex-copilot-ssckdkfbuq3diathsc66z8.streamlit.app/) | 82% accuracy, 50 questions, 33 tests |
| A — ShopFloor Analyst | [voltex-shopfloor](https://github.com/Milonahmed96/voltex-shopfloor) | [Live](https://voltex-shopfloor-ma.streamlit.app/) | 6 embedded problems, 37 tests |
| C — Repair Triage Agent | [voltex-repair](https://github.com/Milonahmed96/voltex-repair) | [Live](https://voltex-repair-ma.streamlit.app/) | 81% accuracy, 20 scenarios, 49 tests |

Each project demonstrates a distinct AI engineering skill:
- **Project B** — retrieval, RAG, policy grounding, structured output
- **Project A** — structured data reasoning, metric computation, comparative analysis
- **Project C** — agentic tool calling, multi-step decision making, LangGraph

---

## Author

**Milon Ahmed**
MSc Data Science with Advanced Research, 
University of Hertfordshire,
BSc Mathematics

[GitHub](https://github.com/Milonahmed96) · [LinkedIn](https://linkedin.com/in/milonahmed96)

---

## Licence

MIT