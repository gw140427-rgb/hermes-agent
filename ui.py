# ui.py
# Hermes Agent 다크모드 반응형 웹 챗 인터페이스

HTML_CHAT_UI = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hermes Agent AI</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            background-color: #1e293b;
            padding: 16px 20px;
            border-bottom: 1px solid #334155;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 18px;
            font-weight: 700;
            color: #38bdf8;
        }
        .status-badge {
            background: rgba(34, 197, 94, 0.15);
            color: #4ade80;
            border: 1px solid #22c55e;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
        }
        #chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .msg {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 16px;
            line-height: 1.5;
            font-size: 15px;
            word-break: break-word;
        }
        .msg.user {
            align-self: flex-end;
            background-color: #2563eb;
            color: #ffffff;
            border-bottom-right-radius: 4px;
        }
        .msg.agent {
            align-self: flex-start;
            background-color: #1e293b;
            border: 1px solid #334155;
            border-bottom-left-radius: 4px;
        }
        .meta-badges {
            display: flex;
            gap: 6px;
            margin-top: 8px;
            font-size: 11px;
        }
        .badge {
            padding: 2px 8px;
            border-radius: 6px;
            font-weight: 600;
        }
        .badge-local {
            background-color: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }
        .badge-web {
            background-color: rgba(168, 85, 247, 0.15);
            color: #c084fc;
            border: 1px solid rgba(168, 85, 247, 0.3);
        }
        .badge-time {
            background-color: rgba(148, 163, 184, 0.1);
            color: #94a3b8;
        }
        .chips {
            display: flex;
            gap: 8px;
            padding: 8px 20px;
            overflow-x: auto;
            white-space: nowrap;
            background-color: #0f172a;
        }
        .chip {
            background-color: #1e293b;
            color: #94a3b8;
            border: 1px solid #334155;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .chip:hover {
            background-color: #334155;
            color: #f8fafc;
        }
        footer {
            padding: 16px 20px;
            background-color: #1e293b;
            border-top: 1px solid #334155;
            display: flex;
            gap: 10px;
        }
        #input-box {
            flex: 1;
            background-color: #0f172a;
            border: 1px solid #475569;
            color: #f8fafc;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 15px;
            outline: none;
        }
        #input-box:focus {
            border-color: #38bdf8;
        }
        #send-btn {
            background-color: #38bdf8;
            color: #0f172a;
            border: none;
            padding: 0 20px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 15px;
            cursor: pointer;
            transition: background 0.2s;
        }
        #send-btn:hover {
            background-color: #0284c7;
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <span>⚡ Hermes Agent AI</span>
        </div>
        <div class="status-badge">🟢 10,000 지식 + 웹 검색 활성</div>
    </header>

    <div class="chips">
        <div class="chip" onclick="sendChip('GPU가 뭐야?')">💡 GPU가 뭐야?</div>
        <div class="chip" onclick="sendChip('세포에 대해 알려줘')">🔬 세포에 대해 알려줘</div>
        <div class="chip" onclick="sendChip('HTML이란 무엇인가요?')">💻 HTML이란?</div>
        <div class="chip" onclick="sendChip('블랙홀')">🌌 블랙홀 (실시간 검색)</div>
    </div>

    <div id="chat-container">
        <div class="msg agent">
            안녕하세요 건우님! ⚡ <strong>Hermes Agent AI</strong>입니다.<br>
            10,000개의 과학·기술·역사 지식과 실시간 웹 검색 기능이 탑재되어 있습니다. 무엇이든 물어보세요!
        </div>
    </div>

    <footer>
        <input type="text" id="input-box" placeholder="질문을 입력하세요..." onkeydown="if(event.key==='Enter') sendMsg()">
        <button id="send-btn" onclick="sendMsg()">전송</button>
    </footer>

    <script>
        const chat = document.getElementById('chat-container');
        const input = document.getElementById('input-box');

        function escapeHtml(value) {
            return String(value ?? '').replace(/[&<>"']/g, c => ({
                '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
            })[c]);
        }

        function appendMsg(text, type, meta = null) {
            const div = document.createElement('div');
            div.className = 'msg ' + type;
            
            let html = escapeHtml(text).replace(/\\n/g, '<br>');
            if (meta) {
                const source = String(meta.source ?? '');
                const badgeClass = source.includes('로컬') ? 'badge-local' : 'badge-web';
                html += `<div class="meta-badges">
                    <span class="badge ${badgeClass}">📌 ${escapeHtml(source)}</span>
                    <span class="badge badge-time">⚡ ${escapeHtml(meta.elapsed)}s</span>
                </div>`;
            }
            div.innerHTML = html;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        async function sendMsg() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';

            appendMsg(text, 'user');

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                appendMsg(data.answer, 'agent', {
                    source: data.source,
                    elapsed: data.elapsed
                });
            } catch (err) {
                appendMsg('서버 연결 오류가 발생했습니다: ' + err, 'agent');
            }
        }

        function sendChip(text) {
            input.value = text;
            sendMsg();
        }
    </script>
</body>
</html>
"""
