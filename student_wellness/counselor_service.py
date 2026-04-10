# Counselor module - Sheldon Gonsalves
import sqlite3

DATABASE = 'mindcheck.db'

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

class CounselorService:
    def __init__(self):
        pass

    # check login credentials, return counselor or None
    def login(self, email, password):
        conn = get_connection()
        counselor = conn.execute(
            "SELECT * FROM counselors WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
        conn.close()
        return counselor

    # get all data needed for the dashboard
    def get_dashboard_data(self, counselor_id):
        conn = get_connection()

        # daily mood averages for the week
        mood_rows = conn.execute("""
            SELECT log_date, ROUND(AVG(mood_score), 1) as avg_mood
            FROM mood_logs
            WHERE log_date BETWEEN '2026-03-09' AND '2026-03-13'
            GROUP BY log_date
            ORDER BY log_date
        """).fetchall()

        # overall campus average
        overall = conn.execute("""
            SELECT ROUND(AVG(mood_score), 1) as avg FROM mood_logs
            WHERE log_date BETWEEN '2026-03-09' AND '2026-03-13'
        """).fetchone()

        # count pending appointments
        pending_count = conn.execute(
            "SELECT COUNT(*) as cnt FROM appointments WHERE counselor_id=? AND status='Pending'",
            (counselor_id,)
        ).fetchone()

        # at-risk students: mood 3.2 or below for 3+ days
        at_risk = conn.execute("""
            SELECT student_anon_id, ROUND(AVG(mood_score), 1) as avg_mood, COUNT(*) as days
            FROM mood_logs
            WHERE mood_score <= 3.2
            GROUP BY student_anon_id
            HAVING days >= 3
            ORDER BY avg_mood ASC
        """).fetchall()

        # today's confirmed appointments
        todays_appts = conn.execute("""
            SELECT * FROM appointments
            WHERE counselor_id=? AND appt_date='2026-03-11' AND status='Confirmed'
            ORDER BY appt_time
        """, (counselor_id,)).fetchall()

        conn.close()

        # label days of the week
        day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        mood_data = []
        for i, row in enumerate(mood_rows):
            mood_data.append({
                'day': day_labels[i] if i < len(day_labels) else row['log_date'],
                'avg': row['avg_mood']
            })

        return {
            'overall_avg': overall['avg'] if overall['avg'] else 0,
            'pending_count': pending_count['cnt'],
            'at_risk': [dict(r) for r in at_risk],
            'mood_data': mood_data,
            'todays_appts': [dict(a) for a in todays_appts]
        }

    # get pending and confirmed appointments separately
    def get_appointments(self, counselor_id):
        conn = get_connection()
        pending = conn.execute(
            "SELECT * FROM appointments WHERE counselor_id=? AND status='Pending' ORDER BY appt_date",
            (counselor_id,)
        ).fetchall()
        confirmed = conn.execute(
            "SELECT * FROM appointments WHERE counselor_id=? AND status='Confirmed' ORDER BY appt_date",
            (counselor_id,)
        ).fetchall()
        conn.close()
        return [dict(a) for a in pending], [dict(a) for a in confirmed]

    # approve, decline, or reschedule an appointment
    def update_appointment(self, appt_id, action, new_date=None, new_time=None):
        conn = get_connection()
        if action == 'approve':
            conn.execute("UPDATE appointments SET status='Confirmed' WHERE id=?", (appt_id,))
        elif action == 'decline':
            conn.execute("UPDATE appointments SET status='Declined' WHERE id=?", (appt_id,))
        elif action == 'reschedule' and new_date and new_time:
            conn.execute(
                "UPDATE appointments SET appt_date=?, appt_time=?, status='Confirmed' WHERE id=?",
                (new_date, new_time, appt_id)
            )
        conn.commit()
        conn.close()

    # get live and draft resources
    def get_resources(self, counselor_id):
        conn = get_connection()
        live = conn.execute(
            "SELECT * FROM resources WHERE counselor_id=? AND status='Live'", (counselor_id,)
        ).fetchall()
        drafts = conn.execute(
            "SELECT * FROM resources WHERE counselor_id=? AND status='Draft'", (counselor_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in live], [dict(r) for r in drafts]

    # add a new resource
    def add_resource(self, counselor_id, title, category, description, link, publish):
        status = 'Live' if publish else 'Draft'
        conn = get_connection()
        conn.execute(
            "INSERT INTO resources (title, category, description, link, status, counselor_id) VALUES (?,?,?,?,?,?)",
            (title, category, description, link, status, counselor_id)
        )
        conn.commit()
        conn.close()

    # unpublish a resource (move to draft)
    def unpublish_resource(self, resource_id):
        conn = get_connection()
        conn.execute("UPDATE resources SET status='Draft' WHERE id=?", (resource_id,))
        conn.commit()
        conn.close()