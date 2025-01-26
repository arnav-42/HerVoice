from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import os

# Local imports
from models import db
from routes import configure_routes
from services import fetch_and_store_bills

app = Flask(__name__)

# Configure the database URI (e.g., SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bills.db?check_same_thread=False' # CHANGE IF BREAK!!!! delete ? and after
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the Flask app
db.init_app(app)

# Register routes from routes.py
configure_routes(app)

# Scheduler setup to run fetch_and_store_bills every minute
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(fetch_and_store_bills, 'interval', minutes=1)
scheduler.start()

@app.route('/')
def home():
    """
    Simple homepage to confirm the app is running.
    """
    return "Bill tracking app is running!"

@app.route('/update-bills')
def update_bills():
    """
    Manually trigger a bill update/fetch.
    """
    fetch_and_store_bills()
    return "Bills have been fetched, stored, and classified!"

if __name__ == '__main__':
    # Create all tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)
