import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_tool(tool_name, team, purpose, data_risk, sso_enabled):
    prompt = f"""
You are an enterprise AI governance analyst.

Classify this AI tool.

Tool: {tool_name}
Team: {team}
Purpose: {purpose}
Data Risk: {data_risk}
SSO Enabled: {sso_enabled}

Return only valid JSON with:
- capability_category
- risk_level
- overlap_risk
- governance_action
- rationale
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Return only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return json.loads(response.choices[0].message.content)