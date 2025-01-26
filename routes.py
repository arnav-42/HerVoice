# routes.py
from flask import request, session, redirect, url_for, render_template, jsonify
from models import User, Bill
from extensions import db
from services import send_all_relevant_bills_to_user  # or whatever else you need

def configure_routes(app):
    @app.route('/')
    def home():
        return redirect(url_for('index'))

    @app.route('/index')
    def index():
        return render_template('index.html')

    @app.route('/process-login', methods=['POST'])
    def process_login():
        email = request.form.get('email')
        if not email:
            return "Email required", 400

        user = User.query.filter_by(email=email).first()
        if not user:
            new_user = User(email=email, interests="")
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
        else:
            session['user_id'] = user.id

        return "OK"

    @app.route('/process-categories', methods=['POST'])
    def process_categories():
        if 'user_id' not in session:
            return "Not logged in", 403

        user = User.query.get(session['user_id'])
        if not user:
            return "User not found", 404

        categories = request.form.getlist('categories')
        user.interests = ",".join(categories)
        db.session.commit()

        # Optionally email the user all relevant bills right now:
        from services import send_all_relevant_bills_to_user
        send_all_relevant_bills_to_user(user)

        return "OK"

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    # 1) Return relevant bills as JSON
    @app.route('/api/relevant-bills', methods=['GET'])
    def relevant_bills():
        if 'user_id' not in session:
            return jsonify({"error": "Not logged in"}), 403

        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Parse user interests
        user_categories = [cat.strip().lower() for cat in (user.interests or "").split(",") if cat.strip()]
        if not user_categories:
            # No categories => no relevant bills
            return jsonify([])

        # Query all bills and filter by category
        all_bills = Bill.query.all()
        filtered = []
        for b in all_bills:
            if b.category and b.category.lower() in user_categories:
                filtered.append({
                    "bill_number": b.bill_number,
                    "title": b.title,
                    "category": b.category,
                    "action_date": b.action_date,
                    "action_desc": b.action_desc,
                    "summary": b.summary[:200] + "..."  # shorten summary in preview
                })

        return jsonify(filtered)

    # 2) Return the user's selected interests as JSON
    @app.route('/api/user-interests', methods=['GET'])
    def user_interests():
        if 'user_id' not in session:
            return jsonify({"error": "Not logged in"}), 403

        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({"error": "User not found"}), 404

        categories = [cat.strip() for cat in (user.interests or "").split(",") if cat.strip()]
        return jsonify(categories)
