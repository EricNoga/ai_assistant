import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_keys=os.getenv("OPENAI_API_KEY"))

def create_plan(user_request: str):
    """
    Break a user request into structured steps
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        massages=[
            {
                "role": "system",
                "content": """
                You are a planning agent.
                Break user requests into simple steps.
                Return ONLY valid JSON like this:
                {
                "steps': [
                "step 1",
                "step 2",
                "step 3"
                ]
                }
                """
            },
            {
                "role": "user",
                "content": user_request
            }
        ]
    )

    return json.loads(response.choies[0].message.content)