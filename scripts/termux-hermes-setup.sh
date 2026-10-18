#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

# Hermes Agent + OpenClaw helper for standard Android Termux (aarch64).
# Hermes official Termux guide has reported a package issue; OpenClaw Android support may vary.
# This script does not intentionally delete projects or user data.

EXPECTED_FINGERPRINT="C572B5FDD1A29CCFA9A912B6840B0848E139156D"
REPO_URL="https://hermes-assets.nousresearch.com/releases/termux/stable"

die() { printf '\n[ERROR] %s\n' "$*" >&2; exit 1; }
confirm() {
  local answer
  read -r -p "$1 Type $2 to continue: " answer
  [ "$answer" = "$2" ]
}

[ "${PREFIX:-}" = "/data/data/com.termux/files/usr" ] || die "Run in the main Termux shell, not Debian/proot."
[ "$(uname -m)" = "aarch64" ] || die "Expected aarch64, got $(uname -m)."
command -v pkg >/dev/null 2>&1 || die "Termux pkg command not found."

hermes_action() {
  echo "[WARNING] Official Hermes Termux guide currently reports that the package is broken and a fix is in progress."
  echo "Guide: https://hermes-agent.nousresearch.com/docs/getting-started/termux"
  confirm "Attempt Hermes install/update anyway?" "HERMES-TRY" || return 0
  pkg install -y curl gnupg
  mkdir -p "$PREFIX/etc/apt/keyrings" "$PREFIX/etc/apt/sources.list.d"
  local key fingerprint
  key="$(mktemp)"
  curl -fsSL "$REPO_URL/key.asc" -o "$key"
  fingerprint="$(gpg --batch --show-keys --with-colons "$key" | awk -F: '$1=="fpr" {print toupper($10); exit}')"
  rm -f "$key"
  [ "$fingerprint" = "$EXPECTED_FINGERPRINT" ] || die "Hermes signing-key fingerprint mismatch; stopped."
  curl -fsSL "$REPO_URL/key.asc" -o "$PREFIX/etc/apt/keyrings/hermes-agent.asc"
  printf '%s\n' "deb [signed-by=$PREFIX/etc/apt/keyrings/hermes-agent.asc] $REPO_URL hermes-stable main" > "$PREFIX/etc/apt/sources.list.d/hermes-agent.list"
  pkg update
  pkg install hermes-agent
  hermes --version || true
}

ensure_node_npm() {
  if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
    echo "[INFO] Node.js and/or npm not found. Installing Termux nodejs-lts package..."
    pkg install nodejs-lts
  fi
  command -v node >/dev/null 2>&1 || die "Node.js is unavailable after installation attempt."
  command -v npm >/dev/null 2>&1 || die "npm is unavailable after installation attempt."
  echo "Node.js: $(node --version)"
  echo "npm: $(npm --version)"
}

openclaw_action() {
  echo "[NOTICE] OpenClaw is installed/updated via npm; Android/Termux compatibility may vary."
  echo "Upstream: https://github.com/openclaw/openclaw"
  confirm "Install Node.js/npm if needed, then install/update OpenClaw?" "OPENCLAW-TRY" || return 0
  ensure_node_npm
  npm install -g openclaw@latest
  openclaw --version || true
  echo "For first-time setup, run: openclaw onboard"
}

echo "=== Hermes Agent + OpenClaw / Termux ==="
echo "1) Install/update Hermes Agent"
echo "2) Install/update OpenClaw"
echo "3) Attempt both"
echo "4) Install/check Node.js and npm"
echo "5) Check installed versions only"
read -r -p "Choose 1-5: " choice
case "$choice" in
  1) hermes_action ;;
  2) openclaw_action ;;
  3) hermes_action; openclaw_action ;;
  4) ensure_node_npm ;;
  5)
    command -v hermes >/dev/null 2>&1 && hermes --version || echo "Hermes: not found"
    command -v openclaw >/dev/null 2>&1 && openclaw --version || echo "OpenClaw: not found"
    command -v node >/dev/null 2>&1 && node --version || echo "Node.js: not found"
    command -v npm >/dev/null 2>&1 && npm --version || echo "npm: not found"
    ;;
  *) die "Invalid choice." ;;
esac
echo "Script finished. Verify the command output; this is not proof that either agent runs successfully."
