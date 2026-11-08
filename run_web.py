# run_web.py
# 아무 패키지(fastapi 등) 없이 순수 파이썬만으로 돌아가는 초경량 웹 챗 서버!
# 실행 방법: python3 run_web.py (터묵스/PC 어디서든 즉시 실행 가능)

import http.server
import json
import os
import socketserver
from knowledge_engine import KnowledgeEngine
from ui import HTML_CHAT_UI

PORT = int(os.getenv("PORT", "8000"))
engine = KnowledgeEngine()

class HermesWebHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/chat":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CHAT_UI.encode("utf-8"))
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            data = {"status": "ok", "items": len(engine.cache), "web_search": True}
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                req = json.loads(post_data.decode("utf-8"))
                query = str(req.get("message", ""))
            except (ValueError, AttributeError):
                self.send_error(400, "Invalid JSON")
                return

            result = engine.ask(query)
            
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

if __name__ == "__main__":
    llm_base = os.getenv("LLM_API_BASE", "")
    llm_model = os.getenv("LLM_MODEL", "qwen3.5:9b")
    print(f"==================================================")
    print(f"⚡ Hermes Agent AI Web Server 준비 완료!")
    print(f"📚 탑재된 지식: {len(engine.cache):,}개")
    if llm_base:
        print(f"🧠 연결된 로컬 LLM: {llm_model} ({llm_base})")
    else:
        print(f"🧠 LLM 상태: 내장 1만 지식베이스 & 실시간 위키백과 검색 모드")
    print(f"🌐 접속 주소: http://localhost:{PORT}")
    print(f"==================================================")
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    socketserver.ThreadingTCPServer.daemon_threads = True
    with socketserver.ThreadingTCPServer(("", PORT), HermesWebHandler) as httpd:
        httpd.serve_forever()
