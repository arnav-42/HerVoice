import requests
import os
from datetime import datetime, timedelta, timezone

CONGRESS_API_BASE_URL = "https://api.congress.gov/v3/summaries"

def test_congress_api():
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    start_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    api_key = os.environ.get("CONGRESS_API_KEY")

    if not api_key:
        print("Congress API key is missing. Set the CONGRESS_API_KEY environment variable.")
        return
    
    url = f"{CONGRESS_API_BASE_URL}?fromDateTime={start_date}&toDateTime={end_date}&sort=updateDate+asc&api_key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print("API call successful. Number of bills received:", len(data.get("summaries", [])))
        print("Sample Bill Data:", data.get("summaries", [])[0] if data.get("summaries") else "No data")
    else:
        print(f"Failed to fetch data. Status Code: {response.status_code}, Response: {response.text}")

test_congress_api()
