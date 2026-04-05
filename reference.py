REFERENCE_RANGES = {
    # ── Complete Blood Count (CBC) ───────────────────────────────────────────
    "Hemoglobin":     {"min": 13.5,    "max": 17.5,       "unit": "g/dL"},
    "RBC":            {"min": 4.5,     "max": 5.9,        "unit": "million/µL"},
    "WBC":            {"min": 4500,    "max": 11000,       "unit": "/µL"},
    "Platelets":      {"min": 150000,  "max": 450000,      "unit": "/µL"},
    "Hematocrit":     {"min": 41.0,    "max": 53.0,        "unit": "%"},
    "MCV":            {"min": 80.0,    "max": 100.0,       "unit": "fL"},
    "MCH":            {"min": 27.0,    "max": 33.0,        "unit": "pg"},
    "MCHC":           {"min": 32.0,    "max": 36.0,        "unit": "g/dL"},
    "Neutrophils":    {"min": 40.0,    "max": 70.0,        "unit": "%"},
    "Lymphocytes":    {"min": 20.0,    "max": 40.0,        "unit": "%"},
    "Monocytes":      {"min": 2.0,     "max": 10.0,        "unit": "%"},
    "Eosinophils":    {"min": 1.0,     "max": 6.0,         "unit": "%"},
    "Basophils":      {"min": 0.0,     "max": 1.0,         "unit": "%"},

    # ── Blood Sugar ──────────────────────────────────────────────────────────
    "Glucose":        {"min": 70.0,    "max": 100.0,       "unit": "mg/dL"},
    "HbA1c":          {"min": 4.0,     "max": 5.7,         "unit": "%"},

    # ── Lipid Panel ──────────────────────────────────────────────────────────
    "Cholesterol":    {"min": 125.0,   "max": 200.0,       "unit": "mg/dL"},
    "HDL":            {"min": 40.0,    "max": 100.0,       "unit": "mg/dL"},
    "LDL":            {"min": 0.0,     "max": 130.0,       "unit": "mg/dL"},
    "Triglycerides":  {"min": 0.0,     "max": 150.0,       "unit": "mg/dL"},
    "VLDL":           {"min": 2.0,     "max": 30.0,        "unit": "mg/dL"},

    # ── Liver Function Tests (LFT) ───────────────────────────────────────────
    "ALT":            {"min": 7.0,     "max": 40.0,        "unit": "U/L"},
    "AST":            {"min": 10.0,    "max": 40.0,        "unit": "U/L"},
    "ALP":            {"min": 44.0,    "max": 147.0,       "unit": "U/L"},
    "Bilirubin":      {"min": 0.1,     "max": 1.2,         "unit": "mg/dL"},
    "DirectBilirubin":{"min": 0.0,     "max": 0.3,         "unit": "mg/dL"},
    "TotalProtein":   {"min": 6.0,     "max": 8.3,         "unit": "g/dL"},
    "Albumin":        {"min": 3.5,     "max": 5.0,         "unit": "g/dL"},
    "Globulin":       {"min": 2.0,     "max": 3.5,         "unit": "g/dL"},

    # ── Kidney Function Tests (KFT) ──────────────────────────────────────────
    "Creatinine":     {"min": 0.7,     "max": 1.3,         "unit": "mg/dL"},
    "BUN":            {"min": 7.0,     "max": 20.0,        "unit": "mg/dL"},
    "Uric Acid":      {"min": 3.5,     "max": 7.2,         "unit": "mg/dL"},
    "eGFR":           {"min": 60.0,    "max": 120.0,       "unit": "mL/min/1.73m²"},

    # ── Thyroid ──────────────────────────────────────────────────────────────
    "TSH":            {"min": 0.4,     "max": 4.0,         "unit": "mIU/L"},
    "T3":             {"min": 80.0,    "max": 200.0,       "unit": "ng/dL"},
    "T4":             {"min": 5.0,     "max": 12.0,        "unit": "µg/dL"},

    # ── Electrolytes ─────────────────────────────────────────────────────────
    "Sodium":         {"min": 136.0,   "max": 145.0,       "unit": "mEq/L"},
    "Potassium":      {"min": 3.5,     "max": 5.0,         "unit": "mEq/L"},
    "Chloride":       {"min": 98.0,    "max": 107.0,       "unit": "mEq/L"},
    "Calcium":        {"min": 8.5,     "max": 10.5,        "unit": "mg/dL"},
    "Magnesium":      {"min": 1.7,     "max": 2.2,         "unit": "mg/dL"},

    # ── Inflammation Markers ─────────────────────────────────────────────────
    "CRP":            {"min": 0.0,     "max": 10.0,        "unit": "mg/L"},
    "ESR":            {"min": 0.0,     "max": 20.0,        "unit": "mm/hr"},

    # ── Iron Studies ─────────────────────────────────────────────────────────
    "Iron":           {"min": 60.0,    "max": 170.0,       "unit": "µg/dL"},
    "Ferritin":       {"min": 12.0,    "max": 300.0,       "unit": "ng/mL"},
    "TIBC":           {"min": 240.0,   "max": 450.0,       "unit": "µg/dL"},

    # ── Vitamins ─────────────────────────────────────────────────────────────
    "VitaminD":       {"min": 30.0,    "max": 100.0,       "unit": "ng/mL"},
    "VitaminB12":     {"min": 200.0,   "max": 900.0,       "unit": "pg/mL"},
}


# ══════════════════════════════════════════════════════════════════════════════
# Model 1 — Classification
# ══════════════════════════════════════════════════════════════════════════════

def classify_value(value, param_name: str) -> str:
    """
    Classify a single blood parameter as HIGH, LOW, or NORMAL.

    Args:
        value  : numeric value (int or float)
        param_name : key matching REFERENCE_RANGES

    Returns:
        'HIGH' | 'LOW' | 'NORMAL' | 'UNKNOWN'
    """
    if value is None:
        return "UNKNOWN"

    try:
        value = float(value)
    except (TypeError, ValueError):
        return "UNKNOWN"

    ranges = REFERENCE_RANGES.get(param_name)
    if not ranges:
        return "UNKNOWN"

    if value < ranges["min"]:
        return "LOW"
    if value > ranges["max"]:
        return "HIGH"
    return "NORMAL"


def classify_all(parameters: dict) -> dict:
    """
    Classify every parameter in a dict.

    Args:
        parameters : {param_name: value}

    Returns:
        {param_name: 'HIGH' | 'LOW' | 'NORMAL' | 'UNKNOWN'}
    """
    return {param: classify_value(value, param) for param, value in parameters.items()}


# ══════════════════════════════════════════════════════════════════════════════
# UI Helpers
# ══════════════════════════════════════════════════════════════════════════════

def get_display_range(param_name: str) -> str:
    """
    Human-readable reference range string for the UI.
    e.g. '13.5 – 17.5 g/dL'
    """
    ranges = REFERENCE_RANGES.get(param_name)
    if not ranges:
        return "Unknown"

    unit    = ranges.get("unit", "")
    ref_min = ranges["min"]
    ref_max = ranges["max"]

    if ref_max >= 9999:
        return f"> {ref_min} {unit}"
    if ref_min == 0:
        return f"< {ref_max} {unit}"
    return f"{ref_min} – {ref_max} {unit}"


def get_unit(param_name: str) -> str:
    """Return the unit string for a parameter, or '' if unknown."""
    return REFERENCE_RANGES.get(param_name, {}).get("unit", "")


def severity_color(status: str) -> str:
    """
    Map a classification status to a hex colour for the UI.

    Returns:
        hex string e.g. '#00b894'
    """
    return {
        "HIGH":    "#d63031",
        "LOW":     "#f39c12",
        "NORMAL":  "#00b894",
        "UNKNOWN": "#b2bec3",
    }.get(status, "#b2bec3")