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

from backend.agents.coding_agent import (
    get_coding_agent_prompt
)

from backend.agents.general_agent import (
    get_general_agent_prompt
)


client = OpenAI(
    api_key=OPENAI_API_KEY
)

MAX_STEPS = MAX_AGENT_STEPS


# -----------------------------------
# TASK PLANNER
# -----------------------------------

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
    # CHOOSE AGENT
    # -----------------------------------

    selected_agent = choose_agent(
        user_message
    )

    logger.info(
        "Selected agent: %s",
        selected_agent
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

    # -----------------------------------
    # CREATE TASK OBJECTS
    # -----------------------------------

    task_ids = []

    for task in task_list:

        task_id = create_task(
            task["task"]
        )

        task_ids.append(task_id)

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

    # -----------------------------------
    # EXECUTE TASKS
    # -----------------------------------

    for task_id in task_ids:

        task = get_task(task_id)

        if not task:

            logger.warning(
                "Task not found: %s",
                task_id
            )

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

            logger.info(
                "Executing task %s | step %s/%s",
                task_id,
                step + 1,
                MAX_STEPS
            )

            # -----------------------------------
            # SELECT PROMPT BY AGENT TYPE
            # -----------------------------------

            if selected_agent == "coding":

                system_prompt = (
                    get_coding_agent_prompt(
                        get_tool_descriptions()
                    )
                )

            else:

                system_prompt = (
                    get_general_agent_prompt(
                        get_tool_descriptions()
                    )
                )

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ] + get_history()

            # -----------------------------------
            # CALL MODEL
            # -----------------------------------

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

                    logger.info(
                        "Running tool: %s with args: %s",
                        tool_name,
                        args
                    )

                    # -----------------------------------
                    # RUN TOOL
                    # -----------------------------------

                    tool_result = run_tool(
                        tool_name,
                        args
                    )

                    logger.info(
                        "Tool result: %s",
                        tool_result
                    )

                    # -----------------------------------
                    # STORE TOOL USAGE
                    # -----------------------------------

                    add_message(
                        "assistant",
                        f"[USED TOOL: {tool_name}]"
                    )

                    # -----------------------------------
                    # FEED TOOL RESULT BACK
                    # -----------------------------------

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

                if is_important(
                    memory_text
                ):

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

                    logger.info(
                        "Stored important memory"
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