import os
from openai import OpenAI
from dotenv import load_dotenv
from backend.memory.chat_memory import add_message, get_history

#Load environment variables
load_dotenv()

#Create OpenAI client
api_key=os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OpenAI API key not set")

client = OpenAI(api_key=api_key)

def get_ai_response(user_message: str):

    add_message("user", user_message)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant."
        }
    ] + get_history()

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    ai_response = response.choices[0].message.content

    add_message("assistant", ai_response)

    return ai_response