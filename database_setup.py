import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db, app

with app.app_context():
    db.create_all()
    print("Database initialized successfully!")
