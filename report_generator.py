# report_generator.py
# Milestone 4 — Report Generation Module
# Generates a downloadable PDF report from orchestrator results

import io
from datetime import datetime
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.platypus import PageBreak


# ── Brand colours ─────────────────────────────────────────────────────────────
BLUE       = colors.HexColor("#1565c0")
BLUE_LIGHT = colors.HexColor("#e3f2fd")
BLUE_MID   = colors.HexColor("#1976d2")
RED        = colors.HexColor("#c62828")
RED_LIGHT  = colors.HexColor("#ffebee")
ORANGE     = colors.HexColor("#e65100")
ORANGE_LT  = colors.HexColor("#fff3e0")
GREEN      = colors.HexColor("#2e7d32")
GREEN_LT   = colors.HexColor("#e8f5e9")
YELLOW_LT  = colors.HexColor("#fff8e1")
GRAY       = colors.HexColor("#546e7a")
GRAY_LT    = colors.HexColor("#f5f7fa")
GRAY_LINE  = colors.HexColor("#eceff1")
WHITE      = colors.white
BLACK      = colors.HexColor("#1a1a2e")


class ReportGenerator:
    """
    Milestone 4 — Report Generation Module.
    Produces a professional, patient-readable PDF blood report.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._build_styles()

    def _build_styles(self):
        """Define all custom paragraph styles."""
        base = dict(fontName="Helvetica", leading=14)

        def add(name, **kwargs):
            self.styles.add(ParagraphStyle(name=name, **{**base, **kwargs}))

        add("ReportTitle",   fontSize=22, textColor=WHITE,
            fontName="Helvetica-Bold", alignment=TA_CENTER, leading=28)
        add("ReportSubtitle",fontSize=11, textColor=colors.HexColor("#bbdefb"),
            alignment=TA_CENTER, leading=16)
        add("SectionHead",   fontSize=13, textColor=BLUE,
            fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
        add("ParamName",     fontSize=10, textColor=BLACK)
        add("ParamValue",    fontSize=10, textColor=BLACK, fontName="Helvetica-Bold")
        add("StatusHigh",    fontSize=10, textColor=RED, fontName="Helvetica-Bold")
        add("StatusLow",     fontSize=10, textColor=ORANGE, fontName="Helvetica-Bold")
        add("StatusNormal",  fontSize=10, textColor=GREEN, fontName="Helvetica-Bold")
        add("ReportBody",      fontSize=10, textColor=GRAY, leading=15)
        add("SmallText",     fontSize=9,  textColor=GRAY, leading=13)
        add("Finding",       fontSize=10, textColor=BLACK, leading=15, leftIndent=8)
        add("RecAction",     fontSize=10, textColor=BLACK, leading=15)
        add("RecFinding",    fontSize=9,  textColor=GRAY,  leading=13)
        add("Disclaimer",    fontSize=8,  textColor=GRAY,  leading=12,
            borderPadding=8)
        add("HeadlineText",  fontSize=11, textColor=BLACK, leading=16)
        add("Positive",      fontSize=10, textColor=GREEN, leading=14)
        add("UrgentText",    fontSize=10, textColor=RED,   fontName="Helvetica-Bold")

    # ══════════════════════════════════════════════════════════════════════════
    # PUBLIC — generate PDF bytes
    # ══════════════════════════════════════════════════════════════════════════

    def generate(self,
                 result,          # OrchestratorResult
                 patient_name: str = "Patient",
                 age:   Optional[int] = None,
                 gender: Optional[str] = None) -> bytes:
        """
        Build the complete PDF report and return as bytes.
        Usage:
            pdf_bytes = generator.generate(result, "Ravi Kumar", 52, "Male")
            st.download_button("Download Report", pdf_bytes, "blood_report.pdf")
        """
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            topMargin=15*mm, bottomMargin=20*mm,
            leftMargin=18*mm, rightMargin=18*mm,
        )

        story = []
        story += self._header(patient_name, age, gender, result)
        story += self._overall_status(result)
        story += self._parameter_table(result)
        story += self._patterns_section(result)
        story += self._risk_scores_section(result)
        story += self._key_findings_section(result)

        if result.synthesis.get("systems_affected"):
            story += self._systems_section(result)

        if result.synthesis.get("positive_findings"):
            story += self._positives_section(result)

        story += self._recommendations_section(result)
        story += self._pipeline_log_section(result)
        story += self._disclaimer_section()

        doc.build(story, onFirstPage=self._page_footer,
                  onLaterPages=self._page_footer)
        return buf.getvalue()

    # ══════════════════════════════════════════════════════════════════════════
    # SECTIONS
    # ══════════════════════════════════════════════════════════════════════════

    def _header(self, name, age, gender, result):
        elements = []
        # Blue header block via table
        info_lines = []
        if age:    info_lines.append(f"Age: {age}")
        if gender: info_lines.append(f"Gender: {gender}")
        info_lines.append(f"Report Date: {result.processed_at}")
        info_lines.append(f"Source: {result.file_name or 'Sample Data'}")

        header_data = [[
            Paragraph("BloodAI", self.styles["ReportTitle"]),
            Paragraph(
                "Automated Blood Report Interpretation System<br/>"
                + " &nbsp;|&nbsp; ".join(info_lines),
                self.styles["ReportSubtitle"]
            ),
        ]]
        t = Table(header_data, colWidths=["30%", "70%"])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), BLUE),
            ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 14),
            ("BOTTOMPADDING",(0,0),(-1,-1), 14),
            ("LEFTPADDING", (0,0),(-1,-1), 12),
            ("ROUNDEDCORNERS", (0,0),(-1,-1), [6,6,6,6]),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

        # Patient name
        elements.append(
            Paragraph(f"Patient: <b>{name}</b>", self.styles["SectionHead"])
        )
        elements.append(HRFlowable(width="100%", thickness=0.5,
                                   color=GRAY_LINE, spaceAfter=8))
        return elements

    def _overall_status(self, result):
        s = result.synthesis
        if not s:
            return []
        elements = []

        STATUS_COLOR = {
            "Urgent":    RED,      "Concern":    ORANGE,
            "Borderline":colors.HexColor("#f9a825"), "Normal": GREEN
        }
        STATUS_BG = {
            "Urgent":    RED_LIGHT, "Concern":    ORANGE_LT,
            "Borderline":YELLOW_LT, "Normal":     GREEN_LT
        }
        ovs    = s.get("overall_status", "Unknown")
        sc     = STATUS_COLOR.get(ovs, GRAY)
        bg     = STATUS_BG.get(ovs, GRAY_LT)
        counts = s.get("counts", {})
        comp   = s.get("completeness", {})

        summary_data = [
            [
                Paragraph(f"Overall Status: <b>{ovs}</b>",
                          ParagraphStyle("OVS", fontName="Helvetica-Bold",
                                         fontSize=14, textColor=sc,
                                         leading=18)),
                Paragraph(
                    f"Parameters: <b>{counts.get('total',0)}</b> &nbsp;|&nbsp; "
                    f"Normal: <b>{counts.get('normal',0)}</b> &nbsp;|&nbsp; "
                    f"Abnormal: <b>{counts.get('high',0)+counts.get('low',0)}</b> &nbsp;|&nbsp; "
                    f"Patterns: <b>{counts.get('patterns',0)}</b> &nbsp;|&nbsp; "
                    f"Coverage: <b>{comp.get('pct',0)}%</b>",
                    self.styles["ReportBody"]
                ),
            ],
            [
                Paragraph(s.get("headline",""), self.styles["HeadlineText"]),
                Paragraph("", self.styles["ReportBody"]),
            ],
        ]
        t = Table(summary_data, colWidths=["40%","60%"])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), bg),
            ("TOPPADDING",    (0,0),(-1,-1), 10),
            ("BOTTOMPADDING", (0,0),(-1,-1), 10),
            ("LEFTPADDING",   (0,0),(-1,-1), 12),
            ("RIGHTPADDING",  (0,0),(-1,-1), 12),
            ("SPAN", (0,1),(-1,1)),
            ("LINEBELOW", (0,0),(-1,0), 0.5, colors.HexColor("#e0e0e0")),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 10))

        # Urgent flags
        flags = s.get("urgent_flags", [])
        if flags:
            elements.append(
                Paragraph("URGENT FLAGS", self.styles["SectionHead"])
            )
            for flag in flags:
                elements.append(
                    Paragraph(f"  !! {flag['message']}", self.styles["UrgentText"])
                )
            elements.append(Spacer(1, 6))

        return elements

    def _parameter_table(self, result):
        if not result.found:
            return []
        elements = []
        elements.append(Paragraph("Blood Parameters", self.styles["SectionHead"]))

        STATUS_COLOR = {"HIGH": RED, "LOW": ORANGE, "NORMAL": GREEN, "UNKNOWN": GRAY}

        from reference import get_display_range, get_unit

        rows = [
            [
                Paragraph("<b>Parameter</b>", self.styles["ParamName"]),
                Paragraph("<b>Value</b>",      self.styles["ParamName"]),
                Paragraph("<b>Unit</b>",        self.styles["ParamName"]),
                Paragraph("<b>Reference Range</b>", self.styles["ParamName"]),
                Paragraph("<b>Status</b>",     self.styles["ParamName"]),
            ]
        ]
        row_styles = [
            ("BACKGROUND", (0,0), (-1,0), BLUE_LIGHT),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1),(-1,-1), [WHITE, GRAY_LT]),
            ("GRID",       (0,0), (-1,-1), 0.3, GRAY_LINE),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ("LEFTPADDING",(0,0), (-1,-1), 7),
        ]

        for i, (param, value) in enumerate(result.found.items()):
            status    = result.classifications.get(param, "UNKNOWN")
            sc        = STATUS_COLOR.get(status, GRAY)
            unit      = get_unit(param)
            ref_range = get_display_range(param)
            rows.append([
                Paragraph(param,           self.styles["ParamName"]),
                Paragraph(str(value),      self.styles["ParamValue"]),
                Paragraph(unit,            self.styles["SmallText"]),
                Paragraph(ref_range,       self.styles["SmallText"]),
                Paragraph(f"<b>{status}</b>",
                          ParagraphStyle(f"S{i}", fontName="Helvetica-Bold",
                                         fontSize=9, textColor=sc, leading=12)),
            ])
            if status in ("HIGH","LOW"):
                row_styles.append(
                    ("BACKGROUND", (4, i+1),(4, i+1),
                     RED_LIGHT if status=="HIGH" else ORANGE_LT)
                )

        t = Table(rows, colWidths=["30%","15%","12%","28%","15%"],
                  repeatRows=1)
        t.setStyle(TableStyle(row_styles))
        elements.append(t)
        elements.append(Spacer(1, 10))
        return elements

    def _patterns_section(self, result):
        if not result.patterns:
            return []
        elements = []
        elements.append(Paragraph("Clinical Patterns Detected (Model 2)",
                                  self.styles["SectionHead"]))
        SEV_COLOR = {"High": RED, "Moderate": ORANGE, "Low": GRAY}

        for p in result.patterns:
            sc    = SEV_COLOR.get(p["severity"], GRAY)
            block = [
                [
                    Paragraph(
                        f"<b>{p['name']}</b> — {p['severity']} severity "
                        f"({p['criteria_met']}/{p['total_criteria']} criteria, "
                        f"{p['confidence']}% confidence)",
                        ParagraphStyle("PH", fontName="Helvetica-Bold",
                                       fontSize=10, textColor=sc, leading=14)
                    ),
                ],
                [Paragraph(p["description"], self.styles["ReportBody"])],
                [Paragraph(
                    "Matched: " + "; ".join(p.get("matched_criteria",[])),
                    self.styles["SmallText"]
                )],
            ]
            tb = Table(block, colWidths=["100%"])
            tb.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,-1), GRAY_LT),
                ("LEFTPADDING",   (0,0),(-1,-1), 10),
                ("RIGHTPADDING",  (0,0),(-1,-1), 10),
                ("TOPPADDING",    (0,0),(-1,-1), 6),
                ("BOTTOMPADDING", (0,0),(-1,-1), 6),
                ("LINEAFTER",     (0,0),(0,-1), 3, sc),
            ]))
            elements.append(tb)
            elements.append(Spacer(1, 5))
        return elements

    def _risk_scores_section(self, result):
        if not result.risk_scores:
            return []
        elements = []
        elements.append(Paragraph("Risk Assessment (Model 2)",
                                  self.styles["SectionHead"]))

        LEVEL_COLOR = {"High": RED, "Moderate": ORANGE, "Low": GREEN}
        LEVEL_BG    = {"High": RED_LIGHT, "Moderate": ORANGE_LT, "Low": GREEN_LT}

        rows_data = [[
            Paragraph("<b>Risk Area</b>",       self.styles["ParamName"]),
            Paragraph("<b>Score</b>",            self.styles["ParamName"]),
            Paragraph("<b>Level</b>",            self.styles["ParamName"]),
            Paragraph("<b>Key Factors</b>",      self.styles["ParamName"]),
        ]]
        row_styles = [
            ("BACKGROUND", (0,0),(-1,0), BLUE_LIGHT),
            ("FONTSIZE",   (0,0),(-1,-1), 9),
            ("GRID",       (0,0),(-1,-1), 0.3, GRAY_LINE),
            ("TOPPADDING", (0,0),(-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ("LEFTPADDING",(0,0),(-1,-1), 7),
        ]

        for i, (name, d) in enumerate(result.risk_scores.items()):
            level   = d.get("level","Unknown")
            score   = d.get("score","N/A")
            max_s   = d.get("max_score",10)
            factors = d.get("factors",[])
            lc      = LEVEL_COLOR.get(level, GRAY)
            lb      = LEVEL_BG.get(level, GRAY_LT)
            rows_data.append([
                Paragraph(name, self.styles["ParamName"]),
                Paragraph(f"{score}/{max_s}", self.styles["ParamValue"]),
                Paragraph(f"<b>{level}</b>",
                          ParagraphStyle(f"L{i}", fontName="Helvetica-Bold",
                                         fontSize=9, textColor=lc, leading=12)),
                Paragraph(", ".join(factors[:3]) or "—", self.styles["SmallText"]),
            ])
            if level in ("High","Moderate"):
                for col in range(4):
                    row_styles.append(("BACKGROUND",(col,i+1),(col,i+1),lb))

        t = Table(rows_data, colWidths=["28%","13%","15%","44%"])
        t.setStyle(TableStyle(row_styles))
        elements.append(t)
        elements.append(Spacer(1, 10))
        return elements

    def _key_findings_section(self, result):
        findings = result.synthesis.get("key_findings",[])
        if not findings:
            return []
        elements = []
        elements.append(Paragraph("Key Findings Summary",
                                  self.styles["SectionHead"]))
        TYPE_COLOR = {
            "HIGH": RED, "LOW": ORANGE, "PATTERN": BLUE,
            "RISK": ORANGE, "RATIO": BLUE_MID, "CONTEXT": GRAY
        }
        for f in findings:
            tc = TYPE_COLOR.get(f.get("type",""), GRAY)
            elements.append(
                Paragraph(
                    f"<b>[{f.get('type','')}]</b> {f.get('text','')}",
                    ParagraphStyle("KF", fontSize=10, textColor=tc,
                                   leading=15, leftIndent=10, spaceAfter=4)
                )
            )
        elements.append(Spacer(1, 8))
        return elements

    def _systems_section(self, result):
        systems = result.synthesis.get("systems_affected",{})
        if not systems:
            return []
        elements = []
        elements.append(Paragraph("Organ Systems Affected",
                                  self.styles["SectionHead"]))
        for system, params_list in systems.items():
            params_txt = ", ".join(
                f"{p['param']} ({p['status']})" for p in params_list
            )
            elements.append(
                Paragraph(f"<b>{system}:</b> {params_txt}",
                          self.styles["Finding"])
            )
        elements.append(Spacer(1, 8))
        return elements

    def _positives_section(self, result):
        positives = result.synthesis.get("positive_findings",[])
        if not positives:
            return []
        elements = []
        elements.append(Paragraph("Positive Findings",
                                  self.styles["SectionHead"]))
        for pos in positives:
            elements.append(
                Paragraph(f"+ {pos}", self.styles["Positive"])
            )
        elements.append(Spacer(1, 8))
        return elements

    def _recommendations_section(self, result):
        recs = result.recommendations
        if not recs:
            return []
        elements = []
        elements.append(PageBreak())
        elements.append(Paragraph("Personalised Recommendations",
                                  self.styles["SectionHead"]))
        elements.append(
            Paragraph(
                "Each recommendation is directly linked to a specific finding in this report.",
                self.styles["SmallText"]
            )
        )
        elements.append(Spacer(1, 8))

        CAT_COLOR = {
            "Diet": BLUE, "Lifestyle": GREEN, "Follow-up": RED,
            "Supplements": ORANGE, "Screening": BLUE_MID
        }
        PRIO_COLOR = {
            "Urgent": RED, "High": RED, "Moderate": ORANGE, "Low": GREEN
        }
        PRIO_BG = {
            "Urgent": RED_LIGHT, "High": RED_LIGHT,
            "Moderate": ORANGE_LT, "Low": GREEN_LT
        }

        cats = {}
        for rec in recs:
            cats.setdefault(rec.get("category","General"), []).append(rec)

        for cat, cat_recs in cats.items():
            cc = CAT_COLOR.get(cat, GRAY)
            elements.append(
                Paragraph(f"<b>{cat}</b>",
                          ParagraphStyle("CatH", fontName="Helvetica-Bold",
                                         fontSize=11, textColor=cc,
                                         leading=16, spaceBefore=8))
            )
            for rec in cat_recs:
                prio   = rec.get("priority","Moderate")
                pc     = PRIO_COLOR.get(prio, GRAY)
                pb     = PRIO_BG.get(prio, GRAY_LT)
                linked = rec.get("linked_to","")
                block  = [
                    [
                        Paragraph(
                            f"<b>[{prio}]</b>  Linked to: {linked}",
                            ParagraphStyle("RH", fontName="Helvetica-Bold",
                                           fontSize=9, textColor=pc, leading=13)
                        ),
                    ],
                    [Paragraph(rec.get("action",""), self.styles["RecAction"])],
                ]
                tb = Table(block, colWidths=["100%"])
                tb.setStyle(TableStyle([
                    ("BACKGROUND",    (0,0),(-1,-1), pb),
                    ("LEFTPADDING",   (0,0),(-1,-1), 10),
                    ("RIGHTPADDING",  (0,0),(-1,-1), 10),
                    ("TOPPADDING",    (0,0),(0,0), 6),
                    ("BOTTOMPADDING", (0,-1),(0,-1), 8),
                    ("LINEAFTER",     (0,0),(0,-1), 3, pc),
                ]))
                elements.append(tb)
                elements.append(Spacer(1, 4))

        return elements

    def _pipeline_log_section(self, result):
        if not result.pipeline_log:
            return []
        elements = []
        elements.append(Spacer(1, 8))
        elements.append(
            Paragraph("Pipeline Execution Log", self.styles["SectionHead"])
        )
        for entry in result.pipeline_log:
            elements.append(Paragraph(entry, self.styles["SmallText"]))
        elements.append(Spacer(1, 8))
        return elements

    def _disclaimer_section(self):
        elements = []
        elements.append(HRFlowable(width="100%", thickness=0.5,
                                   color=GRAY_LINE, spaceBefore=10))
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(
                "<b>MEDICAL DISCLAIMER</b><br/>"
                "This report is generated by an AI system for informational purposes ONLY. "
                "It does NOT constitute medical advice, diagnosis, or treatment. "
                "All findings, patterns, risk scores, and recommendations in this report "
                "are automated interpretations and must be reviewed by a qualified "
                "healthcare professional before any clinical decisions are made. "
                "Do not delay seeking medical advice based on this report alone. "
                "If you are experiencing a medical emergency, contact emergency services immediately.",
                self.styles["Disclaimer"]
            )
        )
        elements.append(
            Paragraph(
                f"Generated by BloodAI  |  {datetime.now().strftime('%d %b %Y, %I:%M %p')}  |  "
                "Model 1: Parameter Interpretation  |  "
                "Model 2: Pattern Recognition  |  "
                "Model 3: Contextual Analysis  |  "
                "Milestone 4: Synthesis & Report Generation",
                ParagraphStyle("Footer", fontSize=7, textColor=GRAY,
                               alignment=TA_CENTER, leading=11)
            )
        )
        return elements

    # ── Page footer (page numbers) ─────────────────────────────────────────────
    @staticmethod
    def _page_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GRAY)
        canvas.drawString(18*mm, 12*mm,
                          f"BloodAI — Automated Blood Report")
        canvas.drawRightString(
            A4[0] - 18*mm, 12*mm,
            f"Page {canvas.getPageNumber()}"
        )
        canvas.restoreState()