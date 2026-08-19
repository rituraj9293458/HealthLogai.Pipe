import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def markdown_to_reportlab_html(text: str) -> str:
    # Convert bold **text** -> <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Convert italic *text* -> <i>text</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    return text


def create_pdf(report: str) -> str:
    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"health_report_{timestamp}.pdf"
    pdf_path = os.path.join(reports_dir, filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        alignment=TA_CENTER,
        spaceAfter=15
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        spaceAfter=4
    )

    story = []

    lines = report.strip().split('\n')
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        formatted_line = markdown_to_reportlab_html(stripped)

        # Main Title detection
        if stripped.upper() == "DAILY HEALTH REPORT" or stripped.startswith("# "):
            clean_title = stripped.replace("# ", "").strip()
            story.append(Paragraph(clean_title, title_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3B82F6'), spaceAfter=15))

        # Section headings (e.g., 1. EXECUTIVE SUMMARY, ## Heading, etc.)
        elif re.match(r'^(#+\s+|\d+\.\s+[A-Z\s]{3,})', stripped) or (stripped.endswith(':') and len(stripped) < 40 and not stripped.startswith('-')):
            clean_heading = re.sub(r'^#+\s*', '', formatted_line)
            story.append(Spacer(1, 4))
            story.append(Paragraph(clean_heading, heading_style))

        # Bullet points
        elif stripped.startswith(('-', '*', '•')) or re.match(r'^\d+\.\s+', stripped):
            bullet_text = re.sub(r'^([-\*•]|\d+\.)\s*', '', formatted_line)
            story.append(Paragraph(f"• {bullet_text}", bullet_style))

        # Paragraph text
        else:
            story.append(Paragraph(formatted_line, body_style))

    doc.build(story)
    return pdf_path


def pdf_node(state):
    report = state.get("final_analysis", "")
    if isinstance(report, list):
        report = "\n".join(str(item) for item in report)
    pdf_path = create_pdf(str(report))
    return {"pdf_path": pdf_path}


if __name__ == "__main__":
    test_report = "DAILY HEALTH REPORT\n\n1. EXECUTIVE SUMMARY\nAll metrics normal."
    print("Test PDF path:", create_pdf(test_report))
