import os
import plotly.express as px
from flask import Flask, render_template, request, redirect, url_for
from flask import send_file
from pdf_generator import generate_pdf
from resume_parser import extract_skills
from analyzer import get_required_skills, analyze
from roadmap import ROADMAP
from models import (
    create_tables,
    save_report,
    get_reports,
    search_reports,
    delete_report
)

app = Flask(__name__)

# ---------------- DATABASE ---------------- #

create_tables()

# ---------------- UPLOAD FOLDER ---------------- #

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- USER TYPE ---------------- #

@app.route("/user-type")
def user_type():
    return render_template("user_type.html")


# ---------------- DREAM JOB ---------------- #

@app.route("/dream-job")
def dream_job():
    return render_template("dream_job.html")


# ---------------- SKILLS ---------------- #

@app.route("/skills", methods=["POST"])
def skills():

    dream_job = request.form.get("dream_job")

    required_skills = get_required_skills(dream_job)

    return render_template(
        "skills.html",
        dream_job=dream_job,
        required_skills=required_skills
    )


# ---------------- HISTORY ---------------- #

@app.route("/history")
def history():

    keyword = request.args.get("search")

    if keyword:
        reports = search_reports(keyword)
    else:
        reports = get_reports()

    return render_template(
        "history.html",
        reports=reports,
        keyword=keyword
    )

@app.route("/delete-report/<int:report_id>", methods=["POST"])
def delete_report_route(report_id):

    delete_report(report_id)

    return redirect(url_for("history"))

# ---------------- ANALYSIS ---------------- #

@app.route("/analysis", methods=["POST"])
def analysis():

    dream_job = request.form.get("dream_job")

    if not dream_job:
        return "Dream Job not selected."

    resume = request.files.get("resume")

    if resume and resume.filename != "":

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            resume.filename
        )

        resume.save(file_path)

        selected_skills = extract_skills(file_path)

    else:

        selected_skills = request.form.getlist("skills")

    required_skills = get_required_skills(dream_job)

    found_skills, missing_skills = analyze(
        selected_skills,
        required_skills
    )

    total_required = len(required_skills)
    total_found = len(found_skills)

    if total_required == 0:
        percentage = 0
    else:
        percentage = int((total_found / total_required) * 100)

    selected_count = len(selected_skills)
    found_count = len(found_skills)
    missing_count = len(missing_skills)

    # ---------------- PIE CHART ---------------- #

    labels = ["Found Skills", "Missing Skills"]
    values = [found_count, missing_count]

    fig = px.pie(
        names=labels,
        values=values,
        title="Skill Distribution",
        hole=0.4,
        color=labels,
        color_discrete_map={
            "Found Skills": "green",
            "Missing Skills": "red"
        }
    )

    graph = fig.to_html(full_html=False)

    # ---------------- RECOMMENDATION ---------------- #

    if percentage >= 80:
        recommendation = "Excellent! You are close to being job-ready."

    elif percentage >= 60:
        recommendation = "Good progress! Learn the missing skills to improve."

    else:
        recommendation = "You are at the beginner level. Keep learning consistently."

    # ---------------- STATUS ---------------- #

    if percentage >= 90:
        status = "🏆 Job Ready"

    elif percentage >= 75:
        status = "🟢 Advanced"

    elif percentage >= 50:
        status = "🟡 Intermediate"

    else:
        status = "🔴 Beginner"

    # ---------------- ROADMAP ---------------- #

    roadmap = []

    week = 1

    for skill in missing_skills:

        if skill in ROADMAP:
            roadmap.append(f"Week {week}: {ROADMAP[skill]}")
            week += 1

    roadmap.append(f"Week {week}: Build a Mini Project")

    # ---------------- SAVE REPORT ---------------- #

    save_report(
        dream_job,
        percentage,
        status,
        found_skills,
        missing_skills
    )

    app.config["LAST_REPORT"] = {
      "dream_job": dream_job,
      "percentage": percentage,
      "status": status,
      "found_skills": found_skills,
      "missing_skills": missing_skills,
      "recommendation": recommendation,
      "roadmap": roadmap
    }

    # ---------------- RESULT ---------------- #

    return render_template(
        "analysis.html",
        dream_job=dream_job,
        skills=selected_skills,
        found_skills=found_skills,
        missing_skills=missing_skills,
        percentage=percentage,
        recommendation=recommendation,
        selected_count=selected_count,
        found_count=found_count,
        missing_count=missing_count,
        status=status,
        graph=graph,
        roadmap=roadmap,
    )


@app.route("/dashboard")
def dashboard():

    reports = get_reports()

    total_reports = len(reports)

    if total_reports > 0:
        average_score = sum(report[2] for report in reports) // total_reports
        highest_score = max(report[2] for report in reports)
    else:
        average_score = 0
        highest_score = 0

    return render_template(
        "dashboard.html",
        reports=reports[:5],
        total_reports=total_reports,
        average_score=average_score,
        highest_score=highest_score
    )

# ---------------- RUN ---------------- #

@app.route("/download-report")
def download_report():

    report = app.config.get("LAST_REPORT")

    if not report:
        return "No report available. Please analyze your skills first."

    filename = "JMS_Analysis_Report.pdf"

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

    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)