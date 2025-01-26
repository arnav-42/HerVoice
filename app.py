from flask import Flask
from models import db, Bill
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import os
from datetime import datetime, timedelta
from groq import Groq

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bills.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Congress API setup
CONGRESS_API_BASE_URL = "https://api.congress.gov/v3/summaries"

def get_congress_api_url():
    """Generates the Congress API URL for the last 7 days."""
    end_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"{CONGRESS_API_BASE_URL}?fromDateTime={start_date}&toDateTime={end_date}&sort=updateDate+asc"

def fetch_and_store_bills():
    """Fetch bills from Congress API, classify them, and store in the database."""
    print("Fetching bills from Congress API...")
    response = requests.get(get_congress_api_url())
    
    if response.status_code == 200:
        bills_data = response.json().get('summaries', [])
        
        for bill in bills_data:
            bill_number = bill['bill']['number']
            title = bill['bill']['title']
            action_date = bill['actionDate']
            action_desc = bill['actionDesc']
            summary = bill['text']

            # Check for duplicate entry
            existing_bill = Bill.query.filter_by(bill_number=bill_number).first()
            if existing_bill is None:
                # Classify the bill with Groq
                category = classify_bill_with_groq(summary)

                new_bill = Bill(
                    bill_number=bill_number,
                    title=title,
                    action_date=action_date,
                    action_desc=action_desc,
                    summary=summary,
                    category=category
                )
                db.session.add(new_bill)
        
        db.session.commit()
        print("Bills stored successfully!")

def classify_bill_with_groq(summary):
    """Classify the bill summary using the Groq API."""
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    system_prompt = "Classify the bill summary into one of the following categories: reproductive rights, sustainability, healthcare, economy, education, security, civil rights."

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": summary}
        ],
        model="llama-3.3-70b-versatile"
    )

    return response.choices[0].message.content.strip()

# Scheduler setup to run every minute
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_store_bills, 'interval', minutes=1)
scheduler.start()

@app.route('/')
def home():
    return "Bill tracking app is running!"

@app.route('/update-bills')
def update_bills():
    fetch_and_store_bills()
    return "Bills have been fetched, stored, and classified!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
