from database import get_connection
from student_wellness.mood_entry import MoodEntry

class MoodRepository:
    #Saves mood entry to database
    def save(self, mood_entry):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO mood_entries (student_id, rating, notes, timestamp) VALUES (?, ?, ?, ?)',
            (mood_entry.student_id, mood_entry.rating, mood_entry.notes, mood_entry.timestamp)
        )
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return entry_id
    
    def find_by_student_id(self, student_id):
        # get all entries for this student
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM mood_entries WHERE student_id = ? ORDER BY timestamp DESC', (student_id,))
        rows = cursor.fetchall()
        conn.close()
        # make list of MoodEntry objects
        entries = []
        for row in rows:
            entry = MoodEntry(row['student_id'], row['rating'], row['notes'], row['timestamp'], row['id'])
            entries.append(entry)
        return entries
    
    def find_recent(self, student_id, days=7):
        # get recent entries for pattern detection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM mood_entries WHERE student_id = ? ORDER BY timestamp DESC LIMIT ?', (student_id, days))
        rows = cursor.fetchall()
        conn.close()
        # convert to MoodEntry objects
        entries = []
        for row in rows:
            entry = MoodEntry(row['student_id'], row['rating'], row['notes'], row['timestamp'], row['id'])
            entries.append(entry)
        return entries