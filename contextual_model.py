# contextual_model.py

# Adjusts interpretation based on age, gender, family history, and lifestyle

from typing import Dict, List, Optional, Tuple


class ContextualAnalyzer:
    """
    Model 3: Adjusts reference ranges and risk interpretation based on
    patient context (age, gender, family history, lifestyle).
    """

    def __init__(self):
        # ── Age/Gender Adjusted Reference Ranges ─────────────────────────────
        # Keys: child (<18), adult_male, adult_female, elderly (60–75), very_elderly (75+)
        self.age_adjusted_ranges: Dict[str, Dict[str, Dict]] = {

            "Hemoglobin": {
                "child":        {"min": 11.0, "max": 14.5},
                "adult_male":   {"min": 13.5, "max": 17.5},
                "adult_female": {"min": 12.0, "max": 16.0},
                "elderly":      {"min": 11.5, "max": 15.5},
                "very_elderly": {"min": 11.0, "max": 15.0},
            },

            "Creatinine": {
                "child":        {"min": 0.3, "max": 0.7},
                "adult_male":   {"min": 0.7, "max": 1.3},
                "adult_female": {"min": 0.6, "max": 1.1},
                "elderly":      {"min": 0.6, "max": 1.2},
                "very_elderly": {"min": 0.5, "max": 1.1},
            },

            "Glucose": {
                "child":        {"min": 60.0,  "max": 100.0},
                "adult_male":   {"min": 70.0,  "max": 100.0},
                "adult_female": {"min": 70.0,  "max": 100.0},
                "elderly":      {"min": 80.0,  "max": 110.0},   # slightly wider in elderly
                "very_elderly": {"min": 80.0,  "max": 115.0},
            },

            "TSH": {
                "child":        {"min": 0.7,  "max": 5.7},
                "adult_male":   {"min": 0.4,  "max": 4.0},
                "adult_female": {"min": 0.4,  "max": 4.0},
                "elderly":      {"min": 0.4,  "max": 6.0},      # TSH naturally rises with age
                "very_elderly": {"min": 0.4,  "max": 7.0},
            },

            "HDL": {
                "child":        {"min": 40.0, "max": 100.0},
                "adult_male":   {"min": 40.0, "max": 100.0},
                "adult_female": {"min": 50.0, "max": 100.0},    # Women need higher HDL
                "elderly":      {"min": 40.0, "max": 100.0},
                "very_elderly": {"min": 40.0, "max": 100.0},
            },

            "Cholesterol": {
                "child":        {"min": 100.0, "max": 170.0},
                "adult_male":   {"min": 125.0, "max": 200.0},
                "adult_female": {"min": 125.0, "max": 200.0},
                "elderly":      {"min": 140.0, "max": 220.0},   # Slightly higher acceptable
                "very_elderly": {"min": 140.0, "max": 240.0},
            },

            "WBC": {
                "child":        {"min": 5000,  "max": 15000},
                "adult_male":   {"min": 4500,  "max": 11000},
                "adult_female": {"min": 4500,  "max": 11000},
                "elderly":      {"min": 3500,  "max": 10500},
                "very_elderly": {"min": 3000,  "max": 10000},
            },

            "Platelets": {
                "child":        {"min": 150000, "max": 500000},
                "adult_male":   {"min": 150000, "max": 450000},
                "adult_female": {"min": 150000, "max": 450000},
                "elderly":      {"min": 100000, "max": 400000},
                "very_elderly": {"min": 100000, "max": 400000},
            },

            "Hematocrit": {
                "child":        {"min": 33.0, "max": 44.0},
                "adult_male":   {"min": 41.0, "max": 53.0},
                "adult_female": {"min": 36.0, "max": 46.0},
                "elderly":      {"min": 35.0, "max": 50.0},
                "very_elderly": {"min": 33.0, "max": 48.0},
            },

            "Ferritin": {
                "child":        {"min": 7.0,  "max": 140.0},
                "adult_male":   {"min": 24.0, "max": 336.0},
                "adult_female": {"min": 12.0, "max": 150.0},    # Lower in premenopausal
                "elderly":      {"min": 20.0, "max": 300.0},
                "very_elderly": {"min": 20.0, "max": 300.0},
            },

            "ALT": {
                "child":        {"min": 7.0,  "max": 30.0},
                "adult_male":   {"min": 7.0,  "max": 55.0},     # Higher upper limit for men
                "adult_female": {"min": 7.0,  "max": 40.0},
                "elderly":      {"min": 7.0,  "max": 45.0},
                "very_elderly": {"min": 7.0,  "max": 40.0},
            },
        }

        # ── Family History Risk Mapping ───────────────────────────────────────
        # Maps family history condition → (parameter to check, threshold, message)
        self.family_risk_map = {
            "diabetes": [
                ("Glucose",       95,  "high", "Family history of diabetes + borderline glucose ({val}) → monitor fasting glucose regularly"),
                ("HbA1c",         5.5, "high", "Family history of diabetes + elevated HbA1c ({val}%) → consider diabetes screening"),
                ("Triglycerides", 130, "high", "Family history of diabetes + high triglycerides → increased metabolic risk"),
            ],
            "heart disease": [
                ("Cholesterol",   190, "high", "Family history of heart disease + elevated cholesterol ({val}) → consider statin therapy discussion"),
                ("HDL",           45,  "low",  "Family history of heart disease + low HDL ({val}) → increase aerobic exercise"),
                ("LDL",           120, "high", "Family history of heart disease + high LDL ({val}) → dietary modification advised"),
            ],
            "high blood pressure": [
                ("Sodium",        142, "high", "Family history of hypertension + high-normal sodium → reduce salt intake"),
                ("Cholesterol",   200, "high", "Family history of hypertension + high cholesterol → compounded cardiovascular risk"),
            ],
            "kidney disease": [
                ("Creatinine", 1.0,  "high", "Family history of kidney disease + elevated creatinine ({val}) → monitor kidney function"),
                ("BUN",        18,   "high", "Family history of kidney disease + elevated BUN ({val}) → hydration and follow-up advised"),
                ("eGFR",       70,   "low",  "Family history of kidney disease + reduced eGFR ({val}) → nephrology review recommended"),
            ],
            "liver disease": [
                ("ALT",       35, "high", "Family history of liver disease + elevated ALT ({val}) → avoid hepatotoxic substances"),
                ("AST",       35, "high", "Family history of liver disease + elevated AST ({val}) → liver function monitoring advised"),
                ("Bilirubin", 1.0, "high", "Family history of liver disease + elevated bilirubin ({val}) → imaging may be warranted"),
            ],
        }

    # ══════════════════════════════════════════════════════════════════════════
    # Age Category
    # ══════════════════════════════════════════════════════════════════════════

    def get_age_category(self, age: int) -> str:
        """Return age category key used in adjusted ranges."""
        if age < 18:   return "child"
        if age < 60:   return "adult"
        if age < 75:   return "elderly"
        return "very_elderly"

    def _get_range_key(self, age_category: str, gender: Optional[str]) -> str:
        """Build the lookup key for age_adjusted_ranges."""
        if age_category == "adult" and gender:
            g = gender.strip().lower()
            if g in ("male", "female"):
                return f"adult_{g}"
        return age_category

    # ══════════════════════════════════════════════════════════════════════════
    # Reference Range Adjustment
    # ══════════════════════════════════════════════════════════════════════════

    def adjust_reference_range(
        self,
        param: str,
        value: float,
        age: Optional[int],
        gender: Optional[str],
    ) -> Dict:
        """
        Return an age/gender-adjusted classification for a single parameter.

        Returns {} if no adjustment data exists for the param.
        Returns dict with: adjusted_range, status, note
        """
        if age is None:
            return {}

        age_category = self.get_age_category(age)
        range_key    = self._get_range_key(age_category, gender)

        param_ranges = self.age_adjusted_ranges.get(param, {})
        adj_range    = param_ranges.get(range_key) or param_ranges.get(age_category)

        if not adj_range:
            return {}

        if value < adj_range["min"]:
            status = "LOW"
        elif value > adj_range["max"]:
            status = "HIGH"
        else:
            status = "NORMAL"

        gender_label = gender if gender else "unspecified gender"
        return {
            "adjusted_range": adj_range,
            "status":         status,
            "note":           f"Adjusted for {age_category.replace('_', ' ')} / {gender_label}",
        }

    def adjust_all(
        self,
        parameters: Dict[str, Optional[float]],
        age: Optional[int],
        gender: Optional[str],
    ) -> Dict[str, Dict]:
        """
        Run adjust_reference_range on every parameter in the dict.
        Returns {param: adjustment_dict}  — only params with adjustments included.
        """
        adjustments = {}
        for param, value in parameters.items():
            if value is not None:
                adj = self.adjust_reference_range(param, value, age, gender)
                if adj:
                    adjustments[param] = adj
        return adjustments

    # ══════════════════════════════════════════════════════════════════════════
    # Family History Risk
    # ══════════════════════════════════════════════════════════════════════════

    def assess_family_history_risk(
        self,
        family_history: List[str],
        parameters: Dict[str, Optional[float]],
    ) -> List[Dict]:
        """
        Return list of risk messages based on family history + actual parameter values.

        Args:
            family_history : list of condition strings from the UI multiselect
            parameters     : extracted blood parameter dict

        Returns:
            list of {condition, parameter, message, severity}
        """
        if not family_history or not parameters:
            return []

        risks = []
        fh_lower = [f.lower() for f in family_history]

        for condition_key, rules in self.family_risk_map.items():
            # Match flexibly: 'heart disease' matches 'Heart Disease', 'Cardiac', etc.
            matched = any(
                condition_key in fh or fh in condition_key
                for fh in fh_lower
            )
            if not matched:
                continue

            for (param, threshold, direction, message_template) in rules:
                val = parameters.get(param)
                if val is None:
                    continue

                triggered = (
                    (direction == "high" and val >= threshold) or
                    (direction == "low"  and val <= threshold)
                )

                if triggered:
                    message = message_template.replace("{val}", str(val))
                    severity = (
                        "High"     if abs(val - threshold) / max(threshold, 1) > 0.2
                        else "Moderate"
                    )
                    risks.append({
                        "condition":  condition_key.title(),
                        "parameter":  param,
                        "message":    message,
                        "severity":   severity,
                    })

        return risks

    # ══════════════════════════════════════════════════════════════════════════
    # Lifestyle Recommendations
    # ══════════════════════════════════════════════════════════════════════════

    def generate_lifestyle_recommendations(
        self,
        parameters: Dict[str, Optional[float]],
        age: Optional[int] = None,
        gender: Optional[str] = None,
        family_history: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Generate personalised, actionable lifestyle recommendations
        based on parameter values, age, gender, and family history.

        Returns list of {category, recommendation, priority}
        """
        recs = []
        fh   = [f.lower() for f in (family_history or [])]

        # ── Diet ──────────────────────────────────────────────────────────────
        chol = parameters.get("Cholesterol")
        if chol and chol > 200:
            recs.append({
                "category":       "Diet",
                "recommendation": "Reduce saturated fats (red meat, butter, full-fat dairy). Increase soluble fibre (oats, beans, lentils) to lower LDL.",
                "priority":       "High" if chol > 240 else "Moderate",
            })

        glucose = parameters.get("Glucose")
        if glucose and glucose > 100:
            recs.append({
                "category":       "Diet",
                "recommendation": "Reduce refined carbohydrates and sugars. Choose low-glycaemic foods (whole grains, vegetables). Avoid sugary drinks.",
                "priority":       "High" if glucose > 126 else "Moderate",
            })

        hdl = parameters.get("HDL")
        if hdl and hdl < 40:
            recs.append({
                "category":       "Diet",
                "recommendation": "Increase healthy fats: olive oil, avocado, nuts, and fatty fish (salmon, mackerel) to raise HDL cholesterol.",
                "priority":       "Moderate",
            })

        tg = parameters.get("Triglycerides")
        if tg and tg > 150:
            recs.append({
                "category":       "Diet",
                "recommendation": "Limit alcohol and simple sugars (sweets, white bread, fruit juice) which directly raise triglycerides.",
                "priority":       "High" if tg > 500 else "Moderate",
            })

        hb = parameters.get("Hemoglobin")
        if hb and hb < 12.0:
            recs.append({
                "category":       "Diet",
                "recommendation": "Increase iron-rich foods: red meat, spinach, legumes, fortified cereals. Take with vitamin C to improve absorption.",
                "priority":       "High",
            })

        # ── Exercise ──────────────────────────────────────────────────────────
        if age:
            if age > 65:
                recs.append({
                    "category":       "Exercise",
                    "recommendation": "Aim for 30 min of low-impact activity daily (walking, swimming, chair yoga). Include balance exercises to prevent falls.",
                    "priority":       "Moderate",
                })
            elif age > 40:
                recs.append({
                    "category":       "Exercise",
                    "recommendation": "Aim for 150 min of moderate aerobic exercise weekly (brisk walking, cycling). Add 2× strength training sessions.",
                    "priority":       "Moderate",
                })
            else:
                recs.append({
                    "category":       "Exercise",
                    "recommendation": "Aim for 150–300 min of moderate exercise or 75 min vigorous exercise weekly for optimal cardiovascular health.",
                    "priority":       "Low",
                })

        # ── Monitoring ────────────────────────────────────────────────────────
        creat = parameters.get("Creatinine")
        if creat and creat > 1.3:
            recs.append({
                "category":       "Monitoring",
                "recommendation": "Stay well hydrated (2–3 L water/day). Avoid NSAIDs (ibuprofen). Repeat kidney function test in 3 months.",
                "priority":       "High",
            })

        tsh = parameters.get("TSH")
        if tsh and (tsh > 4.0 or tsh < 0.4):
            recs.append({
                "category":       "Monitoring",
                "recommendation": "Abnormal TSH detected. Consult an endocrinologist. Repeat thyroid panel (TSH, T3, T4) as advised.",
                "priority":       "High",
            })

        alt = parameters.get("ALT")
        ast = parameters.get("AST")
        if (alt and alt > 60) or (ast and ast > 60):
            recs.append({
                "category":       "Monitoring",
                "recommendation": "Elevated liver enzymes. Avoid alcohol completely. Repeat LFTs in 6–8 weeks. Consider ultrasound abdomen.",
                "priority":       "High",
            })

        # ── Family History ────────────────────────────────────────────────────
        if "diabetes" in fh and glucose and glucose > 90:
            recs.append({
                "category":       "Screening",
                "recommendation": "Family history of diabetes: schedule annual HbA1c and fasting glucose tests even if current values are borderline.",
                "priority":       "Moderate",
            })

        if "heart disease" in fh:
            recs.append({
                "category":       "Screening",
                "recommendation": "Family history of heart disease: consider cardiac stress test and annual lipid panel after age 40.",
                "priority":       "Moderate",
            })

        # ── Vitamins ─────────────────────────────────────────────────────────
        vitd = parameters.get("VitaminD")
        if vitd and vitd < 30:
            recs.append({
                "category":       "Supplements",
                "recommendation": "Vitamin D deficient. Consider supplement (1000–2000 IU/day). Increase safe sun exposure (15–20 min/day).",
                "priority":       "Moderate",
            })

        b12 = parameters.get("VitaminB12")
        if b12 and b12 < 200:
            recs.append({
                "category":       "Supplements",
                "recommendation": "Low B12. Consider methylcobalamin supplement or B12-rich foods (eggs, meat, dairy). Vegetarians are at higher risk.",
                "priority":       "Moderate",
            })

        # Sort: High priority first
        order = {"High": 0, "Moderate": 1, "Low": 2}
        recs.sort(key=lambda r: order.get(r["priority"], 9))
        return recs