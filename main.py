from dotenv import load_dotenv
load_dotenv()
#from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent_service import process_query


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


app = FastAPI(title="Task Manager Agent", version="1.0.0")


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        response_text = process_query(request.message)
        return ChatResponse(response=response_text)
    except Exception as exc:
        print("--- ERROR TRACEBACK ---")
        import traceback
        traceback.print_exc() # זה ידפיס את השגיאה המלאה לטרמינל
        raise HTTPException(status_code=500, detail=str(exc))
