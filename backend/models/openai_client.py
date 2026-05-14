import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from backend.memory.chat_memory import add_message, get_history
from backend.memory.task_memory import create_task, update_task, get_task
from backend.orchestrator.tool_router import run_tool

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MAX_STEPS = 3  # safety limit per task


# -----------------------------
# PLANNER (TASK GENERATION)
# -----------------------------
def create_plan(user_message: str):

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are a task planner.

Convert the user request into a JSON list of tasks.

RULES:
- Output ONLY valid JSON
- Each task must have:
  - "task": short description
- 2–6 tasks max

Example:
[
  {"task": "Read backend files"},
  {"task": "Summarize project structure"}
]
"""
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    return response.choices[0].message.content


# -----------------------------
# MAIN AGENT FUNCTION
# -----------------------------
def get_ai_response(user_message: str):

    # Store user input
    add_message("user", user_message)

    # -----------------------------
    # 1. CREATE TASK PLAN
    # -----------------------------
    raw_plan = create_plan(user_message)

    try:
        task_list = json.loads(raw_plan)
    except Exception:
        return f"Planner returned invalid JSON:\n{raw_plan}"

    task_ids = []

    for t in task_list:
        task_id = create_task(t["task"])
        task_ids.append(task_id)

    add_message("assistant", f"[TASKS CREATED]\n{task_list}")

    final_outputs = []

    # -----------------------------
    # 2. EXECUTE EACH TASK
    # -----------------------------
    for task_id in task_ids:

        task = get_task(task_id)

        execution_prompt = f"""
You are an execution agent.

Complete this task:
{task['description']}

Use tools if needed.
Return a clear final result.
"""

        add_message("user", execution_prompt)

        # -----------------------------
        # EXECUTION LOOP PER TASK
        # -----------------------------
        for step in range(MAX_STEPS):

            messages = [
                {
                    "role": "system",
                    "content": """
You are an AI execution agent.

AVAILABLE TOOLS:
- read_file(path)
- write_file(path, content)
- list_files(path)

If you need a tool respond EXACTLY:

TOOL: tool_name
ARGS: {"key": "value"}

Otherwise respond with final answer.
"""
                }
            ] + get_history()

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages
            )

            reply = response.choices[0].message.content

            # -----------------------------
            # TOOL EXECUTION BRANCH
            # -----------------------------
            if reply and reply.startswith("TOOL:"):

                try:
                    lines = reply.split("\n")

                    tool_name = lines[0].replace("TOOL:", "").strip()
                    args = json.loads(lines[1].replace("ARGS:", "").strip())

                    tool_result = run_tool(tool_name, args)

                    # Feed tool result back into context
                    add_message("user", f"Tool result: {tool_result}")

                except Exception as e:
                    error_msg = f"Tool error: {str(e)}"
                    add_message("assistant", error_msg)
                    update_task(task_id, "failed", error_msg)
                    final_outputs.append(error_msg)
                    break

            else:
                # TASK COMPLETE
                update_task(task_id, "done", reply)
                add_message("assistant", reply)
                final_outputs.append(reply)
                break

    # -----------------------------
    # 3. FINAL RESPONSE
    # -----------------------------
    summary = "\n\n".join(final_outputs)

    add_message("assistant", summary)

    return summary