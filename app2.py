# from flask import Flask, render_template, request, redirect
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reports.db'
# app.secret_key = 'secretkey'
# db = SQLAlchemy(app)

# # Models
# class Report(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     reference_id = db.Column(db.String(10), unique=True, nullable=False)
#     password = db.Column(db.String(20), nullable=False)
#     description = db.Column(db.Text, nullable=False)
#     location = db.Column(db.String(100))
#     time = db.Column(db.String(100))
#     category = db.Column(db.String(100))
#     accused = db.Column(db.String(100))
#     trackings = db.relationship('Tracking', backref='report', lazy=True)

# class Tracking(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
#     message = db.Column(db.String(200), nullable=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# # Create DB and insert dummy data
# with app.app_context():
#     db.create_all()
#     if Report.query.count() == 0:
#         dummy_data = [
#             ('REP123', 'pass123', 'Harassment case in college', 'Bangalore', '2024-05-12 14:00', 'Harassment', 'Mr. X'),
#             ('REP456', 'pass456', 'Cyberbullying on Instagram', 'Mysore', '2024-05-10 16:00', 'Cyberbullying', 'Unknown'),
#         ]
#         for ref, pwd, desc, loc, time, cat, acc in dummy_data:
#             report = Report(reference_id=ref, password=pwd, description=desc,
#                             location=loc, time=time, category=cat, accused=acc)
#             db.session.add(report)
#         db.session.commit()

# # Routes
# @app.route('/')
# def home():
#     return render_template('home.html')

# @app.route('/reporter', methods=['GET', 'POST'])
# def reporter():
#     error = ''
#     if request.method == 'POST':
#         ref = request.form['reference_id']
#         pwd = request.form['password']
#         report = Report.query.filter_by(reference_id=ref, password=pwd).first()
#         if report:
#             trackings = Tracking.query.filter_by(report_id=report.id).all()
#             return render_template('report_view.html', report=report, trackings=trackings)
#         else:
#             error = 'Invalid Reference ID or Password'
#     return render_template('reporter.html', error=error)

# @app.route('/admin', methods=['GET', 'POST'])
# def admin():
#     error = ''
#     if request.method == 'POST':
#         if request.form['admin_pass'] == 'admin123':
#             reports = Report.query.all()
#             return render_template('admin_view.html', reports=reports)
#         else:
#             error = 'Incorrect Admin Password'
#     return render_template('admin.html', error=error)

# @app.route('/add_tracking/<ref_id>', methods=['POST'])
# def add_tracking(ref_id):
#     report = Report.query.filter_by(reference_id=ref_id).first()
#     if report:
#         msg = request.form['message']
#         tracking = Tracking(report_id=report.id, message=msg)
#         db.session.add(tracking)
#         db.session.commit()
#     return redirect('/admin')

# @app.route('/chat/<int:report_id>', methods=['GET', 'POST'])
# def chat(report_id):
#     report = Report.query.get_or_404(report_id)
#     chats = Chat.query.filter_by(report_id=report_id).order_by(Chat.timestamp).all()

#     if request.method == 'POST':
#         sender = request.form['sender']
#         message = request.form['message']
#         new_chat = Chat(report_id=report_id, sender=sender, message=message)
#         db.session.add(new_chat)
#         db.session.commit()
#         return redirect(url_for('chat', report_id=report_id))

#     return render_template('chat.html', report=report, chats=chats)

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import string
from gemini_utils import extract_fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reports.db'
app.secret_key = 'secretkey'
db = SQLAlchemy(app)

# Models
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference_id = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    time = db.Column(db.String(100))
    category = db.Column(db.String(100))
    accused = db.Column(db.String(100))
    trackings = db.relationship('Tracking', backref='report', lazy=True)

class Tracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Utility function to generate reference_id and password
def generate_reference_id():
    while True:
        ref_id = 'REP' + ''.join(random.choices(string.digits, k=3))
        if not Report.query.filter_by(reference_id=ref_id).first():
            return ref_id

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Create DB and insert dummy data
with app.app_context():
    db.create_all()
    # if Report.query.count() == 0:
    #     dummy_data = [
    #         ('REP123', 'pass123', 'Harassment case in college', 'Bangalore', '2024-05-12 14:00', 'Harassment', 'Mr. X'),
    #         ('REP456', 'pass456', 'Cyberbullying on Instagram', 'Mysore', '2024-05-10 16:00', 'Cyberbullying', 'Unknown'),
    #     ]
    #     for ref, pwd, desc, loc, time, cat, acc in dummy_data:
    #         report = Report(reference_id=ref, password=pwd, description=desc,
    #                         location=loc, time=time, category=cat, accused=acc)
    #         db.session.add(report)
    #     db.session.commit()

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/reporter', methods=['GET', 'POST'])
def reporter():
    error = ''
    if request.method == 'POST':
        ref = request.form['reference_id']
        pwd = request.form['password']
        report = Report.query.filter_by(reference_id=ref, password=pwd).first()
        if report:
            trackings = Tracking.query.filter_by(report_id=report.id).all()
            return render_template('report_view.html', report=report, trackings=trackings)
        else:
            error = 'Invalid Reference ID or Password'
    return render_template('reporter.html', error=error)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error = ''
    if request.method == 'POST':
        if request.form['admin_pass'] == 'admin123':
            reports = Report.query.all()
            return render_template('admin_view.html', reports=reports)
        else:
            error = 'Incorrect Admin Password'
    return render_template('admin.html', error=error)

@app.route('/add_tracking/<ref_id>', methods=['POST'])
def add_tracking(ref_id):
    report = Report.query.filter_by(reference_id=ref_id).first()
    if report:
        msg = request.form['message']
        tracking = Tracking(report_id=report.id, message=msg)
        db.session.add(tracking)
        db.session.commit()
    return redirect('/admin')

@app.route('/chat/<int:report_id>', methods=['GET', 'POST'])
def chat(report_id):
    report = Report.query.get_or_404(report_id)
    chats = Chat.query.filter_by(report_id=report_id).order_by(Chat.timestamp).all()

    if request.method == 'POST':
        sender = request.form['sender']
        message = request.form['message']
        new_chat = Chat(report_id=report_id, sender=sender, message=message)
        db.session.add(new_chat)
        db.session.commit()
        return redirect(url_for('chat', report_id=report_id))

    return render_template('chat.html', report=report, chats=chats)

# Voice Agent Routes
@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/process_answers', methods=['POST'])
def process_answers():
    try:
        answers = request.json.get('answers', [])
        if not answers:
            return jsonify({'error': 'No answers provided'}), 400
        
        # Combine answers into a single incident description
        incident_text = ' '.join(answers)
        
        # Extract fields using gemini_utils
        result = extract_fields(incident_text)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # Generate reference_id and password
        reference_id = generate_reference_id()
        password = generate_password()
        
        # Create a new Report
        report = Report(
            reference_id=reference_id,
            password=password,
            description=incident_text,
            location=result.get('location', 'Not mentioned'),
            time=result.get('time', 'Not mentioned'),
            category=result.get('category', 'Not mentioned'),
            accused=result.get('accused', 'Not mentioned')
        )
        db.session.add(report)
        db.session.commit()
        
        # Return the extracted fields along with reference_id and password
        result['reference_id'] = reference_id
        result['password'] = password
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submit_text', methods=['POST'])
def submit_text():
    try:
        incident_text = request.form.get('incident_text', '')
        if not incident_text.strip():
            return jsonify({'error': 'No incident text provided'}), 400
        
        # Extract fields
        result = extract_fields(incident_text)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # Generate reference_id and password
        reference_id = generate_reference_id()
        password = generate_password()
        
        # Create a new Report
        report = Report(
            reference_id=reference_id,
            password=password,
            description=incident_text,
            location=result.get('location', 'Not mentioned'),
            time=result.get('time', 'Not mentioned'),
            category=result.get('category', 'Not mentioned'),
            accused=result.get('accused', 'Not mentioned')
        )
        db.session.add(report)
        db.session.commit()
        
        # Return the extracted fields along with reference_id and password
        result['reference_id'] = reference_id
        result['password'] = password
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)