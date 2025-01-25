import requests
from models import db, Bill

def fetch_and_classify_bills():
    # Fetch recent bills from Congress API
    response = requests.get("https://api.congress.gov/v3/bills/recent")
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
