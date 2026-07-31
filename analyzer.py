import json

def load_jobs():
    with open("data/jobs.json", "r") as file:
        return json.load(file)

def get_required_skills(job_name):
    jobs = load_jobs()

    if job_name in jobs:
        return jobs[job_name]["skills"]

    return []

def analyze(selected_skills, required_skills):
    found = []
    missing = []

    for skill in required_skills:
        if skill in selected_skills:
            found.append(skill)
        else:
            missing.append(skill)

    return found, missing