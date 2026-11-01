# main.py
import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from knowledge_engine import KnowledgeEngine
from ui import HTML_CHAT_UI

app = FastAPI(title="Hermes Agent AI")
engine = KnowledgeEngine()


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
@app.get("/chat", response_class=HTMLResponse)
def chat_ui():
    return HTML_CHAT_UI


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "knowledge_count": len(engine.cache),
        "web_search": "enabled"
    }

@app.post("/api/chat")
def api_chat(req: ChatRequest):
    """웹 챗 UI 통신용 API 엔드포인트"""
    result = engine.ask(req.message)
    return result

@app.post("/query")
def query(prompt: str):
    """기존 API 호환용 엔드포인트"""
    result = engine.ask(prompt)
    return {
        "prompt": prompt,
        "agent_response": result["answer"],
        "source": result["source"],
        "elapsed_sec": result["elapsed"]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
