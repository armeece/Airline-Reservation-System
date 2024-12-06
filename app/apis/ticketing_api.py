from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from app import mongo_db
from datetime import datetime

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'

mail = Mail(app)

@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    data = request.get_json()
    if not data.get('user_id') or not data.get('subject') or not data.get('message'):
        return jsonify({"error": "User ID, subject, and message are required"}), 400

    tickets_collection = mongo_db.get_collection('tickets')
    ticket = {
        "user_id": data['user_id'],
        "subject": data['subject'],
        "message": data['message'],
        "status": "open",
        "timestamp": datetime.now()
    }

    try:
        tickets_collection.insert_one(ticket)
        user_email = data.get('email')
        if user_email:
            msg = Message(
                subject="Ticket Submitted",
                sender=app.config['MAIL_USERNAME'],
                recipients=[user_email],
                body=f"Your ticket '{data['subject']}' has been submitted successfully."
            )
            mail.send(msg)
        return jsonify({"message": "Ticket created and email notification sent successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
