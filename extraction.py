# extraction.py


import re
import io
import json
import platform
from typing import Dict, Optional, Tuple

import pdfplumber
import pytesseract
from PIL import Image
import fitz  # PyMuPDF

# ── Tesseract path (Windows only) ──────────────────────────────────────────────
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ══════════════════════════════════════════════════════════════════════════════
# 1. TEXT EXTRACTION  (PDF → text, image → text, JSON → dict)
# ══════════════════════════════════════════════════════════════════════════════

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from an uploaded PDF file object.
    Tries pdfplumber first (native text), falls back to OCR.
    """
    pdf_bytes = pdf_file.read()
    pdf_file.seek(0)

    text = _extract_native_text(pdf_bytes)
    if not text.strip():
        text = ocr_pdf(pdf_bytes)

    return text


def _extract_native_text(pdf_bytes: bytes) -> str:
    """Use pdfplumber to pull selectable text from a PDF."""
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[pdfplumber] Error: {e}")
    return text


def ocr_pdf(pdf_bytes: bytes) -> str:
    """OCR every page of a scanned PDF using PyMuPDF + Tesseract."""
    text = ""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text += pytesseract.image_to_string(img) + "\n"
        doc.close()
    except Exception as e:
        print(f"[OCR] Error: {e}")
    return text


def extract_text_from_image(image_file) -> str:
    """OCR a PNG/JPG uploaded file."""
    try:
        img = Image.open(image_file)
        return pytesseract.image_to_string(img)
    except Exception as e:
        print(f"[Image OCR] Error: {e}")
        return ""


def extract_from_json(json_file) -> Dict[str, Optional[float]]:
    """
    Parse a JSON blood-report file.
    Accepts formats like: {"Hemoglobin": 14.2, "WBC": 8000} or
    [{"parameter": "Hemoglobin", "value": 14.2}, ...]
    """
    try:
        raw = json.load(json_file)
        if isinstance(raw, dict):
            return {k: _to_float(v) for k, v in raw.items()}
        if isinstance(raw, list):
            return {
                item.get("parameter", item.get("name", "")): _to_float(item.get("value"))
                for item in raw
                if isinstance(item, dict)
            }
    except Exception as e:
        print(f"[JSON] Error: {e}")
    return {}


# ══════════════════════════════════════════════════════════════════════════════
# 2. PARAMETER EXTRACTION  (text → {param: value})
# ══════════════════════════════════════════════════════════════════════════════

# Each entry: param_name → list of regex patterns
_PATTERNS: Dict[str, list] = {
    # CBC
    "Hemoglobin":    [r"Hemoglobin\s*\(Hb\)\s+([\d\.]+)",                               # "Hemoglobin (Hb) 12.5"  ← lab table format
                      r"H(?:a?em)oglobin\b[^:\n\d]*?([\d\.]+)\s*(?:Low|High|Normal|g/dL)", # "Hemoglobin ... 12.5 Low"
                      r"H(?:aem|em)oglobin\s*[:\-]?\s*([\d\.]+)",                         # "Haemoglobin: 12.5"
                      r"\bHb\b\s*[:\-]?\s*([\d\.]+)"],                                    # "Hb: 12.5"
    "RBC":           [r"RBC\s*[:\-]?\s*([\d\.]+)",
                      r"Red\s*Blood\s*Cells?\s*[:\-]?\s*([\d\.]+)"],
    "WBC":           [r"WBC\s*[:\-]?\s*([\d,]+)",
                      r"White\s*Blood\s*(?:Cell|Count)\s*[:\-]?\s*([\d,]+)",
                      r"Leukocytes?\s*[:\-]?\s*([\d,]+)"],
    "Platelets":     [r"Platelets?\s*[:\-]?\s*([\d,]+)",
                      r"\bPLT\s*[:\-]?\s*([\d,]+)"],
    "Hematocrit":    [r"Hematocrit\s*[:\-]?\s*([\d\.]+)",
                      r"\bHCT\s*[:\-]?\s*([\d\.]+)",
                      r"\bPCV\s*[:\-]?\s*([\d\.]+)"],
    "MCV":           [r"\bMCV\s*[:\-]?\s*([\d\.]+)"],
    "MCH":           [r"\bMCH\s*[:\-]?\s*([\d\.]+)"],
    "MCHC":          [r"\bMCHC\s*[:\-]?\s*([\d\.]+)"],
    "Neutrophils":   [r"Neutrophils?\s*[:\-]?\s*([\d\.]+)",
                      r"\bNeut\s*[:\-]?\s*([\d\.]+)"],
    "Lymphocytes":   [r"Lymphocytes?\s*[:\-]?\s*([\d\.]+)",
                      r"\bLymph\s*[:\-]?\s*([\d\.]+)"],
    "Monocytes":     [r"Monocytes?\s*[:\-]?\s*([\d\.]+)"],
    "Eosinophils":   [r"Eosinophils?\s*[:\-]?\s*([\d\.]+)"],
    "Basophils":     [r"Basophils?\s*[:\-]?\s*([\d\.]+)"],

    # Blood Sugar
    "Glucose":       [r"Average\s+Glucose\s+Value\s+For\s+([\d\.]+)\s*mg",              # "Average Glucose Value For 200.12 mg/dL" ← Max Lab format
                      r"(?:Fasting\s+)?Glucose\s*[:\-]?\s*([\d\.]+)",                   # "Glucose: 95"
                      r"Blood\s*Sugar\s*[:\-]?\s*([\d\.]+)",                            # "Blood Sugar: 95"
                      r"\bFBS\s*[:\-]?\s*([\d\.]+)",                                    # "FBS: 95"
                      r"\bRBS\s*[:\-]?\s*([\d\.]+)"],                                   # "RBS: 95"
    "HbA1c":         [r"Glycosylated\s+([\d\.]+)\s*%",                                  # "Glycosylated 8.6 %" ← Max Lab split-line format
                      r"Hb\s*A1c\s*\)?\s+([\d\.]+)",                                   # "Hb A1c) 8.6"
                      r"HbA1c\s*[:\-]?\s*([\d\.]+)",                                   # "HbA1c: 8.6"
                      r"Glycated\s*H(?:a?em)oglobin\s*[:\-]?\s*([\d\.]+)",             # "Glycated Haemoglobin: 8.6"
                      r"A1C\s*[:\-]?\s*([\d\.]+)",                                     # "A1C: 8.6"
                      r"GHb\s*[:\-]?\s*([\d\.]+)"],                                    # "GHb: 8.6"

    # Lipids
    "Cholesterol":   [r"Total\s*Cholesterol\s*[:\-]?\s*([\d\.]+)",
                      r"Cholesterol\s*[:\-]?\s*([\d\.]+)"],
    "HDL":           [r"HDL[\s\-]*(?:Cholesterol)?\s*[:\-]?\s*([\d\.]+)"],
    "LDL":           [r"LDL[\s\-]*(?:Cholesterol)?\s*[:\-]?\s*([\d\.]+)"],
    "Triglycerides": [r"Triglycerides?\s*[:\-]?\s*([\d\.]+)",
                      r"\bTG\s*[:\-]?\s*([\d\.]+)"],
    "VLDL":          [r"\bVLDL\s*[:\-]?\s*([\d\.]+)"],

    # Liver
    "ALT":           [r"\bALT\s*[:\-]?\s*([\d\.]+)",
                      r"Alanine\s*(?:Amino)?transferase\s*[:\-]?\s*([\d\.]+)",
                      r"SGPT\s*[:\-]?\s*([\d\.]+)"],
    "AST":           [r"\bAST\s*[:\-]?\s*([\d\.]+)",
                      r"Aspartate\s*(?:Amino)?transferase\s*[:\-]?\s*([\d\.]+)",
                      r"SGOT\s*[:\-]?\s*([\d\.]+)"],
    "ALP":           [r"\bALP\s*[:\-]?\s*([\d\.]+)",
                      r"Alkaline\s*Phosphatase\s*[:\-]?\s*([\d\.]+)"],
    "Bilirubin":     [r"Total\s*Bilirubin\s*[:\-]?\s*([\d\.]+)",
                      r"Bilirubin\s*[:\-]?\s*([\d\.]+)"],
    "DirectBilirubin":[r"Direct\s*Bilirubin\s*[:\-]?\s*([\d\.]+)"],
    "Albumin":       [r"\bAlbumin\s*[:\-]?\s*([\d\.]+)"],
    "TotalProtein":  [r"Total\s*Protein\s*[:\-]?\s*([\d\.]+)"],

    # Kidney
    "Creatinine":    [r"(?:Serum\s+)?Creatinine\s*[:\-]?\s*([\d\.]+)"],
    "BUN":           [r"\bBUN\s*[:\-]?\s*([\d\.]+)",
                      r"Blood\s*Urea\s*Nitrogen\s*[:\-]?\s*([\d\.]+)",
                      r"Urea\s*[:\-]?\s*([\d\.]+)"],
    "Uric Acid":     [r"Uric\s*Acid\s*[:\-]?\s*([\d\.]+)"],
    "eGFR":          [r"eGFR\s*[:\-]?\s*([\d\.]+)",
                      r"GFR\s*[:\-]?\s*([\d\.]+)"],

    # Thyroid
    "TSH":           [r"\bTSH\s*[:\-]?\s*([\d\.]+)"],
    "T3":            [r"\bT3\s*[:\-]?\s*([\d\.]+)",
                      r"Triiodothyronine\s*[:\-]?\s*([\d\.]+)"],
    "T4":            [r"\bT4\s*[:\-]?\s*([\d\.]+)",
                      r"Thyroxine\s*[:\-]?\s*([\d\.]+)"],

    # Electrolytes
    "Sodium":        [r"\bSodium\s*[:\-]?\s*([\d\.]+)",
                      r"\bNa\+?\s*[:\-]?\s*([\d\.]+)"],
    "Potassium":     [r"\bPotassium\s*[:\-]?\s*([\d\.]+)",
                      r"\bK\+?\s*[:\-]?\s*([\d\.]+)"],
    "Chloride":      [r"\bChloride\s*[:\-]?\s*([\d\.]+)",
                      r"\bCl\-?\s*[:\-]?\s*([\d\.]+)"],
    "Calcium":       [r"\bCalcium\s*[:\-]?\s*([\d\.]+)",
                      r"\bCa\+?\s*[:\-]?\s*([\d\.]+)"],
    "Magnesium":     [r"\bMagnesium\s*[:\-]?\s*([\d\.]+)",
                      r"\bMg\+?\s*[:\-]?\s*([\d\.]+)"],

    # Inflammation
    "CRP":           [r"\bCRP\s*[:\-]?\s*([\d\.]+)",
                      r"C[\s\-]*Reactive\s*Protein\s*[:\-]?\s*([\d\.]+)"],
    "ESR":           [r"\bESR\s*[:\-]?\s*([\d\.]+)",
                      r"Erythrocyte\s*Sedimentation\s*[:\-]?\s*([\d\.]+)"],

    # Iron
    "Iron":          [r"(?:Serum\s+)?Iron\s*[:\-]?\s*([\d\.]+)"],
    "Ferritin":      [r"\bFerritin\s*[:\-]?\s*([\d\.]+)"],
    "TIBC":          [r"\bTIBC\s*[:\-]?\s*([\d\.]+)",
                      r"Total\s*Iron\s*Binding\s*Capacity\s*[:\-]?\s*([\d\.]+)"],

    # Vitamins
    "VitaminD":      [r"Vitamin\s*D\s*[:\-]?\s*([\d\.]+)",
                      r"25[\s\-]*OH[\s\-]*D\s*[:\-]?\s*([\d\.]+)"],
    "VitaminB12":    [r"Vitamin\s*B[\s\-]*12\s*[:\-]?\s*([\d\.]+)",
                      r"Cobalamin\s*[:\-]?\s*([\d\.]+)"],
}


def extract_parameters(text: str) -> Dict[str, Optional[float]]:
    """
    Extract blood parameters from raw text.
    Searches both the original text AND a newline-collapsed version to handle
    multi-line lab report formats (e.g. Max Lab, Drlogy, SRL) where parameter
    names or values span two lines.

    Returns dict {param_name: float_value_or_None}.
    """
    if not text or not text.strip():
        return {}

    # Collapse newlines → single space for multi-line param matching
    joined = re.sub(r'\n+', ' ', text)

    extracted: Dict[str, Optional[float]] = {}
    for param, pattern_list in _PATTERNS.items():
        value = None
        for pattern in pattern_list:
            # Try original text first, then newline-joined version
            for search_text in (text, joined):
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match and match.group(1):
                    value = _to_float(match.group(1).replace(",", ""))
                    if value is not None:
                        break
            if value is not None:
                break
        extracted[param] = value

    return extracted


# ══════════════════════════════════════════════════════════════════════════════
# 3. VALIDATION & STANDARDIZATION  (Milestone 1, Module 3)
# ══════════════════════════════════════════════════════════════════════════════

# Plausibility bounds — anything outside these is almost certainly an OCR error
_PLAUSIBILITY: Dict[str, Tuple[float, float]] = {
    "Hemoglobin":    (1.0,   25.0),
    "RBC":           (0.5,   10.0),
    "WBC":           (500,   100000),
    "Platelets":     (5000,  2000000),
    "Hematocrit":    (5.0,   70.0),
    "MCV":           (40.0,  150.0),
    "MCH":           (10.0,  60.0),
    "MCHC":          (20.0,  45.0),
    "Glucose":       (10.0,  800.0),
    "HbA1c":         (2.0,   20.0),
    "Cholesterol":   (50.0,  600.0),
    "HDL":           (5.0,   200.0),
    "LDL":           (10.0,  500.0),
    "Triglycerides": (10.0,  2000.0),
    "ALT":           (1.0,   5000.0),
    "AST":           (1.0,   5000.0),
    "ALP":           (1.0,   2000.0),
    "Bilirubin":     (0.01,  50.0),
    "Creatinine":    (0.1,   30.0),
    "BUN":           (1.0,   300.0),
    "TSH":           (0.001, 100.0),
    "Sodium":        (100.0, 180.0),
    "Potassium":     (1.0,   10.0),
    "Calcium":       (4.0,   20.0),
    "CRP":           (0.0,   500.0),
    "Ferritin":      (1.0,   10000.0),
    "VitaminD":      (1.0,   300.0),
    "VitaminB12":    (10.0,  5000.0),
}

# Unit conversion factors → target unit
# Only triggered when the extracted value is in the mmol range AND the unit
# appears on the SAME LINE as the value (not just anywhere in the document).
# Format: (unit_hint, multiply_by, mmol_range_max)
# mmol_range_max: if value is ABOVE this, it's already in mg/dL — skip conversion
_UNIT_CONVERSIONS: Dict[str, list] = {
    # Hemoglobin: mmol/L range is ~6–15, g/dL range is same numbers — skip auto-convert
    # (too ambiguous; handled by plausibility check instead)
    # Glucose: mmol/L values are typically 2–30; mg/dL values are 50–800
    "Glucose":       [("mmol", 18.016, 30.0)],
    # Cholesterol: mmol/L values are typically 2–15; mg/dL values are 50–600
    "Cholesterol":   [("mmol", 38.67,  20.0)],
    "HDL":           [("mmol", 38.67,  10.0)],
    "LDL":           [("mmol", 38.67,  15.0)],
    "Triglycerides": [("mmol", 88.57,  15.0)],
    # Creatinine: µmol/L values are typically 40–800; mg/dL values are 0.3–15
    "Creatinine":    [("µmol", 1/88.42, 15.0), ("umol", 1/88.42, 15.0)],
}


def validate_and_standardize(
    extracted: Dict[str, Optional[float]],
    raw_text: str = ""
) -> Tuple[Dict[str, Optional[float]], Dict[str, str]]:
    """
    Clean and validate extracted parameters.

    Returns:
        cleaned  – {param: value}  (None if failed validation)
        warnings – {param: message}
    """
    cleaned: Dict[str, Optional[float]] = {}
    warnings: Dict[str, str] = {}

    for param, value in extracted.items():
        if value is None:
            cleaned[param] = None
            continue

        # 1. Apply unit conversion ONLY when:
        #    a) The value is in the small mmol/L range (not already mg/dL)
        #    b) The unit keyword appears on the same line as the value in the raw text
        if param in _UNIT_CONVERSIONS and raw_text:
            for conv in _UNIT_CONVERSIONS[param]:
                unit_hint, factor, mmol_max = conv
                # Guard: skip if value is already in mg/dL range
                if value > mmol_max:
                    continue
                # Only convert if unit appears on the SAME LINE as the value
                val_str = str(value)
                for line in raw_text.split('\n'):
                    if val_str in line and re.search(unit_hint, line, re.IGNORECASE):
                        value = round(value * factor, 2)
                        warnings[param] = f"Unit converted ({unit_hint} → standard mg/dL)"
                        break

        # 2. Plausibility check
        bounds = _PLAUSIBILITY.get(param)
        if bounds:
            lo, hi = bounds
            if not (lo <= value <= hi):
                warnings[param] = (
                    f"Value {value} outside plausible range [{lo}, {hi}] — "
                    f"possible OCR error, discarded"
                )
                cleaned[param] = None
                continue

        # 3. Round to sensible precision
        cleaned[param] = round(value, 2)

    return cleaned, warnings


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _to_float(value) -> Optional[float]:
    """Safely convert a value to float."""
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None