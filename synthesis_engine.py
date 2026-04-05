#
# a
from typing import Dict, List, Optional


class SynthesisEngine:
    """
    Milestone 3 Core:
    1. Findings Synthesis  — aggregates Model 1 + 2 + 3 outputs into a
                             structured, coherent clinical summary.
    2. Recommendation Generator — produces prioritised, finding-linked
                                  actionable advice (diet, lifestyle, follow-up).
    """

    # ── Urgency mapping ───────────────────────────────────────────────────────
    # Maps pattern names → urgency level for summary triage
    PATTERN_URGENCY = {
        "Kidney Function Pattern":          "Urgent",
        "Infection / Inflammation Pattern": "Urgent",
        "Liver Stress Pattern":             "Urgent",
        "Metabolic Syndrome":               "Monitor",
        "Dyslipidemia Pattern":             "Monitor",
        "Anemia Pattern":                   "Monitor",
        "Thyroid Dysfunction Pattern":      "Monitor",
    }

    # ── Finding → recommendation mapping ─────────────────────────────────────
    # Each entry: finding_key → list of recommendation dicts
    # finding_key matches parameter names, pattern names, or risk score names
    FINDING_REC_MAP = {

        # ── CBC ───────────────────────────────────────────────────────────────
        "Hemoglobin_LOW": [
            {"category": "Diet",       "priority": "High",
             "finding":  "Low Hemoglobin",
             "action":   "Increase iron-rich foods: red meat, spinach, lentils, fortified cereals. "
                         "Pair with Vitamin C (lemon juice, tomatoes) to boost iron absorption."},
            {"category": "Follow-up",  "priority": "High",
             "finding":  "Low Hemoglobin",
             "action":   "Request iron studies (Ferritin, TIBC, Serum Iron) and peripheral blood smear "
                         "to determine the type and cause of anaemia."},
        ],
        "Hemoglobin_HIGH": [
            {"category": "Follow-up",  "priority": "Moderate",
             "finding":  "High Hemoglobin",
             "action":   "High haemoglobin may indicate dehydration or polycythaemia. "
                         "Ensure adequate hydration and consult a physician if persistent."},
        ],
        "WBC_HIGH": [
            {"category": "Follow-up",  "priority": "High",
             "finding":  "Elevated WBC",
             "action":   "Elevated white blood cells suggest infection or inflammation. "
                         "Complete differential count and CRP test recommended within 48 hours."},
        ],
        "WBC_LOW": [
            {"category": "Follow-up",  "priority": "High",
             "finding":  "Low WBC",
             "action":   "Low WBC (leucopenia) may indicate bone marrow suppression or viral infection. "
                         "Avoid crowded places and consult a physician promptly."},
        ],
        "Platelets_LOW": [
            {"category": "Lifestyle",  "priority": "High",
             "finding":  "Low Platelets",
             "action":   "Avoid aspirin and NSAIDs (ibuprofen). Prevent cuts and bruises. "
                         "Seek urgent review if any unusual bleeding or bruising occurs."},
        ],

        # ── Blood Sugar ───────────────────────────────────────────────────────
        "Glucose_HIGH": [
            {"category": "Diet",       "priority": "High",
             "finding":  "High Fasting Glucose",
             "action":   "Eliminate sugary drinks, white rice, and refined carbohydrates. "
                         "Choose whole grains, vegetables, and low-glycaemic foods at every meal."},
            {"category": "Lifestyle",  "priority": "High",
             "finding":  "High Fasting Glucose",
             "action":   "30 minutes of brisk walking daily significantly lowers fasting glucose. "
                         "Aim for at least 5 days per week."},
            {"category": "Follow-up",  "priority": "High",
             "finding":  "High Fasting Glucose",
             "action":   "Request HbA1c test if not already done. Monitor fasting glucose weekly. "
                         "Consult a physician or diabetologist for formal assessment."},
        ],
        "HbA1c_HIGH": [
            {"category": "Diet",       "priority": "High",
             "finding":  "Elevated HbA1c",
             "action":   "HbA1c above 6.5% indicates diabetes. Strict carbohydrate control is essential. "
                         "Reduce portion sizes and avoid sugary foods completely."},
            {"category": "Follow-up",  "priority": "High",
             "finding":  "Elevated HbA1c",
             "action":   "Refer to diabetologist. HbA1c should be rechecked every 3 months. "
                         "Discuss medication options if lifestyle changes are insufficient."},
        ],

        # ── Lipids ────────────────────────────────────────────────────────────
        "Cholesterol_HIGH": [
            {"category": "Diet",       "priority": "High",
             "finding":  "High Total Cholesterol",
             "action":   "Replace saturated fats (butter, red meat, full-fat dairy) with unsaturated fats "
                         "(olive oil, avocado, nuts). Increase soluble fibre: oats, beans, psyllium husk."},
        ],
        "HDL_LOW": [
            {"category": "Lifestyle",  "priority": "High",
             "finding":  "Low HDL (protective cholesterol)",
             "action":   "Aerobic exercise is the most effective way to raise HDL. "
                         "Aim for 150 minutes of moderate cardio weekly. "
                         "Add healthy fats: olive oil, nuts, fatty fish (salmon, mackerel)."},
            {"category": "Lifestyle",  "priority": "High",
             "finding":  "Low HDL",
             "action":   "Quit smoking if applicable — smoking directly lowers HDL. "
                         "Avoid trans fats found in processed and fried foods."},
        ],
        "LDL_HIGH": [
            {"category": "Diet",       "priority": "High",
             "finding":  "High LDL (bad cholesterol)",
             "action":   "Reduce saturated fat to less than 7% of daily calories. "
                         "Add plant sterols (fortified spreads), soluble fibre, and soy protein to your diet."},
            {"category": "Follow-up",  "priority": "Moderate",
             "finding":  "High LDL",
             "action":   "Discuss statin therapy with your physician if LDL remains above 130 mg/dL "
                         "after 3 months of dietary intervention, especially with family history of heart disease."},
        ],
        "Triglycerides_HIGH": [
            {"category": "Diet",       "priority": "High",
             "finding":  "High Triglycerides",
             "action":   "Avoid alcohol, sugary drinks, white bread, and sweets — these directly raise triglycerides. "
                         "Omega-3 fatty acids (fish oil, flaxseed) can significantly lower triglycerides."},
        ],

        # ── Liver ─────────────────────────────────────────────────────────────
        "ALT_HIGH": [
            {"category": "Lifestyle",  "priority": "High",
             "finding":  "Elevated ALT (liver enzyme)",
             "action":   "Avoid alcohol completely. Avoid paracetamol overuse and herbal supplements "
                         "without physician approval. These are directly hepatotoxic."},
            {"category": "Follow-up",  "priority": "High",
             "finding":  "Elevated ALT",
             "action":   "Repeat LFT in 6–8 weeks. If still elevated, request ultrasound abdomen "
                         "to assess for fatty liver or hepatitis."},
        ],
        "AST_HIGH": [
            {"category": "Follow-up",  "priority": "High",
             "finding":  "Elevated AST (liver/muscle enzyme)",
             "action":   "High AST combined with high ALT indicates liver stress. "
                         "If AST/ALT ratio > 2, this may indicate alcoholic liver disease. "
                         "Hepatology consultation recommended."},
        ],
        "Bilirubin_HIGH": [
            {"category": "Follow-up",  "priority": "High",
             "finding":  "High Bilirubin",
             "action":   "Elevated bilirubin may cause jaundice. Check for yellowing of eyes/skin. "
                         "Urgent ultrasound abdomen and hepatology review recommended."},
        ],

        # ── Kidney ────────────────────────────────────────────────────────────
        "Creatinine_HIGH": [
            {"category": "Lifestyle",  "priority": "High",
             "finding":  "High Creatinine",
             "action":   "Drink 2.5–3 litres of water daily. Avoid NSAIDs (ibuprofen, diclofenac) "
                         "and contrast dyes without physician guidance. Reduce high-protein diet if excessive."},
            {"category": "Follow-up",  "priority": "High",
             "finding":  "High Creatinine",
             "action":   "Repeat kidney function test in 2–4 weeks. If eGFR < 60, "
                         "nephrology referral is recommended."},
        ],
        "eGFR_LOW": [
            {"category": "Follow-up",  "priority": "High",
             "finding":  "Reduced eGFR (kidney filtration)",
             "action":   "eGFR below 60 indicates chronic kidney disease Stage 3. "
                         "Nephrology consultation is strongly recommended. "
                         "Monitor blood pressure regularly and restrict sodium intake."},
            {"category": "Diet",       "priority": "High",
             "finding":  "Reduced eGFR",
             "action":   "Restrict dietary phosphorus (dairy, nuts, cola drinks) and potassium "
                         "(bananas, potatoes) as kidneys may struggle to excrete them."},
        ],
        "BUN_HIGH": [
            {"category": "Diet",       "priority": "Moderate",
             "finding":  "High BUN (blood urea nitrogen)",
             "action":   "Reduce red meat and high-protein foods. "
                         "Increase water intake. BUN elevation with high creatinine indicates kidney stress."},
        ],
        "Uric Acid_HIGH": [
            {"category": "Diet",       "priority": "Moderate",
             "finding":  "High Uric Acid (gout risk)",
             "action":   "Avoid organ meats, shellfish, red meat, and alcohol (especially beer). "
                         "Drink plenty of water. Cherry juice may help lower uric acid levels."},
        ],

        # ── Thyroid ───────────────────────────────────────────────────────────
        "TSH_HIGH": [
            {"category": "Follow-up",  "priority": "High",
             "finding":  "High TSH (possible hypothyroidism)",
             "action":   "High TSH indicates the thyroid may be underactive. "
                         "Request Free T3, Free T4, and thyroid antibodies test. "
                         "Endocrinology consultation recommended."},
        ],
        "TSH_LOW": [
            {"category": "Follow-up",  "priority": "High",
             "finding":  "Low TSH (possible hyperthyroidism)",
             "action":   "Low TSH may indicate overactive thyroid. Symptoms include palpitations, "
                         "weight loss, and anxiety. Request Free T3, T4 and nuclear scan if symptomatic."},
        ],

        # ── Vitamins / Iron ───────────────────────────────────────────────────
        "VitaminD_LOW": [
            {"category": "Supplements", "priority": "Moderate",
             "finding":  "Low Vitamin D",
             "action":   "Supplement with Vitamin D3 1000–2000 IU daily with a fatty meal. "
                         "Aim for 15–20 minutes of morning sunlight daily."},
        ],
        "VitaminB12_LOW": [
            {"category": "Supplements", "priority": "Moderate",
             "finding":  "Low Vitamin B12",
             "action":   "Supplement with methylcobalamin 500 mcg daily. "
                         "Increase B12 foods: eggs, dairy, fish, and meat. "
                         "Vegans are at high risk — consider monthly B12 injections."},
        ],
        "Ferritin_LOW": [
            {"category": "Diet",       "priority": "High",
             "finding":  "Low Ferritin (iron stores)",
             "action":   "Depleted iron stores precede anaemia. Start iron supplementation "
                         "(ferrous sulphate 200 mg daily) with Vitamin C. "
                         "Avoid tea/coffee within 1 hour of iron tablets."},
        ],
        "CRP_HIGH": [
            {"category": "Follow-up",  "priority": "High",
             "finding":  "Elevated CRP (inflammation marker)",
             "action":   "Elevated CRP indicates systemic inflammation or infection. "
                         "Identify and treat the underlying cause. "
                         "If no infection found, consider anti-inflammatory diet (Mediterranean diet)."},
        ],

        # ── Pattern-linked recommendations ────────────────────────────────────
        "Metabolic Syndrome": [
            {"category": "Lifestyle",  "priority": "High",
             "finding":  "Metabolic Syndrome pattern",
             "action":   "Metabolic syndrome significantly raises heart disease and diabetes risk. "
                         "Weight loss of even 5–10% body weight dramatically improves all markers. "
                         "Combine calorie reduction with 30 minutes of daily exercise."},
            {"category": "Follow-up",  "priority": "High",
             "finding":  "Metabolic Syndrome pattern",
             "action":   "Annual fasting glucose, lipid panel, and blood pressure check is essential. "
                         "Discuss aspirin therapy and statin therapy with your physician."},
        ],
        "Kidney Function Pattern": [
            {"category": "Follow-up",  "priority": "Urgent",
             "finding":  "Kidney Function Pattern",
             "action":   "Multiple kidney markers are abnormal. Nephrology referral is recommended. "
                         "Stop any nephrotoxic medications. Monitor urine output and blood pressure daily."},
        ],
        "Dyslipidemia Pattern": [
            {"category": "Diet",       "priority": "High",
             "finding":  "Dyslipidemia Pattern",
             "action":   "Full lipid abnormality detected. Switch to Mediterranean diet: "
                         "olive oil, fish, vegetables, whole grains, legumes, and nuts. "
                         "Eliminate processed foods, trans fats, and sugary beverages entirely."},
        ],
        "Anemia Pattern": [
            {"category": "Follow-up",  "priority": "High",
             "finding":  "Anaemia Pattern",
             "action":   "Multiple anaemia markers present. Identify type: iron deficiency, "
                         "B12/folate deficiency, or chronic disease anaemia. "
                         "Peripheral blood smear and iron studies required."},
        ],
        "Infection / Inflammation Pattern": [
            {"category": "Follow-up",  "priority": "Urgent",
             "finding":  "Infection/Inflammation Pattern",
             "action":   "Markers suggest active infection or significant inflammation. "
                         "Blood culture, urine culture, and chest X-ray may be required. "
                         "Do not delay medical consultation."},
        ],
    }

    # ══════════════════════════════════════════════════════════════════════════
    # 1. FINDINGS SYNTHESIS ENGINE
    # ══════════════════════════════════════════════════════════════════════════

    def synthesize(
        self,
        parameters:      Dict[str, Optional[float]],
        classifications: Dict[str, str],
        patterns:        List[Dict],
        risk_scores:     Dict[str, Dict],
        ratios:          Dict[str, Dict],
        adjustments:     Dict[str, Dict],
        age:             Optional[int]    = None,
        gender:          Optional[str]    = None,
        family_history:  Optional[List]   = None,
    ) -> Dict:
        """
        Aggregate all model outputs into a single coherent findings summary.

        Returns a structured dict with:
          overall_status    — Urgent / Concern / Borderline / Normal
          headline          — one-sentence plain-English summary
          key_findings      — list of the most important findings
          systems_affected  — organs/systems with issues
          pattern_summary   — plain-English pattern descriptions
          risk_summary      — plain-English risk interpretation
          urgent_flags      — findings needing immediate attention
          positive_findings — what is normal / good news
          completeness      — how many params were found vs expected
        """
        found = {k: v for k, v in parameters.items() if v is not None}

        # ── Triage: count abnormals ───────────────────────────────────────────
        high_params   = [p for p, s in classifications.items() if s == "HIGH"]
        low_params    = [p for p, s in classifications.items() if s == "LOW"]
        normal_params = [p for p, s in classifications.items() if s == "NORMAL"]
        abnormal      = high_params + low_params

        high_risk_scores = [
            name for name, d in risk_scores.items()
            if d.get("level") == "High"
        ]
        urgent_patterns = [
            p["name"] for p in patterns
            if self.PATTERN_URGENCY.get(p["name"]) == "Urgent"
        ]

        # ── Overall status ────────────────────────────────────────────────────
        if urgent_patterns or len(high_risk_scores) >= 2 or len(abnormal) >= 8:
            overall_status = "Urgent"
        elif len(abnormal) >= 4 or len(high_risk_scores) >= 1 or len(patterns) >= 2:
            overall_status = "Concern"
        elif len(abnormal) >= 1:
            overall_status = "Borderline"
        else:
            overall_status = "Normal"

        # ── Headline ──────────────────────────────────────────────────────────
        headline = self._build_headline(
            overall_status, abnormal, patterns, high_risk_scores,
            age, gender
        )

        # ── Key findings (top 5 most important) ──────────────────────────────
        key_findings = self._build_key_findings(
            high_params, low_params, patterns, risk_scores, ratios, adjustments
        )

        # ── Systems affected ──────────────────────────────────────────────────
        systems = self._identify_systems(classifications, patterns)

        # ── Pattern plain-English summary ────────────────────────────────────
        pattern_summary = self._summarise_patterns(patterns)

        # ── Risk plain-English summary ────────────────────────────────────────
        risk_summary = self._summarise_risks(risk_scores, age, gender)

        # ── Urgent flags ──────────────────────────────────────────────────────
        urgent_flags = self._get_urgent_flags(
            classifications, patterns, risk_scores, found
        )

        # ── Positive findings ─────────────────────────────────────────────────
        positives = self._get_positives(normal_params, patterns, risk_scores)

        # ── Completeness ──────────────────────────────────────────────────────
        expected_core = [
            "Hemoglobin","WBC","Platelets","Glucose","HbA1c",
            "Cholesterol","HDL","LDL","Triglycerides",
            "ALT","AST","Creatinine","BUN","eGFR","TSH"
        ]
        found_core  = [p for p in expected_core if p in found]
        completeness = {
            "found":    len(found),
            "core_found": len(found_core),
            "core_total": len(expected_core),
            "pct":      round(len(found_core) / len(expected_core) * 100),
        }

        return {
            "overall_status":  overall_status,
            "headline":        headline,
            "key_findings":    key_findings,
            "systems_affected":systems,
            "pattern_summary": pattern_summary,
            "risk_summary":    risk_summary,
            "urgent_flags":    urgent_flags,
            "positive_findings":positives,
            "completeness":    completeness,
            "counts": {
                "total":   len(found),
                "normal":  len(normal_params),
                "high":    len(high_params),
                "low":     len(low_params),
                "patterns":len(patterns),
            }
        }

    def _build_headline(self, status, abnormal, patterns, high_risks, age, gender):
        ctx = f"{age}-year-old {gender.lower()}" if age and gender else "this patient"
        if status == "Normal":
            return f"All parameters are within normal range for {ctx}. No significant concerns detected."
        if status == "Urgent":
            main = patterns[0]["name"] if patterns else f"{len(abnormal)} abnormal values"
            return (f"Urgent attention recommended for {ctx}. "
                    f"{main} detected with {len(high_risks)} high-risk score(s). "
                    f"Medical consultation should not be delayed.")
        if status == "Concern":
            sys_txt = f"{len(abnormal)} abnormal parameters"
            pat_txt = f" and {len(patterns)} clinical pattern(s)" if patterns else ""
            return (f"Multiple concerns identified for {ctx}: "
                    f"{sys_txt}{pat_txt}. "
                    f"Medical review recommended within 1–2 weeks.")
        return (f"Borderline findings for {ctx}: {len(abnormal)} parameter(s) outside normal range. "
                f"Monitor and repeat tests in 4–6 weeks.")

    def _build_key_findings(self, high, low, patterns, risk_scores, ratios, adjustments):
        findings = []

        # Critical high values first
        CRITICAL_HIGH = {
            "Glucose": "Fasting glucose is elevated — possible pre-diabetes or diabetes",
            "HbA1c":   "HbA1c is high — reflects poor blood sugar control over 3 months",
            "Creatinine": "Creatinine is elevated — kidney filtration may be reduced",
            "ALT":     "Liver enzyme ALT is elevated — possible liver stress",
            "AST":     "Liver enzyme AST is elevated — possible liver or muscle damage",
            "TSH":     "TSH is elevated — thyroid may be underactive",
            "LDL":     "LDL (bad cholesterol) is high — cardiovascular risk increased",
            "Triglycerides": "Triglycerides are elevated — metabolic and heart risk increased",
            "WBC":     "White blood cell count is high — possible infection or inflammation",
            "CRP":     "CRP is elevated — active inflammation or infection present",
        }
        CRITICAL_LOW = {
            "Hemoglobin": "Haemoglobin is low — possible anaemia",
            "HDL":        "HDL (protective cholesterol) is low — cardiovascular risk increased",
            "eGFR":       "eGFR is reduced — kidney filtration capacity is impaired",
            "Ferritin":   "Ferritin is low — iron stores are depleted",
            "VitaminD":   "Vitamin D is deficient — immune and bone health affected",
            "VitaminB12": "Vitamin B12 is low — nerve and blood cell function affected",
        }
        for p in high:
            if p in CRITICAL_HIGH:
                findings.append({"type": "HIGH", "param": p, "text": CRITICAL_HIGH[p]})
        for p in low:
            if p in CRITICAL_LOW:
                findings.append({"type": "LOW",  "param": p, "text": CRITICAL_LOW[p]})

        # Top patterns
        for pat in patterns[:2]:
            findings.append({
                "type":  "PATTERN",
                "param": pat["name"],
                "text":  f"{pat['name']} detected ({pat['severity']} severity) — {pat['description']}"
            })

        # High risk scores
        for name, d in risk_scores.items():
            if d.get("level") == "High":
                findings.append({
                    "type":  "RISK",
                    "param": name,
                    "text":  f"{name}: {d['score']}/{d['max_score']} — {d['interpretation']}"
                })

        # Notable ratios
        for rname, rd in ratios.items():
            if "High" in rd.get("interpretation", ""):
                findings.append({
                    "type":  "RATIO",
                    "param": rname,
                    "text":  f"{rname} ratio = {rd['value']} ({rd['interpretation']})"
                })

        # Context changes from Model 3
        for param, adj in adjustments.items():
            if adj.get("status") != adj.get("original_status"):
                findings.append({
                    "type":  "CONTEXT",
                    "param": param,
                    "text":  f"{param} reclassified as {adj['status']} after age/gender adjustment"
                })

        return findings[:8]  # top 8 most important

    def _identify_systems(self, classifications, patterns):
        systems = {}
        PARAM_SYSTEM = {
            "Hemoglobin": "Blood / Haematology", "RBC": "Blood / Haematology",
            "WBC": "Blood / Haematology", "Platelets": "Blood / Haematology",
            "Hematocrit": "Blood / Haematology", "MCV": "Blood / Haematology",
            "MCH": "Blood / Haematology", "MCHC": "Blood / Haematology",
            "Neutrophils": "Blood / Haematology", "Lymphocytes": "Blood / Haematology",
            "Glucose": "Endocrine / Metabolism", "HbA1c": "Endocrine / Metabolism",
            "Cholesterol": "Cardiovascular", "HDL": "Cardiovascular",
            "LDL": "Cardiovascular", "Triglycerides": "Cardiovascular",
            "ALT": "Liver / Hepatic", "AST": "Liver / Hepatic",
            "ALP": "Liver / Hepatic", "Bilirubin": "Liver / Hepatic",
            "Albumin": "Liver / Hepatic",
            "Creatinine": "Kidney / Renal", "BUN": "Kidney / Renal",
            "eGFR": "Kidney / Renal", "Uric Acid": "Kidney / Renal",
            "TSH": "Thyroid / Endocrine", "T3": "Thyroid / Endocrine",
            "T4": "Thyroid / Endocrine",
            "Sodium": "Electrolytes", "Potassium": "Electrolytes",
            "Calcium": "Electrolytes", "Magnesium": "Electrolytes",
            "CRP": "Inflammation", "ESR": "Inflammation",
            "Iron": "Iron / Nutrition", "Ferritin": "Iron / Nutrition",
            "VitaminD": "Vitamins / Nutrition", "VitaminB12": "Vitamins / Nutrition",
        }
        for param, status in classifications.items():
            if status in ("HIGH", "LOW"):
                system = PARAM_SYSTEM.get(param, "Other")
                if system not in systems:
                    systems[system] = []
                systems[system].append({"param": param, "status": status})

        return systems

    def _summarise_patterns(self, patterns):
        if not patterns:
            return ["No significant clinical patterns detected. Individual parameters reviewed."]
        summaries = []
        for p in patterns:
            icon = "🔴" if p["severity"] == "High" else "🟠" if p["severity"] == "Moderate" else "🟡"
            summaries.append(
                f"{icon} {p['name']} ({p['severity']} severity, "
                f"{p['confidence']}% confidence): {p['description']}"
            )
        return summaries

    def _summarise_risks(self, risk_scores, age, gender):
        summaries = []
        for name, d in risk_scores.items():
            level = d.get("level", "Unknown")
            score = d.get("score")
            max_s = d.get("max_score", 10)
            factors = d.get("factors", [])
            if level == "Low" and score == 0:
                summaries.append(f"✅ {name}: Low ({score}/{max_s}) — No significant risk factors identified.")
            else:
                fac_txt = ", ".join(factors[:3]) if factors else "see report"
                summaries.append(
                    f"{'🔴' if level=='High' else '🟠' if level=='Moderate' else '🟢'} "
                    f"{name}: {level} ({score}/{max_s}) — Key factors: {fac_txt}."
                )
        return summaries

    def _get_urgent_flags(self, classifications, patterns, risk_scores, found):
        flags = []

        # Critical single values
        URGENT_THRESHOLDS = {
            "Glucose":    ("HIGH", 180, "Glucose > 180 mg/dL — urgent diabetes management needed"),
            "HbA1c":      ("HIGH", 8.0, "HbA1c > 8% — poor long-term glucose control"),
            "Creatinine": ("HIGH", 2.0, "Creatinine > 2.0 mg/dL — significant kidney impairment"),
            "eGFR":       ("LOW",  30,  "eGFR < 30 mL/min — Stage 4 kidney disease"),
            "ALT":        ("HIGH", 80,  "ALT > 80 U/L — significant liver enzyme elevation"),
            "Hemoglobin": ("LOW",  9.0, "Hemoglobin < 9 g/dL — severe anaemia"),
            "Potassium":  ("HIGH", 5.5, "Potassium > 5.5 mEq/L — risk of cardiac arrhythmia"),
            "Potassium":  ("LOW",  3.0, "Potassium < 3.0 mEq/L — risk of cardiac arrhythmia"),
            "Sodium":     ("LOW",  125, "Sodium < 125 mEq/L — severe hyponatraemia"),
        }
        for param, (direction, threshold, message) in URGENT_THRESHOLDS.items():
            val = found.get(param)
            if val is None:
                continue
            if direction == "HIGH" and val >= threshold:
                flags.append({"param": param, "message": message, "value": val})
            elif direction == "LOW" and val <= threshold:
                flags.append({"param": param, "message": message, "value": val})

        # Urgent patterns
        for p in patterns:
            if self.PATTERN_URGENCY.get(p["name"]) == "Urgent":
                flags.append({
                    "param":   p["name"],
                    "message": f"{p['name']} detected — medical consultation required promptly",
                    "value":   None,
                })

        return flags

    def _get_positives(self, normal_params, patterns, risk_scores):
        positives = []
        POSITIVE_MSG = {
            "Hemoglobin":   "Haemoglobin is normal — no anaemia detected",
            "Glucose":      "Fasting glucose is normal — no diabetes risk from glucose alone",
            "HbA1c":        "HbA1c is normal — good long-term blood sugar control",
            "Creatinine":   "Creatinine is normal — kidneys filtering well",
            "eGFR":         "eGFR is normal — good kidney filtration rate",
            "ALT":          "Liver enzyme ALT is normal — no liver stress detected",
            "TSH":          "TSH is normal — thyroid function appears healthy",
            "Cholesterol":  "Total cholesterol is within range",
            "HDL":          "HDL (protective cholesterol) is adequate",
            "WBC":          "White blood cell count is normal — no infection indicators",
        }
        for p in normal_params:
            if p in POSITIVE_MSG:
                positives.append(POSITIVE_MSG[p])

        # Low risk scores
        for name, d in risk_scores.items():
            if d.get("level") == "Low":
                positives.append(f"{name} is low — no major {name.lower()} factors detected")

        return positives[:5]

    # ══════════════════════════════════════════════════════════════════════════
    # 2. PERSONALISED RECOMMENDATION GENERATOR
    # ══════════════════════════════════════════════════════════════════════════

    def generate_recommendations(
        self,
        classifications:  Dict[str, str],
        patterns:         List[Dict],
        risk_scores:      Dict[str, Dict],
        parameters:       Dict[str, Optional[float]],
        age:              Optional[int]  = None,
        gender:           Optional[str] = None,
        family_history:   Optional[List] = None,
    ) -> List[Dict]:
        """
        Generate finding-linked, prioritised recommendations.

        Each recommendation includes:
          category    — Diet / Lifestyle / Follow-up / Supplements / Screening
          priority    — Urgent / High / Moderate / Low
          finding     — the specific finding that triggered this recommendation
          action      — the specific actionable advice
          linked_to   — parameter or pattern name (for UI linking)
        """
        recs = []
        seen = set()  # deduplicate

        def add(rec_list, linked_to):
            for r in rec_list:
                key = r["action"][:60]
                if key not in seen:
                    seen.add(key)
                    recs.append({**r, "linked_to": linked_to})

        # ── Parameter-linked recommendations ──────────────────────────────────
        for param, status in classifications.items():
            if status in ("HIGH", "LOW"):
                key = f"{param}_{status}"
                if key in self.FINDING_REC_MAP:
                    add(self.FINDING_REC_MAP[key], param)

        # ── Pattern-linked recommendations ────────────────────────────────────
        for pattern in patterns:
            pname = pattern["name"]
            if pname in self.FINDING_REC_MAP:
                add(self.FINDING_REC_MAP[pname], pname)

        # ── Age-specific recommendations ──────────────────────────────────────
        if age:
            if age > 60:
                add([{
                    "category": "Screening", "priority": "High",
                    "finding":  "Age > 60",
                    "action":   "Annual comprehensive blood panel recommended including bone density "
                                "and cardiac stress test for patients over 60.",
                }], "Age")
                add([{
                    "category": "Lifestyle", "priority": "Moderate",
                    "finding":  "Age > 60",
                    "action":   "Low-impact daily exercise: 30 minutes walking, swimming, or yoga. "
                                "Include balance exercises to prevent falls.",
                }], "Age")
            elif age > 40:
                add([{
                    "category": "Screening", "priority": "Moderate",
                    "finding":  "Age > 40",
                    "action":   "Annual lipid panel, fasting glucose, and blood pressure check "
                                "recommended for adults over 40.",
                }], "Age")

        # ── Family history recommendations ────────────────────────────────────
        fh_lower = [f.lower() for f in (family_history or [])]
        if "diabetes" in " ".join(fh_lower):
            glucose = parameters.get("Glucose", 0) or 0
            if glucose > 90:
                add([{
                    "category": "Screening", "priority": "High",
                    "finding":  "Family history of Diabetes",
                    "action":   "Annual HbA1c and oral glucose tolerance test strongly recommended "
                                "given family history of diabetes.",
                }], "Family History")
        if "heart disease" in " ".join(fh_lower):
            add([{
                "category": "Screening", "priority": "High",
                "finding":  "Family history of Heart Disease",
                "action":   "Annual lipid panel, ECG, and blood pressure monitoring essential "
                            "given family history of heart disease.",
            }], "Family History")

        # ── High CVD risk — add aspirin discussion ────────────────────────────
        cvd = risk_scores.get("Cardiovascular Risk", {})
        if cvd.get("level") == "High":
            add([{
                "category": "Follow-up", "priority": "High",
                "finding":  "High Cardiovascular Risk Score",
                "action":   "Discuss low-dose aspirin therapy and statin medication with your physician. "
                            "Blood pressure monitoring and annual ECG recommended.",
            }], "Cardiovascular Risk")

        # ── Sort: Urgent → High → Moderate → Low ─────────────────────────────
        ORDER = {"Urgent": 0, "High": 1, "Moderate": 2, "Low": 3}
        recs.sort(key=lambda r: ORDER.get(r.get("priority", "Low"), 4))

        return recs