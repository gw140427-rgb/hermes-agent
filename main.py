# main.py
from fastapi import FastAPI
from hermes_agent import HermesAgent
from openclaw import OpenClawClient

# 환경 변수에서 API 키 로드
import os
from dotenv import load_dotenv
load_dotenv()

HERMES_API_KEY = os.getenv("HERMES_API_KEY")
OPENCLAW_API_KEY = os.getenv("OPENCLAW_API_KEY")

# Hermes Agent 초기화
hermes = HermesAgent(api_key=HERMES_API_KEY)

# Openclaw 클라이언트 초기화
openclaw = OpenClawClient(api_key=OPENCLAW_API_KEY)

app = FastAPI(title="Hermes Agent + Openclaw API")

@app.get("/")
def root():
    return {"message": "Hermes Agent + Openclaw 서버가 정상 작동 중입니다!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/query")
def query(prompt: str):
    # Hermes Agent에서 응답 생성
    response = hermes.generate(prompt=prompt)

    # Openclaw에 액션 전달 (예: 브라우저 자동화 등)
    action_result = openclaw.run(action=response.action)

    return {
        "prompt": prompt,
        "agent_response": response.text,
        "openclaw_action": response.action,
        "action_result": action_result
    }
