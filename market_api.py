import os
import requests

from collections import Counter

from dotenv import load_dotenv


# ==================================================
# LOAD ADZUNA CREDENTIALS
# ==================================================

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")


# ==================================================
# SEARCH JOBS
# ==================================================

def search_jobs(
    job_name,
    country="in",
    page=1,
    results_per_page=20
):
    """
    Search current job listings from Adzuna.
    """

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:

        return {
            "success": False,
            "message": "Adzuna API credentials are missing.",
            "jobs": [],
            "total_results": 0
        }


    url = (
        f"https://api.adzuna.com/"
        f"v1/api/jobs/{country}/search/{page}"
    )


    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": job_name
    }


    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )


        if response.status_code != 200:

            return {
                "success": False,
                "message": (
                    f"Adzuna returned status "
                    f"{response.status_code}."
                ),
                "jobs": [],
                "total_results": 0
            }


        data = response.json()

        jobs = []


        for job in data.get(
            "results",
            []
        ):

            jobs.append({

                "title": job.get(
                    "title",
                    "Unknown"
                ),

                "company": job.get(
                    "company",
                    {}
                ).get(
                    "display_name",
                    "Unknown"
                ),

                "location": job.get(
                    "location",
                    {}
                ).get(
                    "display_name",
                    "Unknown"
                ),

                "description": job.get(
                    "description",
                    ""
                ),

                "salary_min": job.get(
                    "salary_min"
                ),

                "salary_max": job.get(
                    "salary_max"
                ),

                "url": job.get(
                    "redirect_url",
                    ""
                )
            })


        return {

            "success": True,

            "message": (
                "Jobs retrieved successfully."
            ),

            "jobs": jobs,

            "total_results": data.get(
                "count",
                0
            )
        }


    except requests.RequestException as error:

        return {

            "success": False,

            "message": (
                f"Unable to connect to Adzuna: "
                f"{error}"
            ),

            "jobs": [],

            "total_results": 0
        }


# ==================================================
# MARKET INSIGHTS
# ==================================================

def get_market_insights(
    job_name,
    country="in"
):
    """
    Convert live Adzuna job results
    into useful market insights.
    """

    result = search_jobs(
        job_name,
        country=country,
        results_per_page=20
    )


    if not result["success"]:

        return {

            "success": False,

            "message": result["message"],

            "total_jobs": 0,

            "top_companies": [],

            "top_locations": [],

            "salary_min": None,

            "salary_max": None,

            "market_level": "Unavailable"
        }


    jobs = result["jobs"]


    # ------------------------------------------------
    # TOTAL JOBS
    # ------------------------------------------------

    total_jobs = result.get(
        "total_results",
        0
    )


    # ------------------------------------------------
    # TOP COMPANIES
    # ------------------------------------------------

    companies = []

    for job in jobs:

        company = job.get(
            "company"
        )

        if company and company != "Unknown":

            companies.append(
                company
            )


    company_counts = Counter(
        companies
    )


    top_companies = [

        {
            "name": company,
            "count": count
        }

        for company, count
        in company_counts.most_common(5)

    ]


    # ------------------------------------------------
    # TOP LOCATIONS
    # ------------------------------------------------

    locations = []

    for job in jobs:

        location = job.get(
            "location"
        )

        if location and location != "Unknown":

            locations.append(
                location
            )


    location_counts = Counter(
        locations
    )


    top_locations = [

        {
            "name": location,
            "count": count
        }

        for location, count
        in location_counts.most_common(5)

    ]


    # ------------------------------------------------
    # SALARY INFORMATION
    # ------------------------------------------------

    salaries_min = []

    salaries_max = []


    for job in jobs:

        salary_min = job.get(
            "salary_min"
        )

        salary_max = job.get(
            "salary_max"
        )


        if isinstance(
            salary_min,
            (int, float)
        ):

            salaries_min.append(
                salary_min
            )


        if isinstance(
            salary_max,
            (int, float)
        ):

            salaries_max.append(
                salary_max
            )


    average_salary_min = None

    average_salary_max = None


    if salaries_min:

        average_salary_min = round(
            sum(salaries_min)
            / len(salaries_min)
        )


    if salaries_max:

        average_salary_max = round(
            sum(salaries_max)
            / len(salaries_max)
        )


    # ------------------------------------------------
    # MARKET LEVEL
    # ------------------------------------------------

    if total_jobs >= 10000:

        market_level = "Very High"

    elif total_jobs >= 5000:

        market_level = "High"

    elif total_jobs >= 1000:

        market_level = "Moderate"

    elif total_jobs > 0:

        market_level = "Low"

    else:

        market_level = "No Data"


    # ------------------------------------------------
    # RETURN INSIGHTS
    # ------------------------------------------------

    return {

        "success": True,

        "message": (
            "Market insights generated successfully."
        ),

        "total_jobs": total_jobs,

        "top_companies": top_companies,

        "top_locations": top_locations,

        "salary_min": average_salary_min,

        "salary_max": average_salary_max,

        "market_level": market_level
    }


# ==================================================
# TEST MARKET INSIGHTS
# ==================================================

if __name__ == "__main__":

    result = get_market_insights(
        "Data Engineer",
        country="in"
    )


    if result["success"]:

        print(
            "\nAdzuna market insights successful."
        )


        print(
            "\nTotal Jobs:",
            result["total_jobs"]
        )


        print(
            "\nMarket Level:",
            result["market_level"]
        )


        print(
            "\nTop Companies:"
        )

        for company in result[
            "top_companies"
        ]:

            print(
                "-",
                company["name"],
                "(",
                company["count"],
                ")"
            )


        print(
            "\nTop Locations:"
        )

        for location in result[
            "top_locations"
        ]:

            print(
                "-",
                location["name"],
                "(",
                location["count"],
                ")"
            )


        print(
            "\nAverage Salary Minimum:",
            result["salary_min"]
        )


        print(
            "Average Salary Maximum:",
            result["salary_max"]
        )


    else:

        print(
            result["message"]
        )