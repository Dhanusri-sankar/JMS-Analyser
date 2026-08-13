import os
import io
import csv
import uuid

import plotly.graph_objects as go

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    Response,
    send_file
)

from werkzeug.utils import secure_filename

from pdf_generator import generate_pdf
from resume_parser import extract_skills

from analyzer import (
    get_required_skills,
    analyze,
    calculate_weighted_score,
    prioritize_missing_skills,
    match_resume_to_job,
    calculate_resume_match_score
)

from roadmap import ROADMAP

# V7 - LIVE ADZUNA MARKET INSIGHTS
from market_api import get_market_insights

from models import (
    create_tables,
    save_report,
    get_reports,
    search_reports,
    delete_report,
    get_dashboard_stats
)


# ==================================================
# APP SETUP
# ==================================================

app = Flask(__name__)

# Maximum resume upload size = 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


# ==================================================
# DATABASE
# ==================================================

create_tables()


# ==================================================
# UPLOAD FOLDER
# ==================================================

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)
    ),
    "uploads"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==================================================
# USER TYPE
# ==================================================

@app.route("/user-type")
def user_type():

    return render_template(
        "user_type.html"
    )


# ==================================================
# DREAM JOB
# ==================================================

@app.route("/dream-job")
def dream_job():

    return render_template(
        "dream_job.html"
    )


# ==================================================
# SKILLS
# ==================================================

@app.route(
    "/skills",
    methods=["POST"]
)
def skills():

    dream_job = request.form.get(
        "dream_job"
    )

    if not dream_job:

        return """
        <script>
            alert("Please select a Dream Job.");
            window.history.back();
        </script>
        """

    required_skills = get_required_skills(
        dream_job
    )

    return render_template(
        "skills.html",
        dream_job=dream_job,
        required_skills=required_skills
    )


# ==================================================
# HISTORY
# ==================================================

@app.route("/history")
def history():

    keyword = request.args.get(
        "search"
    )

    if keyword:

        reports = search_reports(
            keyword
        )

    else:

        reports = get_reports()

    return render_template(
        "history.html",
        reports=reports,
        keyword=keyword
    )


# ==================================================
# DELETE REPORT
# ==================================================

@app.route(
    "/delete-report/<int:report_id>",
    methods=["POST"]
)
def delete_report_route(report_id):

    delete_report(
        report_id
    )

    return redirect(
        url_for("history")
    )


# ==================================================
# EXPORT CSV
# ==================================================

@app.route("/export-csv")
def export_csv():

    reports = get_reports()

    output = io.StringIO()

    writer = csv.writer(
        output
    )

    writer.writerow([
        "ID",
        "Dream Job",
        "Score",
        "Status",
        "Found Skills",
        "Missing Skills"
    ])

    for report in reports:

        writer.writerow([
            report[0],
            report[1],
            report[2],
            report[3],
            report[4],
            report[5]
        ])

    csv_data = (
        "\ufeff"
        + output.getvalue()
    )

    response = Response(
        csv_data,
        mimetype="text/csv; charset=utf-8"
    )

    response.headers[
        "Content-Disposition"
    ] = (
        "attachment; "
        "filename=JMS_Analysis_History.csv"
    )

    return response


# ==================================================
# EXPORT EXCEL
# ==================================================

@app.route("/export-excel")
def export_excel():

    reports = get_reports()

    workbook = Workbook()

    sheet = workbook.active

    sheet.title = (
        "JMS Analysis History"
    )

    headings = [
        "ID",
        "Dream Job",
        "Score",
        "Status",
        "Found Skills",
        "Missing Skills"
    ]

    sheet.append(
        headings
    )

    for cell in sheet[1]:

        cell.font = Font(
            bold=True
        )

        cell.alignment = Alignment(
            horizontal="center"
        )

    for report in reports:

        sheet.append([
            report[0],
            report[1],
            report[2],
            report[3],
            report[4],
            report[5]
        ])

    sheet.column_dimensions[
        "A"
    ].width = 10

    sheet.column_dimensions[
        "B"
    ].width = 30

    sheet.column_dimensions[
        "C"
    ].width = 15

    sheet.column_dimensions[
        "D"
    ].width = 20

    sheet.column_dimensions[
        "E"
    ].width = 45

    sheet.column_dimensions[
        "F"
    ].width = 55

    output = io.BytesIO()

    workbook.save(
        output
    )

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=(
            "JMS_Analysis_History.xlsx"
        ),
        mimetype=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )


# ==================================================
# ANALYSIS
# ==================================================

@app.route(
    "/analysis",
    methods=["POST"]
)
def analysis():

    dream_job = request.form.get(
        "dream_job"
    )


    # ==================================================
    # DREAM JOB VALIDATION
    # ==================================================

    if not dream_job:

        return """
        <script>
            alert(
                "Dream Job not selected. "
                + "Please select your Dream Job."
            );
            window.history.back();
        </script>
        """


    # ==================================================
    # GET RESUME
    # ==================================================

    resume = request.files.get(
        "resume"
    )


    # --------------------------------------------------
    # RESUME VARIABLES
    # --------------------------------------------------

    resume_uploaded = False

    resume_match_score = 0

    matched_resume_skills = []

    missing_resume_skills = []

    additional_resume_skills = []


    # ==================================================
    # RESUME ANALYSIS
    # ==================================================

    if resume and resume.filename != "":

        resume_uploaded = True


        # ------------------------------------------------
        # ALLOWED FILE TYPES
        # ------------------------------------------------

        allowed_extensions = (
            ".pdf",
            ".docx"
        )


        original_filename = (
            resume.filename
        )


        if not original_filename.lower().endswith(
            allowed_extensions
        ):

            return """
            <script>
                alert(
                    "Invalid resume format. "
                    + "Please upload only PDF "
                    + "or DOCX files."
                );
                window.history.back();
            </script>
            """


        # ------------------------------------------------
        # SECURE ORIGINAL FILE NAME
        # ------------------------------------------------

        filename = secure_filename(
            original_filename
        )


        if not filename:

            return """
            <script>
                alert(
                    "Invalid file name. "
                    + "Please rename your resume "
                    + "and upload it again."
                );
                window.history.back();
            </script>
            """


        # ------------------------------------------------
        # GET FILE EXTENSION
        # ------------------------------------------------

        file_extension = os.path.splitext(
            filename
        )[1].lower()


        # ------------------------------------------------
        # CREATE UNIQUE TEMPORARY FILE NAME
        # ------------------------------------------------
        #
        # We do NOT use the user's original
        # filename for storage.
        #
        # Example:
        #
        # a8f92d7c9e....pdf
        #
        # This reduces filename collision
        # and avoids storing the original
        # personal filename.
        # ------------------------------------------------

        temporary_filename = (
            uuid.uuid4().hex
            + file_extension
        )


        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            temporary_filename
        )


        # ------------------------------------------------
        # PROCESS RESUME TEMPORARILY
        # ------------------------------------------------

        try:

            # --------------------------------------------
            # SAVE TEMPORARY RESUME
            # --------------------------------------------

            resume.save(
                file_path
            )


            # --------------------------------------------
            # EXTRACT SKILLS
            # --------------------------------------------

            selected_skills = extract_skills(
                file_path
            )


        except Exception:

            return """
            <script>
                alert(
                    "Unable to read the resume. "
                    + "Please upload a valid "
                    + "PDF or DOCX file."
                );
                window.history.back();
            </script>
            """


        finally:

            # --------------------------------------------
            # DELETE RESUME IMMEDIATELY
            # --------------------------------------------
            #
            # The resume is only needed while
            # extracting skills.
            #
            # After extraction it is permanently
            # removed from the uploads folder.
            # --------------------------------------------

            if os.path.exists(
                file_path
            ):

                try:

                    os.remove(
                        file_path
                    )

                except OSError:

                    pass


    # ==================================================
    # MANUAL SKILL ANALYSIS
    # ==================================================

    else:

        selected_skills = (
            request.form.getlist(
                "skills"
            )
        )


    # ==================================================
    # SKILL VALIDATION
    # ==================================================

    if not selected_skills:

        return """
        <script>
            alert(
                "No skills were detected. "
                + "Please select at least one skill "
                + "or upload a resume containing "
                + "recognizable skills."
            );
            window.history.back();
        </script>
        """


    # ==================================================
    # GET REQUIRED SKILLS
    # ==================================================

    required_skills = get_required_skills(
        dream_job
    )


    if not required_skills:

        return """
        <script>
            alert(
                "Skill information is not available "
                + "for the selected Dream Job."
            );
            window.history.back();
        </script>
        """


    # ==================================================
    # V7.5 RESUME VS JOB MATCHING
    # ==================================================

    if resume_uploaded:

        (
            matched_resume_skills,
            missing_resume_skills,
            additional_resume_skills
        ) = match_resume_to_job(
            selected_skills,
            required_skills
        )


        resume_match_score = (
            calculate_resume_match_score(
                matched_resume_skills,
                required_skills
            )
        )


        # ----------------------------------------------
        # RESUME MATCHING BECOMES NORMAL ANALYSIS
        # ----------------------------------------------

        found_skills = (
            matched_resume_skills
        )

        missing_skills = (
            missing_resume_skills
        )


    else:

        # ----------------------------------------------
        # EXISTING MANUAL SKILL ANALYSIS
        # ----------------------------------------------

        found_skills, missing_skills = analyze(
            selected_skills,
            required_skills
        )


    # ==================================================
    # V5 WEIGHTED READINESS SCORE
    # ==================================================

    percentage = calculate_weighted_score(
        found_skills,
        required_skills
    )


    # ==================================================
    # V6 MARKET PRIORITY
    # ==================================================

    market_skills = prioritize_missing_skills(
        missing_skills
    )


    # ==================================================
    # V7 LIVE ADZUNA MARKET INSIGHTS
    # ==================================================

    try:

        market_insights = get_market_insights(
            dream_job,
            country="in"
        )

    except Exception:

        market_insights = {

            "success": False,

            "message": (
                "Live market information "
                "is temporarily unavailable."
            ),

            "total_jobs": 0,

            "top_companies": [],

            "top_locations": [],

            "salary_min": None,

            "salary_max": None,

            "market_level": "Unavailable"

        }


    # ==================================================
    # SKILL COUNTS
    # ==================================================

    selected_count = len(
        selected_skills
    )

    found_count = len(
        found_skills
    )

    missing_count = len(
        missing_skills
    )


    # ==================================================
    # PIE CHART
    # ==================================================

    labels = [
        "Found Skills",
        "Missing Skills"
    ]

    values = [
        found_count,
        missing_count
    ]


    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(
                    colors=[
                        "green",
                        "red"
                    ]
                )
            )
        ]
    )


    fig.update_layout(
        title="Skill Distribution"
    )


    graph = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn"
    )


    # ==================================================
    # RECOMMENDATION
    # ==================================================

    if percentage >= 80:

        recommendation = (
            "Excellent! You are close "
            "to being job-ready."
        )

    elif percentage >= 60:

        recommendation = (
            "Good progress! Learn the "
            "missing skills to improve."
        )

    else:

        recommendation = (
            "You are at the beginner level. "
            "Keep learning consistently."
        )


    # ==================================================
    # STATUS
    # ==================================================

    if percentage >= 90:

        status = "🏆 Job Ready"

    elif percentage >= 75:

        status = "🟢 Advanced"

    elif percentage >= 50:

        status = "🟡 Intermediate"

    else:

        status = "🔴 Beginner"


    # ==================================================
    # V7.4 ENHANCED INTELLIGENT LEARNING ROADMAP
    # ==================================================

    roadmap = []

    week = 1


    # ==================================================
    # ROADMAP DETAILS
    # ==================================================

    ROADMAP_DETAILS = {

        "SQL": {

            "learn": (
                "Learn SQL fundamentals, "
                "SELECT queries, filtering, "
                "joins, grouping and subqueries."
            ),

            "practice": (
                "Practice SQL queries using "
                "real-world datasets."
            ),

            "project": (
                "Build a small SQL data-analysis "
                "project with multiple tables."
            )

        },


        "Python": {

            "learn": (
                "Strengthen Python fundamentals, "
                "functions, data structures, "
                "modules and error handling."
            ),

            "practice": (
                "Solve Python programming and "
                "problem-solving exercises."
            ),

            "project": (
                "Build a Python application using "
                "real-world data."
            )

        },


        "Apache Spark": {

            "learn": (
                "Learn Apache Spark fundamentals, "
                "RDDs, DataFrames and transformations."
            ),

            "practice": (
                "Practice processing large datasets "
                "using Spark DataFrames."
            ),

            "project": (
                "Build a mini big-data processing "
                "project using Apache Spark."
            )

        },


        "Hadoop": {

            "learn": (
                "Learn Hadoop architecture, HDFS, "
                "MapReduce and distributed storage."
            ),

            "practice": (
                "Practice basic Hadoop "
                "data-processing operations."
            ),

            "project": (
                "Build a small distributed-data "
                "processing project."
            )

        },


        "Airflow": {

            "learn": (
                "Learn Apache Airflow DAGs, tasks, "
                "operators and scheduling."
            ),

            "practice": (
                "Create and schedule simple "
                "data pipelines."
            ),

            "project": (
                "Build a mini ETL pipeline "
                "using Airflow."
            )

        },


        "Flask": {

            "learn": (
                "Learn Flask routing, templates, "
                "forms and backend development."
            ),

            "practice": (
                "Create small Flask routes and "
                "form-handling applications."
            ),

            "project": (
                "Build a Flask web application "
                "with database integration."
            )

        },


        "Git": {

            "learn": (
                "Learn Git repositories, branches, "
                "commits, merging and GitHub."
            ),

            "practice": (
                "Practice Git using your own "
                "development projects."
            ),

            "project": (
                "Create and maintain a professional "
                "GitHub project repository."
            )

        },


        "OOP": {

            "learn": (
                "Learn classes, objects, inheritance, "
                "polymorphism and encapsulation."
            ),

            "practice": (
                "Solve object-oriented "
                "programming problems."
            ),

            "project": (
                "Build a small object-oriented "
                "application."
            )

        },


        "Pandas": {

            "learn": (
                "Learn Pandas Series, DataFrames, "
                "filtering, grouping and data cleaning."
            ),

            "practice": (
                "Practice data cleaning and "
                "analysis using datasets."
            ),

            "project": (
                "Build a data-analysis project "
                "using Pandas."
            )

        },


        "NumPy": {

            "learn": (
                "Learn NumPy arrays, indexing, "
                "vectorization and numerical operations."
            ),

            "practice": (
                "Practice numerical data-processing "
                "problems."
            ),

            "project": (
                "Build a numerical-analysis "
                "project using NumPy."
            )

        },


        "Machine Learning": {

            "learn": (
                "Learn supervised and unsupervised "
                "learning, model training and evaluation."
            ),

            "practice": (
                "Train and evaluate machine-learning "
                "models using datasets."
            ),

            "project": (
                "Build a machine-learning "
                "prediction project."
            )

        },


        "Deep Learning": {

            "learn": (
                "Learn neural networks, deep-learning "
                "architectures and model training."
            ),

            "practice": (
                "Train simple neural-network "
                "models using datasets."
            ),

            "project": (
                "Build a deep-learning project "
                "for a real-world problem."
            )

        },


        "TensorFlow": {

            "learn": (
                "Learn TensorFlow fundamentals, "
                "tensors, models and training."
            ),

            "practice": (
                "Build and train simple "
                "TensorFlow models."
            ),

            "project": (
                "Create a TensorFlow-based "
                "machine-learning project."
            )

        },


        "Java": {

            "learn": (
                "Learn Java syntax, collections, "
                "exception handling and OOP."
            ),

            "practice": (
                "Solve Java programming problems."
            ),

            "project": (
                "Build a Java application using "
                "object-oriented principles."
            )

        },


        "Spring Boot": {

            "learn": (
                "Learn Spring Boot architecture, "
                "REST controllers and dependency injection."
            ),

            "practice": (
                "Create REST APIs using "
                "Spring Boot."
            ),

            "project": (
                "Build a Spring Boot backend "
                "application."
            )

        },


        "HTML": {

            "learn": (
                "Learn HTML structure, forms, "
                "semantic elements and accessibility."
            ),

            "practice": (
                "Create responsive web pages."
            ),

            "project": (
                "Build a professional "
                "portfolio page."
            )

        },


        "CSS": {

            "learn": (
                "Learn CSS layouts, Flexbox, Grid, "
                "responsive design and styling."
            ),

            "practice": (
                "Recreate modern web-page layouts."
            ),

            "project": (
                "Build a responsive website."
            )

        },


        "JavaScript": {

            "learn": (
                "Learn JavaScript fundamentals, "
                "DOM manipulation and events."
            ),

            "practice": (
                "Create interactive web components."
            ),

            "project": (
                "Build an interactive JavaScript "
                "web application."
            )

        }

    }


    # ==================================================
    # CREATE PERSONALIZED ROADMAP
    # ==================================================

    for item in market_skills:

        skill = item["skill"]

        demand = item["demand"]

        priority = item["priority"]


        details = ROADMAP_DETAILS.get(
            skill
        )


        if not details:

            learning_step = ROADMAP.get(
                skill,
                (
                    f"Learn {skill} fundamentals "
                    "and practice with hands-on exercises."
                )
            )


            details = {

                "learn": learning_step,

                "practice": (
                    f"Practice {skill} using "
                    "small hands-on exercises."
                ),

                "project": (
                    f"Build a mini project using "
                    f"{skill}."
                )

            }


        roadmap.append({

            "week": week,

            "skill": skill,

            "demand": demand,

            "priority": priority,

            "learn": details["learn"],

            "practice": details["practice"],

            "project": details["project"]

        })


        week += 1


    # ==================================================
    # FINAL PORTFOLIO PROJECT
    # ==================================================

    if market_skills:

        highest_priority_skills = [

            item["skill"]

            for item in market_skills[:3]

        ]


        roadmap.append({

            "week": week,

            "skill": "Final Portfolio Project",

            "demand": "Career Focus",

            "priority": 5,

            "learn": (
                "Combine the important skills "
                "you learned during the roadmap."
            ),

            "practice": (
                "Develop the project step-by-step "
                "and test each component."
            ),

            "project": (
                "Build a portfolio-ready project "
                "using: "
                + ", ".join(
                    highest_priority_skills
                )
            )

        })


    else:

        roadmap.append({

            "week": 1,

            "skill": "Advanced Portfolio Project",

            "demand": "Career Focus",

            "priority": 5,

            "learn": (
                "Strengthen your existing skills "
                "through an advanced project."
            ),

            "practice": (
                "Practice solving real-world "
                "development problems."
            ),

            "project": (
                "Build and publish an advanced "
                "portfolio project."
            )

        })


    # ==================================================
    # SAVE REPORT
    # ==================================================

    save_report(
        dream_job,
        percentage,
        status,
        found_skills,
        missing_skills
    )


    # ==================================================
    # SAVE LAST REPORT
    # ==================================================

    app.config["LAST_REPORT"] = {

        "dream_job":
            dream_job,

        "percentage":
            percentage,

        "status":
            status,

        "found_skills":
            found_skills,

        "missing_skills":
            missing_skills,

        "recommendation":
            recommendation,

        "roadmap":
            roadmap

    }


    # ==================================================
    # DISPLAY RESULT
    # ==================================================

    return render_template(

        "analysis.html",

        dream_job=dream_job,

        skills=selected_skills,

        found_skills=found_skills,

        missing_skills=missing_skills,

        market_skills=market_skills,

        market_insights=market_insights,

        percentage=percentage,

        recommendation=recommendation,

        selected_count=selected_count,

        found_count=found_count,

        missing_count=missing_count,

        status=status,

        graph=graph,

        roadmap=roadmap,


        # ==============================================
        # V7.5 RESUME MATCHING DATA
        # ==============================================

        resume_uploaded=resume_uploaded,

        resume_match_score=resume_match_score,

        matched_resume_skills=matched_resume_skills,

        missing_resume_skills=missing_resume_skills,

        additional_resume_skills=additional_resume_skills

    )


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/dashboard")
def dashboard():

    reports = get_reports()

    total_reports = len(
        reports
    )


    if total_reports > 0:

        average_score = int(

            sum(
                report[2]
                for report in reports
            )
            / total_reports

        )


        highest_score = max(

            report[2]
            for report in reports

        )


    else:

        average_score = 0

        highest_score = 0


    unique_jobs, most_analyzed_job = (
        get_dashboard_stats()
    )


    return render_template(

        "dashboard.html",

        reports=reports,

        total_reports=total_reports,

        average_score=average_score,

        highest_score=highest_score,

        unique_jobs=unique_jobs,

        most_analyzed_job=most_analyzed_job

    )


# ==================================================
# DOWNLOAD PDF
# ==================================================

@app.route("/download-report")
def download_report():

    report = app.config.get(
        "LAST_REPORT"
    )


    if not report:

        return """
        <script>

            alert(
                "No report available. "
                + "Please analyze your "
                + "skills first."
            );

            window.location.href = "/";

        </script>
        """


    filename = (
        "JMS_Analysis_Report.pdf"
    )


    generate_pdf(

        filename,

        report["dream_job"],

        report["percentage"],

        report["status"],

        report["found_skills"],

        report["missing_skills"],

        report["recommendation"],

        report["roadmap"]

    )


    return send_file(

        filename,

        as_attachment=True

    )


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    debug_mode = (
        os.getenv(
            "FLASK_DEBUG",
            "1"
        ) == "1"
    )

    app.run(
        debug=debug_mode
    )