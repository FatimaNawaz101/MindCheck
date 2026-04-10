import sqlite3

DATABASE = 'mindcheck.db'

#Get database connection
def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

#Create mood_entries table if it doesn't exist
def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            notes TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    # Counselor tables (Sheldon Gonsalves)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS counselors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            counselor_id INTEGER NOT NULL,
            appt_date TEXT NOT NULL,
            appt_time TEXT NOT NULL,
            concern TEXT,
            status TEXT DEFAULT 'Pending',
            session_number INTEGER DEFAULT 1
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            link TEXT,
            status TEXT DEFAULT 'Live',
            counselor_id INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_anon_id TEXT NOT NULL,
            mood_score REAL NOT NULL,
            log_date TEXT NOT NULL
        )
    ''')

    # seed counselor account
    cursor.execute("SELECT COUNT(*) FROM counselors")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO counselors (name, email, password) VALUES (?, ?, ?)",
            ("Dr. Sheldon Gonsalves", "sheldon@mindcheck.edu", "counselor123")
        )

    # seed appointments
    cursor.execute("SELECT COUNT(*) FROM appointments")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO appointments (student_name, counselor_id, appt_date, appt_time, concern, status, session_number) VALUES (?,?,?,?,?,?,?)",
            [
                ("Fatima N.",  1, "2026-03-11", "2:00 PM",  "Feeling overwhelmed with coursework.", "Confirmed", 3),
                ("Marcus T.",  1, "2026-03-11", "3:30 PM",  "General anxiety and sleep issues.",    "Confirmed", 1),
                ("Fatima N.",  1, "2026-03-14", "10:30 AM", "General wellness check-in.",           "Pending",   4),
                ("Marcus T.",  1, "2026-03-16", "1:00 PM",  "Trouble sleeping and feeling anxious.","Pending",   2),
                ("Priya S.",   1, "2026-03-18", "3:00 PM",  "Academic stress.",                     "Confirmed", 1),
            ]
        )

    # seed mood logs for dashboard charts
    cursor.execute("SELECT COUNT(*) FROM mood_logs")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO mood_logs (student_anon_id, mood_score, log_date) VALUES (?,?,?)",
            [
                ("#1042", 6.5, "2026-03-09"), ("#1087", 6.2, "2026-03-09"), ("#1156", 2.8, "2026-03-09"),
                ("#1042", 6.9, "2026-03-10"), ("#1087", 6.5, "2026-03-10"), ("#1156", 2.5, "2026-03-10"),
                ("#1042", 5.8, "2026-03-11"), ("#1087", 6.0, "2026-03-11"), ("#1156", 2.9, "2026-03-11"),
                ("#1042", 5.2, "2026-03-12"), ("#1087", 5.0, "2026-03-12"), ("#1156", 3.1, "2026-03-12"),
                ("#1042", 6.2, "2026-03-13"), ("#1087", 5.9, "2026-03-13"), ("#1156", 2.7, "2026-03-13"),
            ]
        )

    # seed resources
    cursor.execute("SELECT COUNT(*) FROM resources")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO resources (title, category, description, link, status, counselor_id) VALUES (?,?,?,?,?,?)",
            [
                ("5 Techniques to Manage Academic Stress", "Stress",         "Practical strategies to manage the pressures of student life.", "", "Live", 1),
                ("Understanding Anxiety and How to Cope",  "Anxiety",        "A guide to understanding anxiety and coping mechanisms.",       "", "Live", 1),
                ("Better Sleep Habits for Students",        "Sleep",          "Build a healthy sleep routine even during exam season.",        "", "Live", 1),
                ("Where to Get Immediate Help",             "Crisis Support", "Resources available 24/7 for immediate support.",              "", "Live", 1),
            ]
        )
    conn.commit()
    conn.close()
    print("Database initialized")