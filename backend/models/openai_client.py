import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from backend.memory.chat_memory import (
    add_message,
    get_history
)

from backend.memory.task_memory import (
    create_task,
    update_task,
    get_task
)

from backend.memory.vector_memory import (
    add_memory,
    search_memory,
    is_important,
    summarize_memory
)

from backend.orchestrator.tool_router import run_tool

# -----------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Prevent infinite execution loops
MAX_STEPS = 3


# -----------------------------------
# TASK PLANNER
# -----------------------------------

def create_plan(user_message: str):
    """
    Convert a user request into
    structured executable tasks
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
  {"task": "List backend files"},
  {"task": "Read main.py"},
  {"task": "Summarize the project"}
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


# -----------------------------------
# MAIN AGENT FUNCTION
# -----------------------------------

def get_ai_response(user_message: str):

    # -----------------------------------
    # STORE USER MESSAGE
    # -----------------------------------

    add_message(
        "user",
        user_message
    )

    # -----------------------------------
    # LONG-TERM MEMORY SEARCH
    # -----------------------------------

    relevant_memory = search_memory(
        user_message
    )

    memory_context = ""

    if relevant_memory:
        memory_context = "\n".join(
            relevant_memory
        )

    # -----------------------------------
    # CREATE TASK PLAN
    # -----------------------------------

    raw_plan = create_plan(
        user_message
    )

    try:

        task_list = json.loads(
            raw_plan
        )

    except Exception:

        return (
            "Planner returned invalid JSON:\n"
            f"{raw_plan}"
        )

    # -----------------------------------
    # CREATE TASK OBJECTS
    # -----------------------------------

    task_ids = []

    for task in task_list:

        task_id = create_task(
            task["task"]
        )

        task_ids.append(task_id)

    add_message(
        "assistant",
        "[TASKS CREATED]\n"
        f"{json.dumps(task_list, indent=2)}"
    )

    final_outputs = []

    # -----------------------------------
    # EXECUTE TASKS
    # -----------------------------------

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

        add_message(
            "user",
            execution_prompt
        )

        # -----------------------------------
        # MULTI-STEP EXECUTION LOOP
        # -----------------------------------

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

TOOL USAGE RULES:

If a tool is needed,
respond EXACTLY like this:

TOOL: tool_name
ARGS: {"key":"value"}

Examples:

TOOL: read_file
ARGS: {"path":"backend/api/main.py"}

TOOL: list_files
ARGS: {"path":"backend"}

If no tool is needed:
respond normally with the completed result.
"""
                }
            ] + get_history()

            # -----------------------------------
            # CALL MODEL
            # -----------------------------------

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages
            )

            reply = (
                response
                .choices[0]
                .message
                .content
            )

            # -----------------------------------
            # TOOL EXECUTION
            # -----------------------------------

            if (
                reply
                and reply.startswith("TOOL:")
            ):

                try:

                    lines = reply.split("\n")

                    tool_name = (
                        lines[0]
                        .replace("TOOL:", "")
                        .strip()
                    )

                    args = json.loads(
                        lines[1]
                        .replace("ARGS:", "")
                        .strip()
                    )

                    # Execute tool
                    tool_result = run_tool(
                        tool_name,
                        args
                    )

                    # Store tool usage
                    add_message(
                        "assistant",
                        f"[USED TOOL: {tool_name}]"
                    )

                    # Feed result back
                    add_message(
                        "user",
                        f"Tool result:\n{tool_result}"
                    )

                except Exception as e:

                    error_msg = (
                        "Tool execution error: "
                        f"{str(e)}"
                    )

                    update_task(
                        task_id,
                        "failed",
                        error_msg
                    )

                    add_message(
                        "assistant",
                        error_msg
                    )

                    final_outputs.append(
                        error_msg
                    )

                    break

            else:

                # -----------------------------------
                # TASK COMPLETED
                # -----------------------------------

                update_task(
                    task_id,
                    "done",
                    reply
                )

                add_message(
                    "assistant",
                    reply
                )

                final_outputs.append(
                    reply
                )

                # -----------------------------------
                # SMART LONG-TERM MEMORY STORAGE
                # -----------------------------------

                memory_text = f"""
USER REQUEST:
{user_message}

TASK RESULT:
{reply}
"""

                # Only store important memories
                if is_important(memory_text):

                    summarized_memory = (
                        summarize_memory(
                            [memory_text]
                        )
                    )

                    add_memory(
                        text=summarized_memory,
                        metadata={
                            "type": "important_memory"
                        }
                    )

                break

    # -----------------------------------
    # FINAL RESPONSE
    # -----------------------------------

    final_response = "\n\n".join(
        final_outputs
    )

    add_message(
        "assistant",
        final_response
    )

    return final_response