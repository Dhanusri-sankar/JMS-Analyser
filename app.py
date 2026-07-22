import plotly.express as px
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/user-type")
def user_type():
    return render_template("user_type.html")


@app.route("/dream-job")
def dream_job():
    return render_template("dream_job.html")


@app.route("/skills")
def skills():
    return render_template("skills.html")


@app.route("/analysis", methods=["POST"])
def analysis():

    skills = request.form.getlist("skills")

    required_skills = [
        "Python",
        "SQL",
        "Excel",
        "Pandas",
        "NumPy"
    ]

    found_skills = []
    missing_skills = []

    for skill in required_skills:
        if skill in skills:
            found_skills.append(skill)
        else:
            missing_skills.append(skill)

    total_required = len(required_skills)
    total_found = len(found_skills)

    percentage = int((total_found / total_required) * 100)

    selected_count = len(skills)
    found_count = len(found_skills)
    missing_count = len(missing_skills)

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

    if percentage >= 80:
       recommendation = "Excellent! You are close to being job-ready."

    elif percentage >= 60:
       recommendation = "Good progress! Learn the missing skills to improve."

    else:
      recommendation = "You are at the beginner level. Keep learning consistently."

    if percentage >= 90:
      status = "🏆 Job Ready"

    elif percentage >= 75:
       status = "🟢 Advanced"

    elif percentage >= 50:
       status = "🟡 Intermediate"

    else:
       status = "🔴 Beginner"

    roadmap = []

    if "Python" in missing_skills:
       roadmap.append("Week 1: Learn Python Basics")

    if "SQL" in missing_skills:
       roadmap.append("Week 2: Learn SQL Basics")

    if "Excel" in missing_skills:
        roadmap.append("Week 3: Practice Excel for Data Analysis")

    if "Pandas" in missing_skills:
       roadmap.append("Week 4: Learn Pandas")

    if "NumPy" in missing_skills:
       roadmap.append("Week 5: Learn NumPy")

    roadmap.append("Week 6: Build a Mini Project")
    
    return render_template(
        "analysis.html",
        skills=skills,
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


if __name__ == "__main__":
    app.run(debug=True)