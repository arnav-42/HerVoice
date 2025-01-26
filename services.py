import requests
from datetime import datetime, timedelta
from models import db, Bill
import os
from datetime import datetime, timedelta, timezone

CONGRESS_API_BASE_URL = "https://api.congress.gov/v3/summaries"

def get_congress_api_url():
    """Generates the Congress API URL for the last 7 days with API key."""
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    start_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
    api_key = os.environ.get("CONGRESS_API_KEY")

    if not api_key:
        raise ValueError("Congress API key is missing. Set the CONGRESS_API_KEY environment variable.")

    return f"{CONGRESS_API_BASE_URL}?fromDateTime={start_date}&toDateTime={end_date}&sort=updateDate+asc&api_key={api_key}"

def fetch_and_store_bills():
    print("Fetching bills from Congress API...")

    response = requests.get(get_congress_api_url())
    if response.status_code == 200:
        bills_data = response.json().get('summaries', [])
        print(f"Number of bills retrieved: {len(bills_data)}")

        for bill in bills_data:
            bill_number = bill['bill']['number']
            title = bill['bill']['title']
            action_date = bill['actionDate']
            action_desc = bill['actionDesc']
            summary = bill['text']

            print(f"Processing Bill: {bill_number} - {title}")

            # Check for duplicate entry
            existing_bill = Bill.query.filter_by(bill_number=bill_number).first()
            if existing_bill:
                print(f"Duplicate found: {bill_number}, skipping...")
                continue

            # Save to the database
            new_bill = Bill(
                bill_number=bill_number,
                title=title,
                action_date=action_date,
                action_desc=action_desc,
                summary=summary,
                category="Pending Classification"
            )
            db.session.add(new_bill)

        db.session.commit()
        print("Bills stored successfully!")

    else:
        print(f"Error fetching bills: {response.status_code} - {response.text}")


def classify_bill_with_groq(summary):
    from groq import Groq

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    system_prompt = """
    Objective:
    Your task is to analyze summaries of legislative bills from the U.S. Congress and accurately classify each bill into one of the following seven categories based on the bill's content, intent, and subject matter. Your response should be a single category label from the predefined list below.

    Categories and Detailed Descriptions:
    - **Reproductive Rights**
    Bills that address issues related to reproductive healthcare, including but not limited to:
    Access to abortion services, contraceptive availability and coverage, funding for reproductive health programs (e.g., Planned Parenthood), regulations on fertility treatments, parental leave and maternal health policies.

    - **Environmental Policy**
    Bills focusing on environmental conservation, sustainability, and climate-related initiatives, including:
    Climate change mitigation and adaptation measures, clean energy policies (solar, wind, hydro, etc.), pollution control and emission reductions, wildlife and natural habitat protection, regulations on industrial environmental impacts (e.g., carbon emissions, waste disposal), water and air quality standards, legislation on national parks and conservation efforts.

    - **Healthcare**
    Bills concerning public health systems, insurance, and medical services, including:
    Universal healthcare and access to medical services, Medicaid, Medicare, and healthcare subsidies, prescription drug pricing and affordability, mental health resources and accessibility, pandemic response measures and preparedness, research funding for diseases and medical conditions, rural healthcare access.

    - **Education**
    Bills related to education policies at federal, state, and local levels, such as:
    Public school funding and allocation of resources, student loan policies and financial aid programs, higher education affordability and access, curriculum regulations and educational standards, teacher salaries, training, and recruitment initiatives, school safety measures and mental health support in educational institutions, STEM (Science, Technology, Engineering, and Math) education funding.

    - **Gun Control**
    Bills that regulate the ownership, distribution, and use of firearms, including:
    Background checks for firearm purchases, assault weapon bans or restrictions, gun safety regulations (e.g., storage, carrying laws), licensing and registration of firearms, firearms-related public safety measures, laws concerning concealed carry and open carry policies, regulation of firearm manufacturers and sellers.

    - **Immigration**
    Bills dealing with immigration policies, border control, and legal pathways, such as:
    Border security measures and funding, pathways to citizenship and residency programs, refugee and asylum policies, deportation and enforcement measures, DACA (Deferred Action for Childhood Arrivals) and related programs, work visas, green card policies, and immigration reform, support for immigrant communities and integration programs.

    - **Civil Rights & Social Justice**
    Bills focusing on issues related to equal rights, diversity, and social justice, such as:
    LGBTQ+ rights and anti-discrimination laws, racial and ethnic equality measures, gender equality initiatives (e.g., Equal Pay Act), criminal justice reform and prison system policies, voting rights and election integrity, police reform and community relations, anti-discrimination measures in housing, employment, and education.

    Instructions:
    Read the provided bill summary carefully.
    Determine the primary focus of the bill based on keywords, themes, and legislative intent.
    Select the most appropriate category from the seven predefined options. If the bill overlaps multiple categories, choose the one most directly related to the bill's core purpose.
    Respond only with the category name (e.g., "Healthcare"). Do not provide explanations, justifications, or multiple categories.

    Example Classifications:
    Example 1: Bill Summary: "A bill to provide funding for rural hospitals and expand Medicare coverage to underserved areas." Correct Classification: "Healthcare"
    Example 2: Bill Summary: "A bill to ban high-capacity magazines and require universal background checks for firearm purchases." Correct Classification: "Gun Control"
    Example 3: Bill Summary: "A resolution to uphold LGBTQ+ rights by implementing anti-discrimination policies in the workplace." Correct Classification: "Civil Rights & Social Justice"
    Example 4: Bill Summary: "A bill to reduce greenhouse gas emissions and promote renewable energy initiatives across the country." Correct Classification: "Environmental Policy"

    Additional Considerations:
    If a bill does not clearly fit any category, classify it based on its primary objective, even if secondary topics are present.
    Ensure accuracy and consistency in classification.
    Be mindful of legislative language and phrasing that might indirectly reference a category (e.g., "public health initiatives" can imply "Healthcare").
    By following these guidelines, you will provide precise and meaningful classifications for legislative bills, ensuring users receive relevant notifications based on their selected interests.
    """

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": summary}
        ],
        model="llama-3.3-70b-versatile"
    )

    return response.choices[0].message.content.strip()
