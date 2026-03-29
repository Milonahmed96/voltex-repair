# ⚡ Voltex Repair Triage Agent

> LangGraph-powered agentic repair routing for Voltex Retail — a fictional UK omnichannel technology and appliances retailer.

[![CI](https://github.com/Milonahmed96/voltex-repair/actions/workflows/ci.yml/badge.svg)](https://github.com/Milonahmed96/voltex-repair/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
[![Live Demo](https://img.shields.io/badge/live%20demo-streamlit-FF4B4B)](https://voltex-repair-ma.streamlit.app/)
![Tests](https://img.shields.io/badge/tests-49%20passing-brightgreen)
![Evaluation](https://img.shields.io/badge/evaluation-81.0%25-brightgreen)

## Live Demo

🚀 **[Try Voltex Repair Triage Agent here](https://voltex-repair-ma.streamlit.app/)**

> **Suggested test scenarios:**
> - **Phone liquid damage** — spill coffee on phone, VoltCare Complete → HIGH urgency, Newark, escalate
> - **Fridge BER test** — old fridge compressor failure → repair cost exceeds 65% product value → Replace
> - **Laptop screen crack** — dropped laptop, VoltCare Plus → Tech Bar, same day, excess applies
> - **Ambiguous fault** — vague description → LOW confidence → escalation triggered

## What This Is

Voltex Repair Triage Agent is a LangGraph ReAct agent that takes a customer fault report and routes it through a multi-step decision process — classifying the fault, checking parts availability, determining warranty coverage, estimating repair cost, and making a final routing decision. It simulates the agentic repair workflow being deployed at UK tech retailers like Currys through their Vyntelligence partnership.

## Agent Architecture
```
Fault report
     │
     ▼
┌─────────────────┐
│ classify_fault  │ → product type + fault component
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ check_parts     │ → availability + cost
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ check_warranty  │ → VoltCare / CRA / manufacturer
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ estimate_cost   │ → BER check
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ make_decision   │ → Tech Bar / Newark / Engineer / Replace
└─────────────────┘
```

## Part of the Voltex AI Engineering Series

| Project | Repo | Demo | Key metrics |
|---|---|---|---|
| B — Contact Centre Co-Pilot | [voltex-copilot](https://github.com/Milonahmed96/voltex-copilot) | [Live](https://voltex-copilot-ssckdkfbuq3diathsc66z8.streamlit.app/) | 82% accuracy, 50 questions, 33 tests |
| A — ShopFloor Analyst | [voltex-shopfloor](https://github.com/Milonahmed96/voltex-shopfloor) | [Live](https://voltex-shopfloor-ma.streamlit.app/) | 6 embedded problems, 37 tests |
| C — Repair Triage Agent | [voltex-repair](https://github.com/Milonahmed96/voltex-repair) | [Live](https://voltex-repair-ma.streamlit.app/) | 81% accuracy, 20 scenarios, 49 tests |

## Author

**Milon Ahmed** — MSc Data Science, University of Hertfordshire

## Licence

MIT