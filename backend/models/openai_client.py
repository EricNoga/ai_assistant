import json

from openai import OpenAI
from openai import OpenAIError
from openai import RateLimitError

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

from backend.memory.run_memory import (
    create_run,
    add_task_to_run,
    complete_run,
    fail_run
)

from backend.memory.vector_memory import (
    add_memory,
    search_memory,
    is_important,
    summarize_memory
)

from backend.orchestrator.tool_router import run_tool
from backend.orchestrator.multi_agent_router import choose_agents

from backend.tools.registry import get_tool_descriptions

from backend.agents.coding_agent import get_coding_agent_prompt
from backend.agents.general_agent import get_general_agent_prompt
from backend.agents.cybersecurity_agent import get_cybersecurity_agent_prompt
from backend.agents.media_agent import get_media_agent_prompt
from backend.agents.reviewer_agent import get_reviewer_agent_prompt


client = OpenAI(
    api_key=OPENAI_API_KEY
)

MAX_STEPS = MAX_AGENT_STEPS


def create_plan(
    user_message: str,
    selected_agents: list
):
    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"""
You are an agent-aware task planner.

Available agents for this request:
{selected_agents}

Convert the user request into a JSON list of tasks.

RULES:
- Output ONLY valid JSON.
- Each item must contain:
{{
  "task": "description",
  "agent": "general | coding | cybersecurity | media"
}}

- Only use agents from this available list:
{selected_agents}

- Keep tasks short.
- Use 2 to 6 tasks maximum.
- Choose the best agent for each task.

Example:
[
  {{"task": "Analyze security log", "agent": "cybersecurity"}},
  {{"task": "Write parser", "agent": "coding"}}
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

    except RateLimitError as e:
        logger.error(
            "OpenAI quota/rate limit error: %s",
            str(e)
        )

        fallback_plan = [
            {
                "task": user_message,
                "agent": selected_agents[0]
            }
        ]

        return json.dumps(
            fallback_plan
        )

    except OpenAIError as e:
        logger.error(
            "OpenAI API error: %s",
            str(e)
        )

        fallback_plan = [
            {
                "task": user_message,
                "agent": selected_agents[0]
            }
        ]

        return json.dumps(
            fallback_plan
        )


def review_final_response(
    user_message: str,
    draft_response: str
):
    try:
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": get_reviewer_agent_prompt()
                },
                {
                    "role": "user",
                    "content": f"""
Original user request:
{user_message}

Draft response:
{draft_response}
"""
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(
            "Reviewer agent failed: %s",
            str(e)
        )

        return draft_response


def get_system_prompt(selected_agent: str):
    tool_descriptions = get_tool_descriptions()

    if selected_agent == "coding":
        return get_coding_agent_prompt(tool_descriptions)

    if selected_agent == "cybersecurity":
        return get_cybersecurity_agent_prompt(tool_descriptions)

    if selected_agent == "media":
        return get_media_agent_prompt(tool_descriptions)

    return get_general_agent_prompt(tool_descriptions)


def normalize_agent(
    requested_agent: str,
    selected_agents: list
):
    if requested_agent in selected_agents:
        return requested_agent

    if selected_agents:
        return selected_agents[0]

    return "general"


def get_ai_response(user_message: str):
    add_message(
        "user",
        user_message
    )

    selected_agents = choose_agents(
        user_message
    )

    run_id = create_run(
        user_message,
        selected_agents
    )

    logger.info(
        "Created run: %s",
        run_id
    )

    logger.info(
        "Selected agents: %s",
        selected_agents
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
        user_message,
        selected_agents
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
        error_response = (
            "Planner returned invalid JSON:\n"
            f"{raw_plan}"
        )

        logger.error(
            "Planner returned invalid JSON: %s",
            raw_plan
        )

        fail_run(
            run_id,
            error_response
        )

        return error_response

    task_ids = []
    task_agent_map = {}

    for task in task_list:
        task_description = task.get(
            "task",
            ""
        )

        requested_agent = task.get(
            "agent",
            selected_agents[0]
        )

        normalized_agent = normalize_agent(
            requested_agent,
            selected_agents
        )

        task_id = create_task(
            task_description
        )

        task_ids.append(
            task_id
        )

        add_task_to_run(
            run_id,
            task_id
        )

        task_agent_map[task_id] = normalized_agent

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

        selected_agent = task_agent_map.get(
            task_id,
            selected_agents[0]
        )

        logger.info(
            "Task %s assigned to agent: %s",
            task_id,
            selected_agent
        )

        execution_prompt = f"""
You are an execution agent.

Run ID:
{run_id}

Available agents for this request:
{selected_agents}

Assigned agent for this task:
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
                "Run %s | task %s | step %s/%s",
                run_id,
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

            try:
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

            except RateLimitError as e:
                logger.error(
                    "Run %s | OpenAI quota exceeded: %s",
                    run_id,
                    str(e)
                )

                reply = (
                    "OpenAI quota exceeded. "
                    "Switch to mock mode or add API credits."
                )

            except OpenAIError as e:
                logger.error(
                    "Run %s | OpenAI API error: %s",
                    run_id,
                    str(e)
                )

                reply = (
                    "OpenAI API error occurred. "
                    "Check your API key, billing, model name, or network connection."
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
                        "Run %s | running tool: %s with args: %s",
                        run_id,
                        tool_name,
                        args
                    )

                    tool_result = run_tool(
                        tool_name,
                        args
                    )

                    logger.info(
                        "Run %s | tool result: %s",
                        run_id,
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
                        "Run %s | tool execution failed: %s",
                        run_id,
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
                    f"[{selected_agent.upper()} AGENT]\n{reply}"
                )

                memory_text = f"""
USER REQUEST:
{user_message}

RUN ID:
{run_id}

SELECTED AGENTS:
{selected_agents}

TASK AGENT:
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
                            "agent": selected_agent,
                            "run_id": run_id
                        }
                    )

                    logger.info(
                        "Run %s | stored important memory",
                        run_id
                    )

                break

    draft_response = "\n\n".join(
        final_outputs
    )

    reviewed_response = review_final_response(
        user_message,
        draft_response
    )

    complete_run(
        run_id,
        reviewed_response
    )

    add_message(
        "assistant",
        reviewed_response
    )

    return reviewed_response