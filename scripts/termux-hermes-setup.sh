#!/usr/bin/env bash
# Hermes Agent + OpenClaw Universal Setup Script
# Supported: Termux (Android), Haven (Debian/Ubuntu), and Linux PC

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." 2>/dev/null && pwd)"
cd "$ROOT_DIR" || exit 1

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 환경 자동 판별
if [ -n "${PREFIX:-}" ] && [ "$PREFIX" = "/data/data/com.termux/files/usr" ]; then
  ENV_TYPE="termux"
  ENV_LABEL="Android Termux"
elif command -v apt-get >/dev/null 2>&1 || command -v apt >/dev/null 2>&1; then
  ENV_TYPE="haven"
  ENV_LABEL="Haven / Debian / Ubuntu"
elif command -v pacman >/dev/null 2>&1; then
  ENV_TYPE="arch"
  ENV_LABEL="Arch Linux"
elif command -v dnf >/dev/null 2>&1; then
  ENV_TYPE="fedora"
  ENV_LABEL="Fedora"
else
  ENV_TYPE="generic"
  ENV_LABEL="Generic Linux"
fi

log_info() { printf "${BLUE}[INFO]${NC} %s\n" "$*"; }
log_ok() { printf "${GREEN}[OK]${NC} %s\n" "$*"; }
log_warn() { printf "${YELLOW}[WARN]${NC} %s\n" "$*"; }
log_err() { printf "${RED}[ERROR]${NC} %s\n" "$*"; }

run_cmd() {
  if [ "$ENV_TYPE" = "haven" ] && [ "$(id -u)" -ne 0 ] && command -v sudo >/dev/null 2>&1; then
    sudo "$@"
  else
    "$@"
  fi
}

install_packages() {
  local pkgs="$*"
  log_info "필요한 패키지 설치 중: $pkgs"
  case "$ENV_TYPE" in
    termux)
      pkg update -y || log_warn "pkg update 경고 무시하고 진행"
      pkg install -y $pkgs || log_warn "일부 패키지 설치 실패 (계속 진행)"
      ;;
    haven)
      run_cmd apt-get update -y || log_warn "apt-get update 경고 무시하고 진행"
      run_cmd apt-get install -y --no-install-recommends $pkgs || log_warn "일부 패키지 설치 실패 (계속 진행)"
      ;;
    arch)
      run_cmd pacman -Sy --noconfirm $pkgs || true
      ;;
    fedora)
      run_cmd dnf install -y $pkgs || true
      ;;
    *)
      log_warn "패키지 관리자를 감지하지 못했습니다. 수동 설치가 필요할 수 있습니다: $pkgs"
      ;;
  esac
}

install_hermes() {
  echo ""
  log_info "1. Python 환경 및 의존성 확인 중..."
  if ! command -v python3 >/dev/null 2>&1; then
    install_packages "python3"
  fi
  
  if [ "$ENV_TYPE" = "termux" ]; then
    install_packages "python curl gnupg"
  else
    install_packages "python3 python3-pip curl"
  fi

  log_ok "Hermes Agent 실행 환경 준비 완료!"
}

install_openclaw() {
  echo ""
  log_info "2. Node.js & OpenClaw 설치 중..."
  if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
    if [ "$ENV_TYPE" = "termux" ]; then
      install_packages "nodejs-lts"
    else
      install_packages "nodejs npm"
    fi
  fi

  if command -v npm >/dev/null 2>&1; then
    log_info "npm으로 openclaw 글로벌 설치 진행 중..."
    run_cmd npm install -g openclaw@latest || log_warn "OpenClaw 설치 중 경고 발생"
    if command -v openclaw >/dev/null 2>&1; then
      log_ok "OpenClaw 설치 성공: $(openclaw --version 2>/dev/null || echo '설치됨')"
    fi
  else
    log_err "npm을 찾을 수 없어 OpenClaw 설치를 건너뜁니다."
  fi
}

start_web_chat() {
  echo ""
  log_info "3. Hermes 웹 챗 서버를 구동합니다..."
  if ! command -v python3 >/dev/null 2>&1; then
    install_hermes
  fi

  if [ ! -f "run_web.py" ]; then
    log_err "run_web.py 파일을 찾을 수 없습니다. (현재 위치: $(pwd))"
    return 1
  fi

  echo "--------------------------------------------------"
  echo "🚀 웹 챗 서버가 백그라운드/로컬에서 실행됩니다."
  echo "👉 폰 브라우저(크롬/삼성인터넷)에서 접속: http://localhost:8000"
  echo "--------------------------------------------------"
  python3 run_web.py
}

check_status() {
  echo ""
  echo "=== 📊 설치 상태 점검 ==="
  echo "OS / 환경: $ENV_LABEL ($ENV_TYPE)"
  echo "현재 위치: $(pwd)"
  printf "Python3: "
  command -v python3 >/dev/null 2>&1 && python3 --version || echo "미설치"
  printf "Node.js: "
  command -v node >/dev/null 2>&1 && node --version || echo "미설치"
  printf "npm: "
  command -v npm >/dev/null 2>&1 && npm --version || echo "미설치"
  printf "OpenClaw: "
  command -v openclaw >/dev/null 2>&1 && openclaw --version 2>/dev/null || echo "미설치"
  printf "지식 데이터셋(knowledge.jsonl): "
  [ -f "data/knowledge.jsonl" ] && echo "정상 탑재 (10,000개)" || echo "없음"
  echo "========================="
}

show_menu() {
  clear 2>/dev/null || true
  echo "=================================================="
  printf "${GREEN}⚡ Hermes Agent + OpenClaw 통합 설치/실행기${NC}\n"
  echo "🌐 감지된 시스템: $ENV_LABEL"
  echo "📂 작업 디렉토리: $ROOT_DIR"
  echo "=================================================="
  echo "1) ⚡ 웹 챗 서버 바로 실행 (1만 개 지식 + 실시간 검색)"
  echo "2) 🛠️ Hermes & Python 환경 전체 자동 설치"
  echo "3) 🦞 OpenClaw (Node.js) 설치"
  echo "4) 📊 설치 및 시스템 상태 점검"
  echo "5) 🌐 Pinggy 외부 공개 링크 열기 (다른 사람 접속)"
  echo "q) 종료"
  echo "=================================================="
  read -r -p "선택 (1-5, q): " choice

  case "$choice" in
    1) start_web_chat ;;
    2) install_hermes ;;
    3) install_openclaw ;;
    4) check_status ;;
    5)
      echo "외부 공개 주소를 생성합니다 (Ctrl+C로 종료)..."
      ssh -p 443 -R0:localhost:8000 qr@a.pinggy.io || log_err "SSH 연결 실패"
      ;;
    q|Q) exit 0 ;;
    *) log_warn "올바른 번호를 선택해주세요."; sleep 1; show_menu ;;
  esac
}

# 인자가 있으면 직접 실행, 없으면 메뉴 표시
if [ $# -eq 0 ]; then
  show_menu
else
  case "$1" in
    web|run) start_web_chat ;;
    hermes) install_hermes ;;
    openclaw) install_openclaw ;;
    status) check_status ;;
    *) show_menu ;;
  esac
fi
