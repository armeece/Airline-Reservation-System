from flask import Flask, request, jsonify, render_template_string
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'

mail = Mail(app)

@app.route('/api/notify/email', methods=['POST'])
def send_email():
    data = request.get_json()
    if not data.get('recipient') or not data.get('template_data'):
        return jsonify({"error": "Recipient and template data are required"}), 400

    email_template = """
    Subject: Booking Confirmation - Flight {{ flight_number }}

    Dear {{ user_name }},

    Your booking for flight {{ flight_number }} has been confirmed. Here are the details:
    - Flight: {{ flight_number }}
    - Date: {{ flight_date }}
    - Seat: {{ seat }}
    - Total Price: ${{ price }}

    Thank you for choosing our airline.

    Best regards,
    Airline Reservation System
    """
    rendered_template = render_template_string(email_template, **data['template_data'])

    subject, body = rendered_template.split("\n\n", 1)

    try:
        msg = Message(subject=subject.strip(), sender=app.config['MAIL_USERNAME'], recipients=[data['recipient']])
        msg.body = body
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
