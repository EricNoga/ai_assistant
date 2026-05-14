import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from backend.memory.chat_memory import add_message, get_history
from backend.orchestrator.tool_router import run_tool

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_plan(user_message: str):
    """
    Turns a user request into a step-by-step plan
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are a planning agent.

Break the user request into simple numbered steps.

Rules:
- Keep steps short
- Be specific
- Use 2–6 steps max
- Focus on actions that can be executed using tools
"""
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    return response.choices[0].message.content

MAX_STEPS = 3  # safety limit to prevent infinite loops

def get_ai_response(user_message: str):

    add_message("user", user_message)

    # ------------------------
    # 1. CREATE PLAN
    # ------------------------
    plan = create_plan(user_message)
    add_message("assistant", f"[PLAN]\n{plan}")

    # Convert plan into execution prompt
    execution_input = f"""
You are an execution agent.

Follow this plan step-by-step:

{plan}

Use tools when needed.
Return final result when complete.
"""

    add_message("user", execution_input)

    # ------------------------
    # 2. EXECUTION LOOP
    # ------------------------
    for step in range(MAX_STEPS):

        messages = [
            {
                "role": "system",
                "content": """
You are an execution agent.

You may use tools:
- read_file(path)
- write_file(path, content)
- list_files(path)

If using tools, respond:

TOOL: tool_name
ARGS: {"key": "value"}
"""
            }
        ] + get_history()

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages
        )

        reply = response.choices[0].message.content

        # ------------------------
        # TOOL HANDLING
        # ------------------------
        if reply and reply.startswith("TOOL:"):

            try:
                lines = reply.split("\n")

                tool_name = lines[0].replace("TOOL:", "").strip()
                args = json.loads(lines[1].replace("ARGS:", "").strip())

                tool_result = run_tool(tool_name, args)

                add_message("assistant", f"[Tool used: {tool_name}]")
                add_message("user", f"Tool result: {tool_result}")

            except Exception as e:
                error = f"Tool error: {str(e)}"
                add_message("assistant", error)
                return error

        else:
            # FINAL ANSWER
            add_message("assistant", reply)
            return reply

    fallback = "Task stopped: max steps reached."
    add_message("assistant", fallback)
    return fallback