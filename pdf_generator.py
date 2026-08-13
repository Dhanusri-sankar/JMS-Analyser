from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet


# ==================================================
# GENERATE JMS ANALYZER PDF REPORT
# ==================================================

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

    # ==================================================
    # CREATE PDF DOCUMENT
    # ==================================================

    doc = SimpleDocTemplate(
        filename
    )

    styles = getSampleStyleSheet()

    story = []


    # ==================================================
    # REPORT TITLE
    # ==================================================

    story.append(
        Paragraph(
            "<b>JMS Analyzer Report</b>",
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 12)
    )


    # ==================================================
    # BASIC INFORMATION
    # ==================================================

    story.append(
        Paragraph(
            f"<b>Dream Job:</b> {dream_job}",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Readiness Score:</b> {percentage}%",
            styles["Normal"]
        )
    )

    story.append(
        Paragraph(
            f"<b>Status:</b> {status}",
            styles["Normal"]
        )
    )

    story.append(
        Spacer(1, 15)
    )


    # ==================================================
    # FOUND SKILLS
    # ==================================================

    story.append(
        Paragraph(
            "<b>Found Skills</b>",
            styles["Heading2"]
        )
    )

    if found_skills:

        for skill in found_skills:

            story.append(
                Paragraph(
                    f"• {skill}",
                    styles["Normal"]
                )
            )

    else:

        story.append(
            Paragraph(
                "No matching skills found.",
                styles["Normal"]
            )
        )

    story.append(
        Spacer(1, 15)
    )


    # ==================================================
    # MISSING SKILLS
    # ==================================================

    story.append(
        Paragraph(
            "<b>Missing Skills</b>",
            styles["Heading2"]
        )
    )

    if missing_skills:

        for skill in missing_skills:

            story.append(
                Paragraph(
                    f"• {skill}",
                    styles["Normal"]
                )
            )

    else:

        story.append(
            Paragraph(
                "No missing skills.",
                styles["Normal"]
            )
        )

    story.append(
        Spacer(1, 15)
    )


    # ==================================================
    # RECOMMENDATION
    # ==================================================

    story.append(
        Paragraph(
            "<b>Recommendation</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            str(recommendation),
            styles["Normal"]
        )
    )

    story.append(
        Spacer(1, 15)
    )


    # ==================================================
    # LEARNING ROADMAP
    # ==================================================

    story.append(
        Paragraph(
            "<b>Learning Roadmap</b>",
            styles["Heading2"]
        )
    )


    # ==================================================
    # ROADMAP ITEMS
    # ==================================================

    for step in roadmap:

        # ------------------------------------------------
        # NEW V7 ROADMAP FORMAT
        # ------------------------------------------------
        #
        # Example:
        #
        # {
        #     "week": 1,
        #     "skill": "Python",
        #     "demand": "Very High",
        #     "priority": 5,
        #     "learn": "...",
        #     "practice": "...",
        #     "project": "..."
        # }
        #
        # ------------------------------------------------

        if isinstance(
            step,
            dict
        ):

            week = step.get(
                "week",
                ""
            )

            skill = step.get(
                "skill",
                "Skill"
            )

            demand = step.get(
                "demand",
                "Unknown"
            )

            priority = step.get(
                "priority",
                0
            )

            learn = step.get(
                "learn",
                ""
            )

            practice = step.get(
                "practice",
                ""
            )

            project = step.get(
                "project",
                ""
            )


            # --------------------------------------------
            # WEEK + SKILL
            # --------------------------------------------

            story.append(
                Paragraph(
                    f"<b>Week {week}: {skill}</b>",
                    styles["Heading3"]
                )
            )


            # --------------------------------------------
            # MARKET INFORMATION
            # --------------------------------------------

            story.append(
                Paragraph(
                    f"<b>Market Demand:</b> "
                    f"{demand} "
                    f"&nbsp;&nbsp; "
                    f"<b>Priority:</b> "
                    f"{priority}/5",
                    styles["Normal"]
                )
            )


            # --------------------------------------------
            # LEARN
            # --------------------------------------------

            if learn:

                story.append(
                    Paragraph(
                        f"<b>Learn:</b> {learn}",
                        styles["Normal"]
                    )
                )


            # --------------------------------------------
            # PRACTICE
            # --------------------------------------------

            if practice:

                story.append(
                    Paragraph(
                        f"<b>Practice:</b> {practice}",
                        styles["Normal"]
                    )
                )


            # --------------------------------------------
            # PROJECT
            # --------------------------------------------

            if project:

                story.append(
                    Paragraph(
                        f"<b>Project:</b> {project}",
                        styles["Normal"]
                    )
                )


            story.append(
                Spacer(1, 10)
            )


        # ------------------------------------------------
        # OLD ROADMAP FORMAT
        # ------------------------------------------------

        else:

            story.append(
                Paragraph(
                    str(step),
                    styles["Normal"]
                )
            )

            story.append(
                Spacer(1, 8)
            )


    # ==================================================
    # BUILD PDF
    # ==================================================

    doc.build(
        story
    )