import requests

def classify_bill(summary):
    # Placeholder for Groq API call to classify bill
    response = requests.post("https://api.groq.com/classify", json={"summary": summary})
    return response.json()
