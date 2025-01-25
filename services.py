import requests
import os
from models import db, Bill

def fetch_and_classify_bills():
    c_key = os.getenv("CONGRESS_API_KEY")
    g_key = os.getenv("GROQ_API_KEY")
    # Fetch recent bills from Congress API
    response = requests.get("https://api.congress.gov/v3/bill")
    headers = {
        "Authorization": f"Bearer {c_key}",
        "Accept": "application/json"
    }
    bills = response.json().get('bills', [])

    for bill in bills:
        name = bill.get('name')
        summary = bill.get('summary')

        # Classify the summary using Groq API
        groq_response = requests.post("https://api.groq.com/classify", json={"summary": summary})
        interest = groq_response.json().get('interest')

        # Store in database
        new_bill = Bill(name=name, summary=summary, interest=interest)
        db.session.add(new_bill)
    
    db.session.commit()
