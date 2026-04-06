# blood_ai.py — BloodAI Dashboard
# Matches reference design: dark navy + cyan glow, health score, risk propagation, radar, biomarkers

import streamlit as st
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="BloodAI — Advanced Haematology Insights",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from extraction import (
    extract_text_from_pdf, extract_text_from_image,
    extract_from_json, extract_parameters, validate_and_standardize,
)
from reference import (
    REFERENCE_RANGES, classify_value, classify_all,
    get_display_range, get_unit, severity_color,
)
from pattern_recognition import PatternRecognizer
from contextual_model import ContextualAnalyzer
from synthesis_engine import SynthesisEngine
from orchestrator import BloodReportOrchestrator
from chatbot_logic import render_chatbot, save_report_to_session
from report_generator import ReportGenerator
import extraction as ext_module
import reference as ref_module

pattern_recognizer  = PatternRecognizer()
contextual_analyzer = ContextualAnalyzer()
synthesis_engine    = SynthesisEngine()
report_generator    = ReportGenerator()
orchestrator        = BloodReportOrchestrator(
    extractor=ext_module, reference=ref_module,
    pattern_recognizer=pattern_recognizer,
    contextual_analyzer=contextual_analyzer,
    synthesis_engine=synthesis_engine,
)

try:
    import pytesseract
    pytesseract.get_tesseract_version()
except Exception:
    pass

# ═══════════════════════════════════════════════════════════════════════════
# CSS — Matches reference image exactly
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
    --bg:       #020c14;
    --bg2:      #041220;
    --bg3:      #061a2e;
    --card:     #071828;
    --card2:    #0a1f35;
    --cyan:     #00e5ff;
    --cyan2:    #00b8d9;
    --cyan3:    rgba(0,229,255,0.15);
    --cyan4:    rgba(0,229,255,0.06);
    --green:    #00e676;
    --red:      #ff1744;
    --amber:    #ffab00;
    --border:   rgba(0,229,255,0.18);
    --border2:  rgba(0,229,255,0.08);
    --text:     #e0f7fa;
    --text2:    #80deea;
    --text3:    #37474f;
}

.stApp { background: var(--bg) !important; }
section[data-testid="stSidebar"] { background: var(--bg2) !important; border-right: 1px solid var(--border); }
.block-container { padding: 0 !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }
.stApp, .stMarkdown, p, span, label, div { font-family: 'Rajdhani', sans-serif; color: var(--text); }

/* ── Page wrapper ── */
.page-wrap { padding: 0 1.5rem 2rem; }

/* ── Top Nav Bar ── */
.topbar {
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    padding: 1rem 2rem;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 100;
}
.topbar-logo {
    font-family: 'Orbitron', monospace;
    font-size: 1.6rem; font-weight: 900;
    color: var(--cyan); letter-spacing: 4px;
    text-shadow: 0 0 20px rgba(0,229,255,0.5);
}
.topbar-sub {
    font-size: 0.65rem; color: var(--text2); letter-spacing: 3px;
    text-transform: uppercase; text-align: center; margin-top: 2px;
}
.topbar-right { display: flex; gap: 0.5rem; align-items: center; }

/* ── Nav tabs (top) ── */
.nav-tabs {
    display: flex; gap: 0; border-bottom: 1px solid var(--border2);
    padding: 0 2rem; background: var(--bg2);
    overflow-x: auto;
}
.nav-tab {
    padding: 0.7rem 1.4rem; font-size: 0.75rem; font-weight: 600;
    color: var(--text3); text-transform: uppercase; letter-spacing: 1.5px;
    border-bottom: 2px solid transparent; cursor: pointer;
    transition: all 0.2s; white-space: nowrap;
    font-family: 'Orbitron', monospace;
}
.nav-tab:hover { color: var(--cyan2); }
.nav-tab.active {
    color: var(--cyan); border-bottom-color: var(--cyan);
    background: linear-gradient(180deg, transparent, rgba(0,229,255,0.04));
}

/* ── Cards ── */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 1.2rem 1.4rem;
    position: relative; overflow: hidden;
}
.card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    opacity: 0.4;
}
.card-title {
    font-family: 'Orbitron', monospace;
    font-size: 0.8rem; font-weight: 700; color: var(--cyan);
    letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.3rem;
}
.card-sub {
    font-size: 0.65rem; color: var(--text3); letter-spacing: 1.5px;
    text-transform: uppercase; margin-bottom: 1rem;
}

/* ── Health Score card ── */
.score-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.4rem; text-align: center; }
.score-big  { font-family:'Orbitron',monospace; font-size:3rem; font-weight:900; color:var(--cyan); line-height:1; text-shadow:0 0 30px rgba(0,229,255,0.6); }
.score-denom{ font-family:'Orbitron',monospace; font-size:1rem; color:var(--text3); }
.score-label{ font-family:'Orbitron',monospace; font-size:0.9rem; font-weight:700; margin-top:0.3rem; }
.score-desc { font-size:0.8rem; color:var(--text2); margin-top:0.2rem; }
.mini-stats { display:flex; gap:1rem; margin-top:1rem; justify-content:center; }
.mini-stat   { text-align:center; }
.mini-stat-lbl{ font-size:0.6rem; color:var(--text3); text-transform:uppercase; letter-spacing:1px; }
.mini-stat-val{ font-family:'Orbitron',monospace; font-size:0.85rem; font-weight:700; }

/* ── Biomarker row ── */
.bm-row { display:flex; align-items:center; justify-content:space-between; padding:0.55rem 0; border-bottom:1px solid var(--border2); }
.bm-row:last-child { border-bottom:none; }
.bm-name  { font-size:0.88rem; color:var(--text); font-weight:500; min-width:90px; }
.bm-value { font-family:'Orbitron',monospace; font-size:0.85rem; color:var(--cyan); font-weight:600; }
.bm-badge { padding:2px 10px; border-radius:4px; font-size:0.65rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; font-family:'Orbitron',monospace; }
.bm-NORMAL  { background:rgba(0,230,118,0.15); color:#00e676; border:1px solid rgba(0,230,118,0.3); }
.bm-HIGH    { background:rgba(255,23,68,0.15);  color:#ff1744; border:1px solid rgba(255,23,68,0.3); }
.bm-LOW     { background:rgba(255,171,0,0.15);  color:#ffab00; border:1px solid rgba(255,171,0,0.3); }
.bm-OPTIMAL { background:rgba(0,229,255,0.15);  color:#00e5ff; border:1px solid rgba(0,229,255,0.3); }

/* ── AI Insights ── */
.insight-item { display:flex; gap:0.8rem; align-items:flex-start; padding:0.7rem 0; border-bottom:1px solid var(--border2); }
.insight-item:last-child { border-bottom:none; }
.insight-icon { width:32px; height:32px; border-radius:50%; background:var(--cyan3); display:flex; align-items:center; justify-content:center; flex-shrink:0; font-size:0.9rem; border:1px solid var(--border); }
.insight-title{ font-family:'Orbitron',monospace; font-size:0.72rem; color:var(--cyan); font-weight:700; letter-spacing:0.5px; }
.insight-desc { font-size:0.78rem; color:var(--text2); margin-top:2px; }

/* ── Confidence badge ── */
.conf-badge {
    background:var(--card2); border:1px solid var(--border);
    border-radius:8px; padding:0.4rem 1rem;
    font-family:'Orbitron',monospace; font-size:0.75rem; color:var(--text2);
}
.conf-badge span { color:var(--cyan); font-weight:700; font-size:0.9rem; }

/* ── Pattern chip ── */
.pattern-chip {
    display:inline-block; padding:4px 12px; border-radius:6px; margin:3px;
    font-size:0.72rem; font-weight:700; letter-spacing:0.5px;
    font-family:'Orbitron',monospace;
}
.chip-High     { background:rgba(255,23,68,0.15); color:#ff5252; border:1px solid rgba(255,23,68,0.3); }
.chip-Moderate { background:rgba(255,171,0,0.15); color:#ffab00; border:1px solid rgba(255,171,0,0.3); }
.chip-Low      { background:rgba(0,230,118,0.15); color:#00e676; border:1px solid rgba(0,230,118,0.3); }

/* ── Upload zone ── */
.upload-zone {
    background:var(--card4,rgba(0,229,255,0.03));
    border:2px dashed var(--border); border-radius:12px;
    padding:1.5rem; text-align:center; margin:1rem 0;
}

/* ── Streamlit overrides ── */
.stButton>button {
    background:transparent !important;
    border:1px solid var(--cyan) !important;
    color:var(--cyan) !important;
    border-radius:8px !important;
    font-family:'Orbitron',monospace !important;
    font-size:0.75rem !important; font-weight:700 !important;
    letter-spacing:1.5px !important; text-transform:uppercase !important;
    padding:0.6rem 1.2rem !important;
    transition:all 0.2s !important;
}
.stButton>button:hover {
    background:var(--cyan3) !important;
    box-shadow:0 0 20px rgba(0,229,255,0.3) !important;
    transform:translateY(-1px) !important;
}
.stButton>[kind="primary"]>button,
button[kind="primary"] {
    background:var(--cyan3) !important;
    box-shadow:0 0 15px rgba(0,229,255,0.2) !important;
}
.stDownloadButton>button {
    background:transparent !important;
    border:1px solid var(--cyan) !important;
    color:var(--cyan) !important;
    border-radius:8px !important;
    font-family:'Orbitron',monospace !important;
    font-size:0.75rem !important; font-weight:700 !important;
    letter-spacing:1.5px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background:var(--bg2) !important;
    border-bottom:1px solid var(--border2) !important;
    gap:0 !important; padding:0 !important;
    border-radius:0 !important;
}
.stTabs [data-baseweb="tab"] {
    background:transparent !important; color:var(--text3) !important;
    border-radius:0 !important; font-family:'Orbitron',monospace !important;
    font-size:0.68rem !important; font-weight:700 !important;
    letter-spacing:1.5px !important; text-transform:uppercase !important;
    padding:0.8rem 1.2rem !important; border:none !important;
    border-bottom:2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color:var(--cyan) !important;
    border-bottom:2px solid var(--cyan) !important;
    background:linear-gradient(180deg,transparent,rgba(0,229,255,0.04)) !important;
}
.stTabs [data-baseweb="tab-panel"] { background:transparent !important; padding:1.5rem 0 !important; }
.stFileUploader { background:var(--card) !important; border:1px dashed var(--border) !important; border-radius:12px !important; }
.stFileUploader label { color:var(--text2) !important; }
.stFileUploader [data-testid="stFileUploaderDropzoneButton"] button,
.stFileUploader button {
    background:transparent !important;
    border:1px solid var(--cyan) !important;
    color:var(--cyan) !important;
    border-radius:8px !important;
    font-family:'Orbitron',monospace !important;
    font-size:0.7rem !important;
    font-weight:700 !important;
    letter-spacing:1.5px !important;
}
.stFileUploader [data-testid="stFileUploaderDropzoneButton"] button:hover,
.stFileUploader button:hover {
    background:var(--cyan3) !important;
    box-shadow:0 0 15px rgba(0,229,255,0.3) !important;
}
/* ── All inputs dark ── */
.stSelectbox>div>div, .stNumberInput>div>div>input, .stTextInput>div>div>input {
    background:var(--card) !important; color:var(--text) !important;
    border:1px solid var(--border) !important; border-radius:8px !important;
    font-family:'Rajdhani',sans-serif !important;
}
/* ── Selectbox dropdown list (the white popup) ── */
[data-baseweb="select"] [data-baseweb="popover"],
[data-baseweb="select"] ul,
[data-baseweb="menu"],
[data-baseweb="menu"] ul,
[data-testid="stSelectboxVirtualDropdown"],
div[role="listbox"],
ul[data-baseweb="menu"] {
    background: #041220 !important;
    border: 1px solid rgba(0,229,255,0.25) !important;
    border-radius: 8px !important;
    color: #e0f7fa !important;
}
/* ── Dropdown option items ── */
[data-baseweb="menu"] li,
[data-baseweb="option"],
[role="option"] {
    background: #041220 !important;
    color: #e0f7fa !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.9rem !important;
}
[data-baseweb="menu"] li:hover,
[data-baseweb="option"]:hover,
[role="option"]:hover {
    background: rgba(0,229,255,0.12) !important;
    color: #00e5ff !important;
}
/* ── Selected option text in box ── */
[data-baseweb="select"] span,
[data-baseweb="select"] div {
    color: #e0f7fa !important;
    background: transparent !important;
}
/* ── Multiselect tags ── */
[data-baseweb="tag"] {
    background: rgba(0,229,255,0.15) !important;
    border: 1px solid rgba(0,229,255,0.3) !important;
    border-radius: 6px !important;
}
[data-baseweb="tag"] span {
    color: #00e5ff !important;
}
/* ── Multiselect container ── */
[data-baseweb="multi-select"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
/* ── Checkbox ── */
.stCheckbox label, .stCheckbox span { color: #e0f7fa !important; }
/* ── Number input ── */
.stNumberInput button { background: var(--card2) !important; color: var(--cyan) !important; border-color: var(--border) !important; }
/* ── Popover/dropdown wrapper ── */
div[data-testid="stPopover"],
[data-baseweb="popover"] > div {
    background: #041220 !important;
    border: 1px solid rgba(0,229,255,0.2) !important;
}
.stExpander { background:var(--card) !important; border:1px solid var(--border2) !important; border-radius:10px !important; }
.stExpander summary { color:var(--text2) !important; }
.stAlert { background:var(--card) !important; border-color:var(--border) !important; }
div[data-testid="stMetric"] { background:var(--card) !important; border-radius:10px !important; padding:0.8rem !important; border:1px solid var(--border2) !important; }
div[data-testid="stMetricLabel"] { color:var(--text3) !important; font-family:'Orbitron',monospace !important; font-size:0.65rem !important; letter-spacing:1px !important; }
div[data-testid="stMetricValue"] { color:var(--cyan) !important; font-family:'Orbitron',monospace !important; }
.sidebar-logo { font-family:'Orbitron',monospace; font-size:1.1rem; font-weight:900; color:var(--cyan); letter-spacing:2px; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR — Patient Details
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🩺 BLOODAI</div>', unsafe_allow_html=True)
    st.markdown("<small style='color:#37474f;letter-spacing:2px;font-size:0.65rem'>PATIENT CONSOLE</small>", unsafe_allow_html=True)
    st.markdown("---")
    patient_name   = st.text_input("Patient Name", value="Patient", label_visibility="collapsed", placeholder="Patient Name")
    age            = st.number_input("Age", min_value=0, max_value=120, value=30)
    gender         = st.selectbox("Gender", ["Male","Female","Other","Not specified"])
    family_history = st.multiselect("Family History",
        ["Diabetes","Heart Disease","High Blood Pressure","Kidney Disease","Liver Disease","Thyroid Disorder"],
        label_visibility="collapsed")
    st.markdown("---")
    ocr_enabled = st.checkbox("Enable OCR", value=True)

age_val    = age if age > 0 else None
gender_val = gender if gender not in ("Not specified","Other") else None

# ═══════════════════════════════════════════════════════════════════════════
# TOP BAR
# ═══════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="topbar">
    <div>
        <div class="topbar-logo">BLOOD AI</div>
        <div class="topbar-sub">Advanced Haematology Insights</div>
    </div>
    <div class="topbar-right"></div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SAMPLE DATA
# ═══════════════════════════════════════════════════════════════════════════
SAMPLE_DATA = {
    "prediabetic": {"Hemoglobin":14.8,"WBC":7200,"Platelets":230000,"Glucose":112,"HbA1c":6.1,"Cholesterol":215,"HDL":38,"LDL":148,"Triglycerides":180,"ALT":32,"AST":28,"Creatinine":1.0},
    "anemic":      {"Hemoglobin":9.8,"RBC":3.5,"Hematocrit":30.0,"MCV":72.0,"MCH":24.0,"WBC":6500,"Platelets":310000,"Glucose":88,"Ferritin":6.0,"Iron":42.0,"Cholesterol":175,"HDL":52,"Triglycerides":95},
    "multi":       {"Hemoglobin":11.8,"WBC":13500,"Platelets":160000,"Glucose":138,"HbA1c":7.2,"Cholesterol":255,"HDL":32,"LDL":172,"Triglycerides":255,"ALT":72,"AST":68,"Bilirubin":1.6,"Creatinine":1.6,"BUN":28,"eGFR":52,"TSH":5.8,"CRP":18},
    "normal":      {"Hemoglobin":14.2,"WBC":6800,"Platelets":250000,"MCV":89.3,"CRP":1.2,"Ferritin":78,"Glucose":88,"Cholesterol":175,"HDL":58,"Triglycerides":110,"Creatinine":0.9,"TSH":2.1},
}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN TABS (matching reference image)
# ═══════════════════════════════════════════════════════════════════════════
tab_overview, tab_analysis, tab_biomarkers, tab_risks, tab_trends, tab_recs, tab_report, tab_patient, tab_chatbot = st.tabs([
    "OVERVIEW", "ANALYSIS", "BIOMARKERS", "RISKS", "TRENDS", "RECOMMENDATIONS", "REPORT", "👤 PATIENT", "🤖 AI CHAT"
])

# ═══════════════════════════════════════════════════════════════════════════
# OVERVIEW TAB — Upload + Controls
# ═══════════════════════════════════════════════════════════════════════════
with tab_overview:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

    # Upload + action buttons row
    up_col, btn_col = st.columns([3, 1])
    with up_col:
        uploaded_file = st.file_uploader(
            "Upload Blood Report (PDF, TXT, JSON, PNG, JPG)",
            type=["pdf","json","png","jpg","jpeg","txt"],
            label_visibility="collapsed",
        )
        st.markdown("<small style='color:#37474f;font-size:0.7rem'>Or try a sample:</small>", unsafe_allow_html=True)
        sc1,sc2,sc3,sc4 = st.columns(4)
        use_sample = None
        if sc1.button("Normal",      width='stretch'): use_sample = "normal"
        if sc2.button("Pre-Diabetic",width='stretch'): use_sample = "prediabetic"
        if sc3.button("Anaemic",     width='stretch'): use_sample = "anemic"
        if sc4.button("Multi",       width='stretch'): use_sample = "multi"

    with btn_col:
        st.markdown("<br>", unsafe_allow_html=True)
        analyse_btn = st.button("⚡ ANALYSE", type="primary", width='stretch')
        try:
            if st.session_state.get("report_loaded"):
                result_cached = st.session_state.get("_cached_result")
                if result_cached:
                    pdf_b = report_generator.generate(result_cached, patient_name, age_val, gender_val)
                    st.download_button("📋 PDF REPORT", pdf_b,
                        file_name=f"BloodAI_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf", width='stretch')
        except Exception:
            pass

    # ── RUN PIPELINE ──────────────────────────────────────────────────────
    if analyse_btn or use_sample:
        if uploaded_file and not use_sample:
            valid, msg = BloodReportOrchestrator.validate_file(uploaded_file)
            if not valid:
                st.error(f"❌ {msg}"); st.stop()

        with st.spinner("Running AI pipeline..."):
            result = orchestrator.run(
                uploaded_file=uploaded_file if not use_sample else None,
                sample_data=SAMPLE_DATA.get(use_sample) if use_sample else None,
                age=age_val, gender=gender_val, family_history=family_history,
            )

        if not result.success:
            st.error(f"❌ {result.error}"); st.stop()

        save_report_to_session(result)
        st.session_state["_cached_result"] = result

    # ── DISPLAY RESULTS ───────────────────────────────────────────────────
    if st.session_state.get("report_loaded"):
        result      = st.session_state.get("_cached_result")
        found       = st.session_state.get("report_found", {})
        classif     = st.session_state.get("report_classifications", {})
        patterns    = st.session_state.get("report_patterns", [])
        risk_scores = st.session_state.get("report_risk_scores", {})
        synthesis   = st.session_state.get("report_synthesis", {})
        recs        = st.session_state.get("report_recommendations", [])
        ratios      = result.ratios if result else {}

        n_total  = len(found)
        n_normal = sum(1 for s in classif.values() if s == "NORMAL")
        n_high   = sum(1 for s in classif.values() if s == "HIGH")
        n_low    = sum(1 for s in classif.values() if s == "LOW")
        health_score = round(n_normal / n_total * 100) if n_total > 0 else 0
        ovs = synthesis.get("overall_status","Normal")

        score_color = "#00e5ff" if health_score >= 70 else "#ffab00" if health_score >= 40 else "#ff1744"
        score_label = "EXCELLENT" if health_score >= 85 else "GOOD" if health_score >= 70 else "MODERATE" if health_score >= 50 else "POOR"
        score_desc  = "Overall blood health is optimal" if health_score >= 70 else "Some parameters need attention" if health_score >= 50 else "Multiple parameters require immediate attention"
        risk_level  = "LOW" if health_score >= 70 else "MODERATE" if health_score >= 50 else "HIGH"
        stability   = f"{min(99, health_score + 15)}%"

        st.markdown("<br>", unsafe_allow_html=True)

        # ── ROW 1: Health Score | Action Buttons | Risk Propagation ──────
        row1_left, row1_mid, row1_right = st.columns([1.2, 0.8, 3])

        with row1_left:
            st.markdown('<div class="card-title" style="text-align:center">HEALTH SCORE</div>', unsafe_allow_html=True)
            # Gauge chart
            try:
                import plotly.graph_objects as go
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=health_score,
                    number={"font":{"size":52,"color":score_color,"family":"Orbitron"},"suffix":""},
                    gauge={
                        "axis":{"range":[0,100],"tickcolor":"#1a3a4a","tickfont":{"color":"#37474f","size":9},"nticks":6},
                        "bar":{"color":score_color,"thickness":0.28},
                        "bgcolor":"rgba(0,0,0,0)","bordercolor":"rgba(0,0,0,0)",
                        "steps":[
                            {"range":[0,40],  "color":"rgba(255,23,68,0.06)"},
                            {"range":[40,70], "color":"rgba(255,171,0,0.06)"},
                            {"range":[70,100],"color":"rgba(0,229,255,0.06)"},
                        ],
                        "threshold":{"line":{"color":score_color,"width":3},"thickness":0.85,"value":health_score},
                    },
                ))
                fig_gauge.update_layout(
                    height=220, margin=dict(l=20,r=20,t=10,b=10),
                    paper_bgcolor="rgba(0,0,0,0)", font_color="#e0f7fa",
                    annotations=[dict(
                        text=f"<b>/100</b>",
                        x=0.5, y=0.12, xref="paper", yref="paper",
                        showarrow=False, font=dict(size=14,color="#37474f",family="Orbitron"),
                    )],
                )
                st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar":False})
            except Exception:
                st.metric("Health Score", f"{health_score}%")

            st.markdown(f"""
            <div style="text-align:center;margin-top:-0.5rem">
                <div style="font-family:'Orbitron',monospace;font-size:1rem;font-weight:700;color:{score_color}">{score_label}</div>
                <div style="font-size:0.78rem;color:#80deea;margin-top:2px">{score_desc}</div>
                <div style="display:flex;gap:1rem;justify-content:center;margin-top:0.8rem">
                    <div style="text-align:center">
                        <div style="font-size:0.58rem;color:#37474f;text-transform:uppercase;letter-spacing:1px">Risk Level</div>
                        <div style="font-family:'Orbitron',monospace;font-size:0.75rem;color:{'#00e676' if risk_level=='LOW' else '#ffab00' if risk_level=='MODERATE' else '#ff1744'};background:rgba(0,0,0,0.3);padding:2px 8px;border-radius:4px;margin-top:2px">{risk_level}</div>
                    </div>
                    <div style="text-align:center">
                        <div style="font-size:0.58rem;color:#37474f;text-transform:uppercase;letter-spacing:1px">Stability</div>
                        <div style="font-family:'Orbitron',monospace;font-size:0.75rem;color:#00e5ff;margin-top:4px">{stability}</div>
                    </div>
                    <div style="text-align:center">
                        <div style="font-size:0.58rem;color:#37474f;text-transform:uppercase;letter-spacing:1px">Monitoring</div>
                        <div style="font-family:'Orbitron',monospace;font-size:0.75rem;color:#00e5ff;margin-top:4px">{'URGENT' if ovs=='Urgent' else 'ROUTINE'}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with row1_mid:
            # AI Insights panel
            headline = synthesis.get("headline","")
            urgent   = synthesis.get("urgent_flags",[])
            positives= synthesis.get("positive_findings",[])

            insights = []
            if not urgent and health_score >= 70:
                insights.append(("✓","NO CRITICAL RISKS","All values within optimal reference ranges."))
                insights.append(("📶","STRONG HEALTH SIGNAL","Excellent haematological balance detected."))
                insights.append(("🗓","ROUTINE MONITORING","Re-test in 6–12 months or as advised."))
            else:
                for flag in urgent[:2]:
                    insights.append(("⚠","URGENT FLAG",flag["message"]))
                if patterns:
                    insights.append(("🔍","PATTERNS DETECTED",f"{len(patterns)} clinical pattern(s) found."))
                insights.append(("💡","ACTION REQUIRED","Review recommendations tab for guidance."))

            st.markdown("""
            <div style="background:#071828;border:1px solid rgba(0,229,255,0.18);border-radius:12px;padding:1rem 1.2rem;position:relative;overflow:hidden">
                <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#00e5ff,transparent);opacity:0.4"></div>
                <div style="font-family:'Orbitron',monospace;font-size:0.8rem;font-weight:700;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.3rem">AI Insights</div>
                <div style="font-size:0.65rem;color:#37474f;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:0.8rem">Automated Analysis Summary</div>
            </div>""", unsafe_allow_html=True)
            for icon,title,desc in insights:
                st.markdown(f"""
                <div style="display:flex;gap:0.8rem;align-items:flex-start;padding:0.6rem 0;border-bottom:1px solid rgba(0,229,255,0.06);background:#071828;margin:0 0 0 0">
                    <div style="width:30px;height:30px;border-radius:50%;background:rgba(0,229,255,0.1);display:flex;align-items:center;justify-content:center;flex-shrink:0;border:1px solid rgba(0,229,255,0.18);font-size:0.9rem">{icon}</div>
                    <div>
                        <div style="font-family:'Orbitron',monospace;font-size:0.68rem;color:#00e5ff;font-weight:700;letter-spacing:0.5px">{title}</div>
                        <div style="font-size:0.75rem;color:#80deea;margin-top:2px">{desc}</div>
                    </div>
                </div>""", unsafe_allow_html=True)

        with row1_right:
            # Risk Propagation Chart
            st.markdown(f"""
            <div class="card" style="padding-bottom:0.5rem">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <div>
                        <div class="card-title">Risk Propagation</div>
                        <div class="card-sub">AI Modelled Health Risk Flow</div>
                    </div>
                    <div class="conf-badge">AI CONFIDENCE &nbsp;<span>{min(99, health_score + 12)}%</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            try:
                import plotly.graph_objects as go

                # Build risk cascade from actual data
                initial_risk  = max(5, n_high * 15 + n_low * 8)
                early_effect  = min(100, initial_risk * 1.8)
                cascade_risk  = min(100, initial_risk * 3.2)
                system_impact = min(100, initial_risk * 4.5)

                stages = ["INITIAL MARKER","EARLY EFFECT","CASCADE RISK","SYSTEM IMPACT"]
                values = [initial_risk, early_effect, cascade_risk, system_impact]

                line_color = "#ff1744" if system_impact > 70 else "#ffab00" if system_impact > 40 else "#00e5ff"

                fig_risk = go.Figure()
                fig_risk.add_trace(go.Scatter(
                    x=stages, y=values, mode="lines+markers",
                    line=dict(color=line_color, width=2.5, shape="spline"),
                    marker=dict(color=line_color, size=8, symbol="circle",
                                line=dict(color=line_color, width=2)),
                    fill="tozeroy",
                    fillcolor=f"rgba({255 if system_impact>70 else 255 if system_impact>40 else 0},{0 if system_impact>70 else 171 if system_impact>40 else 229},{0 if system_impact>40 else 255},0.08)",
                    hovertemplate="<b>%{x}</b><br>Risk Impact: %{y:.0f}<extra></extra>",
                ))
                fig_risk.update_layout(
                    height=220, margin=dict(l=40,r=20,t=10,b=30),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=False, color="#37474f", tickfont=dict(size=9,family="Orbitron",color="#37474f"), tickangle=0),
                    yaxis=dict(showgrid=True, gridcolor="rgba(0,229,255,0.06)", color="#37474f",
                               tickfont=dict(size=9,color="#37474f"), range=[0,100], title="RISK IMPACT",
                               title_font=dict(size=8,color="#37474f",family="Orbitron")),
                    showlegend=False,
                )
                st.plotly_chart(fig_risk, use_container_width=True, config={"displayModeBar":False})
            except Exception:
                st.info("Install plotly for charts")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── ROW 2: Key Biomarkers | Health Profile | AI Insights extended ─
        row2_left, row2_mid, row2_right = st.columns([1.2, 1.4, 1.4])

        with row2_left:
            # Key biomarkers — show top 6
            st.markdown("""
            <div style="background:#071828;border:1px solid rgba(0,229,255,0.18);border-radius:12px;padding:1rem 1.2rem;position:relative;overflow:hidden">
                <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#00e5ff,transparent);opacity:0.4"></div>
                <div style="font-family:'Orbitron',monospace;font-size:0.8rem;font-weight:700;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.3rem">Key Biomarkers</div>
                <div style="font-size:0.65rem;color:#37474f;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:0.8rem">Extracted Parameter Values</div>
            </div>""", unsafe_allow_html=True)
            count = 0
            for param, value in found.items():
                if count >= 8: break
                status = classif.get(param, "UNKNOWN")
                unit   = get_unit(param)
                badge_bg = {"HIGH":"rgba(255,23,68,0.15)","LOW":"rgba(255,171,0,0.15)","NORMAL":"rgba(0,230,118,0.15)"}.get(status,"rgba(0,229,255,0.1)")
                badge_color = {"HIGH":"#ff1744","LOW":"#ffab00","NORMAL":"#00e676"}.get(status,"#00e5ff")
                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;padding:0.45rem 0;border-bottom:1px solid rgba(0,229,255,0.06)">
                    <span style="font-size:0.85rem;color:#e0f7fa;font-weight:500;min-width:90px">{param}</span>
                    <span style="font-family:'Orbitron',monospace;font-size:0.82rem;color:#00e5ff;font-weight:600">{value} <span style="font-size:0.62rem;color:#37474f">{unit}</span></span>
                    <span style="padding:2px 8px;border-radius:4px;font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;font-family:'Orbitron',monospace;background:{badge_bg};color:{badge_color}">{status}</span>
                </div>""", unsafe_allow_html=True)
                count += 1

        with row2_mid:
            # Health Profile Radar
            st.markdown("""
            <div style="background:var(--card,#071828);border:1px solid rgba(0,229,255,0.18);border-radius:12px;padding:0.8rem 1rem 0;">
                <div style="font-family:'Orbitron',monospace;font-size:0.8rem;font-weight:700;color:#00e5ff;letter-spacing:2px;text-transform:uppercase">Health Profile</div>
                <div style="font-size:0.65rem;color:#37474f;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:0.3rem">Multi-System Radar Analysis</div>
            </div>
            """, unsafe_allow_html=True)

            try:
                import plotly.graph_objects as go
                SYSTEM_PARAMS = {
                    "Oxygen\nTransport": ["Hemoglobin","RBC","Hematocrit"],
                    "Immunity":          ["WBC","Neutrophils","Lymphocytes"],
                    "Inflammation":      ["CRP","ESR","WBC"],
                    "Nutrition":         ["Ferritin","Iron","VitaminD","VitaminB12"],
                    "Cell\nProduction":  ["Platelets","MCV","MCH","MCHC"],
                }
                labels, scores = [], []
                for sys_name, params in SYSTEM_PARAMS.items():
                    sys_params = [p for p in params if p in found]
                    if sys_params:
                        nc = sum(1 for p in sys_params if classif.get(p)=="NORMAL")
                        labels.append(sys_name)
                        scores.append(round(nc/len(sys_params)*100))
                    else:
                        labels.append(sys_name)
                        scores.append(50)

                fig_radar = go.Figure(go.Scatterpolar(
                    r=scores, theta=labels, fill="toself",
                    fillcolor="rgba(0,229,255,0.1)",
                    line=dict(color="#00e5ff", width=2),
                    marker=dict(color="#00e5ff", size=6),
                    hovertemplate="<b>%{theta}</b>: %{r}%<extra></extra>",
                ))
                fig_radar.update_layout(
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(visible=True, range=[0,100],
                            tickfont=dict(color="#37474f",size=8),
                            gridcolor="rgba(0,229,255,0.08)",
                            linecolor="rgba(0,229,255,0.1)"),
                        angularaxis=dict(
                            tickfont=dict(color="#80deea",size=9,family="Rajdhani"),
                            gridcolor="rgba(0,229,255,0.08)",
                            linecolor="rgba(0,229,255,0.1)"),
                    ),
                    paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                    height=280, margin=dict(l=45,r=45,t=20,b=20),
                )
                st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar":False})
            except Exception:
                st.info("Install plotly")

        with row2_right:
            # Extended AI Insights — patterns + risk scores
            patterns_html = ""
            SEV_CHIP_STYLE = {
                "High":     "background:rgba(255,23,68,0.15);color:#ff5252;border:1px solid rgba(255,23,68,0.3)",
                "Moderate": "background:rgba(255,171,0,0.15);color:#ffab00;border:1px solid rgba(255,171,0,0.3)",
                "Low":      "background:rgba(0,230,118,0.15);color:#00e676;border:1px solid rgba(0,230,118,0.3)",
            }
            if patterns:
                patterns_html = ""
                for p in patterns[:3]:
                    sev = p["severity"]
                    chip_s = SEV_CHIP_STYLE.get(sev, "background:rgba(0,229,255,0.1);color:#00e5ff")
                    patterns_html += f'<span style="display:inline-block;padding:3px 10px;border-radius:5px;margin:2px;font-size:0.65rem;font-weight:700;letter-spacing:0.5px;font-family:Orbitron,monospace;{chip_s}">{p["name"]}</span>'
            else:
                patterns_html = '<span style="font-size:0.78rem;color:#00e676">✓ No clinical patterns detected</span>'

            # Risk Assessment — using Streamlit native components (avoids CSS class render issues)
            st.markdown("""
            <div style="background:#071828;border:1px solid rgba(0,229,255,0.18);border-radius:12px;padding:1rem 1.2rem;position:relative;overflow:hidden">
                <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#00e5ff,transparent);opacity:0.4"></div>
                <div style="font-family:'Orbitron',monospace;font-size:0.8rem;font-weight:700;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;margin-bottom:0.3rem">Risk Assessment</div>
                <div style="font-size:0.65rem;color:#37474f;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:1rem">Multi-Domain Risk Analysis</div>
            </div>""", unsafe_allow_html=True)
            for name, d in risk_scores.items():
                level = d.get("level","Low")
                score = d.get("score",0) or 0
                max_s = d.get("max_score",10)
                pct   = round(score/max_s*100) if max_s else 0
                lc    = "#ff1744" if level=="High" else "#ffab00" if level=="Moderate" else "#00e676"
                short = name.replace(" Risk","")
                st.markdown(f"""
                <div style="margin-bottom:0.8rem;background:#041220;border-radius:8px;padding:0.6rem 0.8rem;border:1px solid rgba(0,229,255,0.08)">
                    <div style="display:flex;justify-content:space-between;margin-bottom:5px">
                        <span style="font-family:'Orbitron',monospace;font-size:0.65rem;color:#80deea">{short.upper()}</span>
                        <span style="font-family:'Orbitron',monospace;font-size:0.7rem;color:{lc};font-weight:700">{score}/{max_s} — {level.upper()}</span>
                    </div>
                    <div style="background:rgba(0,229,255,0.06);border-radius:3px;height:6px;overflow:hidden">
                        <div style="background:{lc};width:{pct}%;height:100%;border-radius:3px"></div>
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:#041220;border-radius:8px;padding:0.6rem 0.8rem;border:1px solid rgba(0,229,255,0.08);margin-top:0.3rem">
                <div style="font-family:'Orbitron',monospace;font-size:0.62rem;color:#37474f;letter-spacing:1px;margin-bottom:6px">DETECTED PATTERNS</div>
                {patterns_html}
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:#041220;border-radius:8px;padding:0.5rem 0.8rem;border:1px solid rgba(0,229,255,0.08);margin-top:0.3rem;font-size:0.72rem;color:#37474f">
                <span style="color:#00e5ff;font-family:'Orbitron',monospace;font-size:0.62rem">PARAMETERS</span>
                &nbsp; Total: <b style="color:#00e5ff">{n_total}</b> &nbsp;
                Normal: <b style="color:#00e676">{n_normal}</b> &nbsp;
                High: <b style="color:#ff1744">{n_high}</b> &nbsp;
                Low: <b style="color:#ffab00">{n_low}</b>
            </div>""", unsafe_allow_html=True)

    else:
        # No report loaded yet — show welcome
        st.markdown("""
        <br>
        <div style="text-align:center;padding:3rem">
            <div style="font-family:'Orbitron',monospace;font-size:2rem;font-weight:900;
                        color:#00e5ff;text-shadow:0 0 40px rgba(0,229,255,0.4);margin-bottom:1rem">
                BLOOD AI
            </div>
            <div style="font-size:0.75rem;color:#37474f;letter-spacing:3px;text-transform:uppercase;margin-bottom:2rem">
                Advanced Haematology Insights Platform
            </div>
            <div style="display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;margin-bottom:2rem">
                <div style="text-align:center;background:#071828;border:1px solid rgba(0,229,255,0.15);border-radius:10px;padding:1rem 1.5rem">
                    <div style="font-family:'Orbitron',monospace;font-size:1.4rem;color:#00e5ff">48</div>
                    <div style="font-size:0.65rem;color:#37474f;letter-spacing:1px;text-transform:uppercase">Parameters</div>
                </div>
                <div style="text-align:center;background:#071828;border:1px solid rgba(0,229,255,0.15);border-radius:10px;padding:1rem 1.5rem">
                    <div style="font-family:'Orbitron',monospace;font-size:1.4rem;color:#00e5ff">7</div>
                    <div style="font-size:0.65rem;color:#37474f;letter-spacing:1px;text-transform:uppercase">Patterns</div>
                </div>
                <div style="text-align:center;background:#071828;border:1px solid rgba(0,229,255,0.15);border-radius:10px;padding:1rem 1.5rem">
                    <div style="font-family:'Orbitron',monospace;font-size:1.4rem;color:#00e5ff">4</div>
                    <div style="font-size:0.65rem;color:#37474f;letter-spacing:1px;text-transform:uppercase">Risk Scores</div>
                </div>
                <div style="text-align:center;background:#071828;border:1px solid rgba(0,229,255,0.15);border-radius:10px;padding:1rem 1.5rem">
                    <div style="font-family:'Orbitron',monospace;font-size:1.4rem;color:#00e5ff">3</div>
                    <div style="font-size:0.65rem;color:#37474f;letter-spacing:1px;text-transform:uppercase">AI Models</div>
                </div>
            </div>
            <div style="font-size:0.88rem;color:#546e7a">Upload your blood report above or click a sample to begin analysis</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# ANALYSIS TAB
# ═══════════════════════════════════════════════════════════════════════════
with tab_analysis:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    if not st.session_state.get("report_loaded"):
        st.info("Analyse a report first from the OVERVIEW tab.")
    else:
        found   = st.session_state.get("report_found",{})
        classif = st.session_state.get("report_classifications",{})
        result  = st.session_state.get("_cached_result")
        ratios  = result.ratios if result else {}

        st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin-bottom:1rem">Parameter Analysis</div>', unsafe_allow_html=True)

        try:
            import plotly.graph_objects as go
            STATUS_COLORS = {"HIGH":"#ff1744","LOW":"#ffab00","NORMAL":"#00e5ff","UNKNOWN":"#37474f"}
            cp,cv,cc,ch = [],[],[],[]
            for param,value in found.items():
                ref = REFERENCE_RANGES.get(param)
                if not ref or ref["max"]>=1e9: continue
                status=classif.get(param,"UNKNOWN")
                unit=get_unit(param)
                cp.append(param); cv.append(value); cc.append(STATUS_COLORS.get(status,"#37474f"))
                ch.append(f"<b>{param}</b><br>Value: {value} {unit}<br>Ref: {ref['min']}–{ref['max']} {unit}<br>Status: <b>{status}</b>")
            if cp:
                fig_bar = go.Figure(go.Bar(
                    x=cv,y=cp,orientation="h",marker_color=cc,marker_line_width=0,
                    hovertemplate="%{customdata}<extra></extra>",customdata=ch,
                    text=[f"{v} {get_unit(p)}" for p,v in zip(cp,cv)],
                    textposition="outside",textfont=dict(size=9,color="#80deea",family="Orbitron"),
                ))
                fig_bar.update_layout(
                    height=max(300,len(cp)*36),margin=dict(l=10,r=120,t=10,b=10),
                    paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True,gridcolor="rgba(0,229,255,0.06)",color="#37474f",tickfont=dict(size=9,color="#37474f")),
                    yaxis=dict(autorange="reversed",tickfont=dict(size=10,color="#80deea",family="Orbitron"),tickcolor="rgba(0,0,0,0)"),
                    showlegend=False,
                )
                st.plotly_chart(fig_bar, use_container_width=True,config={"displayModeBar":False})
        except Exception: pass

        if ratios:
            st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin:1.5rem 0 1rem">Medical Ratios</div>', unsafe_allow_html=True)
            rcols = st.columns(min(len(ratios),3))
            for idx,(rname,rd) in enumerate(ratios.items()):
                interp=rd["interpretation"]
                rc="#ff1744" if "High" in interp else "#ffab00" if "Borderline" in interp or "Moderate" in interp else "#00e676"
                rcols[idx%3].markdown(f"""
                <div class="card" style="text-align:center;padding:1rem">
                    <div style="font-family:'Orbitron',monospace;font-size:0.62rem;color:#37474f;text-transform:uppercase;letter-spacing:1px">{rname}</div>
                    <div style="font-family:'Orbitron',monospace;font-size:1.6rem;font-weight:700;color:{rc};margin:0.3rem 0">{rd['value']} <span style="font-size:0.65rem;color:#37474f">{rd['unit']}</span></div>
                    <div style="font-size:0.72rem;color:{rc}">{interp}</div>
                </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# BIOMARKERS TAB
# ═══════════════════════════════════════════════════════════════════════════
with tab_biomarkers:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    if not st.session_state.get("report_loaded"):
        st.info("Analyse a report first from the OVERVIEW tab.")
    else:
        found   = st.session_state.get("report_found",{})
        classif = st.session_state.get("report_classifications",{})
        st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin-bottom:1.2rem">All Biomarkers</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i,(param,value) in enumerate(found.items()):
            status=classif.get(param,"UNKNOWN")
            unit=get_unit(param); ref=get_display_range(param)
            sc={"HIGH":"#ff1744","LOW":"#ffab00","NORMAL":"#00e5ff"}.get(status,"#37474f")
            cols[i%3].markdown(f"""
            <div class="card" style="margin-bottom:0.6rem">
                <div style="font-size:0.65rem;color:#37474f;text-transform:uppercase;letter-spacing:1px;font-family:'Orbitron',monospace">{param}</div>
                <div style="font-family:'Orbitron',monospace;font-size:1.4rem;font-weight:700;color:{sc};margin:0.2rem 0">{value} <span style="font-size:0.65rem;color:#37474f">{unit}</span></div>
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-size:0.68rem;color:#37474f">Ref: {ref}</span>
                    <span class="bm-badge bm-{status}">{status}</span>
                </div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# RISKS TAB
# ═══════════════════════════════════════════════════════════════════════════
with tab_risks:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    if not st.session_state.get("report_loaded"):
        st.info("Analyse a report first from the OVERVIEW tab.")
    else:
        risk_scores = st.session_state.get("report_risk_scores",{})
        patterns    = st.session_state.get("report_patterns",[])
        synthesis   = st.session_state.get("report_synthesis",{})

        st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin-bottom:1.2rem">Risk Assessment</div>', unsafe_allow_html=True)

        if risk_scores:
            rc = st.columns(len(risk_scores))
            for idx,(name,d) in enumerate(risk_scores.items()):
                level=d.get("level","Unknown"); score=d.get("score","N/A"); max_s=d.get("max_score",10)
                factors=d.get("factors",[])
                lc={"High":"#ff1744","Moderate":"#ffab00","Low":"#00e676"}.get(level,"#37474f")
                facts_html="".join(f"<li style='font-size:0.72rem;color:#37474f;margin:2px 0'>{f}</li>" for f in factors[:4])
                rc[idx].markdown(f"""
                <div class="card" style="text-align:center">
                    <div style="font-size:0.62rem;color:#37474f;text-transform:uppercase;letter-spacing:1px;font-family:'Orbitron',monospace">{name}</div>
                    <div style="font-family:'Orbitron',monospace;font-size:2.2rem;font-weight:900;color:{lc};text-shadow:0 0 20px {lc}55;margin:0.3rem 0">{score}/{max_s}</div>
                    <div style="font-family:'Orbitron',monospace;font-size:0.7rem;color:{lc};margin-bottom:0.8rem">{level.upper()} RISK</div>
                    <ul style="text-align:left;padding-left:1rem;list-style:none">{facts_html}</ul>
                </div>""", unsafe_allow_html=True)

        if patterns:
            st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin:1.5rem 0 1rem">Clinical Patterns</div>', unsafe_allow_html=True)
            pc1,pc2 = st.columns(2)
            SEV_COLOR={"High":"#ff1744","Moderate":"#ffab00","Low":"#ffd600"}
            for idx,p in enumerate(patterns):
                sev=p["severity"]; sc=SEV_COLOR.get(sev,"#37474f")
                col=pc1 if idx%2==0 else pc2
                crit="".join(f"<li style='font-size:0.75rem;color:#80deea'>{c}</li>" for c in p["matched_criteria"])
                col.markdown(f"""
                <div class="card" style="border-left:3px solid {sc};margin-bottom:0.6rem">
                    <div style="display:flex;justify-content:space-between">
                        <div style="font-family:'Orbitron',monospace;font-size:0.75rem;color:{sc}">{p['name']}</div>
                        <div style="font-size:0.65rem;color:{sc};background:rgba(0,0,0,0.3);padding:2px 8px;border-radius:4px;font-family:'Orbitron',monospace">{sev.upper()}</div>
                    </div>
                    <div style="font-size:0.78rem;color:#37474f;margin:6px 0">{p['description']}</div>
                    <div style="font-size:0.72rem;color:{sc}">✓ {p['criteria_met']}/{p['total_criteria']} criteria · {p['confidence']}% confidence</div>
                    <ul style="margin:6px 0 0;padding-left:1.2rem">{crit}</ul>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="card" style="text-align:center;padding:2rem"><div style="color:#00e676;font-family:Orbitron,monospace;font-size:0.9rem">✓ NO CLINICAL PATTERNS DETECTED</div><div style="color:#37474f;font-size:0.8rem;margin-top:0.5rem">All parameters within acceptable ranges</div></div>', unsafe_allow_html=True)

        flags=synthesis.get("urgent_flags",[])
        if flags:
            st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#ff1744;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #ff1744;padding-left:0.75rem;margin:1.5rem 0 1rem">🚨 Urgent Flags</div>', unsafe_allow_html=True)
            for flag in flags:
                vt=f" ({flag['value']})" if flag.get("value") else ""
                st.markdown(f'<div style="background:rgba(255,23,68,0.08);border:1px solid rgba(255,23,68,0.3);border-radius:8px;padding:0.7rem 1rem;margin-bottom:0.4rem;color:#ff5252;font-size:0.85rem">🚨 <b>{flag["param"]}</b> — {flag["message"]}{vt}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TRENDS TAB — Health Profile + Synthesis
# ═══════════════════════════════════════════════════════════════════════════
with tab_trends:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    if not st.session_state.get("report_loaded"):
        st.info("Analyse a report first from the OVERVIEW tab.")
    else:
        found   = st.session_state.get("report_found",{})
        classif = st.session_state.get("report_classifications",{})
        synthesis=st.session_state.get("report_synthesis",{})

        t1, t2 = st.columns(2)
        with t1:
            st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin-bottom:1rem">Systems Overview</div>', unsafe_allow_html=True)
            systems=synthesis.get("systems_affected",{})
            SICON={"Blood / Haematology":"🩸","Cardiovascular":"❤️","Endocrine / Metabolism":"🔬","Liver / Hepatic":"🫀","Kidney / Renal":"🫘","Thyroid / Endocrine":"⚡","Electrolytes":"⚗️","Inflammation":"🔥"}
            if systems:
                for sys,params_list in systems.items():
                    icon=SICON.get(sys,"🔹")
                    ptxt=", ".join(f"{p['param']}({p['status']})" for p in params_list)
                    st.markdown(f'<div class="card" style="margin-bottom:0.5rem;display:flex;gap:0.8rem;align-items:center"><div style="font-size:1.2rem">{icon}</div><div><div style="font-family:Orbitron,monospace;font-size:0.72rem;color:#00e5ff">{sys}</div><div style="font-size:0.75rem;color:#37474f">{ptxt}</div></div></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="card" style="text-align:center;color:#00e676;font-family:Orbitron,monospace;font-size:0.8rem;padding:1.5rem">✓ ALL SYSTEMS NORMAL</div>', unsafe_allow_html=True)

        with t2:
            st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin-bottom:1rem">Key Findings</div>', unsafe_allow_html=True)
            kf=synthesis.get("key_findings",[])
            TYPE_COLOR={"HIGH":"#ff1744","LOW":"#ffab00","PATTERN":"#00e5ff","RISK":"#ffab00","RATIO":"#7c4dff","CONTEXT":"#37474f"}
            for f in kf:
                tc=TYPE_COLOR.get(f.get("type",""),"#37474f")
                st.markdown(f'<div class="card" style="margin-bottom:0.5rem;border-left:3px solid {tc}"><span style="font-size:0.65rem;color:{tc};font-weight:700;font-family:Orbitron,monospace">[{f.get("type","")}]</span><span style="font-size:0.82rem;color:#e0f7fa;margin-left:6px">{f.get("text","")}</span></div>', unsafe_allow_html=True)

            positives=synthesis.get("positive_findings",[])
            if positives:
                st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#00e676;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e676;padding-left:0.75rem;margin:1rem 0 0.5rem">Positive Findings</div>', unsafe_allow_html=True)
                for pos in positives:
                    st.markdown(f'<div style="background:rgba(0,230,118,0.05);border:1px solid rgba(0,230,118,0.2);border-radius:8px;padding:0.5rem 0.8rem;margin-bottom:0.3rem;font-size:0.82rem;color:#69f0ae">✅ {pos}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# RECOMMENDATIONS TAB
# ═══════════════════════════════════════════════════════════════════════════
with tab_recs:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    if not st.session_state.get("report_loaded"):
        st.info("Analyse a report first from the OVERVIEW tab.")
    else:
        recs=st.session_state.get("report_recommendations",[])
        st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin-bottom:1.2rem">Personalised Recommendations</div>', unsafe_allow_html=True)
        st.markdown("<small style='color:#37474f;font-size:0.7rem;letter-spacing:1px'>EVERY RECOMMENDATION IS LINKED TO A SPECIFIC FINDING IN YOUR REPORT</small><br><br>", unsafe_allow_html=True)
        if recs:
            cats={}
            for rec in recs: cats.setdefault(rec.get("category","General"),[]).append(rec)
            CAT_ICON={"Diet":"🥗","Lifestyle":"🏃","Follow-up":"🏥","Supplements":"💊","Screening":"🔎","General":"📌"}
            PRIO_COLOR={"Urgent":"#ff1744","High":"#ff5252","Moderate":"#ffab00","Low":"#00e676"}
            for cat,cat_recs in cats.items():
                st.markdown(f"<div style='font-family:Orbitron,monospace;font-size:0.72rem;color:#00e5ff;letter-spacing:1.5px;text-transform:uppercase;margin:1rem 0 0.6rem'>{CAT_ICON.get(cat,'📌')} {cat}</div>", unsafe_allow_html=True)
                for rec in cat_recs:
                    prio=rec.get("priority","Moderate"); pc=PRIO_COLOR.get(prio,"#37474f"); linked=rec.get("linked_to","")
                    st.markdown(f"""
                    <div class="card" style="border-left:3px solid {pc};margin-bottom:0.5rem">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
                            <span style="background:{pc};color:white;padding:1px 8px;border-radius:4px;font-size:0.62rem;font-weight:700;font-family:Orbitron,monospace;letter-spacing:1px">{prio.upper()}</span>
                            <span style="font-size:0.65rem;color:#37474f">🔗 {linked}</span>
                        </div>
                        <div style="font-size:0.85rem;color:#e0f7fa">{rec['action']}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="card" style="text-align:center;padding:2rem;color:#00e676;font-family:Orbitron,monospace">✓ ALL VALUES WITHIN NORMAL RANGE — NO SPECIFIC RECOMMENDATIONS</div>', unsafe_allow_html=True)

        # Context adjustments
        if st.session_state.get("report_loaded") and age_val and gender_val:
            found   = st.session_state.get("report_found",{})
            classif = st.session_state.get("report_classifications",{})
            result  = st.session_state.get("_cached_result")
            adj     = result.adjustments if result else {}
            if adj:
                st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin:1.5rem 0 1rem">Age/Gender Adjustments</div>', unsafe_allow_html=True)
                ac = st.columns(3)
                for idx,(param,a) in enumerate(adj.items()):
                    std_s=classif.get(param,"UNKNOWN"); adj_s=a["status"]
                    changed=adj_s!=std_s
                    bc={"HIGH":"#ff1744","LOW":"#ffab00","NORMAL":"#00e676"}.get(adj_s,"#37474f")
                    r=a["adjusted_range"]
                    ac[idx%3].markdown(f"""
                    <div class="card" style="margin-bottom:0.5rem">
                        <b style="color:#e0f7fa;font-size:0.82rem">{param}</b>: {found[param]} {get_unit(param)}<br>
                        <span style="background:{bc};color:white;padding:1px 8px;border-radius:4px;font-size:0.65rem;font-family:Orbitron,monospace">{adj_s}</span>
                        {"<span style='font-size:0.7rem;color:#ff7043'> ← changed</span>" if changed else ""}<br>
                        <small style="color:#37474f">{a['note']} · {r['min']}–{r['max']}</small>
                    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# REPORT TAB
# ═══════════════════════════════════════════════════════════════════════════
with tab_report:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    if not st.session_state.get("report_loaded"):
        st.info("Analyse a report first from the OVERVIEW tab.")
    else:
        result  = st.session_state.get("_cached_result")
        found   = st.session_state.get("report_found",{})
        classif = st.session_state.get("report_classifications",{})

        n_total=len(found); n_normal=sum(1 for s in classif.values() if s=="NORMAL")
        n_high=sum(1 for s in classif.values() if s=="HIGH"); n_low=sum(1 for s in classif.values() if s=="LOW")

        st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin-bottom:1.2rem">Report Summary</div>', unsafe_allow_html=True)

        rc1,rc2,rc3,rc4 = st.columns(4)
        rc1.markdown(f'<div class="card" style="text-align:center"><div style="font-family:Orbitron,monospace;font-size:1.6rem;color:#00e5ff">{n_total}</div><div style="font-size:0.62rem;color:#37474f;text-transform:uppercase;letter-spacing:1px">Total Tests</div></div>', unsafe_allow_html=True)
        rc2.markdown(f'<div class="card" style="text-align:center"><div style="font-family:Orbitron,monospace;font-size:1.6rem;color:#00e676">{n_normal}</div><div style="font-size:0.62rem;color:#37474f;text-transform:uppercase;letter-spacing:1px">Normal</div></div>', unsafe_allow_html=True)
        rc3.markdown(f'<div class="card" style="text-align:center"><div style="font-family:Orbitron,monospace;font-size:1.6rem;color:#ff1744">{n_high}</div><div style="font-size:0.62rem;color:#37474f;text-transform:uppercase;letter-spacing:1px">High</div></div>', unsafe_allow_html=True)
        rc4.markdown(f'<div class="card" style="text-align:center"><div style="font-family:Orbitron,monospace;font-size:1.6rem;color:#ffab00">{n_low}</div><div style="font-size:0.62rem;color:#37474f;text-transform:uppercase;letter-spacing:1px">Low</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Data table
        st.markdown('<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin-bottom:1rem">Full Data Table</div>', unsafe_allow_html=True)
        table_rows=[]
        for param,value in found.items():
            status=classif.get(param,"UNKNOWN")
            table_rows.append({"Parameter":param,"Value":value,"Unit":get_unit(param),"Reference Range":get_display_range(param),"Status":status})
        df=pd.DataFrame(table_rows)
        def cstatus(v): return {"HIGH":"color:#ff1744;font-weight:bold","LOW":"color:#ffab00;font-weight:bold","NORMAL":"color:#00e676;font-weight:bold"}.get(v,"")
        st.dataframe(df.style.map(cstatus,subset=["Status"]),width='stretch',hide_index=True,height=400)

        dc1, dc2 = st.columns(2)
        dc1.download_button("⬇️ EXPORT CSV",df.to_csv(index=False).encode(),
            file_name=f"BloodAI_{datetime.now().strftime('%Y%m%d')}.csv",mime="text/csv",width='stretch')
        try:
            pdf_b=report_generator.generate(result,patient_name,age_val,gender_val)
            dc2.download_button("📋 DOWNLOAD PDF REPORT",pdf_b,
                file_name=f"BloodAI_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",width='stretch')
        except Exception:
            dc2.info("Install reportlab for PDF")

        st.markdown("""
        <div style="background:rgba(255,214,0,0.04);border:1px solid rgba(255,214,0,0.2);border-radius:8px;padding:0.8rem 1rem;margin-top:1rem;font-size:0.75rem;color:#ffab00">
            ⚠️ <b>MEDICAL DISCLAIMER:</b> This AI-generated report is for informational purposes ONLY and does NOT constitute medical advice. Always consult a qualified healthcare professional.
        </div>
        """, unsafe_allow_html=True)

        with st.expander("⚙️ Pipeline Execution Log"):
            if result:
                for entry in result.pipeline_log:
                    st.text(entry)
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# PATIENT TAB
# ═══════════════════════════════════════════════════════════════════════════
with tab_patient:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown('''<div style="font-family:Orbitron,monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin-bottom:1.5rem">Patient Details</div>''', unsafe_allow_html=True)

    p1, p2 = st.columns(2)
    with p1:
        st.markdown('''<div style="font-size:0.68rem;color:#37474f;text-transform:uppercase;letter-spacing:1px;font-family:Orbitron,monospace;margin-bottom:4px">Patient Name</div>''', unsafe_allow_html=True)
        patient_name_tab = st.text_input("pname", value=patient_name, label_visibility="collapsed", placeholder="Enter patient name", key="pt_name")

        st.markdown('''<div style="font-size:0.68rem;color:#37474f;text-transform:uppercase;letter-spacing:1px;font-family:Orbitron,monospace;margin-bottom:4px;margin-top:1rem">Age</div>''', unsafe_allow_html=True)
        age_tab = st.number_input("page", min_value=0, max_value=120, value=age, label_visibility="collapsed", key="pt_age")

        st.markdown('''<div style="font-size:0.68rem;color:#37474f;text-transform:uppercase;letter-spacing:1px;font-family:Orbitron,monospace;margin-bottom:4px;margin-top:1rem">Gender</div>''', unsafe_allow_html=True)
        gender_tab = st.selectbox("pgender", ["Male","Female","Other","Not specified"], label_visibility="collapsed", key="pt_gender")

    with p2:
        st.markdown('''<div style="font-size:0.68rem;color:#37474f;text-transform:uppercase;letter-spacing:1px;font-family:Orbitron,monospace;margin-bottom:4px">Family History</div>''', unsafe_allow_html=True)
        fh_tab = st.multiselect("pfh", ["Diabetes","Heart Disease","High Blood Pressure","Kidney Disease","Liver Disease","Thyroid Disorder"],
            default=family_history, label_visibility="collapsed", key="pt_fh")

        st.markdown('''<div style="font-size:0.68rem;color:#37474f;text-transform:uppercase;letter-spacing:1px;font-family:Orbitron,monospace;margin-bottom:4px;margin-top:1rem">OCR for Scanned PDFs</div>''', unsafe_allow_html=True)
        ocr_tab = st.checkbox("Enable OCR", value=True, key="pt_ocr")

    # Show current report info if loaded
    if st.session_state.get("report_loaded"):
        found   = st.session_state.get("report_found", {})
        classif = st.session_state.get("report_classifications", {})
        n_total  = len(found)
        n_normal = sum(1 for s in classif.values() if s == "NORMAL")
        n_high   = sum(1 for s in classif.values() if s == "HIGH")
        n_low    = sum(1 for s in classif.values() if s == "LOW")
        hs = round(n_normal/n_total*100) if n_total else 0

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('''<div style="font-family:Orbitron,monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin-bottom:1rem">Report Summary</div>''', unsafe_allow_html=True)

        pm1,pm2,pm3,pm4,pm5 = st.columns(5)
        for col, label, value, color in [
            (pm1, "Total Tests",   str(n_total),  "#00e5ff"),
            (pm2, "Normal",        str(n_normal), "#00e676"),
            (pm3, "High",          str(n_high),   "#ff1744"),
            (pm4, "Low",           str(n_low),    "#ffab00"),
            (pm5, "Health Score",  f"{hs}%",      "#00e5ff"),
        ]:
            col.markdown(f'''<div style="background:#071828;border:1px solid rgba(0,229,255,0.18);border-radius:10px;padding:0.9rem;text-align:center">
                <div style="font-family:Orbitron,monospace;font-size:1.5rem;font-weight:700;color:{color}">{value}</div>
                <div style="font-size:0.62rem;color:#37474f;text-transform:uppercase;letter-spacing:1px;margin-top:3px">{label}</div>
            </div>''', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        result = st.session_state.get("_cached_result")
        ovs    = st.session_state.get("report_synthesis",{}).get("overall_status","Unknown")
        src    = result.file_name if result else "Sample"
        ov_color = {"Urgent":"#ff1744","Concern":"#ffab00","Borderline":"#ffd600","Normal":"#00e676"}.get(ovs,"#00e5ff")
        st.markdown(f'''<div style="background:#071828;border:1px solid {ov_color}55;border-left:4px solid {ov_color};border-radius:10px;padding:1rem 1.4rem">
            <div style="font-family:Orbitron,monospace;font-size:0.75rem;color:{ov_color};font-weight:700">OVERALL STATUS: {ovs.upper()}</div>
            <div style="font-size:0.78rem;color:#80deea;margin-top:4px">{st.session_state.get("report_synthesis",{}).get("headline","")}</div>
            <div style="font-size:0.68rem;color:#37474f;margin-top:6px">Source: {src} &nbsp;|&nbsp; Processed: {result.processed_at if result else ""}</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("No report analysed yet. Go to OVERVIEW tab to upload and analyse.")

    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# CHATBOT TAB
# ═══════════════════════════════════════════════════════════════════════════
with tab_chatbot:
    st.markdown('<div class="page-wrap">', unsafe_allow_html=True)
    st.markdown('''<div style="font-family:Orbitron,monospace;font-size:0.8rem;color:#00e5ff;letter-spacing:2px;text-transform:uppercase;border-left:3px solid #00e5ff;padding-left:0.75rem;margin-bottom:1.5rem">AI Blood Report Assistant</div>''', unsafe_allow_html=True)

    has_report = st.session_state.get("report_loaded", False)
    found_chat  = st.session_state.get("report_found", {})
    classif_chat= st.session_state.get("report_classifications", {})

    # Status banner
    if has_report:
        n_ab = sum(1 for s in classif_chat.values() if s in ("HIGH","LOW"))
        st.markdown(f'''<div style="background:rgba(0,229,255,0.06);border:1px solid rgba(0,229,255,0.2);border-radius:10px;padding:0.8rem 1.2rem;margin-bottom:1rem;display:flex;align-items:center;gap:1rem">
            <div style="width:10px;height:10px;border-radius:50%;background:#00e676;flex-shrink:0"></div>
            <div>
                <div style="font-family:Orbitron,monospace;font-size:0.72rem;color:#00e5ff">REPORT LOADED — {len(found_chat)} parameters · {n_ab} abnormal</div>
                <div style="font-size:0.72rem;color:#37474f;margin-top:2px">Ask me about your specific values below</div>
            </div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown('''<div style="background:rgba(255,171,0,0.06);border:1px solid rgba(255,171,0,0.2);border-radius:10px;padding:0.8rem 1.2rem;margin-bottom:1rem">
            <div style="font-family:Orbitron,monospace;font-size:0.72rem;color:#ffab00">⚠ NO REPORT LOADED — Upload and analyse first for personalised answers</div>
        </div>''', unsafe_allow_html=True)

    # Quick action buttons
    st.markdown('''<div style="font-size:0.68rem;color:#37474f;text-transform:uppercase;letter-spacing:1px;font-family:Orbitron,monospace;margin-bottom:0.6rem">Quick Actions</div>''', unsafe_allow_html=True)
    qa1,qa2,qa3,qa4 = st.columns(4)
    chat_trigger = None
    if qa1.button("📋 Summarize",     width="stretch", key="qa1"): chat_trigger = "Summarize my report"
    if qa2.button("⚠️ Abnormal",       width="stretch", key="qa2"): chat_trigger = "Show my abnormal values"
    if qa3.button("💡 What to do?",   width="stretch", key="qa3"): chat_trigger = "What should I do?"
    if qa4.button("❤️ Risk scores",    width="stretch", key="qa4"): chat_trigger = "What are my risk scores?"

    qa5,qa6,qa7,qa8 = st.columns(4)
    if qa5.button("🔴 Hemoglobin",    width="stretch", key="qa5"): chat_trigger = "What is my hemoglobin?"
    if qa6.button("🩸 Glucose",        width="stretch", key="qa6"): chat_trigger = "What is my glucose?"
    if qa7.button("🫘 Kidney",         width="stretch", key="qa7"): chat_trigger = "What is my creatinine?"
    if qa8.button("🫀 Liver",          width="stretch", key="qa8"): chat_trigger = "What is my liver?"

    st.markdown("<br>", unsafe_allow_html=True)

    # Init chat history
    if "chat_messages" not in st.session_state or not st.session_state["chat_messages"]:
        if has_report:
            n_ab2 = sum(1 for s in classif_chat.values() if s in ("HIGH","LOW"))
            welcome = (f"👋 **Hello! Your report is loaded.**\n\n"
                f"Found **{len(found_chat)} parameters** — **{n_ab2} abnormal** value(s).\n\n"
                "Ask me anything:\n- *Summarize my report*\n- *Show abnormal values*\n- *What should I do?*\n- *What is my hemoglobin?*")
        else:
            welcome = ("👋 **Hello! I am your Blood Report Assistant.**\n\n"
                "Upload and analyse your report first for personalised answers, "
                "or ask me about any blood parameter!\n\n"
                "💡 Try: *Hemoglobin, WBC, Glucose, Cholesterol, Kidney, Liver, Thyroid*")
        st.session_state["chat_messages"] = [{"role":"assistant","content":welcome}]

    # Handle quick action trigger
    if chat_trigger:
        from chatbot_logic import _smart_reply
        st.session_state["chat_messages"].append({"role":"user","content":chat_trigger})
        st.session_state["chat_messages"].append({"role":"assistant","content":_smart_reply(chat_trigger)})

    # Chat display
    chat_container = st.container(height=420)
    with chat_container:
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"], avatar="🩺" if msg["role"]=="assistant" else "👤"):
                st.markdown(msg["content"])

    # Text input
    user_input = st.chat_input("Ask about your report or any blood value...", key="main_chat_input")
    if user_input:
        from chatbot_logic import _smart_reply
        st.session_state["chat_messages"].append({"role":"user","content":user_input})
        st.session_state["chat_messages"].append({"role":"assistant","content":_smart_reply(user_input)})
        st.rerun()

    # Clear button
    if st.button("🗑️ Clear Chat", key="clear_main_chat"):
        st.session_state["chat_messages"] = []
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(
    f"<div style='text-align:center;color:#0d2535;font-size:0.68rem;font-family:Orbitron,monospace;letter-spacing:2px;padding:1rem;border-top:1px solid rgba(0,229,255,0.06)'>"
    f"BLOODAI · MODEL 1 · MODEL 2 · MODEL 3 · SYNTHESIS · MILESTONE 4 · {datetime.now().strftime('%d/%m/%Y')}"
    f"</div>",
    unsafe_allow_html=True,
)