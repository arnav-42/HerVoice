from extensions import db

class Bill(db.Model):
    __tablename__ = 'bills'

    id = db.Column(db.Integer, primary_key=True)
    bill_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    action_date = db.Column(db.String(50), nullable=False)
    action_desc = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # We no longer store or check passwords in this simplified version
    interests = db.Column(db.Text, nullable=True)  
    # e.g. "Healthcare,Education"

    def __repr__(self):
        return f"<User {self.email}>"
