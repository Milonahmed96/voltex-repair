"""
Voltex Repair Triage Agent
app.py — Streamlit UI

Repair triage interface showing the agent's reasoning steps,
tool calls, and final repair brief in a clean dashboard.
"""

import streamlit as st
from agent import RepairTriageAgent, RepairBrief

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Voltex Repair Triage",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────

st.markdown("""
<style>
    .stApp { background: #0F1923; }
    .main .block-container { padding-top: 0; max-width: 1300px; }

    .hero {
        background: linear-gradient(135deg, #1A2535 0%, #253347 100%);
        padding: 2rem 2.5rem 1.5rem;
        margin: -1rem -1rem 1.5rem -1rem;
        border-bottom: 3px solid #1D9E75;
    }
    .hero h1 { color: #E1F5EE; font-size: 2rem; font-weight: 700; margin: 0 0 0.3rem 0; }
    .hero p  { color: #888; font-size: 0.9rem; margin: 0; }

    .section-label { font-size: 0.72rem; color: #5DCAA5; text-transform: uppercase;
                     letter-spacing: 0.08em; margin-bottom: 0.5rem; margin-top: 1rem; }

    .brief-card { background: #1A2535; border: 1px solid #253347;
                  border-radius: 10px; padding: 1.25rem 1.5rem; margin-bottom: 0.75rem; }

    .routing-box { border-radius: 10px; padding: 1.25rem 1.5rem; margin-bottom: 0.75rem; }
    .routing-tech-bar { background: #0D3D2E; border: 1px solid #1D9E75; }
    .routing-newark   { background: #1A1A2E; border: 1px solid #534AB7; }
    .routing-engineer { background: #2D1E0A; border: 1px solid #BA7517; }
    .routing-replace  { background: #2D1515; border: 1px solid #E24B4A; }

    .urgency-high   { background:#2D1515; color:#F7C1C1; padding:4px 14px;
                      border-radius:20px; font-size:0.82rem; font-weight:600;
                      border:1px solid #E24B4A; display:inline-block; }
    .urgency-medium { background:#2D1E0A; color:#FAC775; padding:4px 14px;
                      border-radius:20px; font-size:0.82rem; font-weight:600;
                      border:1px solid #BA7517; display:inline-block; }
    .urgency-low    { background:#0D3D2E; color:#5DCAA5; padding:4px 14px;
                      border-radius:20px; font-size:0.82rem; font-weight:600;
                      border:1px solid #1D9E75; display:inline-block; }

    .coverage-badge { background:#1A1A3A; color:#AFA9EC; padding:4px 14px;
                      border-radius:20px; font-size:0.82rem; border:1px solid #534AB7;
                      display:inline-block; }

    .step-card { background: #141E2B; border-left: 3px solid #253347;
                 border-radius: 0 8px 8px 0; padding: 0.6rem 0.85rem;
                 margin-bottom: 0.5rem; }
    .step-card.active { border-left-color: #1D9E75; }
    .step-tool { font-size: 0.78rem; color: #5DCAA5; font-weight: 600;
                 text-transform: uppercase; letter-spacing: 0.06em; }
    .step-detail { font-size: 0.82rem; color: #888; margin-top: 0.2rem; line-height: 1.4; }

    .note-item { background:#141E2B; border-left:3px solid #FAC775;
                 border-radius:0 6px 6px 0; padding:0.5rem 0.75rem;
                 font-size:0.85rem; color:#B4B2A9; margin-bottom:0.4rem;
                 line-height:1.5; }
    .note-item.danger { border-left-color:#E24B4A; color:#F7C1C1; }

    .escalate-banner { background:#2D1515; border:1px solid #E24B4A;
                       border-radius:8px; padding:0.75rem 1rem;
                       font-size:0.9rem; color:#F7C1C1; font-weight:500;
                       margin-bottom:0.75rem; }

    .metric-pill { background:#1A2535; border:1px solid #253347; border-radius:8px;
                   padding:0.75rem 1rem; text-align:center; }
    .metric-pill-label { font-size:0.7rem; color:#5DCAA5; text-transform:uppercase;
                         letter-spacing:0.08em; margin-bottom:0.25rem; }
    .metric-pill-value { font-size:1.1rem; font-weight:600; color:#E1F5EE; }

    .confidence-high   { color:#5DCAA5; font-weight:600; }
    .confidence-medium { color:#FAC775; font-weight:600; }
    .confidence-low    { color:#F7C1C1; font-weight:600; }

    .stTextArea textarea { background:#141E2B !important; color:#D3D1C7 !important;
                           border:1px solid #253347 !important; border-radius:8px !important; }
    .stSelectbox > div, .stNumberInput > div { background:#1A2535 !important; }
    .stButton > button[kind="primary"] { background:#1D9E75 !important;
                                         border:none !important; color:white !important;
                                         border-radius:8px !important; font-size:1rem !important; }
    .stButton > button:not([kind="primary"]) { background:#1A2535 !important;
                                               border:1px solid #253347 !important;
                                               color:#B4B2A9 !important; border-radius:8px !important; }
    #MainMenu { visibility:hidden; }
    footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INIT
# ─────────────────────────────────────────────

@st.cache_resource
def get_agent():
    return RepairTriageAgent()

agent = get_agent()

if "result" not in st.session_state:
    st.session_state.result = None

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <h1>🔧 Voltex Repair Triage Agent</h1>
    <p>LangGraph agentic repair routing · 5 tools · classify → parts → warranty → cost → decision</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────

left, right = st.columns([1, 1.4], gap="large")

# ─────────────────────────────────────────────
# LEFT — INPUT FORM
# ─────────────────────────────────────────────

with left:
    st.markdown('<div class="section-label">Fault report</div>', unsafe_allow_html=True)

    fault_description = st.text_area(
        "Fault description",
        placeholder="Describe what the customer reported...\n\ne.g. Customer dropped their laptop and the screen has cracked. Display still works but has a crack across the corner.",
        height=130,
        label_visibility="collapsed",
    )

    col1, col2 = st.columns(2)
    with col1:
        product_type = st.selectbox(
            "Product type",
            ["laptop", "phone", "tv", "washing_machine", "fridge_freezer", "dishwasher"],
            format_func=lambda x: x.replace("_", " ").title(),
        )
    with col2:
        product_age = st.number_input(
            "Product age (months)", min_value=0, max_value=120, value=8
        )

    col3, col4 = st.columns(2)
    with col3:
        product_value = st.number_input(
            "Product value (£)", min_value=0, max_value=5000, value=750, step=50
        )
    with col4:
        is_accidental = st.selectbox(
            "Accidental damage?", ["No", "Yes"]
        )

    has_voltcare = st.checkbox("Customer has VoltCare")
    voltcare_tier = None
    if has_voltcare:
        voltcare_tier = st.selectbox(
            "VoltCare tier", ["essential", "plus", "complete"]
        )

    st.divider()

    run = st.button("Run triage agent ↗", type="primary", use_container_width=True)

    # Quick test scenarios
    st.markdown('<div class="section-label" style="margin-top:1rem;">Quick test scenarios</div>',
                unsafe_allow_html=True)

    scenarios = [
        {
            "label"              : "📱 Phone cracked screen",
            "fault_description"  : "Customer dropped phone on pavement and smashed the screen. Touch still works but display is cracked.",
            "product_type"       : "phone",
            "product_age_months" : 6,
            "product_value"      : 500.0,
            "has_voltcare"       : True,
            "voltcare_tier"      : "plus",
            "is_accidental_damage": True,
        },
        {
            "label"              : "💻 Laptop battery swollen",
            "fault_description"  : "Laptop battery is swollen and the trackpad is being pushed up. Laptop still turns on.",
            "product_type"       : "laptop",
            "product_age_months" : 20,
            "product_value"      : 600.0,
            "has_voltcare"       : False,
            "voltcare_tier"      : None,
            "is_accidental_damage": False,
        },
        {
            "label"              : "📺 TV backlight failure",
            "fault_description"  : "TV screen has gone dark but can faintly see picture. Backlight appears to have failed.",
            "product_type"       : "tv",
            "product_age_months" : 26,
            "product_value"      : 400.0,
            "has_voltcare"       : True,
            "voltcare_tier"      : "complete",
            "is_accidental_damage": False,
        },
        {
            "label"              : "🧺 Washing machine drum noise",
            "fault_description"  : "Very loud banging noise when drum spins. Gets worse at high spin speeds. Machine is vibrating excessively.",
            "product_type"       : "washing_machine",
            "product_age_months" : 48,
            "product_value"      : 380.0,
            "has_voltcare"       : True,
            "voltcare_tier"      : "essential",
            "is_accidental_damage": False,
        },
        {
            "label"              : "❄️ Fridge not cooling (BER test)",
            "fault_description"  : "Fridge completely stopped cooling. Compressor making loud clicking noise then going quiet. Food spoiling.",
            "product_type"       : "fridge_freezer",
            "product_age_months" : 84,
            "product_value"      : 280.0,
            "has_voltcare"       : False,
            "voltcare_tier"      : None,
            "is_accidental_damage": False,
        },
    ]

    for scenario in scenarios:
        if st.button(scenario["label"], use_container_width=True):
            with st.spinner(f"Running triage for {scenario['label']}..."):
                s = {k: v for k, v in scenario.items() if k != "label"}
                st.session_state.result = agent.triage(**s)
            st.rerun()

# ─────────────────────────────────────────────
# RUN TRIAGE
# ─────────────────────────────────────────────

if run and fault_description.strip():
    with st.spinner("Agent reasoning through 5 tools..."):
        st.session_state.result = agent.triage(
            fault_description    = fault_description.strip(),
            product_type         = product_type,
            product_age_months   = product_age,
            product_value        = float(product_value),
            has_voltcare         = has_voltcare,
            voltcare_tier        = voltcare_tier,
            is_accidental_damage = is_accidental == "Yes",
        )
    st.rerun()

# ─────────────────────────────────────────────
# RIGHT — RESULTS
# ─────────────────────────────────────────────

with right:
    result = st.session_state.result

    if result is None:
        st.markdown("""
        <div style="color:#3A4A5A;font-size:0.92rem;margin-top:2rem;text-align:center;
                    line-height:2.5;padding:2rem;border:1px dashed #253347;border-radius:12px;">
            🔧 Enter a fault report and click <strong>Run triage agent</strong><br>
            <span style="font-size:0.82rem;">or click a quick test scenario on the left</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        brief = result["brief"]
        steps = result["steps"]

        # ── Routing decision header
        path_styles = {
            "tech_bar": ("routing-tech-bar", "🏪", "#5DCAA5"),
            "newark"  : ("routing-newark",   "🏭", "#AFA9EC"),
            "engineer": ("routing-engineer", "🔧", "#FAC775"),
            "replace" : ("routing-replace",  "📦", "#F7C1C1"),
        }
        style_cls, path_icon, path_color = path_styles.get(
            brief.repair_path, ("brief-card", "❓", "#888")
        )

        urgency_cls = {
            "HIGH"  : "urgency-high",
            "MEDIUM": "urgency-medium",
            "LOW"   : "urgency-low",
        }.get(brief.urgency, "urgency-medium")

        urgency_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(brief.urgency, "⚪")

        st.markdown(f"""
        <div class="routing-box {style_cls}">
            <div style="font-size:0.72rem;color:{path_color};text-transform:uppercase;
                        letter-spacing:0.08em;margin-bottom:0.4rem;">Routing decision</div>
            <div style="font-size:1.3rem;font-weight:700;color:#E1F5EE;margin-bottom:0.3rem;">
                {path_icon} {brief.repair_path_description}
            </div>
            <span class="{urgency_cls}">{urgency_icon} {brief.urgency} urgency</span>
            &nbsp;&nbsp;
            <span class="coverage-badge">{brief.coverage_type.replace('_', ' ').title()}</span>
        </div>
        """, unsafe_allow_html=True)

        # ── Escalation banner
        if brief.escalate:
            st.markdown(
                f'<div class="escalate-banner">⚠ Escalate — {brief.escalation_reason}</div>',
                unsafe_allow_html=True,
            )

        # ── Metric row
        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.markdown(f"""
            <div class="metric-pill">
                <div class="metric-pill-label">Product</div>
                <div class="metric-pill-value">{brief.product_type.replace('_',' ').title()}</div>
            </div>""", unsafe_allow_html=True)

        with m2:
            st.markdown(f"""
            <div class="metric-pill">
                <div class="metric-pill-label">Fault</div>
                <div class="metric-pill-value">{brief.fault_component.replace('_',' ').title()}</div>
            </div>""", unsafe_allow_html=True)

        with m3:
            cost_display = f"£{brief.estimated_cost_to_customer:.0f}" if brief.customer_pays else "No charge"
            st.markdown(f"""
            <div class="metric-pill">
                <div class="metric-pill-label">Customer cost</div>
                <div class="metric-pill-value">{cost_display}</div>
            </div>""", unsafe_allow_html=True)

        with m4:
            excess_display = f"£{brief.excess_amount:.0f}" if brief.excess_applies else "None"
            st.markdown(f"""
            <div class="metric-pill">
                <div class="metric-pill-label">Excess</div>
                <div class="metric-pill-value">{excess_display}</div>
            </div>""", unsafe_allow_html=True)

        # ── Two column detail
        detail_left, detail_right = st.columns(2)

        with detail_left:
            # Agent reasoning steps
            st.markdown('<div class="section-label">Agent reasoning steps</div>',
                        unsafe_allow_html=True)

            tool_icons = {
                "classify_fault"      : "🔍 Classify fault",
                "check_parts"         : "📦 Check parts",
                "check_warranty"      : "📋 Check warranty",
                "estimate_repair_cost": "💰 Estimate cost",
                "make_triage_decision": "✅ Make decision",
            }

            for i, step in enumerate(steps):
                tool_label = tool_icons.get(step["tool"], step["tool"])
                is_last    = i == len(steps) - 1

                output_preview = ""
                if "output" in step and isinstance(step["output"], dict):
                    out = step["output"]
                    if step["tool"] == "classify_fault":
                        output_preview = (
                            f"→ {out.get('fault_component','?')} "
                            f"({out.get('confidence','?')} confidence)"
                        )
                    elif step["tool"] == "check_parts":
                        found = out.get("parts_found", False)
                        if found and out.get("best_part"):
                            output_preview = (
                                f"→ {out['best_part']['name'][:35]}... "
                                f"£{out['best_part']['cost']:.2f} "
                                f"({out['best_part']['availability']})"
                            )
                        else:
                            output_preview = "→ No standard parts found"
                    elif step["tool"] == "check_warranty":
                        output_preview = (
                            f"→ {out.get('coverage_type','?').replace('_',' ')} "
                            f"| pays: {out.get('customer_pays','?')}"
                        )
                    elif step["tool"] == "estimate_repair_cost":
                        output_preview = (
                            f"→ £{out.get('total_repair_cost',0):.2f} total "
                            f"({'BER' if out.get('is_beyond_economical_repair') else 'economical'})"
                        )
                    elif step["tool"] == "make_triage_decision":
                        output_preview = f"→ {out.get('repair_path','?')} | {out.get('urgency','?')} urgency"

                st.markdown(f"""
                <div class="step-card {'active' if is_last else ''}">
                    <div class="step-tool">[{i+1}] {tool_label}</div>
                    {f'<div class="step-detail">{output_preview}</div>' if output_preview else ''}
                </div>
                """, unsafe_allow_html=True)

        with detail_right:
            # Technician notes
            if brief.technician_notes:
                st.markdown('<div class="section-label">Technician notes</div>',
                            unsafe_allow_html=True)
                for note in brief.technician_notes:
                    is_danger = any(w in note.upper() for w in ["LIQUID", "DO NOT", "BER"])
                    st.markdown(
                        f'<div class="note-item {"danger" if is_danger else ""}">{note}</div>',
                        unsafe_allow_html=True,
                    )

            # BER warning
            if brief.is_ber:
                st.markdown("""
                <div style="background:#2D1515;border:1px solid #E24B4A;border-radius:8px;
                            padding:0.75rem 1rem;margin-top:0.5rem;">
                    <div style="color:#F7C1C1;font-weight:600;margin-bottom:0.3rem;">
                        📦 Beyond Economical Repair
                    </div>
                    <div style="color:#B4B2A9;font-size:0.85rem;">
                        Repair cost exceeds 65% of product value.
                        Initiate replacement process.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Agent reasoning summary
            st.markdown('<div class="section-label">Agent reasoning</div>',
                        unsafe_allow_html=True)
            conf_cls = {
                "HIGH": "confidence-high",
                "MEDIUM": "confidence-medium",
                "LOW": "confidence-low",
            }.get(brief.confidence, "confidence-medium")

            st.markdown(f"""
            <div class="brief-card">
                <div style="font-size:0.88rem;color:#B4B2A9;line-height:1.6;margin-bottom:0.5rem;">
                    {brief.reasoning_summary}
                </div>
                <div style="font-size:0.78rem;">
                    Confidence: <span class="{conf_cls}">{brief.confidence}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🔧 Repair Triage Agent")
    st.divider()
    st.markdown("""
    **5 agent tools:**
    1. 🔍 Classify fault
    2. 📦 Check parts
    3. 📋 Check warranty
    4. 💰 Estimate cost
    5. ✅ Make decision
    """)
    st.divider()
    st.markdown("""
    **Repair paths:**
    - 🏪 Tech Bar — same day
    - 🏭 Newark — 5 working days
    - 🔧 Engineer — 3-7 days
    - 📦 Replace — BER threshold
    """)
    st.divider()
    st.markdown("""
    **BER threshold:** 65% of product value

    **VoltCare Complete:** 48-hour SLA → HIGH urgency
    """)
    st.divider()
    st.caption("Voltex Retail is a fictional business.")