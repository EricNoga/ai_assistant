from backend.memory.chat_memory import add_message, get_history
from backend.orchestrator.tool_router import run_tool
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_ai_response(user_message: str):

    add_message("user", user_message)

    messages = [
        {
            "role": "system",
            "content": """
You are an AI agent with tool access.

TOOLS AVAILABLE:
- read_file(path)
- write_file(path, content)
- list_files(path)

If you need a tool, respond EXACTLY like this:

TOOL: tool_name
ARGS: {"key": "value"}

If no tool is needed, respond normally.
"""
        }
    ] + get_history()

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    reply = response.choices[0].message.content

    # -------------------------------
    # TOOL DETECTION LOGIC
    # -------------------------------
    if reply.startswith("TOOL:"):

        try:
            lines = reply.split("\n")

            tool_name = lines[0].replace("TOOL:", "").strip()
            args = json.loads(lines[1].replace("ARGS:", "").strip())

            tool_result = run_tool(tool_name, args)

            # Send tool result back to AI
            follow_up = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI agent. Use tool results to answer."
                    },
                    {
                        "role": "user",
                        "content": f"Tool result: {tool_result}"
                    }
                ]
            )

            final_answer = follow_up.choices[0].message.content

        except Exception as e:
            final_answer = f"Tool execution error: {str(e)}"

    else:
        final_answer = reply

    add_message("assistant", final_answer)

    return final_answer