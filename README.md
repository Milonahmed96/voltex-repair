# ⚡ Voltex Repair Triage Agent

> LangGraph-powered agentic repair routing for Voltex Retail — a fictional UK omnichannel technology and appliances retailer.

[![CI](https://github.com/Milonahmed96/voltex-repair/actions/workflows/ci.yml/badge.svg)](https://github.com/Milonahmed96/voltex-repair/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

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

| Project | Repo | Demo |
|---|---|---|
| B — Contact Centre Co-Pilot | [voltex-copilot](https://github.com/Milonahmed96/voltex-copilot) | [Live](https://voltex-copilot-ssckdkfbuq3diathsc66z8.streamlit.app/) |
| A — ShopFloor Analyst | [voltex-shopfloor](https://github.com/Milonahmed96/voltex-shopfloor) | [Live](https://voltex-shopfloor-ma.streamlit.app/) |
| C — Repair Triage Agent | voltex-repair (this repo) | Coming soon |

## Author

**Milon Ahmed** — MSc Data Science, University of Hertfordshire

## Licence

MIT