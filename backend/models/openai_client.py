import os
from openai import OpenAI
from dotenv import load_dotenv

#Load environment variables
load_dotenv()

#Create OpenAI client
api_key=os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OpenAI API key not set")

client = OpenAI(api_key=api_key)

def get_ai_response(user_message: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            message=[
                {
                    "role": "system",
                    "content":
                        "You are a modular AI assistant "
                        "designed for coding, cybersecurity, "
                        "media production, and autonomous workflows."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("OPENAI ERROR:", str(e))
        return f"Error calling AI model: {str(e)}"