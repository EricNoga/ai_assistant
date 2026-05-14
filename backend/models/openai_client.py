import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from backend.memory.chat_memory import add_message, get_history
from backend.orchestrator.tool_router import run_tool

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_STEPS = 3  # safety limit to prevent infinite loops


def get_ai_response(user_message: str):
    """
    Main agent loop:
    - Handles memory
    - Lets AI decide tool usage
    - Executes tools
    - Feeds results back into model
    - Returns final response
    """

    # Store user message in memory
    add_message("user", user_message)

    for step in range(MAX_STEPS):

        messages = [
            {
                "role": "system",
                "content": """
You are an AI agent with tool access.

You can use the following tools:
- read_file(path)
- write_file(path, content)
- list_files(path)

RULES:
If you need a tool, respond EXACTLY in this format:

TOOL: tool_name
ARGS: {"key": "value"}

If no tool is needed, respond normally.
"""
            }
        ] + get_history()

        # Call the model
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages
        )

        reply = response.choices[0].message.content

        # ----------------------------
        # TOOL EXECUTION BRANCH
        # ----------------------------
        if reply and reply.startswith("TOOL:"):

            try:
                lines = reply.split("\n")

                tool_name = lines[0].replace("TOOL:", "").strip()
                args = json.loads(lines[1].replace("ARGS:", "").strip())

                # Execute tool
                tool_result = run_tool(tool_name, args)

                # Log tool usage in memory
                add_message("assistant", f"[Used tool: {tool_name}]")

                # Feed tool result back into conversation
                add_message("user", f"Tool result: {tool_result}")

                # Continue loop (AI thinks again)

            except Exception as e:
                error_msg = f"Tool execution error: {str(e)}"
                add_message("assistant", error_msg)
                return error_msg

        else:
            # FINAL RESPONSE (no tool needed)
            add_message("assistant", reply)
            return reply

    # Safety fallback if loop exceeds MAX_STEPS
    fallback = "Task stopped: maximum reasoning steps reached."
    add_message("assistant", fallback)
    return fallback