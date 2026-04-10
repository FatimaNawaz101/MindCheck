from student_wellness.mood_entry import MoodEntry
from student_wellness.mood_repository import MoodRepository

class MoodTrackingService:
    def __init__(self):
        self.repository = MoodRepository()
    
    def validate_mood_entry(self, rating, notes):
        #Step 1:check if rating exists
        if not rating:
            return "Rating is required"
        
        #Step 2: check if rating is in valid range
        if rating < 1 or rating > 10:
            return "Rating must be between 1 and 10"
        return None
    
    def save_mood_entry(self, student_id, rating, notes):
        # validate the input first
        error = self.validate_mood_entry(rating, notes)
        if error:
            return {'success': False, 'message': error}
        
        # create new mood entry
        entry = MoodEntry(student_id, rating, notes)
        self.repository.save(entry)
        # check if student needs counseling
        alert = self.check_mood_patterns(student_id)
        
        # return result
        result = {
            'success': True,
            'message': 'Mood logged successfully',
            'counseling_alert': alert
        }
        return result
    
    # get recent entries to check pattern
    def check_mood_patterns(self, student_id):
        recent_entries = self.repository.find_recent(student_id, 7)
        return self.detect_low_mood_pattern(recent_entries)
    
     # count consecutive days with low mood (rating below 4)
    def detect_low_mood_pattern(self, entries):
        consecutive_low = 0
        for entry in entries:
            if entry.is_low_mood():
                consecutive_low = consecutive_low + 1
                if consecutive_low >= 5:
                    return True
            else:
                consecutive_low = 0
        return False
    
    # get all mood entries for student
    def get_mood_history(self, student_id):
        return self.repository.find_by_student_id(student_id)