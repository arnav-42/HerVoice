from flask import Flask, render_template, request, redirect, url_for
from models import db, User
from routes import configure_routes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()  # Creates database tables from SQLAlchemy models

configure_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
