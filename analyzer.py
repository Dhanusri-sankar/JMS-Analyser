import json
import os


# ==================================================
# LOAD JOBS
# ==================================================

def load_jobs():

    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    jobs_file = os.path.join(
        base_dir,
        "data",
        "jobs.json"
    )

    with open(
        jobs_file,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==================================================
# GET REQUIRED SKILLS
# ==================================================

def get_required_skills(job_name):

    jobs = load_jobs()

    if job_name in jobs:

        return jobs[job_name].get(
            "skills",
            []
        )

    return []


# ==================================================
# ANALYZE SKILLS
# ==================================================

def analyze(
    selected_skills,
    required_skills
):

    found = []
    missing = []

    selected_lower = {
        skill.lower()
        for skill in selected_skills
    }

    for skill in required_skills:

        if skill.lower() in selected_lower:

            found.append(skill)

        else:

            missing.append(skill)

    return found, missing


# ==================================================
# V5 WEIGHTED READINESS SCORE
# ==================================================

def calculate_weighted_score(
    found_skills,
    required_skills
):

    if not required_skills:

        return 0

    total_weight = 0
    earned_weight = 0

    found_lower = {
        skill.lower()
        for skill in found_skills
    }

    for index, skill in enumerate(
        required_skills
    ):

        # First 3 skills = Core Skills
        if index < 3:

            weight = 3

        # Next 3 skills = Important Skills
        elif index < 6:

            weight = 2

        # Remaining skills = Supporting Skills
        else:

            weight = 1

        total_weight += weight

        if skill.lower() in found_lower:

            earned_weight += weight

    percentage = round(
        (
            earned_weight
            / total_weight
        ) * 100
    )

    return percentage