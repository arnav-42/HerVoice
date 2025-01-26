import os
from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

with app.app_context():
    try:
        msg = Message(
            subject="Test Email",
            body="This is a test from Flask-Mail!",
            sender=os.environ.get('MAIL_USERNAME'),
            recipients=["akalekar@purdue.edu"]
        )
        mail.send(msg)
        print("Test email sent successfully!")
    except Exception as e:
        print("Error sending test email:", e)
