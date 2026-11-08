# 🦞 Hermes Agent AI

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/gw140427-rgb/hermes-agent/blob/main/colab_hermes_llm.ipynb)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Model](https://img.shields.io/badge/LLM-Qwen%202.5%20%7C%20Gemma%202-orange.svg)

10,000개 지식베이스와 실시간 웹 검색, 그리고 Google Colab T4 GPU의 **Qwen 2.5 / Gemma 2** 로컬 LLM 두뇌를 연결할 수 있는 초경량 AI 에이전트 시스템입니다.

---

## ⚡ 1클릭 Google Colab GPU 두뇌 실행

무료 Google Colab T4 GPU를 사용해 최신 오픈소스 모델(**Qwen 2.5 7B** / **Gemma 2 9B**)을 구동하고 Hermes Agent와 연결할 수 있습니다:

👉 **[Google Colab에서 실행하기](https://colab.research.google.com/github/gw140427-rgb/hermes-agent/blob/main/colab_hermes_llm.ipynb)**

1. 위 링크 클릭 후 Colab에서 모든 셀 순서대로 실행
2. 3번 셀에 출력되는 `https://xxxx.trycloudflare.com/v1` 복사
3. 폰이나 서버의 Hermes Agent에 아래와 같이 연결:
   ```bash
   export LLM_API_BASE="https://xxxx.trycloudflare.com/v1"
   export LLM_MODEL="qwen2.5:7b"
   python3 run_web.py
   ```

---

## 🚀 빠른 시작 (Termux / Linux)

```bash
git clone https://github.com/gw140427-rgb/hermes-agent.git
cd hermes-agent
bash scripts/setup.sh
```

### 환경변수 옵션 (로컬 LLM 연결)
- `LLM_API_BASE`: OpenAI 호환 API 엔드포인트 주소 (예: Colab Cloudflare 터널 주소 `/v1`)
- `LLM_MODEL`: 모델명 (기본값: `qwen2.5:7b`, 선택: `gemma2:9b`, `qwen2.5:3b`)

*LLM_API_BASE가 설정되지 않은 경우, 내장된 10,000개 지식베이스와 실시간 위키백과 검색 엔진으로 자동 폴백 동작합니다.*

---

## 🛠️ 주요 기능

- 🧠 **하이브리드 RAG 지식 엔진**: 1만 개 로컬 지식 + 위키백과 실시간 검색 데이터를 LLM 프롬프트에 자동 주입
- ⚡ **Google Colab 연동**: 무료 T4 GPU에서 Qwen 2.5 7B 실시간 서빙
- 📱 **모바일 최적화 웹 챗 UI**: 스마트폰 브라우저에서도 부드럽게 작동하는 다크모드 반응형 웹 인터페이스
- 🌐 **원클릭 공인 터널**: Cloudflare 및 Pinggy를 통한 무설치 외부 접속 지원
