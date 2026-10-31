#!/usr/bin/env bash
set -Eeuo pipefail

# Hermes Agent + OpenClaw helper for Termux and Haven (Debian / Ubuntu / Linux).
# Works on both Android Termux and Haven / Debian VM environments.

EXPECTED_FINGERPRINT="C572B5FDD1A29CCFA9A912B6840B0848E139156D"
REPO_URL="https://hermes-assets.nousresearch.com/releases/termux/canary"

die() { printf '\n[ERROR] %s\n' "$*" >&2; exit 1; }
confirm() {
  local answer
  read -r -p "$1 Type $2 to continue: " answer
  [ "$answer" = "$2" ]
}

# 환경 자동 감지 (Termux vs Haven Debian/Ubuntu)
if [ -n "${PREFIX:-}" ] && [ "$PREFIX" = "/data/data/com.termux/files/usr" ]; then
  ENV_TYPE="termux"
  echo "[환경 감지] Android Termux 환경입니다."
elif command -v apt-get >/dev/null 2>&1 || command -v apt >/dev/null 2>&1; then
  ENV_TYPE="haven"
  echo "[환경 감지] Haven / Debian / Ubuntu 환경입니다."
else
  ENV_TYPE="linux"
  echo "[환경 감지] 일반 Linux 환경입니다."
fi

pkg_install() {
  local pkgs="$*"
  if [ "$ENV_TYPE" = "termux" ]; then
    pkg install -y $pkgs
  elif [ "$ENV_TYPE" = "haven" ] || [ "$ENV_TYPE" = "linux" ]; then
    if [ "$(id -u)" -eq 0 ]; then
      apt-get update && apt-get install -y $pkgs
    elif command -v sudo >/dev/null 2>&1; then
      sudo apt-get update && sudo apt-get install -y $pkgs
    else
      apt-get update && apt-get install -y $pkgs
    fi
  fi
}

hermes_action() {
  if [ "$ENV_TYPE" = "termux" ]; then
    echo "[NOTICE] Termux 공식 패키지 저장소를 확인합니다."
    confirm "Termux 저장소 업데이트 및 패키지 설치를 진행할까요?" "YES" || return 0
    pkg update -y && pkg upgrade -y
    pkg_install curl gnupg
    mkdir -p "$PREFIX/etc/apt/keyrings" "$PREFIX/etc/apt/sources.list.d"
    local key fingerprint
    key="$(mktemp)"
    curl -fsSL "$REPO_URL/key.asc" -o "$key"
    fingerprint="$(gpg --batch --show-keys --with-colons "$key" | awk -F: '$1=="fpr" {print toupper($10); exit}')"
    rm -f "$key"
    if [ "$fingerprint" = "$EXPECTED_FINGERPRINT" ]; then
      curl -fsSL "$REPO_URL/key.asc" -o "$PREFIX/etc/apt/keyrings/hermes-agent.asc"
      printf '%s\n' "deb [signed-by=$PREFIX/etc/apt/keyrings/hermes-agent.asc] $REPO_URL hermes-canary main" > "$PREFIX/etc/apt/sources.list.d/hermes-agent.list"
      pkg update
      pkg install -y hermes-agent || true
    fi
  else
    echo "[Haven/Linux] Python 기반 Hermes 환경을 준비합니다."
    pkg_install python3 python3-pip curl
  fi
  echo "[완료] Hermes 환경 준비가 끝났습니다."
}

ensure_node_npm() {
  if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
    echo "[INFO] Node.js 및 npm 설치를 시도합니다..."
    if [ "$ENV_TYPE" = "termux" ]; then
      pkg_install nodejs-lts
    else
      pkg_install nodejs npm
    fi
  fi
  command -v node >/dev/null 2>&1 && echo "Node.js: $(node --version)" || echo "Node.js: 미설치"
  command -v npm >/dev/null 2>&1 && echo "npm: $(npm --version)" || echo "npm: 미설치"
}

openclaw_action() {
  echo "[NOTICE] OpenClaw를 npm으로 설치합니다."
  ensure_node_npm
  if command -v npm >/dev/null 2>&1; then
    npm install -g openclaw@latest || true
    echo "설치 확인: openclaw --version"
  fi
}

run_web_server() {
  echo "[실행] 10,000 지식 기반 Hermes 웹 챗 서버를 구동합니다..."
  python3 run_web.py
}

echo "============================================="
echo "⚡ Hermes Agent + OpenClaw 설치/실행 도우미"
echo "🌐 감지된 시스템: $ENV_TYPE"
echo "============================================="
echo "1) Hermes 환경 자동 설치/업데이트"
echo "2) OpenClaw (Node.js) 설치/업데이트"
echo "3) 전체 자동 설치 (Hermes + OpenClaw)"
echo "4) ⚡ 웹 챗 서버 바로 실행 (python3 run_web.py)"
echo "5) 설치된 버전 상태 점검"
echo "============================================="
read -r -p "선택 (1-5): " choice
case "$choice" in
  1) hermes_action ;;
  2) openclaw_action ;;
  3) hermes_action; openclaw_action ;;
  4) run_web_server ;;
  5)
    command -v hermes >/dev/null 2>&1 && hermes --version || echo "Hermes: not found"
    command -v openclaw >/dev/null 2>&1 && openclaw --version || echo "OpenClaw: not found"
    command -v python3 >/dev/null 2>&1 && python3 --version || echo "Python: not found"
    command -v node >/dev/null 2>&1 && node --version || echo "Node.js: not found"
    command -v npm >/dev/null 2>&1 && npm --version || echo "npm: not found"
    ;;
  *) die "올바른 번호를 선택해주세요." ;;
esac
echo "스크립트 작업이 완료되었습니다."
