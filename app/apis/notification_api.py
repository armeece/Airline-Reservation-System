from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from twilio.rest import Client
from app import mongo_db

app = Flask(__name__)

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'

mail = Mail(app)

# SMS Configuration
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/api/notify/email', methods=['POST'])
def send_email():
    data = request.get_json()
    if not data.get('recipient') or not data.get('subject') or not data.get('body'):
        return jsonify({"error": "Recipient, subject, and body are required"}), 400

    try:
        msg = Message(
            subject=data['subject'],
            sender=app.config['MAIL_USERNAME'],
            recipients=[data['recipient']],
            body=data['body']
        )
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notify/sms', methods=['POST'])
def send_sms():
    data = request.get_json()
    if not data.get('recipient') or not data.get('message'):
        return jsonify({"error": "Recipient and message are required"}), 400

    try:
        message = twilio_client.messages.create(
            body=data['message'],
            from_=TWILIO_PHONE_NUMBER,
            to=data['recipient']
        )
        return jsonify({"message": "SMS sent successfully", "sid": message.sid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
