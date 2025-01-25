from flask import Flask
from models import db, init_db_command
from services import fetch_and_classify_bills

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bills.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.cli.add_command(init_db_command)

@app.route('/update-bills')
def update_bills():
    fetch_and_classify_bills()
    return "Bills updated and classified!"

if __name__ == '__main__':
    app.run(debug=True)
