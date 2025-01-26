from flask import request, render_template, redirect, url_for
from models import db, User

def configure_routes(app):
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        """
        Example route to sign up a new user.
        """
        if request.method == 'POST':
            email = request.form['email']
            interests = request.form['interests']
            location = request.form['location']
            
            # Simple check to see if the user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return "User already registered!", 400
            
            new_user = User(email=email, interests=interests, location=location)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('dashboard'))
        
        # In a real app, you'd return a template with a signup form
        return """
        <form method="POST">
          Email: <input type="text" name="email"><br>
          Interests: <input type="text" name="interests"><br>
          Location: <input type="text" name="location"><br>
          <input type="submit" value="Sign Up">
        </form>
        """

    @app.route('/dashboard')
    def dashboard():
        """
        Example dashboard showing all users. 
        In a real app, you'd likely use a template here.
        """
        users = User.query.all()
        user_list = [f"{u.email} | Interests: {u.interests} | Location: {u.location}" for u in users]
        return "<br>".join(user_list)
