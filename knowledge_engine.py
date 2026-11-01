# knowledge_engine.py
# Hermes Agent 하이브리드 검색 엔진 (1만개 지식베이스 + 실시간 웹/위키 검색)

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

    def ask(self, query: str):
        start = time.time()
        local_matches = self.search_local(query)
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

        web_match = self.search_web(query)
        elapsed = time.time() - start
        if web_match:
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
