import pdfplumber
from docx import Document

SKILLS = [
    "Python", "SQL", "Excel", "Pandas", "NumPy",
    "Java", "Spring Boot", "React", "Node.js",
    "HTML", "CSS", "JavaScript", "Flask",
    "Git", "Machine Learning", "Deep Learning",
    "TensorFlow", "Apache Spark", "Hadoop",
    "Airflow", "MongoDB", "REST API"
]


def extract_text(file_path):

    text = ""

    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""

    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    return text


def extract_skills(file_path):

    text = extract_text(file_path).lower()

    found = []

    for skill in SKILLS:
        if skill.lower() in text:
            found.append(skill)

    return found