import json
from openai import OpenAI

from backend.core.config import (
    OPENAI_API_KEY,
    DEFAULT_MODEL,
    MAX_AGENT_STEPS
)

from backend.core.logger import logger

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
from backend.orchestrator.agent_router import choose_agent

from backend.tools.registry import get_tool_descriptions

from backend.agents.coding_agent import get_coding_agent_prompt
from backend.agents.general_agent import get_general_agent_prompt
from backend.agents.cybersecurity_agent import get_cybersecurity_agent_prompt


client = OpenAI(
    api_key=OPENAI_API_KEY
)

MAX_STEPS = MAX_AGENT_STEPS


def create_plan(user_message: str):
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
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


def get_system_prompt(selected_agent: str):
    tool_descriptions = get_tool_descriptions()

    if selected_agent == "coding":
        return get_coding_agent_prompt(tool_descriptions)

    if selected_agent == "cybersecurity":
        return get_cybersecurity_agent_prompt(tool_descriptions)

    return get_general_agent_prompt(tool_descriptions)


def get_ai_response(user_message: str):
    add_message(
        "user",
        user_message
    )

    selected_agent = choose_agent(
        user_message
    )

    logger.info(
        "Selected agent: %s",
        selected_agent
    )

    relevant_memory = search_memory(
        user_message
    )

    memory_context = ""

    if relevant_memory:
        memory_context = "\n".join(
            relevant_memory
        )

    raw_plan = create_plan(
        user_message
    )

    logger.info(
        "Planner raw output: %s",
        raw_plan
    )

    try:
        task_list = json.loads(
            raw_plan
        )

    except Exception:
        logger.error(
            "Planner returned invalid JSON: %s",
            raw_plan
        )

        return (
            "Planner returned invalid JSON:\n"
            f"{raw_plan}"
        )

    task_ids = []

    for task in task_list:
        task_id = create_task(
            task["task"]
        )

        task_ids.append(
            task_id
        )

    logger.info(
        "Created %s task(s)",
        len(task_ids)
    )

    add_message(
        "assistant",
        "[TASKS CREATED]\n"
        f"{json.dumps(task_list, indent=2)}"
    )

    final_outputs = []

    for task_id in task_ids:
        task = get_task(
            task_id
        )

        if not task:
            logger.warning(
                "Task not found: %s",
                task_id
            )

            continue

        execution_prompt = f"""
You are an execution agent.

Selected agent:
{selected_agent}

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

        for step in range(MAX_STEPS):
            logger.info(
                "Executing task %s | step %s/%s",
                task_id,
                step + 1,
                MAX_STEPS
            )

            messages = [
                {
                    "role": "system",
                    "content": get_system_prompt(
                        selected_agent
                    )
                }
            ] + get_history()

            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=messages
            )

            reply = (
                response
                .choices[0]
                .message
                .content
            )

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

                    logger.info(
                        "Running tool: %s with args: %s",
                        tool_name,
                        args
                    )

                    tool_result = run_tool(
                        tool_name,
                        args
                    )

                    logger.info(
                        "Tool result: %s",
                        tool_result
                    )

                    add_message(
                        "assistant",
                        f"[USED TOOL: {tool_name}]"
                    )

                    add_message(
                        "user",
                        f"Tool result:\n{tool_result}"
                    )

                except Exception as e:
                    error_msg = (
                        "Tool execution error: "
                        f"{str(e)}"
                    )

                    logger.error(
                        "Tool execution failed: %s",
                        str(e)
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

                memory_text = f"""
USER REQUEST:
{user_message}

SELECTED AGENT:
{selected_agent}

TASK RESULT:
{reply}
"""

                if is_important(
                    memory_text
                ):
                    summarized_memory = summarize_memory(
                        [memory_text]
                    )

                    add_memory(
                        text=summarized_memory,
                        metadata={
                            "type": "important_memory",
                            "agent": selected_agent
                        }
                    )

                    logger.info(
                        "Stored important memory"
                    )

                break

    final_response = "\n\n".join(
        final_outputs
    )

    add_message(
        "assistant",
        final_response
    )

    return final_response