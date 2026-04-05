# pattern_recognition.py

# Identifies clinical patterns, calculates risk scores and medical ratios

from typing import Dict, List, Tuple, Optional


class PatternRecognizer:
    """
    Model 2: Detects multi-parameter clinical patterns, computes risk scores,
    and calculates key medical ratios from a blood report parameter dict.
    """

    def __init__(self):
        # ── Clinical Pattern Definitions ─────────────────────────────────────
        # Each pattern has: criteria list, min criteria needed, description
        self.patterns = {

            "Metabolic Syndrome": {
                "description": (
                    "Cluster of conditions increasing risk of heart disease, "
                    "stroke, and type 2 diabetes."
                ),
                "min_criteria_met": 2,
                "criteria": [
                    {"param": "Glucose",       "condition": "high", "threshold": 100,
                     "label": "Fasting glucose ≥ 100 mg/dL (impaired fasting)"},
                    {"param": "HDL",           "condition": "low",  "threshold": 40,
                     "label": "HDL < 40 mg/dL (low protective cholesterol)"},
                    {"param": "Triglycerides", "condition": "high", "threshold": 150,
                     "label": "Triglycerides ≥ 150 mg/dL (elevated)"},
                    {"param": "Cholesterol",   "condition": "high", "threshold": 200,
                     "label": "Total cholesterol > 200 mg/dL"},
                ],
            },

            "Anemia Pattern": {
                "description": (
                    "Reduced oxygen-carrying capacity. May indicate iron deficiency, "
                    "chronic disease, or nutritional deficiency."
                ),
                "min_criteria_met": 2,
                "criteria": [
                    {"param": "Hemoglobin",  "condition": "low",  "threshold": 13.5,
                     "label": "Hemoglobin < 13.5 g/dL"},
                    {"param": "RBC",         "condition": "low",  "threshold": 4.5,
                     "label": "RBC count < 4.5 million/µL"},
                    {"param": "Hematocrit",  "condition": "low",  "threshold": 40.0,
                     "label": "Hematocrit < 40%"},
                    {"param": "MCV",         "condition": "low",  "threshold": 80.0,
                     "label": "MCV < 80 fL (microcytic — possible iron deficiency)"},
                    {"param": "Ferritin",    "condition": "low",  "threshold": 12.0,
                     "label": "Ferritin < 12 ng/mL (depleted iron stores)"},
                ],
            },

            "Infection / Inflammation Pattern": {
                "description": (
                    "Elevated markers suggest active bacterial infection or "
                    "systemic inflammation."
                ),
                "min_criteria_met": 2,
                "criteria": [
                    {"param": "WBC",         "condition": "high", "threshold": 11000,
                     "label": "WBC > 11,000/µL (leukocytosis)"},
                    {"param": "Neutrophils", "condition": "high", "threshold": 70.0,
                     "label": "Neutrophils > 70% (neutrophilia)"},
                    {"param": "CRP",         "condition": "high", "threshold": 10.0,
                     "label": "CRP > 10 mg/L (elevated C-reactive protein)"},
                    {"param": "ESR",         "condition": "high", "threshold": 20.0,
                     "label": "ESR > 20 mm/hr (elevated sedimentation rate)"},
                ],
            },

            "Liver Stress Pattern": {
                "description": (
                    "Elevated liver enzymes suggest hepatocellular damage, "
                    "fatty liver, or hepatitis."
                ),
                "min_criteria_met": 2,
                "criteria": [
                    {"param": "ALT",             "condition": "high", "threshold": 40.0,
                     "label": "ALT > 40 U/L (liver enzyme elevated)"},
                    {"param": "AST",             "condition": "high", "threshold": 40.0,
                     "label": "AST > 40 U/L (liver/muscle enzyme elevated)"},
                    {"param": "ALP",             "condition": "high", "threshold": 147.0,
                     "label": "ALP > 147 U/L (bile duct or bone marker)"},
                    {"param": "Bilirubin",       "condition": "high", "threshold": 1.2,
                     "label": "Total bilirubin > 1.2 mg/dL"},
                    {"param": "DirectBilirubin", "condition": "high", "threshold": 0.3,
                     "label": "Direct bilirubin > 0.3 mg/dL (biliary obstruction risk)"},
                ],
            },

            "Kidney Function Pattern": {
                "description": (
                    "Elevated waste markers suggest reduced kidney filtration. "
                    "May indicate chronic kidney disease or acute injury."
                ),
                "min_criteria_met": 2,
                "criteria": [
                    {"param": "Creatinine", "condition": "high", "threshold": 1.3,
                     "label": "Creatinine > 1.3 mg/dL (elevated)"},
                    {"param": "BUN",        "condition": "high", "threshold": 20.0,
                     "label": "BUN > 20 mg/dL (elevated urea)"},
                    {"param": "Uric Acid",  "condition": "high", "threshold": 7.2,
                     "label": "Uric Acid > 7.2 mg/dL (hyperuricemia / gout risk)"},
                    {"param": "eGFR",       "condition": "low",  "threshold": 60.0,
                     "label": "eGFR < 60 mL/min/1.73m² (reduced filtration)"},
                ],
            },

            "Thyroid Dysfunction Pattern": {
                "description": (
                    "Abnormal thyroid markers suggest hypothyroidism or hyperthyroidism."
                ),
                "min_criteria_met": 1,
                "criteria": [
                    {"param": "TSH", "condition": "high", "threshold": 4.0,
                     "label": "TSH > 4.0 mIU/L (possible hypothyroidism)"},
                    {"param": "TSH", "condition": "low",  "threshold": 0.4,
                     "label": "TSH < 0.4 mIU/L (possible hyperthyroidism)"},
                    {"param": "T3",  "condition": "low",  "threshold": 80.0,
                     "label": "T3 < 80 ng/dL (low triiodothyronine)"},
                    {"param": "T4",  "condition": "low",  "threshold": 5.0,
                     "label": "T4 < 5.0 µg/dL (low thyroxine)"},
                ],
            },

            "Dyslipidemia Pattern": {
                "description": (
                    "Abnormal lipid profile significantly increasing cardiovascular risk."
                ),
                "min_criteria_met": 2,
                "criteria": [
                    {"param": "Cholesterol",   "condition": "high", "threshold": 200.0,
                     "label": "Total cholesterol > 200 mg/dL"},
                    {"param": "LDL",           "condition": "high", "threshold": 130.0,
                     "label": "LDL > 130 mg/dL (high bad cholesterol)"},
                    {"param": "Triglycerides", "condition": "high", "threshold": 150.0,
                     "label": "Triglycerides > 150 mg/dL"},
                    {"param": "HDL",           "condition": "low",  "threshold": 40.0,
                     "label": "HDL < 40 mg/dL (low protective cholesterol)"},
                ],
            },
        }

    # ══════════════════════════════════════════════════════════════════════════
    # Pattern Analysis  (Milestone 2 Goal 1)
    # ══════════════════════════════════════════════════════════════════════════

    def analyze_patterns(self, parameters: Dict[str, Optional[float]]) -> List[Dict]:
        """
        Identify clinical patterns from a parameter dict.

        Returns list of dicts:
            name, description, severity, criteria_met, total_criteria,
            matched_criteria, confidence
        """
        if not parameters:
            return []

        detected = []

        for pattern_name, pattern_info in self.patterns.items():
            criteria_met = 0
            matched_criteria = []

            for criterion in pattern_info["criteria"]:
                param = criterion["param"]
                value = parameters.get(param)
                if value is None:
                    continue

                condition  = criterion["condition"]
                threshold  = criterion["threshold"]
                label      = criterion["label"]

                if condition == "high" and value >= threshold:
                    criteria_met += 1
                    matched_criteria.append(f"{label}  →  found: {value}")
                elif condition == "low" and value <= threshold:
                    criteria_met += 1
                    matched_criteria.append(f"{label}  →  found: {value}")

            total = len(pattern_info["criteria"])
            if criteria_met >= pattern_info["min_criteria_met"]:
                detected.append({
                    "name":             pattern_name,
                    "description":      pattern_info["description"],
                    "severity":         self._assess_severity(criteria_met, total),
                    "criteria_met":     criteria_met,
                    "total_criteria":   total,
                    "matched_criteria": matched_criteria,
                    "confidence":       round(criteria_met / total * 100),
                })

        # Sort: highest severity first
        order = {"High": 0, "Moderate": 1, "Low": 2}
        detected.sort(key=lambda x: order.get(x["severity"], 9))
        return detected

    def _assess_severity(self, met: int, total: int) -> str:
        ratio = met / total if total else 0
        if ratio >= 0.75:
            return "High"
        elif ratio >= 0.5:
            return "Moderate"
        return "Low"

    # ══════════════════════════════════════════════════════════════════════════
    # Risk Score Calculations  (Milestone 2 Goal 1)
    # ══════════════════════════════════════════════════════════════════════════

    def calculate_risk_scores(
        self,
        parameters: Dict[str, Optional[float]],
        age: Optional[int] = None,
        gender: Optional[str] = None,
    ) -> Dict[str, Dict]:
        """
        Calculate cardiovascular, diabetes, liver, and kidney risk scores.
        Returns dict of {risk_name: {score, max_score, level, interpretation, factors}}
        """
        calculators = {
            "Cardiovascular Risk": self._calculate_cvd_risk,
            "Diabetes Risk":       self._calculate_diabetes_risk,
            "Liver Risk":          self._calculate_liver_risk,
            "Kidney Risk":         self._calculate_kidney_risk,
        }

        results = {}
        for name, func in calculators.items():
            try:
                results[name] = func(parameters, age, gender)
            except Exception as e:
                results[name] = {
                    "score":          None,
                    "max_score":      10,
                    "level":          "Unknown",
                    "interpretation": f"Could not calculate: {e}",
                    "factors":        [],
                }
        return results

    def _calculate_cvd_risk(
        self,
        params: Dict,
        age: Optional[int],
        gender: Optional[str],
    ) -> Dict:
        score = 0
        max_score = 10
        factors = []

        # Age
        if age:
            if age > 65:   score += 2; factors.append("Age > 65")
            elif age > 45: score += 1; factors.append("Age 45–65")

        # Gender
        if gender and gender.lower() == "male":
            score += 1; factors.append("Male gender")

        # Cholesterol
        chol = params.get("Cholesterol")
        if chol:
            if chol > 240:   score += 2; factors.append(f"High cholesterol ({chol})")
            elif chol > 200: score += 1; factors.append(f"Borderline cholesterol ({chol})")

        # HDL (protective — penalise if low)
        hdl = params.get("HDL")
        if hdl:
            if hdl < 35:   score += 2; factors.append(f"Very low HDL ({hdl})")
            elif hdl < 40: score += 1; factors.append(f"Low HDL ({hdl})")

        # LDL
        ldl = params.get("LDL")
        if ldl:
            if ldl > 160:   score += 2; factors.append(f"High LDL ({ldl})")
            elif ldl > 130: score += 1; factors.append(f"Borderline LDL ({ldl})")

        # Triglycerides
        tg = params.get("Triglycerides")
        if tg and tg > 200:
            score += 1; factors.append(f"High triglycerides ({tg})")

        score = min(score, max_score)
        level = "High" if score >= 6 else "Moderate" if score >= 3 else "Low"
        return {
            "score":          score,
            "max_score":      max_score,
            "level":          level,
            "interpretation": f"{level} cardiovascular risk (score {score}/{max_score})",
            "factors":        factors,
        }

    def _calculate_diabetes_risk(
        self,
        params: Dict,
        age: Optional[int],
        gender: Optional[str],
    ) -> Dict:
        score = 0
        max_score = 8
        factors = []

        glucose = params.get("Glucose")
        if glucose:
            if glucose > 126:   score += 4; factors.append(f"Diabetic range glucose ({glucose})")
            elif glucose > 100: score += 2; factors.append(f"Pre-diabetic glucose ({glucose})")
            elif glucose > 90:  score += 1; factors.append(f"High-normal glucose ({glucose})")

        hba1c = params.get("HbA1c")
        if hba1c:
            if hba1c >= 6.5:   score += 3; factors.append(f"HbA1c diabetic range ({hba1c}%)")
            elif hba1c >= 5.7: score += 2; factors.append(f"HbA1c pre-diabetic ({hba1c}%)")

        if age and age > 45:
            score += 1; factors.append("Age > 45")

        hdl = params.get("HDL")
        if hdl and hdl < 40:
            score += 1; factors.append(f"Low HDL ({hdl})")

        tg = params.get("Triglycerides")
        if tg and tg > 150:
            score += 1; factors.append(f"High triglycerides ({tg})")

        score = min(score, max_score)
        level = "High" if score >= 5 else "Moderate" if score >= 2 else "Low"
        return {
            "score":          score,
            "max_score":      max_score,
            "level":          level,
            "interpretation": f"{level} diabetes risk (score {score}/{max_score})",
            "factors":        factors,
        }

    def _calculate_liver_risk(
        self,
        params: Dict,
        age: Optional[int],
        gender: Optional[str],
    ) -> Dict:
        score = 0
        max_score = 8
        factors = []

        alt = params.get("ALT")
        if alt:
            if alt > 80:   score += 3; factors.append(f"Severely elevated ALT ({alt})")
            elif alt > 60: score += 2; factors.append(f"High ALT ({alt})")
            elif alt > 40: score += 1; factors.append(f"Borderline ALT ({alt})")

        ast = params.get("AST")
        if ast:
            if ast > 80:   score += 3; factors.append(f"Severely elevated AST ({ast})")
            elif ast > 60: score += 2; factors.append(f"High AST ({ast})")
            elif ast > 40: score += 1; factors.append(f"Borderline AST ({ast})")

        bili = params.get("Bilirubin")
        if bili:
            if bili > 2.0: score += 2; factors.append(f"High bilirubin ({bili})")
            elif bili > 1.2: score += 1; factors.append(f"Borderline bilirubin ({bili})")

        alp = params.get("ALP")
        if alp and alp > 147:
            score += 1; factors.append(f"High ALP ({alp})")

        score = min(score, max_score)
        level = "High" if score >= 5 else "Moderate" if score >= 2 else "Low"
        return {
            "score":          score,
            "max_score":      max_score,
            "level":          level,
            "interpretation": f"{level} liver risk (score {score}/{max_score})",
            "factors":        factors,
        }

    def _calculate_kidney_risk(
        self,
        params: Dict,
        age: Optional[int],
        gender: Optional[str],
    ) -> Dict:
        score = 0
        max_score = 8
        factors = []

        creat = params.get("Creatinine")
        if creat:
            if creat > 2.0:  score += 3; factors.append(f"Severely elevated creatinine ({creat})")
            elif creat > 1.3: score += 2; factors.append(f"High creatinine ({creat})")

        bun = params.get("BUN")
        if bun:
            if bun > 40:   score += 2; factors.append(f"Severely elevated BUN ({bun})")
            elif bun > 20: score += 1; factors.append(f"High BUN ({bun})")

        egfr = params.get("eGFR")
        if egfr:
            if egfr < 30:   score += 3; factors.append(f"Severely reduced eGFR ({egfr})")
            elif egfr < 60: score += 2; factors.append(f"Reduced eGFR ({egfr})")

        uric = params.get("Uric Acid")
        if uric and uric > 7.2:
            score += 1; factors.append(f"High uric acid ({uric})")

        score = min(score, max_score)
        level = "High" if score >= 5 else "Moderate" if score >= 2 else "Low"
        return {
            "score":          score,
            "max_score":      max_score,
            "level":          level,
            "interpretation": f"{level} kidney risk (score {score}/{max_score})",
            "factors":        factors,
        }

    # ══════════════════════════════════════════════════════════════════════════
    # Medical Ratio Calculations  (Milestone 2 Goal 1)
    # ══════════════════════════════════════════════════════════════════════════

    def calculate_ratios(self, params: Dict[str, Optional[float]]) -> Dict[str, Dict]:
        """
        Calculate clinically important ratios from available parameters.
        Only calculates a ratio when all required parameters are present.
        """
        ratios = {}

        # 1. Friedewald LDL estimate (if LDL not directly measured)
        c   = params.get("Cholesterol")
        hdl = params.get("HDL")
        tg  = params.get("Triglycerides")
        ldl = params.get("LDL")

        if c and hdl and tg and not ldl:
            calc_ldl = c - hdl - (tg / 5)
            ratios["Calculated LDL"] = {
                "value":          round(calc_ldl, 1),
                "unit":           "mg/dL",
                "interpretation": (
                    "High" if calc_ldl > 160 else
                    "Borderline" if calc_ldl > 130 else
                    "Optimal" if calc_ldl > 100 else "Very Optimal"
                ),
            }

        # 2. Total Cholesterol / HDL ratio  (Castelli Risk Index)
        if c and hdl:
            chol_hdl = c / hdl
            ratios["Cholesterol / HDL"] = {
                "value":          round(chol_hdl, 2),
                "unit":           "ratio",
                "interpretation": (
                    "High Risk (> 5)" if chol_hdl > 5 else
                    "Moderate Risk (3.5–5)" if chol_hdl > 3.5 else
                    "Low Risk (< 3.5)"
                ),
            }

        # 3. Triglycerides / HDL ratio  (insulin resistance proxy)
        if tg and hdl:
            tg_hdl = tg / hdl
            ratios["Triglycerides / HDL"] = {
                "value":          round(tg_hdl, 2),
                "unit":           "ratio",
                "interpretation": (
                    "High (> 3.0 — insulin resistance risk)" if tg_hdl > 3.0 else
                    "Borderline (2.0–3.0)" if tg_hdl > 2.0 else
                    "Normal (< 2.0)"
                ),
            }

        # 4. LDL / HDL ratio
        effective_ldl = ldl or (ratios.get("Calculated LDL", {}).get("value"))
        if effective_ldl and hdl:
            ldl_hdl = effective_ldl / hdl
            ratios["LDL / HDL"] = {
                "value":          round(ldl_hdl, 2),
                "unit":           "ratio",
                "interpretation": (
                    "High Risk (> 3.5)" if ldl_hdl > 3.5 else
                    "Moderate Risk (2.5–3.5)" if ldl_hdl > 2.5 else
                    "Low Risk (< 2.5)"
                ),
            }

        # 5. BUN / Creatinine ratio  (pre-renal vs renal cause)
        bun   = params.get("BUN")
        creat = params.get("Creatinine")
        if bun and creat and creat > 0:
            bun_cr = bun / creat
            ratios["BUN / Creatinine"] = {
                "value":          round(bun_cr, 1),
                "unit":           "ratio",
                "interpretation": (
                    "High (> 20 — pre-renal cause likely)" if bun_cr > 20 else
                    "Normal (10–20)" if bun_cr >= 10 else
                    "Low (< 10 — possible liver disease)"
                ),
            }

        # 6. AST / ALT ratio  (alcoholic liver disease indicator)
        ast = params.get("AST")
        alt = params.get("ALT")
        if ast and alt and alt > 0:
            ast_alt = ast / alt
            ratios["AST / ALT"] = {
                "value":          round(ast_alt, 2),
                "unit":           "ratio",
                "interpretation": (
                    "High (> 2.0 — possible alcoholic liver disease)" if ast_alt > 2.0 else
                    "Elevated (1.0–2.0 — monitor)" if ast_alt > 1.0 else
                    "Normal (< 1.0)"
                ),
            }

        return ratios