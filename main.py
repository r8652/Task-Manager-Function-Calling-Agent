from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agent_service import agent


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


app = FastAPI(title="Task Manager Agent", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    with open("templates/index.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        response_text = agent(request.message)
        return ChatResponse(response=response_text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
