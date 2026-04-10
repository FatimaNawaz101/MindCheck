from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from database import init_database
from student_wellness.mood_tracking_service import MoodTrackingService

app = Flask(__name__)
CORS(app)

# initialize database when app starts
init_database()

# create service instance
mood_service = MoodTrackingService()

# Routes to serve HTML pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log-mood')
def log_mood_page():
    return render_template('log-mood.html')

@app.route('/mood-confirmation')
def mood_confirmation_page():
    return render_template('mood-confirmation.html')

@app.route('/resources')
def resources_page():
    return render_template('resources.html')

@app.route('/appointments')
def appointments_page():
    return render_template('appointments.html')

@app.route('/admin')
def admin_login_page():
    return render_template('admin-login.html')

@app.route('/admin/dashboard')
def admin_dashboard_page():
    return render_template('admin-dashboard.html')

@app.route('/admin/report-preview')
def admin_report_preview_page():
    return render_template('admin-report-preview.html')

@app.route('/admin/report', methods=['GET'])
def generate_admin_report():
    # fake/demo data for prototype
    report_data = {
        'success': True,
        'average_mood': 6.4,
        'active_students': 132,
        'check_ins': 320,
        'appointment_requests': 18,
        'stress_periods': ['Midterm Week', 'Final Exam Period']
    }

    return jsonify(report_data), 200

@app.route('/api/mood-entries', methods=['POST'])
def log_mood():
    # get data from request
    data = request.json
    student_id = data.get('student_id')
    rating = data.get('rating')
    notes = data.get('notes', '') #try to get notes from data but if student doesnt pass anything then set it to empty string
    
    # save mood entry using service
    result = mood_service.save_mood_entry(student_id, rating, notes)

   #convert python dictionary to JSON format then check status code 
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route('/api/mood-history/<int:student_id>', methods=['GET'])
def get_history(student_id):
    # get all entries for this student
    entries = mood_service.get_mood_history(student_id)
    # convert to dictionaries for JSON
    entry_data = []
    for e in entries:
        entry_data.append(e.to_dict())
    
    return jsonify({'success': True, 'entries': entry_data}), 200

if __name__ == '__main__':
    print("MindCheck Backend Server")
    print("Running on http://localhost:5000")
    app.run(debug=True, port=5000)