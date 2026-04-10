from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from database import init_database
from student_wellness.mood_tracking_service import MoodTrackingService
from student_wellness.counselor_service import CounselorService

app = Flask(__name__)
app.secret_key = 'mindcheck-dev-key'
CORS(app)

# initialize database when app starts
init_database()

# create service instances
mood_service = MoodTrackingService()
counselor_service = CounselorService()

# ─── Student Routes ───────────────────────────────────────────────────────────

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

# ─── Admin Routes ─────────────────────────────────────────────────────────────

@app.route('/admin')
def admin_login_page():
    return render_template('admin-login.html')

@app.route('/admin/dashboard')
def admin_dashboard_page():
    return render_template('admin-dashboard.html')

@app.route('/admin/report-preview')
def admin_report_preview_page():
    period = request.args.get('period', 'semester')
    format_type = request.args.get('format', 'pdf')
    report_type = request.args.get('type', 'summary')
    report_data = {
        'average_mood': 6.4,
        'active_students': 132,
        'check_ins': 320,
        'appointment_requests': 18,
        'stress_periods': ['Midterm Week', 'Final Exam Period']
    }
    return render_template(
        'admin-report-preview.html',
        period=period,
        format=format_type,
        report_type=report_type,
        report=report_data
    )

# ─── Mood API Routes ──────────────────────────────────────────────────────────

@app.route('/api/mood-entries', methods=['POST'])
def log_mood():
    data = request.json
    student_id = data.get('student_id')
    rating = data.get('rating')
    notes = data.get('notes', '')
    result = mood_service.save_mood_entry(student_id, rating, notes)
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route('/api/mood-history/<int:student_id>', methods=['GET'])
def get_history(student_id):
    entries = mood_service.get_mood_history(student_id)
    entry_data = [e.to_dict() for e in entries]
    return jsonify({'success': True, 'entries': entry_data}), 200

# ─── Counselor Routes (Sheldon Gonsalves) ────────────────────────────────────

@app.route('/counselor/login', methods=['GET', 'POST'])
def counselor_login_page():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        counselor = counselor_service.login(email, password)
        if counselor:
            session['counselor_id'] = counselor['id']
            session['counselor_name'] = counselor['name']
            return redirect(url_for('counselor_dashboard_page'))
        else:
            error = 'Invalid email or password.'
    return render_template('counselor-login.html', error=error)

@app.route('/counselor/logout')
def counselor_logout():
    session.clear()
    return redirect(url_for('counselor_login_page'))

@app.route('/counselor/dashboard')
def counselor_dashboard_page():
    if 'counselor_id' not in session:
        return redirect(url_for('counselor_login_page'))
    data = counselor_service.get_dashboard_data(session['counselor_id'])
    return render_template('counselor-dashboard.html',
        counselor_name=session['counselor_name'],
        overall_avg=data['overall_avg'],
        pending_count=data['pending_count'],
        at_risk=data['at_risk'],
        mood_data=data['mood_data'],
        todays_appts=data['todays_appts']
    )

@app.route('/counselor/appointments')
def counselor_appointments_page():
    if 'counselor_id' not in session:
        return redirect(url_for('counselor_login_page'))
    pending, confirmed = counselor_service.get_appointments(session['counselor_id'])
    return render_template('counselor-appointments.html',
        counselor_name=session['counselor_name'],
        pending=pending,
        confirmed=confirmed
    )

@app.route('/counselor/appointments/action/<int:appt_id>', methods=['POST'])
def counselor_appointment_action(appt_id):
    if 'counselor_id' not in session:
        return redirect(url_for('counselor_login_page'))
    action = request.form.get('action')
    new_date = request.form.get('new_date')
    new_time = request.form.get('new_time')
    counselor_service.update_appointment(appt_id, action, new_date, new_time)
    return redirect(url_for('counselor_appointments_page'))

@app.route('/counselor/resources')
def counselor_resources_page():
    if 'counselor_id' not in session:
        return redirect(url_for('counselor_login_page'))
    live, drafts = counselor_service.get_resources(session['counselor_id'])
    return render_template('counselor-resources.html',
        counselor_name=session['counselor_name'],
        live_resources=live,
        draft_resources=drafts
    )

@app.route('/counselor/resources/add', methods=['POST'])
def counselor_add_resource():
    if 'counselor_id' not in session:
        return redirect(url_for('counselor_login_page'))
    counselor_service.add_resource(
        counselor_id=session['counselor_id'],
        title=request.form.get('title'),
        category=request.form.get('category'),
        description=request.form.get('description'),
        link=request.form.get('link', ''),
        publish=request.form.get('action') == 'publish'
    )
    return redirect(url_for('counselor_resources_page'))

@app.route('/counselor/resources/unpublish/<int:res_id>', methods=['POST'])
def counselor_unpublish_resource(res_id):
    if 'counselor_id' not in session:
        return redirect(url_for('counselor_login_page'))
    counselor_service.unpublish_resource(res_id)
    return redirect(url_for('counselor_resources_page'))

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("MindCheck Backend Server")
    print("Running on http://localhost:5000")
    app.run(debug=True, port=5000)