from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    interests = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(100), nullable=False)
