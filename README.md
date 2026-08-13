# 📊 JMS Analyzer

## Job Market Skill Analyzer

JMS Analyzer is a Flask-based web application designed to help students and job seekers understand the skills required for their dream job.

The application compares a user's current skills or resume with job requirements, analyzes market demand, identifies skill gaps, calculates job readiness, and provides a personalized learning roadmap.

---

## 🎯 Project Objective

Many students know which career they want to pursue but are unsure about the skills currently expected by employers.

JMS Analyzer helps solve this problem through:

**Current Skills → Job Requirements → Market Analysis → Skill Gap → Learning Roadmap**

The system helps users understand:

- What skills they already have
- What skills they are missing
- Which missing skills have higher market demand
- How ready they are for their selected job
- What they should learn next

---

## 🚀 Features

### 💼 Dream Job Selection

Users can select their target career/job role.

Examples include:

- Data Engineer
- Data Analyst
- Python Developer
- AI Engineer

### 🧠 Skill Analysis

Users can manually select the technical skills they already know.

The system compares the selected skills with the required skills for the chosen job.

### 📄 Resume Skill Detection

Users can upload a resume in:

- PDF
- DOCX

The application extracts recognizable technical skills from the resume.

### 🔍 Resume-to-Job Matching

The extracted resume skills are compared with the selected job requirements.

The system identifies:

- Matched Skills
- Missing Skills
- Additional Skills
- Resume Match Score

### 📈 Market Skill Demand

JMS Analyzer provides market-demand information for required skills.

Missing skills are prioritized according to their market importance.

### 📊 Job Readiness Score

The application calculates a readiness percentage based on the user's skills compared with the required job skills.

### 🗺️ Personalized Learning Roadmap

The system generates a structured roadmap to improve job readiness.

The roadmap can include:

- Skills to learn
- Market demand
- Priority
- Learning activities
- Practice activities
- Mini projects

### 📊 Market Insights

JMS Analyzer integrates the Adzuna Job Search API to retrieve current job-market information.

Market insights include:

- Total matching jobs
- Market level
- Top companies
- Top locations
- Job listings
- Salary information when available

### 📋 Analysis History

Previous analysis results can be stored and viewed through the History page.

### 📊 Dashboard

The Dashboard provides useful statistics about previous analyses and readiness results.

### 📥 Report Export

Users can export analysis information as:

- PDF
- CSV
- Excel

### 🔐 Resume Privacy

Uploaded resumes are processed temporarily for skill extraction.

After processing, the uploaded resume is automatically deleted.

The application also provides a privacy notice to guide users when uploading resumes.

---

## 🛠️ Technologies Used

### Backend

- Python
- Flask

### Frontend

- HTML
- CSS
- Jinja2 Templates

### Database & Data

- SQLite
- JSON

### API

- Adzuna Job Search API

### Resume Processing

- pdfplumber
- python-docx

### Data Visualization

- Plotly

### Report Generation

- ReportLab
- OpenPyXL

### Version Control

- Git
- GitHub

---

## 🏗️ Application Workflow

```text
Start
  ↓
Select User Type
  ↓
Select Dream Job
  ↓
Select Current Skills
      OR
Upload Resume
  ↓
Extract / Process Skills
  ↓
Compare With Job Requirements
  ↓
Calculate Readiness Score
  ↓
Analyze Market Demand
  ↓
Identify Missing Skills
  ↓
Prioritize Skill Gaps
  ↓
Generate Learning Roadmap
  ↓
View Analysis Report
  ↓
Save Analysis History
  ↓
Export Report