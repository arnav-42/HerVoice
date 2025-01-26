from flask import request, session, redirect, url_for, render_template
from extensions import db
from models import User

def configure_routes(app):
    @app.route('/')
    def home():
        # We’ll just redirect to /index for the main front-end page
        return redirect(url_for('index'))

    @app.route('/index')
    def index():
        """
        Renders index.html which has email-only login and category selection.
        """
        return render_template('index.html')

    @app.route('/process-login', methods=['POST'])
    def process_login():
        """
        Processes the email form. If user doesn't exist, create them.
        """
        email = request.form.get('email')
        if not email:
            return "Email required", 400

        user = User.query.filter_by(email=email).first()
        if not user:
            # Create a new user if not found
            new_user = User(email=email, interests="")
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
        else:
            # "Log in" existing user
            session['user_id'] = user.id

        return "OK"

    @app.route('/process-categories', methods=['POST'])
    def process_categories():
        """
        Stores the user's category selections in the database.
        """
        if 'user_id' not in session:
            return "Not logged in", 403

        user = User.query.get(session['user_id'])
        if not user:
            return "User not found", 404

        categories = request.form.getlist('categories')
        user.interests = ",".join(categories)
        db.session.commit()

        return "OK"

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))
