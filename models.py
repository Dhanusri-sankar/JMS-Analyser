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