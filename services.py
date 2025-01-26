import requests
from datetime import datetime, timedelta, timezone
import os

from models import db, Bill

def get_congress_api_url():
    """
    Generates the Congress API URL for the last 7 days with API key.
    """
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    start_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    api_key = os.environ.get("CONGRESS_API_KEY")

    if not api_key:
        raise ValueError("ERROR: Congress API key is missing. Set CONGRESS_API_KEY in your environment.")

    base_url = "https://api.congress.gov/v3/summaries"
    # Attach the API key and the date range in the query params
    url = f"{base_url}?fromDateTime={start_date}&toDateTime={end_date}&sort=updateDate+asc&api_key={api_key}"
    return url

def fetch_and_store_bills():
    """
    Fetch bills from Congress API, store them if they don't exist,
    and classify them using the Groq classification function.
    """
    print("Fetching bills from Congress API...")
    response = requests.get(get_congress_api_url())

    if response.status_code != 200:
        print(f"Error fetching bills: {response.status_code} - {response.text}")
        return

    bills_data = response.json().get('summaries', [])
    print(f"Number of bills retrieved: {len(bills_data)}")

    for bill in bills_data:
        bill_number = bill['bill']['number']
        title = bill['bill']['title']
        action_date = bill['actionDate']
        action_desc = bill['actionDesc']
        summary = bill['text']

        # Check if this bill_number already exists in DB
        existing_bill = Bill.query.filter_by(bill_number=bill_number).first()
        if existing_bill:
            print(f"Duplicate found: {bill_number}, skipping...")
            continue

        # Classify the bill with Groq
        category = classify_bill_with_groq(summary)

        # Create new Bill object and add to the database
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
    print("Bills stored and classified successfully!")

def classify_bill_with_groq(summary):
    """
    Classify the bill summary using the Groq API.
    """
    # If GROQ_API_KEY isn't set, just return "Unclassified"
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        return "Unclassified (Missing GROQ_API_KEY)"

    try:
        from groq import Groq
    except ImportError:
        print("groq package not installed. Install via pip install groq")
        return "Unclassified (groq package missing)"

    # Craft a system prompt for classification
    system_prompt = """
    Objective:
    Your task is to analyze summaries of legislative bills from the U.S. Congress and accurately classify each bill into 
    one of the following categories based on the bill's content, intent, and subject matter. Your response should be 
    a single category label from the predefined list below.

    Categories:
    - Reproductive Rights
    - Environmental Policy
    - Healthcare
    - Education
    - Gun Control
    - Immigration
    - Civil Rights & Social Justice

    Instructions:
    Respond only with the correct category name. No additional text or explanation.
    """

    client = Groq(api_key=groq_key)

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": summary}
        ],
        model="llama-3.3-70b-versatile"
    )

    if hasattr(response, 'choices') and len(response.choices) > 0:
        return response.choices[0].message.content.strip()

    return "Unclassified (No valid response from Groq)"
