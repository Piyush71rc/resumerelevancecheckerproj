# db.py
import sqlite3

DB_NAME = "evaluations.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        candidate_name TEXT,
        score REAL,
        verdict TEXT,
        matched_skills TEXT,
        missing_skills TEXT
    )
    """)
    
    conn.commit()
    conn.close()

def insert_evaluation(job_title, candidate_name, score, verdict, matched_skills, missing_skills):
    matched_str = ", ".join(matched_skills) if isinstance(matched_skills, list) else str(matched_skills)
    missing_str = ", ".join(missing_skills) if isinstance(missing_skills, list) else str(missing_skills)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO evaluations(job_title, candidate_name, score, verdict, matched_skills, missing_skills)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (job_title, candidate_name, score, verdict, matched_str, missing_str))
    conn.commit()
    conn.close()



def fetch_all_evaluations():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM evaluations")
    rows = cursor.fetchall()
    conn.close()
    return rows

def clear_evaluations():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM evaluations")
    conn.commit()
    conn.close()