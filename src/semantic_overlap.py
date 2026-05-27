import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def cosine_similarity(vec_a, vec_b):
    a = np.array(vec_a)
    b = np.array(vec_b)

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def detect_semantic_overlap(df, threshold=0.72):
    records = []

    tools = df.to_dict("records")

    embeddings = {}

    for tool in tools:
        #text = f"{tool['tool']} - {tool['purpose']} - Team: {tool['team']}"
        text = tool["purpose"]
        embeddings[tool["tool"]] = get_embedding(text)

    for i in range(len(tools)):
        for j in range(i + 1, len(tools)):
            tool_a = tools[i]["tool"]
            tool_b = tools[j]["tool"]

            similarity = cosine_similarity(
                embeddings[tool_a],
                embeddings[tool_b],
            )

            if similarity >= threshold:
                records.append({
                    "tool_a": tool_a,
                    "tool_b": tool_b,
                    "team_a": tools[i]["team"],
                    "team_b": tools[j]["team"],
                    "similarity": round(similarity, 3),
                    "purpose_a": tools[i]["purpose"],
                    "purpose_b": tools[j]["purpose"],
                })

    return records

def explain_overlap(tool_a, tool_b, purpose_a, purpose_b):

    prompt = f"""
You are an enterprise AI governance advisor.

Explain why these two AI tools may overlap.

Tool A: {tool_a}
Purpose A: {purpose_a}

Tool B: {tool_b}
Purpose B: {purpose_b}

Provide:
1. overlap explanation
2. governance concern
3. consolidation recommendation

Keep response concise and executive-friendly.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an enterprise AI governance strategist."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content