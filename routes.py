from flask import request, render_template, redirect, url_for
from models import db, User

def configure_routes(app):

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            email = request.form['email']
            interests = request.form['interests']
            location = request.form['location']
            new_user = User(email=email, interests=interests, location=location)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        users = User.query.all()
        return render_template('dashboard.html', users=users)
