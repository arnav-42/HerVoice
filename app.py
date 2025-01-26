from flask import Flask
import os
from apscheduler.schedulers.background import BackgroundScheduler
from extensions import db, mail

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your_secret"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bills.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Mail config
    app.config['MAIL_SERVER'] = "smtp.gmail.com" #os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = 587 #int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    db.init_app(app)
    mail.init_app(app)

    from routes import configure_routes
    configure_routes(app)

    return app

app = create_app()

from services import fetch_and_store_bills

scheduler = BackgroundScheduler()

def run_fetch_job():
    """
    This function wraps the fetch job in an app context so we can safely
    use the DB, mail, etc.
    """
    with app.app_context():
        fetch_and_store_bills()

# Example: run the fetch job every minute
scheduler.add_job(run_fetch_job, 'interval', minutes=1)
scheduler.start()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # **Immediately fetch bills on startup:**
        fetch_and_store_bills()  
    # Now run the app
    app.run(debug=True)