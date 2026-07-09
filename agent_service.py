from __future__ import annotations
import json
import os
from typing import Any
from dotenv import load_dotenv
from openai import OpenAI
from todo_service import add_task, delete_task, get_tasks, update_task

# טעינת המשתנים מקובץ .env
load_dotenv()

def _get_client() -> OpenAI:
    # הטעינה של המשתנים מהקובץ .env מתבצעת בשורה הבאה:
    api_key = os.getenv("OPENAI_API_KEY")
    
    # בדיקת אבטחה קטנה (תעזור לנו לראות אם המפתח מגיע או לא)
    if not api_key:
        print("DEBUG: המפתח ריק!")
        raise ValueError("OPENAI_API_KEY is not found in .env file!")
    
    return OpenAI(api_key=api_key)

def _build_tools() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "get_tasks",
                "description": "Retrieve tasks, optionally filtered by status or task type.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                        "task_type": {"type": "string", "enum": ["work", "personal", "study", "errand"]},
                    },
                    "additionalProperties": False,
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                        "task_type": {"type": "string", "enum": ["work", "personal", "study", "errand"]},
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
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]},
                        "task_type": {"type": "string", "enum": ["work", "personal", "study", "errand"]},
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
        return get_tasks(status=arguments.get("status"), task_type=arguments.get("task_type"))
    if function_name == "add_task":
        return add_task(title=arguments["title"], description=arguments.get("description", ""), status=arguments.get("status", "pending"), task_type=arguments.get("task_type", "personal"))
    if function_name == "update_task":
        return update_task(task_id=arguments["task_id"], title=arguments.get("title"), description=arguments.get("description"), status=arguments.get("status"), task_type=arguments.get("task_type"))
    if function_name == "delete_task":
        return delete_task(task_id=arguments["task_id"])
    raise ValueError(f"Unsupported tool: {function_name}")

def process_query(user_query: str) -> str:
    client = _get_client()
    tools = _build_tools()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    messages = [
        {"role": "system", "content": "You are a helpful task manager assistant. Use the provided tools to add, update, list, or delete tasks."},
        {"role": "user", "content": user_query},
    ]

    first_response = client.chat.completions.create(model=model, messages=messages, tools=tools, tool_choice="auto")
    first_message = first_response.choices[0].message
    
    if not first_message.tool_calls:
        return first_message.content or "I can help you manage your tasks."

    messages.append(first_message)

    for tool_call in first_message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments or "{}")
        result = _run_tool(function_name, arguments)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })

    second_response = client.chat.completions.create(model=model, messages=messages, tools=tools)
    return second_response.choices[0].message.content or "The task operation completed."