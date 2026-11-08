# knowledge_engine.py
# Hermes Agent 하이브리드 지식 & 로컬 LLM(Qwen/Gemma) 엔진

import html
import json
import os
import re
import time
import urllib.parse
import urllib.request

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "knowledge.jsonl")

class KnowledgeEngine:
    def __init__(self, data_path=DATA_PATH):
        self.data_path = data_path
        self.cache = []
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.data_path):
            return
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.cache.append(json.loads(line))
        except Exception as e:
            print(f"[KnowledgeEngine] 데이터 로드 실패: {e}")

    def search_local(self, query: str, limit: int = 3):
        clean_q = re.sub(r"[?.,!~]", "", query)
        raw_words = clean_q.split()
        keywords = set()
        particles = ["이란", "이란?", "란", "이", "가", "은", "는", "을", "를", "의", "에", "에서", "에 대해", "에 관해", "뭐야", "알려줘", "설명해줘"]

        for w in raw_words:
            w_lower = w.lower()
            keywords.add(w_lower)
            for p in particles:
                if w_lower.endswith(p) and len(w_lower) > len(p):
                    keywords.add(w_lower[:-len(p)])

        results = []
        seen_answers = set()

        for item in self.cache:
            q_text = item.get("question", "").lower()
            a_text = item.get("answer", "")

            score = 0
            for kw in keywords:
                if len(kw) < 2:
                    continue
                if kw in q_text:
                    score += 2
                if kw in a_text.lower():
                    score += 1

            if score > 0 and a_text not in seen_answers:
                results.append((score, item))
                seen_answers.add(a_text)

        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:limit]]

    def search_web(self, query: str):
        try:
            url = f"https://ko.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&utf8=1"
            req = urllib.request.Request(url, headers={"User-Agent": "HermesAgent/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                search_results = data.get("query", {}).get("search", [])
                if search_results:
                    first = search_results[0]
                    snippet = html.unescape(re.sub(r"<[^>]+>", "", first.get("snippet", "")))
                    return {
                        "source": "실시간 위키백과",
                        "title": first.get("title"),
                        "text": snippet
                    }
        except Exception:
            pass
        return None

    def ask_llm(self, query: str, context: str = ""):
        """Colab / Ollama / OpenAI 호환 API 엔드포인트 호출"""
        api_base = os.getenv("LLM_API_BASE", "").strip().rstrip("/")
        if not api_base:
            return None

        model = os.getenv("LLM_MODEL", "qwen2.5:7b").strip()
        system_prompt = "당신은 Hermes Agent의 고성능 AI 두뇌입니다. 질문에 한국어로 친절하고 정확하게 답해주세요."
        if context:
            system_prompt += f"\n\n[참고 지식 및 검색 자료]\n{context}"

        endpoint = f"{api_base}/chat/completions"
        payload_dict = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            "stream": False
        }
        payload = json.dumps(payload_dict).encode("utf-8")
        api_key = os.getenv("LLM_API_KEY", "not-needed")

        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            print(f"[KnowledgeEngine] LLM({model}) 호출 실패 (API: {endpoint}): {e}")
            return None

    def ask(self, query: str):
        start = time.time()
        local_matches = self.search_local(query)
        web_match = self.search_web(query)

        # 1. 지식베이스/검색 컨텍스트 구성
        context_parts = []
        source_label = ""
        if local_matches:
            context_parts.append(f"[로컬 10,000 지식]: {local_matches[0].get('answer')}")
            source_label = "로컬 지식"
        if web_match:
            context_parts.append(f"[실시간 위키]: [{web_match['title']}] {web_match['text']}")
            if not source_label:
                source_label = "웹 검색"

        context_str = "\n".join(context_parts)

        # 2. 로컬 LLM(Colab Qwen/Gemma)이 연결되어 있으면 생성형 AI 응답 우선 생성
        llm_reply = self.ask_llm(query, context=context_str)
        if llm_reply:
            elapsed = time.time() - start
            model_name = os.getenv("LLM_MODEL", "qwen2.5:7b")
            src_desc = f"⚡ Colab AI ({model_name})"
            if source_label:
                src_desc += f" + {source_label}"
            return {
                "source": src_desc,
                "category": "로컬 LLM 두뇌",
                "answer": llm_reply,
                "elapsed": round(elapsed, 4)
            }

        # 3. LLM 미연결 시 기존 규칙대로 폴백
        if local_matches:
            best = local_matches[0]
            elapsed = time.time() - start
            return {
                "source": "로컬 10,000 지식베이스",
                "category": best.get("category"),
                "answer": best.get("answer"),
                "fact_id": best.get("fact_id"),
                "elapsed": round(elapsed, 4)
            }

        if web_match:
            elapsed = time.time() - start
            return {
                "source": "실시간 웹 검색 (위키백과)",
                "category": "웹 검색",
                "answer": f"[{web_match['title']}] {web_match['text']}",
                "elapsed": round(elapsed, 4)
            }

        return {
            "source": "기본 응답",
            "category": "알림",
            "answer": "죄송합니다, 관련 지식이나 검색 결과를 찾지 못했습니다.",
            "elapsed": round(elapsed, 4)
        }
