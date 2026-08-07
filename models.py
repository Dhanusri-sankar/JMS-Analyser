from database import connect_db


# ---------------- CREATE REPORT TABLE ---------------- #

def create_tables():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        dream_job TEXT,

        score INTEGER,

        status TEXT,

        found_skills TEXT,

        missing_skills TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- SAVE REPORT ---------------- #

def save_report(
    dream_job,
    score,
    status,
    found_skills,
    missing_skills
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO reports(
        dream_job,
        score,
        status,
        found_skills,
        missing_skills
    )
    VALUES (?, ?, ?, ?, ?)
    """, (
        dream_job,
        score,
        status,
        ",".join(found_skills),
        ",".join(missing_skills)
    ))

    conn.commit()
    conn.close()


# ---------------- GET REPORTS ---------------- #

def get_reports():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        dream_job,
        score,
        status,
        found_skills,
        missing_skills
    FROM reports
    ORDER BY id DESC
    """)

    reports = cursor.fetchall()

    conn.close()

    return reports

def search_reports(keyword):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        id,
        dream_job,
        score,
        status,
        found_skills,
        missing_skills
    FROM reports
    WHERE dream_job LIKE ?
    ORDER BY id DESC
    """, ('%' + keyword + '%',))

    reports = cursor.fetchall()

    conn.close()

    return reports

def delete_report(report_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM reports WHERE id = ?",
        (report_id,)
    )

    conn.commit()
    conn.close()
def get_dashboard_stats():

    conn = connect_db()
    cursor = conn.cursor()

    # Total unique dream jobs analyzed
    cursor.execute("""
        SELECT COUNT(DISTINCT dream_job)
        FROM reports
    """)
    unique_jobs = cursor.fetchone()[0]

    # Most frequently analyzed dream job
    cursor.execute("""
        SELECT dream_job, COUNT(*) AS total
        FROM reports
        GROUP BY dream_job
        ORDER BY total DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    if result:
        most_analyzed_job = result[0]
    else:
        most_analyzed_job = "No Data"

    conn.close()

    return unique_jobs, most_analyzed_job