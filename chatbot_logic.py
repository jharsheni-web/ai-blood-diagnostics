# chatbot_logic.py
# Milestone 4 — Smart Report-Aware Chatbot
# STANDALONE — no imports from blood_ai.py or any project module that imports blood_ai

import streamlit as st

# ── Inline helpers (avoids any circular import risk) ──────────────────────────
_REFERENCE_RANGES = {
    "Hemoglobin":{"min":13.5,"max":17.5,"unit":"g/dL"},
    "RBC":       {"min":4.5, "max":5.9, "unit":"million/µL"},
    "WBC":       {"min":4500,"max":11000,"unit":"/µL"},
    "Platelets": {"min":150000,"max":450000,"unit":"/µL"},
    "Hematocrit":{"min":41.0,"max":53.0,"unit":"%"},
    "MCV":       {"min":80.0,"max":100.0,"unit":"fL"},
    "MCH":       {"min":27.0,"max":33.0,"unit":"pg"},
    "Glucose":   {"min":70.0,"max":100.0,"unit":"mg/dL"},
    "HbA1c":     {"min":4.0, "max":5.7, "unit":"%"},
    "Cholesterol":{"min":125.0,"max":200.0,"unit":"mg/dL"},
    "HDL":       {"min":40.0,"max":100.0,"unit":"mg/dL"},
    "LDL":       {"min":0.0, "max":130.0,"unit":"mg/dL"},
    "Triglycerides":{"min":0.0,"max":150.0,"unit":"mg/dL"},
    "ALT":       {"min":7.0, "max":40.0, "unit":"U/L"},
    "AST":       {"min":10.0,"max":40.0, "unit":"U/L"},
    "ALP":       {"min":44.0,"max":147.0,"unit":"U/L"},
    "Bilirubin": {"min":0.1, "max":1.2,  "unit":"mg/dL"},
    "Albumin":   {"min":3.5, "max":5.0,  "unit":"g/dL"},
    "Creatinine":{"min":0.7, "max":1.3,  "unit":"mg/dL"},
    "BUN":       {"min":7.0, "max":20.0, "unit":"mg/dL"},
    "Uric Acid": {"min":3.5, "max":7.2,  "unit":"mg/dL"},
    "eGFR":      {"min":60.0,"max":120.0,"unit":"mL/min/1.73m²"},
    "TSH":       {"min":0.4, "max":4.0,  "unit":"mIU/L"},
    "T3":        {"min":80.0,"max":200.0,"unit":"ng/dL"},
    "T4":        {"min":5.0, "max":12.0, "unit":"µg/dL"},
    "Sodium":    {"min":136.0,"max":145.0,"unit":"mEq/L"},
    "Potassium": {"min":3.5, "max":5.0,  "unit":"mEq/L"},
    "CRP":       {"min":0.0, "max":10.0, "unit":"mg/L"},
    "ESR":       {"min":0.0, "max":20.0, "unit":"mm/hr"},
    "Ferritin":  {"min":12.0,"max":300.0,"unit":"ng/mL"},
    "Iron":      {"min":60.0,"max":170.0,"unit":"µg/dL"},
    "VitaminD":  {"min":30.0,"max":100.0,"unit":"ng/mL"},
    "VitaminB12":{"min":200.0,"max":900.0,"unit":"pg/mL"},
}

def _get_unit(param):
    return _REFERENCE_RANGES.get(param, {}).get("unit", "")

def _get_display_range(param):
    r = _REFERENCE_RANGES.get(param)
    if not r: return "Unknown"
    mn, mx, unit = r["min"], r["max"], r.get("unit","")
    if mx >= 9999: return f"> {mn} {unit}"
    if mn == 0:    return f"< {mx} {unit}"
    return f"{mn} – {mx} {unit}"

# ── Status helpers ─────────────────────────────────────────────────────────────
_STATUS_ICON  = {"HIGH":"🔴","LOW":"🟡","NORMAL":"🟢","UNKNOWN":"⚪"}
_STATUS_LABEL = {"HIGH":"HIGH ⚠️","LOW":"LOW ⚠️","NORMAL":"NORMAL ✅"}

# ── Knowledge Base ─────────────────────────────────────────────────────────────
_KB = {
    "hemoglobin": {
        "keys":       ["hemoglobin","haemoglobin","hb","hgb"],
        "param":      "Hemoglobin",
        "general":    "**Hemoglobin (Hb)** — Oxygen carrier\n\n📊 **Normal Ranges:**\n- Men: 13.5–17.5 g/dL\n- Women: 12.0–15.5 g/dL\n- Children: 11.0–14.5 g/dL\n\n🔴 **Low** → Possible anaemia or blood loss\n🔼 **High** → Dehydration or polycythaemia\n\n💡 If low, also check Iron, Ferritin, and B12",
        "low_advice": "Increase iron-rich foods (spinach, lentils, red meat). Take Vitamin C with iron. Request Ferritin and Iron studies.",
        "high_advice":"May indicate dehydration or polycythaemia. Increase water intake and consult your physician.",
    },
    "rbc": {
        "keys":       ["rbc","red blood cell","erythrocyte"],
        "param":      "RBC",
        "general":    "**RBC (Red Blood Cells)** — Carry oxygen\n\n📊 **Normal:**\n- Men: 4.5–5.9 million/µL\n- Women: 4.1–5.1 million/µL\n\n🔴 **Low** → Anaemia or nutritional deficiency\n🔼 **High** → Dehydration or lung conditions",
        "low_advice": "Evaluate for anaemia — check Hemoglobin, Ferritin, B12. Increase iron and B12 rich foods.",
        "high_advice":"May indicate dehydration. Increase water intake and consult your doctor.",
    },
    "wbc": {
        "keys":       ["wbc","white blood cell","leukocyte","white blood count"],
        "param":      "WBC",
        "general":    "**WBC (White Blood Cells)** — Immune defenders\n\n📊 **Normal:** 4,500–11,000 cells/µL\n\n🔴 **Low** → Viral illness, bone marrow suppression\n🔼 **High** → Infection, inflammation\n\n💡 Check Neutrophils/Lymphocytes for more detail",
        "low_advice": "Low WBC increases infection risk. Avoid crowded places and contact your physician promptly.",
        "high_advice":"Elevated WBC suggests infection or inflammation. Request CRP and blood culture if symptomatic.",
    },
    "platelets": {
        "keys":       ["platelet","plt","thrombocyte"],
        "param":      "Platelets",
        "general":    "**Platelets (PLT)** — Blood clotting cells\n\n📊 **Normal:** 150,000–450,000 /µL\n\n🔴 **Low** → Bleeding risk — avoid aspirin and NSAIDs\n🔼 **High** → Clotting risk or iron deficiency",
        "low_advice": "Avoid NSAIDs and aspirin. Report any unusual bleeding to your doctor immediately.",
        "high_advice":"High platelets can increase clotting risk. Consult your doctor.",
    },
    "glucose": {
        "keys":       ["glucose","blood sugar","fasting glucose","fbs","sugar"],
        "param":      "Glucose",
        "general":    "**Blood Glucose** — Energy fuel\n\n📊 **Fasting Ranges:**\n- Normal: 70–100 mg/dL\n- Pre-diabetic: 100–125 mg/dL\n- Diabetic: ≥126 mg/dL\n\n🔴 **High** → Diabetes risk — check HbA1c\n🔴 **Low (<70)** → Hypoglycaemia — eat immediately",
        "low_advice": "Low blood sugar — eat something sugary immediately. Monitor regularly.",
        "high_advice":"Reduce sugary drinks, white rice, and refined carbs. Walk 30 min daily. Request HbA1c test.",
    },
    "hba1c": {
        "keys":       ["hba1c","a1c","glycated","glycosylated"],
        "param":      "HbA1c",
        "general":    "**HbA1c** — 3-month blood sugar average\n\n📊 **Ranges:**\n- Normal: < 5.7%\n- Pre-diabetic: 5.7–6.4%\n- Diabetic: ≥ 6.5%\n\n🔼 **High** → Poor long-term blood sugar control",
        "low_advice": "HbA1c is normal. Maintain healthy diet and exercise.",
        "high_advice":"HbA1c ≥ 6.5% indicates diabetes. Strict carbohydrate control needed. Consult a diabetologist.",
    },
    "cholesterol": {
        "keys":       ["cholesterol","total cholesterol"],
        "param":      "Cholesterol",
        "general":    "**Total Cholesterol** — Blood fat\n\n📊 **Normal:** < 200 mg/dL\n- Borderline: 200–239 mg/dL\n- High: ≥ 240 mg/dL\n\n🔼 **High** → Heart disease and stroke risk\n\n💡 Always check HDL, LDL, and Triglycerides together",
        "low_advice": "Low total cholesterol — generally not a concern. Ensure adequate nutrition.",
        "high_advice":"Reduce saturated fats. Increase soluble fibre (oats, beans). Discuss statin therapy with doctor.",
    },
    "hdl": {
        "keys":       ["hdl","good cholesterol"],
        "param":      "HDL",
        "general":    "**HDL Cholesterol** — The 'good' cholesterol\n\n📊 **Normal:**\n- Men: > 40 mg/dL\n- Women: > 50 mg/dL\n- Optimal: > 60 mg/dL\n\n🔴 **Low** → Increased cardiovascular risk\n\n💡 Exercise and healthy fats raise HDL",
        "low_advice": "Low HDL increases heart disease risk. Do 150 min aerobic exercise weekly. Eat healthy fats.",
        "high_advice":"High HDL is generally protective and beneficial. No concern.",
    },
    "ldl": {
        "keys":       ["ldl","bad cholesterol"],
        "param":      "LDL",
        "general":    "**LDL Cholesterol** — The 'bad' cholesterol\n\n📊 **Normal:**\n- Optimal: < 100 mg/dL\n- Borderline: 130–159 mg/dL\n- High: ≥ 160 mg/dL\n\n🔼 **High** → Artery buildup, heart attack risk",
        "low_advice": "LDL is within optimal range. Maintain healthy diet.",
        "high_advice":"Reduce saturated fat. Add plant sterols and soluble fibre. Discuss statin therapy with doctor.",
    },
    "triglycerides": {
        "keys":       ["triglyceride","tg","triglycerides"],
        "param":      "Triglycerides",
        "general":    "**Triglycerides** — Blood fats\n\n📊 **Normal:** < 150 mg/dL\n- Borderline: 150–199 mg/dL\n- High: ≥ 200 mg/dL\n\n🔼 **High** → Pancreatitis and cardiovascular risk",
        "low_advice": "Triglycerides are within normal range.",
        "high_advice":"Avoid alcohol, sugary drinks, and refined carbs. Add omega-3 fatty acids (fish oil).",
    },
    "liver": {
        "keys":       ["liver","alt","sgpt","ast","sgot","bilirubin","lft","liver function"],
        "param":      "ALT",
        "general":    "**Liver Function Tests (LFT)**\n\n📊 **Normal Ranges:**\n- ALT (SGPT): 7–40 U/L\n- AST (SGOT): 10–40 U/L\n- ALP: 44–147 U/L\n- Total Bilirubin: 0.1–1.2 mg/dL\n\n🔼 **Elevated enzymes** → Liver stress or hepatitis\n\n💡 Avoid alcohol if liver enzymes are elevated",
        "low_advice": "ALT is within normal range — liver function appears healthy.",
        "high_advice":"Avoid alcohol and paracetamol overuse. Repeat LFT in 6–8 weeks. Consider liver ultrasound.",
    },
    "kidney": {
        "keys":       ["kidney","creatinine","renal","bun","egfr","kft","kidney function"],
        "param":      "Creatinine",
        "general":    "**Kidney Function Tests (KFT)**\n\n📊 **Normal Ranges:**\n- Creatinine: 0.7–1.3 mg/dL (men), 0.6–1.1 (women)\n- BUN: 7–20 mg/dL\n- eGFR: > 60 mL/min/1.73m²\n\n🔼 **High creatinine / low eGFR** → Reduced kidney filtration\n\n💡 Drink 2.5–3 litres water daily. Avoid NSAIDs.",
        "low_advice": "Low creatinine may indicate low muscle mass. Generally not concerning.",
        "high_advice":"Drink 2.5–3 litres water daily. Avoid NSAIDs. Repeat kidney function test in 2–4 weeks.",
    },
    "thyroid": {
        "keys":       ["thyroid","tsh","t3","t4","thyroxine"],
        "param":      "TSH",
        "general":    "**Thyroid Function Tests**\n\n📊 **Normal Ranges:**\n- TSH: 0.4–4.0 mIU/L\n- T3: 80–200 ng/dL\n- T4: 5.0–12.0 µg/dL\n\n🔼 **High TSH** → Possible hypothyroidism\n🔴 **Low TSH** → Possible hyperthyroidism",
        "low_advice": "Low TSH may indicate hyperthyroidism. Request Free T3, T4 and consult endocrinologist.",
        "high_advice":"High TSH suggests hypothyroidism. Request Free T3, T4, thyroid antibodies. Consult endocrinologist.",
    },
    "vitamin": {
        "keys":       ["vitamin","vitamin d","vitamin b12","b12","vit d"],
        "param":      "VitaminD",
        "general":    "**Vitamins**\n\n📊 **Normal Ranges:**\n- Vitamin D: 30–100 ng/mL (< 20 = deficient)\n- Vitamin B12: 200–900 pg/mL (< 200 = deficient)\n\n🔴 **Low Vit D** → Bone pain, fatigue, low immunity\n🔴 **Low B12** → Fatigue, tingling, memory problems",
        "low_advice": "Supplement with Vitamin D3 1000–2000 IU daily with a fatty meal. 15–20 min morning sunlight.",
        "high_advice":"Very high Vitamin D can be toxic. Reduce supplementation and consult your doctor.",
    },
}

_QUICK_SUGGESTIONS = [
    ("📋 Summarize report",   "Summarize my report"),
    ("⚠️ Abnormal values",    "Show my abnormal values"),
    ("💡 What should I do?",  "What should I do?"),
    ("❤️ Risk scores",         "What are my risk scores?"),
    ("🔴 My Hemoglobin",      "What is my hemoglobin?"),
    ("🩸 My Glucose",          "What is my glucose?"),
    ("🫘 My Kidney",           "What is my creatinine?"),
    ("🫀 My Liver",            "What is my liver?"),
]


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE — save orchestrator result
# ══════════════════════════════════════════════════════════════════════════════

def save_report_to_session(result):
    """Store orchestrator result in session state for chatbot access."""
    if result and result.success:
        st.session_state["report_found"]           = result.found
        st.session_state["report_classifications"] = result.classifications
        st.session_state["report_patterns"]        = result.patterns
        st.session_state["report_risk_scores"]     = result.risk_scores
        st.session_state["report_recommendations"] = result.recommendations
        st.session_state["report_synthesis"]       = result.synthesis
        st.session_state["report_loaded"]          = True


# ══════════════════════════════════════════════════════════════════════════════
# SMART REPLY ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def _smart_reply(user_input):
    q           = user_input.lower().strip()
    has_report  = st.session_state.get("report_loaded", False)
    found       = st.session_state.get("report_found", {})
    classif     = st.session_state.get("report_classifications", {})
    patterns    = st.session_state.get("report_patterns", [])
    risk_scores = st.session_state.get("report_risk_scores", {})
    recs        = st.session_state.get("report_recommendations", [])
    synthesis   = st.session_state.get("report_synthesis", {})

    # 1. REPORT SUMMARY
    if any(k in q for k in ["summarize","summary","summarise","my report","overall","overview"]):
        if not has_report:
            return "⚠️ No report loaded yet.\n\nPlease **upload and analyse** your blood report first, then ask me to summarize it!"
        n_total  = len(found)
        n_normal = sum(1 for s in classif.values() if s == "NORMAL")
        n_high   = sum(1 for s in classif.values() if s == "HIGH")
        n_low    = sum(1 for s in classif.values() if s == "LOW")
        ovs      = synthesis.get("overall_status","Unknown")
        headline = synthesis.get("headline","")
        lines = [
            "## 📋 Your Report Summary\n",
            f"**Overall Status:** {ovs}",
            f"*{headline}*\n",
            f"- Total parameters: **{n_total}**",
            f"- Normal ✅: **{n_normal}**",
            f"- High 🔴: **{n_high}**",
            f"- Low 🟡: **{n_low}**\n",
        ]
        if patterns:
            lines.append("**Patterns:** " + ", ".join(p["name"] for p in patterns) + "\n")
        high_risk = [n for n,d in risk_scores.items() if d.get("level")=="High"]
        if high_risk:
            lines.append("**High risk:** " + ", ".join(high_risk) + "\n")
        lines.append("*Ask me **'abnormal values'** or **'what should I do'** for more!*")
        return "\n".join(lines)

    # 2. ABNORMAL VALUES
    if any(k in q for k in ["abnormal","problem","issue","concern","not normal","out of range"]):
        if not has_report:
            return "⚠️ No report loaded yet.\n\nPlease **upload and analyse** your blood report first!"
        high_p = [(p,v) for p,v in found.items() if classif.get(p)=="HIGH"]
        low_p  = [(p,v) for p,v in found.items() if classif.get(p)=="LOW"]
        if not high_p and not low_p:
            return "✅ **Great news! All your parameters are within normal range.**\n\nNo abnormal values found."
        lines = ["## ⚠️ Your Abnormal Values\n"]
        if high_p:
            lines.append("**🔴 HIGH values:**")
            for param,val in high_p:
                lines.append(f"- **{param}:** {val} {_get_unit(param)} *(above normal)*")
            lines.append("")
        if low_p:
            lines.append("**🟡 LOW values:**")
            for param,val in low_p:
                lines.append(f"- **{param}:** {val} {_get_unit(param)} *(below normal)*")
            lines.append("")
        lines.append("*Ask me **'what should I do?'** for recommendations.*")
        return "\n".join(lines)

    # 3. RECOMMENDATIONS
    if any(k in q for k in ["recommend","advice","what should","what to do","how to improve","tips","action"]):
        if not has_report:
            return "⚠️ No report loaded yet.\n\nPlease **upload and analyse** your report first!"
        if not recs:
            return "✅ **Your report looks healthy!**\n\nAll values are within normal range — maintain healthy diet, exercise, and annual checkups."
        lines = ["## 💡 Your Personalised Recommendations\n"]
        cats = {}
        for rec in recs[:12]:
            cats.setdefault(rec.get("category","General"),[]).append(rec)
        cat_icons  = {"Diet":"🥗","Lifestyle":"🏃","Follow-up":"🏥","Supplements":"💊","Screening":"🔎","General":"📌"}
        prio_icons = {"Urgent":"🚨","High":"🔴","Moderate":"🟠","Low":"🟢"}
        for cat, cat_recs in cats.items():
            lines.append(f"**{cat_icons.get(cat,'📌')} {cat}:**")
            for rec in cat_recs:
                prio   = rec.get("priority","Moderate")
                linked = rec.get("linked_to","")
                lines.append(f"{prio_icons.get(prio,'•')} *[{prio}]* {rec['action']} *(→ {linked})*")
            lines.append("")
        return "\n".join(lines)

    # 4. RISK SCORES
    if any(k in q for k in ["risk","risk score","cardiovascular","diabetes risk","heart risk"]):
        if not has_report:
            return "⚠️ No report loaded yet.\n\nPlease upload and analyse your report first!"
        if not risk_scores:
            return "Risk scores could not be calculated. Please set **age** and **gender** in the sidebar."
        lines = ["## ⚠️ Your Risk Scores\n"]
        icons = {"High":"🔴","Moderate":"🟠","Low":"🟢"}
        for name,d in risk_scores.items():
            level   = d.get("level","Unknown")
            score   = d.get("score","N/A")
            max_s   = d.get("max_score",10)
            factors = d.get("factors",[])
            lines.append(f"{icons.get(level,'⚪')} **{name}:** {score}/{max_s} — **{level}**")
            if factors:
                lines.append(f"   *Factors: {', '.join(factors[:3])}*")
        return "\n".join(lines)

    # 5. PATTERNS
    if any(k in q for k in ["pattern","syndrome","metabolic","anemia","anaemia","infection"]):
        if not has_report:
            return "⚠️ No report loaded yet.\n\nPlease upload and analyse your report first!"
        if not patterns:
            return "✅ No significant clinical patterns detected in your report."
        lines = ["## 🔍 Clinical Patterns in Your Report\n"]
        sev_icons = {"High":"🔴","Moderate":"🟠","Low":"🟡"}
        for p in patterns:
            lines.append(f"{sev_icons.get(p['severity'],'⚪')} **{p['name']}** ({p['severity']}, {p['confidence']}%)")
            lines.append(f"   {p['description']}")
            lines.append("")
        return "\n".join(lines)

    # 6. PERSONALISED PARAM QUERY ("what is MY hemoglobin")
    my_words    = ["my ","what is my","show my","tell me my","check my","is my"]
    is_personal = any(w in q for w in my_words)

    for topic, data in _KB.items():
        for key in data["keys"]:
            if key in q:
                param_name = data["param"]
                if has_report and param_name in found:
                    val    = found[param_name]
                    status = classif.get(param_name,"UNKNOWN")
                    unit   = _get_unit(param_name)
                    ref    = _get_display_range(param_name)
                    icon   = _STATUS_ICON.get(status,"⚪")
                    label  = _STATUS_LABEL.get(status,status)
                    lines  = [f"## {icon} Your {param_name} Result\n"]
                    lines.append(f"**Your Value:** `{val} {unit}`")
                    lines.append(f"**Status:** {label}")
                    lines.append(f"**Reference Range:** {ref}\n")
                    if status == "HIGH":
                        lines.append(f"⚠️ **Your {param_name} is above normal range.**\n")
                        lines.append(f"💡 **What to do:** {data['high_advice']}")
                    elif status == "LOW":
                        lines.append(f"⚠️ **Your {param_name} is below normal range.**\n")
                        lines.append(f"💡 **What to do:** {data['low_advice']}")
                    else:
                        lines.append(f"✅ **Your {param_name} is within normal range.** No concern.")
                    lines.append("\n---\n*Ask **'what should I do?'** for your full personalised plan.*")
                    return "\n".join(lines)
                elif is_personal and not has_report:
                    return (
                        f"⚠️ I don't have your **{param_name}** value yet.\n\n"
                        f"Please **upload and analyse your blood report** first!\n\n"
                        f"**General information:**\n\n{data['general']}"
                    )
                else:
                    return data["general"]

    # 7. HELLO
    if any(k in q for k in ["hello","hi","hey","start","help","good morning","good evening"]):
        if has_report:
            n_ab = sum(1 for s in classif.values() if s in ("HIGH","LOW"))
            return (
                f"👋 **Hello! Your report is loaded.**\n\n"
                f"Found **{len(found)} parameters** — **{n_ab} abnormal** value(s).\n\n"
                "Ask me:\n- *\"Summarize my report\"*\n"
                "- *\"Show my abnormal values\"*\n"
                "- *\"What should I do?\"*\n"
                "- *\"What is my hemoglobin?\"*"
            )
        return (
            "👋 **Hello! I am your Blood Report Assistant.**\n\n"
            "Upload and analyse your blood report for **personalised answers**, "
            "or ask me about any blood parameter!\n\n"
            "💡 Try: *Hemoglobin, WBC, Glucose, Cholesterol, Kidney, Liver, Thyroid*"
        )

    # 8. FALLBACK
    if has_report:
        return (
            "I didn't catch that. Try:\n\n"
            "📋 *\"Summarize my report\"*\n"
            "⚠️ *\"Show my abnormal values\"*\n"
            "💡 *\"What should I do?\"*\n"
            "❤️ *\"What are my risk scores?\"*\n"
            "🔬 *\"What is my hemoglobin?\"* (any parameter)"
        )
    return (
        "I can help with:\n\n"
        "📋 **CBC:** Hemoglobin, RBC, WBC, Platelets\n"
        "🩸 **Metabolic:** Glucose, HbA1c\n"
        "❤️ **Lipids:** Cholesterol, HDL, LDL, Triglycerides\n"
        "🫀 **Liver:** ALT, AST, Bilirubin\n"
        "🫘 **Kidney:** Creatinine, BUN, eGFR\n"
        "⚡ **Thyroid:** TSH, T3, T4\n"
        "💊 **Vitamins:** Vitamin D, B12\n\n"
        "**Upload your report for personalised answers!**"
    )


# ══════════════════════════════════════════════════════════════════════════════
# RENDER CHATBOT
# ══════════════════════════════════════════════════════════════════════════════

def render_chatbot():
    """Render the report-aware chatbot in the Streamlit sidebar."""

    st.sidebar.markdown("---")

    # Toggle state
    if "show_chatbot" not in st.session_state:
        st.session_state["show_chatbot"] = False

    has_report = st.session_state.get("report_loaded", False)

    # Warning badge when abnormal values exist
    if has_report and not st.session_state["show_chatbot"]:
        n_ab = sum(
            1 for s in st.session_state.get("report_classifications",{}).values()
            if s in ("HIGH","LOW")
        )
        if n_ab > 0:
            st.sidebar.warning(f"⚠️ {n_ab} abnormal value(s) — open assistant!")

    # Toggle button
    btn_label = (
        "🩺 Open AI Assistant"
        if not st.session_state["show_chatbot"]
        else "❌ Close Assistant"
    )
    if st.sidebar.button(
        btn_label,
        type="primary" if not st.session_state["show_chatbot"] else "secondary",
        width='stretch',
        key="chatbot_toggle_btn"
    ):
        st.session_state["show_chatbot"] = not st.session_state["show_chatbot"]
        st.rerun()

    if not st.session_state["show_chatbot"]:
        return

    # Header
    report_badge = "🟢 Report loaded" if has_report else "🔵 No report loaded"
    st.sidebar.markdown(
        f"""<div style="background:linear-gradient(135deg,#1565c0,#0d47a1);
            padding:12px 14px;border-radius:10px;margin:6px 0">
            <div style="color:white;font-size:14px;font-weight:600">
                🩺 Blood Report Assistant
            </div>
            <div style="color:#90caf9;font-size:11px;margin-top:3px">
                {report_badge} · Report-aware · AI-powered
            </div>
        </div>""",
        unsafe_allow_html=True
    )

    # Init chat history
    if "chat_messages" not in st.session_state or not st.session_state["chat_messages"]:
        if has_report:
            found   = st.session_state.get("report_found",{})
            classif = st.session_state.get("report_classifications",{})
            n_ab    = sum(1 for s in classif.values() if s in ("HIGH","LOW"))
            welcome = (
                f"👋 **Hello! Your report is loaded.**\n\n"
                f"Found **{len(found)} parameters** — **{n_ab} abnormal** value(s).\n\n"
                "Try:\n- *\"Summarize my report\"*\n"
                "- *\"Show abnormal values\"*\n"
                "- *\"What should I do?\"*\n"
                "- *\"What is my hemoglobin?\"*"
            )
        else:
            welcome = (
                "👋 **Hello! I am your Blood Report Assistant.**\n\n"
                "Upload and analyse your report for **personalised answers**, "
                "or ask me about any blood parameter!"
            )
        st.session_state["chat_messages"] = [{"role":"assistant","content":welcome}]

    # Quick suggestion buttons
    st.sidebar.markdown("<small><b>Quick actions:</b></small>", unsafe_allow_html=True)
    c1, c2 = st.sidebar.columns(2)
    for i,(label,query) in enumerate(_QUICK_SUGGESTIONS):
        col = c1 if i%2==0 else c2
        if col.button(label, key=f"qs_{i}", width='stretch'):
            st.session_state["chat_messages"].append({"role":"user",      "content":query})
            st.session_state["chat_messages"].append({"role":"assistant", "content":_smart_reply(query)})
            st.rerun()

    # Chat display
    chat_box = st.sidebar.container(height=350)
    with chat_box:
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"],
                                  avatar="🩺" if msg["role"]=="assistant" else "👤"):
                st.markdown(msg["content"])

    # Text input
    user_input = st.sidebar.chat_input("Ask about your report or any blood value...")
    if user_input:
        st.session_state["chat_messages"].append({"role":"user",      "content":user_input})
        st.session_state["chat_messages"].append({"role":"assistant", "content":_smart_reply(user_input)})
        st.rerun()

    # Clear
    if st.sidebar.button("🗑️ Clear Chat", width='stretch', key="clear_chat_btn"):
        st.session_state["chat_messages"] = []
        st.rerun()