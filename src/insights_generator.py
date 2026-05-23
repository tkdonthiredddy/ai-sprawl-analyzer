import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_executive_insights(classified_df):

    data_summary = classified_df.to_csv(index=False)

    prompt = f"""
You are an enterprise AI governance advisor.

Analyze this AI tool inventory and provide:

1. Executive summary
2. Key overlap risks
3. Governance concerns
4. Cost optimization opportunities
5. Recommended next actions

AI Tool Inventory:
{data_summary}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert enterprise AI governance consultant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content