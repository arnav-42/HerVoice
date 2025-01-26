import requests
import os
from datetime import datetime, timedelta, timezone
from flask import current_app
from flask_mail import Message
from extensions import db, mail
from models import Bill, User

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
    url = f"{base_url}?fromDateTime={start_date}&toDateTime={end_date}&sort=updateDate+asc&api_key={api_key}"
    return url

def fetch_and_store_bills():
    """
    Fetch bills, store if new, classify them using Groq, then email matching users.
    """
    with current_app.app_context():
        print("Fetching bills from Congress API...")
        response = requests.get(get_congress_api_url())
        if response.status_code != 200:
            print(f"Error fetching bills: {response.status_code} - {response.text}")
            return

        bills_data = response.json().get('summaries', [])
        print(f"Number of bills retrieved: {len(bills_data)}")

        new_bills = []
        for bill_data in bills_data:
            bill_number = bill_data['bill']['number']
            title = bill_data['bill']['title']
            action_date = bill_data['actionDate']
            action_desc = bill_data['actionDesc']
            summary = bill_data['text']

            existing_bill = Bill.query.filter_by(bill_number=bill_number).first()
            if existing_bill:
                # Skip if we've already seen it
                continue

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
            new_bills.append(new_bill)

        db.session.commit()

        # Notify interested users about each new bill
        for bill in new_bills:
            notify_users_of_new_bill(bill)

        print("Bills stored and classified successfully!")

def classify_bill_with_groq(summary):
    """
    Calls the Groq API to classify the bill into a single category.
    """
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key:
        return "Unclassified (Missing GROQ_API_KEY)"

    try:
        from groq import Groq
    except ImportError:
        print("groq package not installed. Install via pip install groq")
        return "Unclassified (groq package missing)"

    system_prompt = """
    You will classify the following legislative bill summary into exactly one of the categories:
    - Reproductive Rights
    - Environmental Policy
    - Healthcare
    - Education
    - Gun Control
    - Immigration
    - Civil Rights & Social Justice

    Respond with only the category name, no extra text.
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
    return "Unclassified"

def notify_users_of_new_bill(bill):
    """
    Emails all users whose interests include the bill's category.
    """
    if not bill.category:
        return

    # Compare in lowercase to handle user-interests reliably
    category = bill.category.lower()
    users = User.query.all()
    matched_users = [user for user in users if user.interests and category in user.interests.lower()]

    print(f"Bill {bill.bill_number} matched {len(matched_users)} user(s). Sending emails...")

    for user in matched_users:
        subject = f"New Bill Alert: {bill.title}"
        body = (
            f"Hello {user.email},\n\n"
            f"A new bill matching your interest in '{bill.category}' is available:\n\n"
            f"Bill Number: {bill.bill_number}\n"
            f"Title: {bill.title}\n"
            f"Action Date: {bill.action_date}\n"
            f"Action Description: {bill.action_desc}\n\n"
            f"Summary:\n{bill.summary}\n\n"
            f"Regards,\nHer Voice Team"
        )
        send_email(user.email, subject, body)

def send_all_relevant_bills_to_user(user):
    """
    For a given user, finds all bills matching the user's category interests
    and emails them in a single message.
    """
    if not user.interests:
        return  # User didn't pick any interests yet.

    # Convert user interests (e.g. "Healthcare,Education") to a lowercase list
    user_categories = [cat.strip().lower() for cat in user.interests.split(",") if cat.strip()]

    # Get all bills from the database
    all_bills = Bill.query.all()

    # Filter out only those bills whose category is in the user's interests
    relevant_bills = [
        bill for bill in all_bills
        if bill.category and bill.category.lower() in user_categories
    ]

    if not relevant_bills:
        return  # No matching bills => skip sending

    # Build up the email message with all relevant bills in one email
    lines = []
    lines.append(f"Hello {user.email},")
    lines.append("Here are the existing bills matching your category interests:")
    lines.append("")
    for bill in relevant_bills:
        lines.append(f"Bill Number: {bill.bill_number}")
        lines.append(f"Title: {bill.title}")
        lines.append(f"Category: {bill.category}")
        lines.append(f"Action Date: {bill.action_date}")
        lines.append(f"Action Description: {bill.action_desc}")
        lines.append("Summary:")
        lines.append(bill.summary)
        lines.append("\n" + "-"*40 + "\n")
    lines.append("Regards,\nHer Voice Team")

    body = "\n".join(lines)
    send_email(user.email, "Your Relevant Bills", body)

#
# **Single** send_email definition
#
def send_email(to_email, subject, body):
    """
    Send an email via Flask-Mail.
    """
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body,
            sender=current_app.config['MAIL_USERNAME']# or "noreply@example.com"
        )
        mail.send(msg)
        print(f"[DEBUG] Email sent to {to_email} with subject '{subject}'.")
    except Exception as e:
        print(f"[ERROR] Could not send email to {to_email}: {e}")
