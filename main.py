# main.py
import os
import time
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from knowledge_engine import KnowledgeEngine
from ui import HTML_CHAT_UI

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
