"""
pdf_exporter.py
---------------
Generates a downloadable PDF pathway report for a Rooted user.

HOW IT FITS INTO ROOTED:
  1. Frontend sends match results + pathway text to /export-pdf
  2. main.py calls generate_pdf() from this file
  3. This file builds and returns a PDF as bytes
  4. FastAPI streams it back to the browser as a file download

TO USE THIS FILE:
  from app.pdf_exporter import generate_pdf

  pdf_bytes = generate_pdf(
      user_text="I was a nurse in Syria for 8 years...",
      detected_language="Arabic",
      province="Ontario",
      jobs=matches,           # list of Job dicts from get_match()
      pathway_text="...",     # string from generate_pathway_card()
  )

DEPENDENCIES:
  pip install reportlab

MULTILINGUAL NOTE:
  reportlab's built-in fonts (Helvetica) only support Latin characters.
  For Arabic, Somali, Dari, Tigrinya etc., a Unicode font must be
  registered. See register_unicode_font() at the bottom of this file.
  Currently the PDF content is always in English — the detected_language
  is shown as a note. Full translation of PDF content can be added later
  by passing translated text from translator.py.
"""

from __future__ import annotations

import io
from datetime import date
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
)
from reportlab.lib import colors


# ---------------------------------------------------------------------------
# Rooted brand colours
# ---------------------------------------------------------------------------

GREEN_DARK   = colors.HexColor("#1e362c")
GREEN_MID    = colors.HexColor("#2d5243")
BEIGE        = colors.HexColor("#f5f1e8")
BEIGE_DARK   = colors.HexColor("#e8e2d4")
GOLD         = colors.HexColor("#b48c50")
TEXT_DARK    = colors.HexColor("#282823")
TEXT_MUTED   = colors.HexColor("#7a776a")
WHITE        = colors.white

LABEL_COLORS = {
    "Direct match":       colors.HexColor("#0f6e56"),
    "Related field":      colors.HexColor("#185fa5"),
    "Transferable skills": colors.HexColor("#854f0b"),
}
LABEL_BG = {
    "Direct match":       colors.HexColor("#e1f5ee"),
    "Related field":      colors.HexColor("#e6f1fb"),
    "Transferable skills": colors.HexColor("#faeeda"),
}

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
CONTENT_W = PAGE_W - 2 * MARGIN


# ---------------------------------------------------------------------------
# Paragraph styles
# ---------------------------------------------------------------------------

def _style(name, **kwargs) -> ParagraphStyle:
    defaults = dict(fontName="Helvetica", fontSize=10, leading=14,
                    textColor=TEXT_DARK, spaceAfter=0, spaceBefore=0)
    defaults.update(kwargs)
    return ParagraphStyle(name, **defaults)


S = {
    "title":       _style("title",    fontName="Helvetica-Bold", fontSize=22,
                           textColor=WHITE, leading=28),
    "tagline":     _style("tagline",  fontName="Helvetica-Oblique", fontSize=9,
                           textColor=colors.HexColor("#c8dcd4")),
    "h2":          _style("h2",       fontName="Helvetica-Bold", fontSize=13,
                           textColor=GREEN_DARK, spaceBefore=6, spaceAfter=4),
    "body":        _style("body",     fontSize=10, leading=15, textColor=TEXT_DARK),
    "muted":       _style("muted",    fontSize=9,  textColor=TEXT_MUTED),
    "card_title":  _style("cardtitle",fontName="Helvetica-Bold", fontSize=11,
                           textColor=TEXT_DARK),
    "card_noc":    _style("cardnoc",  fontSize=8, textColor=TEXT_MUTED),
    "card_label":  _style("cardlabel",fontName="Helvetica-Bold", fontSize=8),
    "card_desc":   _style("carddesc", fontSize=9, leading=13, textColor=TEXT_DARK),
    "card_link":   _style("cardlink", fontSize=8, textColor=colors.HexColor("#185fa5")),
    "footer":      _style("footer",   fontSize=7, textColor=TEXT_MUTED,
                           alignment=TA_CENTER),
    "best_badge":  _style("bestbadge",fontName="Helvetica-Bold", fontSize=7,
                           textColor=WHITE, alignment=TA_CENTER),
    "pathway":     _style("pathway",  fontSize=10, leading=16, textColor=TEXT_DARK),
}


# ---------------------------------------------------------------------------
# Header canvas callback
# ---------------------------------------------------------------------------

def _draw_header(canvas, doc):
    """Draw the dark green header band on every page."""
    canvas.saveState()

    # Green banner
    canvas.setFillColor(GREEN_DARK)
    canvas.rect(0, PAGE_H - 28 * mm, PAGE_W, 28 * mm, fill=1, stroke=0)

    # Rooted wordmark
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 20)
    canvas.drawString(MARGIN, PAGE_H - 13 * mm, "Rooted")

    # Tagline
    canvas.setFillColor(colors.HexColor("#c8dcd4"))
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.drawString(MARGIN, PAGE_H - 20 * mm,
                      "Your skills are real. Let Canada see them.")

    # Date — top right
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#c8dcd4"))
    date_str = date.today().strftime("%B %d, %Y")
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 13 * mm, date_str)

    # Page number — bottom right
    canvas.setFillColor(TEXT_MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(PAGE_W - MARGIN, 8 * mm,
                            f"Page {doc.page}")

    # Footer privacy text
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawCentredString(PAGE_W / 2, 12 * mm,
        "Rooted is a starting point, not a verdict. Always verify with actual regulators.")
    canvas.drawCentredString(PAGE_W / 2, 8 * mm,
        "Nothing is shared with immigration authorities or any government office.")

    canvas.restoreState()


# ---------------------------------------------------------------------------
# Section helpers
# ---------------------------------------------------------------------------

def _section_title(title: str) -> list:
    return [
        Paragraph(title, S["h2"]),
        HRFlowable(width=CONTENT_W, thickness=0.5,
                   color=GREEN_DARK, spaceAfter=6),
    ]


def _match_card(job: dict[str, Any], is_best: bool) -> Table:
    """Build a styled table row representing one match card."""
    label      = job.get("match_label", "")
    noc_code   = job.get("noc_code", "")
    title      = job.get("job_title", "")
    desc       = job.get("job_description", "")
    noc_url    = job.get("noc_url", "")
    label_color = LABEL_COLORS.get(label, GREEN_DARK)
    label_bg    = LABEL_BG.get(label, BEIGE)

    rows = []

    # Best match badge
    if is_best:
        badge = Table(
            [[Paragraph("★  Best match", S["best_badge"])]],
            colWidths=[28 * mm],
        )
        badge.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GREEN_DARK),
            ("ROUNDEDCORNERS", [3]),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        rows.append([badge, ""])

    # Title row
    rows.append([
        Paragraph(title, S["card_title"]),
        Paragraph(label, ParagraphStyle(
            "lp", fontName="Helvetica-Bold", fontSize=8,
            textColor=label_color, alignment=TA_RIGHT,
        )),
    ])

    # NOC + link row
    noc_cell = Paragraph(
        f'NOC {noc_code} &nbsp;&nbsp;'
        f'<a href="{noc_url}" color="#185fa5">View open jobs on Job Bank →</a>',
        S["card_noc"],
    )
    rows.append([noc_cell, ""])

    # Description
    rows.append([Paragraph(desc, S["card_desc"]), ""])

    card = Table(rows, colWidths=[CONTENT_W * 0.75, CONTENT_W * 0.25])
    bg = colors.HexColor("#f0f6f3") if is_best else colors.HexColor("#f8f8f6")
    card.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (0, 0),   8),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 10),
        ("LINEAFTER",     (0, 0), (0, -1),
         2, GREEN_DARK if is_best else label_color),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return card


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def generate_pdf(
    user_text: str,
    detected_language: str,
    province: str,
    jobs: list[dict[str, Any]],
    pathway_text: str = "",
) -> bytes:
    """
    Build and return a Rooted pathway PDF as bytes.

    Parameters
    ----------
    user_text           User's original background description
    detected_language   Language name e.g. "Arabic", "English"
    province            Canadian province/territory selected by the user
    jobs                List of Job dicts returned by get_match()
    pathway_text        Pathway next-steps string from generate_pathway_card()
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=32 * mm,    # leave room for header band
        bottomMargin=22 * mm, # leave room for footer
        title="Rooted — Your Pathway Report",
        author="Rooted",
    )

    story = []

    # ── Province + intro ────────────────────────────────────────────────────
    if province:
        story.append(Paragraph(
            f"<b>Province / Territory:</b> {province}", S["muted"]))
        story.append(Spacer(1, 4 * mm))

    # ── Your background ─────────────────────────────────────────────────────
    story += _section_title("Your background")

    if detected_language and detected_language.lower() not in ("english", "eng_latn", "auto"):
        story.append(Paragraph(
            f"Original language: {detected_language}", S["muted"]))
        story.append(Spacer(1, 2 * mm))

    story.append(Paragraph(user_text or "—", S["body"]))
    story.append(Spacer(1, 8 * mm))

    # ── Match results ────────────────────────────────────────────────────────
    story += _section_title("Your Canadian career matches")

    for i, job in enumerate(jobs):
        story.append(_match_card(job, is_best=(i == 0)))
        story.append(Spacer(1, 3 * mm))

    story.append(Spacer(1, 5 * mm))

    # ── Pathway next steps ───────────────────────────────────────────────────
    if pathway_text:
        story += _section_title("Suggested next steps")
        for line in pathway_text.split("\n"):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 2 * mm))
                continue
            story.append(Paragraph(line, S["pathway"]))
        story.append(Spacer(1, 8 * mm))

    # ── Privacy notice ───────────────────────────────────────────────────────
    story += _section_title("Important")
    story.append(Paragraph(
        "Rooted matches your experience to Canadian frameworks for guidance and "
        "informational planning only. We do not make immigration decisions or offer "
        "official legal verdicts. Always verify with actual regulators.",
        S["muted"],
    ))

    doc.build(story, onFirstPage=_draw_header, onLaterPages=_draw_header)
    return buffer.getvalue()
