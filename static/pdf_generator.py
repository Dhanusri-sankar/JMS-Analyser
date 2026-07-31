from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(
    filename,
    dream_job,
    percentage,
    status,
    found_skills,
    missing_skills,
    recommendation,
    roadmap
):

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>JMS Analyzer Report</b>", styles["Title"]))
    story.append(Paragraph(f"<b>Dream Job:</b> {dream_job}", styles["Normal"]))
    story.append(Paragraph(f"<b>Readiness Score:</b> {percentage}%", styles["Normal"]))
    story.append(Paragraph(f"<b>Status:</b> {status}", styles["Normal"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph("<b>Found Skills</b>", styles["Heading2"]))
    for skill in found_skills:
        story.append(Paragraph(f"• {skill}", styles["Normal"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph("<b>Missing Skills</b>", styles["Heading2"]))
    for skill in missing_skills:
        story.append(Paragraph(f"• {skill}", styles["Normal"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph("<b>Recommendation</b>", styles["Heading2"]))
    story.append(Paragraph(recommendation, styles["Normal"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph("<b>Learning Roadmap</b>", styles["Heading2"]))
    for step in roadmap:
        story.append(Paragraph(step, styles["Normal"]))

    doc.build(story)