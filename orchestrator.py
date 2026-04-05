

import traceback
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class OrchestratorResult:
    """Structured result object returned by the orchestrator."""

    def __init__(self):
        self.success          = False
        self.stage            = "init"
        self.error            = None
        self.warnings         = {}

        # Stage outputs
        self.raw_text         = ""
        self.parameters       = {}
        self.found            = {}
        self.classifications  = {}
        self.patterns         = []
        self.risk_scores      = {}
        self.ratios           = {}
        self.adjustments      = {}
        self.fh_risks         = []
        self.lifestyle_recs   = []
        self.synthesis        = {}
        self.recommendations  = []

        # Meta
        self.file_name        = ""
        self.file_type        = ""
        self.processed_at     = datetime.now().strftime("%d %b %Y, %I:%M %p")
        self.pipeline_log     = []

    def log(self, stage, msg, ok=True):
        icon = "✅" if ok else "⚠️"
        self.pipeline_log.append(f"{icon} [{stage}] {msg}")
        self.stage = stage


class BloodReportOrchestrator:
    """
    Milestone 4 — Multi-Model Orchestrator.

    Runs the complete end-to-end pipeline:
      Stage 1 → Input parsing  (extraction.py)
      Stage 2 → Validation     (extraction.py)
      Stage 3 → Model 1        (reference.py)
      Stage 4 → Model 2        (pattern_recognition.py)
      Stage 5 → Model 3        (contextual_model.py)
      Stage 6 → Synthesis      (synthesis_engine.py)
      Stage 7 → Recommendations(synthesis_engine.py)

    Each stage is wrapped in try/except so one failure never
    crashes the entire pipeline — downstream stages get whatever
    data is available.
    """

    def __init__(self,
                 extractor,
                 reference,
                 pattern_recognizer,
                 contextual_analyzer,
                 synthesis_engine):
        self.ext  = extractor
        self.ref  = reference
        self.pr   = pattern_recognizer
        self.ca   = contextual_analyzer
        self.se   = synthesis_engine

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN ENTRY POINT
    # ══════════════════════════════════════════════════════════════════════════

    def run(self,
            uploaded_file=None,
            sample_data:   Optional[Dict]  = None,
            raw_text:      str             = "",
            age:           Optional[int]   = None,
            gender:        Optional[str]   = None,
            family_history: Optional[List] = None) -> OrchestratorResult:
        """
        Run the full pipeline. Pass either:
          - uploaded_file  (Streamlit UploadedFile)
          - sample_data    (dict of {param: value})
          - raw_text       (already extracted text string)
        """
        r = OrchestratorResult()
        r.file_name = getattr(uploaded_file, "name", "sample_data")
        family_history = family_history or []

        # ── Stage 1: Input Parsing ────────────────────────────────────────────
        try:
            r.log("Stage 1", "Input parsing")
            if sample_data:
                r.found      = {k: v for k, v in sample_data.items() if v is not None}
                r.parameters = sample_data
                r.raw_text   = ""
                r.file_type  = "sample"
                r.log("Stage 1", f"Sample data loaded — {len(r.found)} parameters")

            elif raw_text:
                r.raw_text  = raw_text
                r.file_type = "text"
                r.log("Stage 1", "Raw text provided directly")

            elif uploaded_file is not None:
                name = uploaded_file.name.lower()
                r.file_type = name.rsplit(".", 1)[-1]

                if name.endswith(".json"):
                    r.parameters = self.ext.extract_from_json(uploaded_file)
                    r.found      = {k: v for k, v in r.parameters.items() if v is not None}
                    r.log("Stage 1", f"JSON parsed — {len(r.found)} parameters")

                elif name.endswith(".txt"):
                    r.raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
                    r.log("Stage 1", f"Text file read — {len(r.raw_text)} chars")

                elif name.endswith(".pdf"):
                    r.raw_text = self.ext.extract_text_from_pdf(uploaded_file)
                    r.log("Stage 1", f"PDF extracted — {len(r.raw_text)} chars")

                elif name.endswith((".png", ".jpg", ".jpeg")):
                    r.raw_text = self.ext.extract_text_from_image(uploaded_file)
                    r.log("Stage 1", f"Image OCR — {len(r.raw_text)} chars")

                else:
                    raise ValueError(f"Unsupported file type: {name}")
            else:
                raise ValueError("No input provided")

        except Exception as e:
            r.error = f"Stage 1 failed: {str(e)}"
            r.log("Stage 1", f"FAILED — {e}", ok=False)
            return r

        # ── Stage 2: Parameter Extraction + Validation ────────────────────────
        try:
            r.log("Stage 2", "Parameter extraction & validation")
            if not r.found and r.raw_text:
                raw_params = self.ext.extract_parameters(r.raw_text)
                r.parameters, r.warnings = self.ext.validate_and_standardize(
                    raw_params, r.raw_text
                )
                r.found = {k: v for k, v in r.parameters.items() if v is not None}

            if not r.found:
                r.error = "No blood parameters could be extracted from the provided input."
                r.log("Stage 2", "No parameters found", ok=False)
                return r

            r.log("Stage 2", f"{len(r.found)} valid parameters extracted")

        except Exception as e:
            r.error = f"Stage 2 failed: {str(e)}"
            r.log("Stage 2", f"FAILED — {e}", ok=False)
            return r

        # ── Stage 3: Model 1 — Parameter Classification ───────────────────────
        try:
            r.log("Stage 3", "Model 1 — Parameter classification")
            r.classifications = self.ref.classify_all(r.found)
            n_high   = sum(1 for s in r.classifications.values() if s == "HIGH")
            n_low    = sum(1 for s in r.classifications.values() if s == "LOW")
            n_normal = sum(1 for s in r.classifications.values() if s == "NORMAL")
            r.log("Stage 3", f"Classified — Normal:{n_normal} High:{n_high} Low:{n_low}")

        except Exception as e:
            r.classifications = {}
            r.log("Stage 3", f"FAILED — {e}", ok=False)

        # ── Stage 4: Model 2 — Pattern Recognition + Risk ────────────────────
        try:
            r.log("Stage 4", "Model 2 — Pattern recognition & risk scores")
            r.patterns    = self.pr.analyze_patterns(r.found)
            r.risk_scores = self.pr.calculate_risk_scores(r.found, age, gender)
            r.ratios      = self.pr.calculate_ratios(r.found)
            r.log("Stage 4",
                  f"Patterns:{len(r.patterns)} "
                  f"Ratios:{len(r.ratios)}")

        except Exception as e:
            r.patterns    = []
            r.risk_scores = {}
            r.ratios      = {}
            r.log("Stage 4", f"FAILED — {e}", ok=False)

        # ── Stage 5: Model 3 — Contextual Analysis ───────────────────────────
        try:
            r.log("Stage 5", "Model 3 — Contextual analysis")
            if age and gender:
                r.adjustments   = self.ca.adjust_all(r.found, age, gender)
                r.fh_risks      = self.ca.assess_family_history_risk(
                    family_history, r.found
                )
                r.lifestyle_recs = self.ca.generate_lifestyle_recommendations(
                    r.found, age, gender, family_history
                )
                r.log("Stage 5",
                      f"Adjustments:{len(r.adjustments)} "
                      f"FH risks:{len(r.fh_risks)}")
            else:
                r.log("Stage 5", "Skipped — age/gender not provided", ok=False)

        except Exception as e:
            r.adjustments    = {}
            r.fh_risks       = []
            r.lifestyle_recs = []
            r.log("Stage 5", f"FAILED — {e}", ok=False)

        # ── Stage 6: Synthesis ────────────────────────────────────────────────
        try:
            r.log("Stage 6", "Synthesis engine — aggregating all findings")
            r.synthesis = self.se.synthesize(
                parameters      = r.found,
                classifications = r.classifications,
                patterns        = r.patterns,
                risk_scores     = r.risk_scores,
                ratios          = r.ratios,
                adjustments     = r.adjustments,
                age             = age,
                gender          = gender,
                family_history  = family_history,
            )
            r.log("Stage 6",
                  f"Status: {r.synthesis.get('overall_status','?')} — "
                  f"KeyFindings:{len(r.synthesis.get('key_findings',[]))}")

        except Exception as e:
            r.synthesis = {}
            r.log("Stage 6", f"FAILED — {e}", ok=False)

        # ── Stage 7: Recommendations ──────────────────────────────────────────
        try:
            r.log("Stage 7", "Recommendation generator")
            r.recommendations = self.se.generate_recommendations(
                classifications = r.classifications,
                patterns        = r.patterns,
                risk_scores     = r.risk_scores,
                parameters      = r.found,
                age             = age,
                gender          = gender,
                family_history  = family_history,
            )
            r.log("Stage 7", f"{len(r.recommendations)} recommendations generated")

        except Exception as e:
            r.recommendations = []
            r.log("Stage 7", f"FAILED — {e}", ok=False)

        r.success = True
        r.log("Complete", f"Pipeline finished successfully at {r.processed_at}")
        return r

    # ══════════════════════════════════════════════════════════════════════════
    # EDGE CASE HELPERS
    # ══════════════════════════════════════════════════════════════════════════

    @staticmethod
    def validate_file(uploaded_file) -> Tuple[bool, str]:
        """Pre-check file before running pipeline."""
        if uploaded_file is None:
            return False, "No file uploaded."
        name = uploaded_file.name.lower()
        allowed = (".pdf", ".txt", ".json", ".png", ".jpg", ".jpeg")
        if not name.endswith(allowed):
            return False, f"Unsupported format. Please upload: PDF, TXT, JSON, PNG, or JPG."
        size_mb = uploaded_file.size / (1024 * 1024)
        if size_mb > 50:
            return False, f"File too large ({size_mb:.1f} MB). Maximum allowed is 50 MB."
        return True, "OK"

    @staticmethod
    def get_pipeline_health(result: OrchestratorResult) -> Dict:
        """Return a health summary of the pipeline run."""
        stages_run    = len(result.pipeline_log)
        stages_failed = sum(1 for l in result.pipeline_log if "FAILED" in l)
        stages_ok     = stages_run - stages_failed
        return {
            "stages_run":    stages_run,
            "stages_ok":     stages_ok,
            "stages_failed": stages_failed,
            "health_pct":    round(stages_ok / max(stages_run, 1) * 100),
            "params_found":  len(result.found),
            "success":       result.success,
        }