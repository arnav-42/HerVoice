from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    action_date = db.Column(db.String(50), nullable=False)
    action_desc = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True)
