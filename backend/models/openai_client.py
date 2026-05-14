import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from backend.memory.chat_memory import add_message, get_history
from backend.memory.task_memory import create_task, update_task, get_task
from backend.memory.vector_memory import (
    add_memory,
    search_memory,
    is_important,
    summarize_memory
)
from backend.orchestrator.tool_router import run_tool


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MAX_STEPS = 3


def create_plan(user_message: str):
    """
    Convert a user request into structured executable tasks.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": """
You are a task planning AI.

Convert the user request into a JSON list of tasks.

RULES:
- Output ONLY valid JSON
- Each item must contain:
{
  "task": "description"
}
- Keep tasks short
- Use 2 to 6 tasks maximum

Example:
[
  {"task": "Write Python code"},
  {"task": "Run the Python code"},
  {"task": "Explain the result"}
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


def get_ai_response(user_message: str):
    """
    Main AI agent function:
    - stores chat memory
    - retrieves long-term memory
    - creates tasks
    - executes tools
    - stores important results
    """

    add_message("user", user_message)

    relevant_memory = search_memory(user_message)
    memory_context = "\n".join(relevant_memory) if relevant_memory else ""

    raw_plan = create_plan(user_message)

    try:
        task_list = json.loads(raw_plan)
    except Exception:
        return f"Planner returned invalid JSON:\n{raw_plan}"

    task_ids = []

    for task in task_list:
        task_id = create_task(task["task"])
        task_ids.append(task_id)

    add_message(
        "assistant",
        "[TASKS CREATED]\n"
        f"{json.dumps(task_list, indent=2)}"
    )

    final_outputs = []

    for task_id in task_ids:
        task = get_task(task_id)

        if not task:
            continue

        execution_prompt = f"""
You are an execution agent.

Relevant long-term memory:
{memory_context}

Current task:
{task['description']}

Complete this task carefully.

Use tools if needed.

Return a final answer when complete.
"""

        add_message("user", execution_prompt)

        for step in range(MAX_STEPS):
            messages = [
                {
                    "role": "system",
                    "content": """
You are an autonomous AI execution agent.

AVAILABLE TOOLS:
- read_file(path)
- write_file(path, content)
- list_files(path)
- run_python_code(code)

TOOL USAGE RULES:

If a tool is needed, respond EXACTLY like this:

TOOL: tool_name
ARGS: {"key":"value"}

Examples:

TOOL: read_file
ARGS: {"path":"backend/api/main.py"}

TOOL: list_files
ARGS: {"path":"backend"}

TOOL: run_python_code
ARGS: {"code":"print('hello')"}

If no tool is needed:
respond normally with the completed result.
"""
                }
            ] + get_history()

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages
            )

            reply = response.choices[0].message.content

            if reply and reply.startswith("TOOL:"):
                try:
                    lines = reply.split("\n")

                    tool_name = lines[0].replace("TOOL:", "").strip()

                    args = json.loads(
                        lines[1]
                        .replace("ARGS:", "")
                        .strip()
                    )

                    tool_result = run_tool(tool_name, args)

                    add_message(
                        "assistant",
                        f"[USED TOOL: {tool_name}]"
                    )

                    add_message(
                        "user",
                        f"Tool result:\n{tool_result}"
                    )

                except Exception as e:
                    error_msg = f"Tool execution error: {str(e)}"

                    update_task(
                        task_id,
                        "failed",
                        error_msg
                    )

                    add_message("assistant", error_msg)
                    final_outputs.append(error_msg)

                    break

            else:
                update_task(
                    task_id,
                    "done",
                    reply
                )

                add_message("assistant", reply)
                final_outputs.append(reply)

                memory_text = f"""
USER REQUEST:
{user_message}

TASK RESULT:
{reply}
"""

                if is_important(memory_text):
                    summarized_memory = summarize_memory([memory_text])

                    add_memory(
                        text=summarized_memory,
                        metadata={
                            "type": "important_memory"
                        }
                    )

                break

    final_response = "\n\n".join(final_outputs)

    add_message("assistant", final_response)

    return final_response