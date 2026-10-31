# Hermes Agent + OpenClaw — Universal Helper (Termux & Haven)

이 저장소는 Android **Termux**와 **Haven (Debian/Ubuntu/Linux)** 환경 모두에서 완벽하게 작동하는 통합 설치 및 실행기를 제공합니다.

## 실행 방법

저장소를 클론한 후 스크립트를 실행하세요:

```bash
git clone https://github.com/gw140427-rgb/hermes-agent.git
cd hermes-agent
bash scripts/termux-hermes-setup.sh
```
(또는 `bash scripts/setup.sh`)

## 주요 메뉴

- **1) ⚡ 웹 챗 서버 바로 실행**: 10,000개 과학·기술·역사 지식과 실시간 웹 검색이 탑재된 반응형 웹 챗(`http://localhost:8000`)을 구동합니다.
- **2) 🛠️ Hermes & Python 환경 자동 설치**: 시스템에 맞게 Python3 및 필요 도구를 설치합니다.
- **3) 🦞 OpenClaw 설치**: Node.js와 OpenClaw를 자동으로 설치합니다.
- **4) 📊 설치 및 시스템 상태 점검**: 현재 환경, 설치된 언어 버전, 지식 데이터셋 탑재 여부를 점검합니다.
- **5) 🌐 Pinggy 외부 공개 링크 열기**: 다른 사람도 외부에서 접속할 수 있는 공인 HTTPS 주소를 생성합니다.

## 지원 환경

- **Android Termux** (ARM64/aarch64)
- **Haven / Debian / Ubuntu / PRoot Linux**
- **일반 Linux PC**
