import json
import os

import pdfplumber
from docx import Document


# -------------------------------------------------
# LOAD ALL SKILLS FROM jobs.json
# -------------------------------------------------

def load_skills():

    base_dir = os.path.dirname(os.path.abspath(__file__))

    jobs_file = os.path.join(
        base_dir,
        "data",
        "jobs.json"
    )

    with open(jobs_file, "r", encoding="utf-8") as file:
        jobs_data = json.load(file)

    skills = []

    for job_data in jobs_data.values():

        for skill in job_data.get("skills", []):

            if skill not in skills:
                skills.append(skill)

    return skills


# -------------------------------------------------
# EXTRACT TEXT FROM RESUME
# -------------------------------------------------

def extract_text(file_path):

    text = ""

    file_path_lower = file_path.lower()

    # PDF
    if file_path_lower.endswith(".pdf"):

        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

    # DOCX
    elif file_path_lower.endswith(".docx"):

        document = Document(file_path)

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

    else:

        raise ValueError(
            "Unsupported resume format. Use PDF or DOCX."
        )

    return text


# -------------------------------------------------
# EXTRACT SKILLS FROM RESUME
# -------------------------------------------------

def extract_skills(file_path):

    text = extract_text(file_path).lower()

    skills = load_skills()

    found_skills = []

    for skill in skills:

        if skill.lower() in text:
            found_skills.append(skill)

    return found_skills