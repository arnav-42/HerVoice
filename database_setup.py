import sys
import os
from app import app, db

# Make sure the app context is set so db.create_all() works properly
with app.app_context():
    db.create_all()
    print("Database initialized successfully!")
