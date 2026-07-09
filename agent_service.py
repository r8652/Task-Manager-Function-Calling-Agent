from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
import requests
from typing import Optional

from todo_service import add_task, delete_task, get_tasks, update_task

load_dotenv()
MOCK_OPENAI = os.getenv("MOCK_OPENAI", "false").lower() in ("1", "true", "yes")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip() or None
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "text-bison@001")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip() or None
GROQ_MODEL = os.getenv("GROQ_MODEL", "default")


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key.lower().startswith("your"):
        raise ValueError(
            "OPENAI_API_KEY is not set or still uses a placeholder value. Please add a valid key to your .env file."
        )
    return OpenAI(api_key=api_key)


def _call_google_model(prompt: str, model: str | None = None) -> str:
    model = model or GOOGLE_MODEL
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set in environment.")
    url = f"https://generativelanguage.googleapis.com/v1beta2/models/{model}:generateText"
    params = {"key": GOOGLE_API_KEY}
    payload = {"prompt": {"text": prompt}, "temperature": 0.2, "maxOutputTokens": 512}
    resp = requests.post(url, params=params, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    try:
        return data["candidates"][0]["content"]
    except Exception:
        # fallback: join candidate contents
        parts = [c.get("content", "") for c in data.get("candidates", [])]
        return "\n".join(parts)


def _call_groq_model(prompt: str, model: Optional[str] = None) -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in environment.")
    # Minimal Groq text generation using their REST key endpoint (example)
    url = "https://api.groq.com/v1/generate"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "max_output_tokens": 256}
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    # Attempt common response fields
    if isinstance(data, dict):
        if "text" in data:
            return data["text"]
        # try candidates or outputs
        for key in ("candidates", "outputs", "choices"):
            if key in data and isinstance(data[key], list) and data[key]:
                first = data[key][0]
                if isinstance(first, dict):
                    for f in ("text", "content", "output"):
                        if f in first:
                            return first[f]
                if isinstance(first, str):
                    return first
    # Fallback to raw dump
    return json.dumps(data)


def _build_tools() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "get_tasks",
                "description": "Retrieve tasks, optionally filtered by status, task type, or code.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                        "task_type": {"type": "string", "enum": ["work", "personal", "study", "errand"]},
                        "code": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task with the requested details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "task_type": {"type": "string", "enum": ["work", "personal", "study", "errand"]},
                        "start_date": {"type": "string"},
                        "end_date": {"type": "string"},
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                    },
                    "required": ["title"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update an existing task by its ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "code": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "task_type": {"type": "string", "enum": ["work", "personal", "study", "errand"]},
                        "start_date": {"type": "string"},
                        "end_date": {"type": "string"},
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                    },
                    "required": ["task_id"],
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task by its ID.",
                "parameters": {
                    "type": "object",
                    "properties": {"task_id": {"type": "string"}},
                    "required": ["task_id"],
                    "additionalProperties": False,
                },
            },
        },
    ]


def _run_tool(function_name: str, arguments: dict[str, Any]) -> Any:
    if function_name == "get_tasks":
        return get_tasks(
            status=arguments.get("status"),
            task_type=arguments.get("task_type"),
            code=arguments.get("code"),
        )
    if function_name == "add_task":
        return add_task(
            title=arguments["title"],
            description=arguments.get("description", ""),
            task_type=arguments.get("task_type", "personal"),
            start_date=arguments.get("start_date"),
            end_date=arguments.get("end_date"),
            status=arguments.get("status", "pending"),
            code=arguments.get("code"),
        )
    if function_name == "update_task":
        return update_task(
            task_id=arguments["task_id"],
            title=arguments.get("title"),
            description=arguments.get("description"),
            task_type=arguments.get("task_type"),
            start_date=arguments.get("start_date"),
            end_date=arguments.get("end_date"),
            status=arguments.get("status"),
            code=arguments.get("code"),
        )
    if function_name == "delete_task":
        return delete_task(task_id=arguments["task_id"])
    raise ValueError(f"Unsupported tool: {function_name}")


def agent(user_query: str) -> str:
    # If mock mode is enabled, simulate the function-calling flow locally
    tools = _build_tools()
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    # If a Google API key is provided, prefer calling Google Generative API
    # for simple text responses (fallback when OpenAI key is not present).
    # Prefer Groq if provided, then Google
    if GROQ_API_KEY and not MOCK_OPENAI:
        try:
            return _call_groq_model(user_query)
        except Exception:
            pass
    if GOOGLE_API_KEY and not MOCK_OPENAI:
        try:
            return _call_google_model(user_query, model=GOOGLE_MODEL)
        except Exception:
            pass
    if MOCK_OPENAI:
        # Simple keyword-based mapper to pick a tool and arguments
        q = user_query.lower()
        if any(k in q for k in ("הוסף", "add", "create", "new")):
            # Use the full query as title if no quotes provided
            title = None
            if '"' in user_query:
                parts = user_query.split('"')
                if len(parts) >= 3:
                    title = parts[1]
            if not title:
                title = user_query.strip()[:120]
            result = _run_tool("add_task", {"title": title})
            return f"(MOCK) Added task: {result.get('title')} (code={result.get('code')})"
        if any(k in q for k in ("הצג", "show", "list", "get")):
            result = _run_tool("get_tasks", {})
            return f"(MOCK) Tasks:\n" + ("\n".join([f"- {t['code']}: {t['title']} ({t['status']})" for t in result]) or "(no tasks)")
        if any(k in q for k in ("מחק", "delete", "remove")):
            # try to pick an id/code if present
            tokens = q.split()
            candidate = next((t for t in tokens if t.startswith("task-") or t.upper().startswith("TASK-")), None)
            if candidate:
                # map candidate to existing task by code
                tasks = get_tasks()
                found = next((t for t in tasks if t.get("code") == candidate or t.get("code") == candidate.upper()), None)
                if found:
                    res = _run_tool("delete_task", {"task_id": found["id"]})
                    return f"(MOCK) Deleted: {found.get('title')}"
            return "(MOCK) No task id found to delete in request."
        if any(k in q for k in ("עדכן", "update", "change", "set")):
            # naive update: mark first task as completed
            tasks = get_tasks()
            if not tasks:
                return "(MOCK) No tasks to update."
            first = tasks[0]
            res = _run_tool("update_task", {"task_id": first["id"], "status": "completed"})
            return f"(MOCK) Updated task {first.get('title')} -> completed"
        return "(MOCK) I understood your request but couldn't map it to a known action. Try: add, show, update, delete."

    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "You are a helpful task manager assistant. "
                "Use the available tools to add, update, list, or delete tasks. "
                "Each task has a code, title, description, task_type, start_date, end_date, and status."
            ),
        },
        {"role": "user", "content": user_query},
    ]

    client = _get_client()
    first_response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    first_message = first_response.choices[0].message

    if not first_message.tool_calls:
        return first_message.content or "I can help you manage your tasks."

    assistant_message: dict[str, Any] = {
        "role": "assistant",
        "content": first_message.content or "",
        "tool_calls": [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
            for tool_call in first_message.tool_calls
        ],
    }
    messages.append(assistant_message)

    for tool_call in first_message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments or "{}")
        result = _run_tool(function_name, arguments)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            }
        )

    second_response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    return second_response.choices[0].message.content or "The task operation completed."


def process_query(user_query: str) -> str:
    return agent(user_query)
