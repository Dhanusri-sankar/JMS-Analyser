import json
import os


# ==================================================
# FILE PATHS
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

JOBS_FILE = os.path.join(
    BASE_DIR,
    "data",
    "jobs.json"
)

MARKET_FILE = os.path.join(
    BASE_DIR,
    "data",
    "skill_market.json"
)


# ==================================================
# LOAD JOB DATA
# ==================================================

def load_jobs():

    with open(
        JOBS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==================================================
# LOAD MARKET DATA
# ==================================================

def load_market_data():

    with open(
        MARKET_FILE,
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

        # First 3 skills = Core
        if index < 3:

            weight = 3

        # Next 3 = Important
        elif index < 6:

            weight = 2

        # Remaining = Supporting
        else:

            weight = 1

        total_weight += weight

        if skill.lower() in found_lower:

            earned_weight += weight

    if total_weight == 0:

        return 0

    return round(
        (
            earned_weight
            / total_weight
        ) * 100
    )


# ==================================================
# V6 GET SKILL MARKET INFORMATION
# ==================================================

def get_skill_market_info(skill):

    market_data = load_market_data()

    if skill in market_data:

        return market_data[skill]

    # Safe fallback if a skill has not yet
    # been added to skill_market.json
    return {
        "demand": "Unknown",
        "priority": 0
    }


# ==================================================
# V6 GET MARKET INFORMATION FOR JOB SKILLS
# ==================================================

def get_job_market_skills(job_name):

    required_skills = get_required_skills(
        job_name
    )

    market_data = load_market_data()

    result = []

    for skill in required_skills:

        information = market_data.get(
            skill,
            {
                "demand": "Unknown",
                "priority": 0
            }
        )

        result.append({
            "skill": skill,
            "demand": information.get(
                "demand",
                "Unknown"
            ),
            "priority": information.get(
                "priority",
                0
            )
        })

    return result


# ==================================================
# V6 PRIORITIZE MISSING SKILLS
# ==================================================

def prioritize_missing_skills(
    missing_skills
):

    market_data = load_market_data()

    prioritized = []

    for skill in missing_skills:

        information = market_data.get(
            skill,
            {
                "demand": "Unknown",
                "priority": 0
            }
        )

        prioritized.append({
            "skill": skill,
            "demand": information.get(
                "demand",
                "Unknown"
            ),
            "priority": information.get(
                "priority",
                0
            )
        })

    # Highest priority first
    prioritized.sort(
        key=lambda item: item["priority"],
        reverse=True
    )

    return prioritized