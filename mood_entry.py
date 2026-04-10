from datetime import datetime

 #Represents a single mood log entry
class MoodEntry:
    def __init__(self, student_id, rating, notes, timestamp=None, entry_id=None):
        self.id = entry_id
        self.student_id = student_id
        self.rating = rating
        self.notes = notes
        self.timestamp = timestamp if timestamp else datetime.now().isoformat()
    
     #Checks if mood rating is below 4
    def is_low_mood(self):
        return self.rating < 4
    
     #Get the mood rating value
    def get_rating(self):
        return self.rating
    
    #Convert to dictionary for JSON
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'rating': self.rating,
            'notes': self.notes,
            'timestamp': self.timestamp
        }