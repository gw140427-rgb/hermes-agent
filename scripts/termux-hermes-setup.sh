#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

# Hermes Agent official Termux APT setup helper.
# Official guide: https://hermes-agent.nousresearch.com/docs/getting-started/termux
# The official guide currently warns that the Termux package is broken and a fix is in progress.
# This script checks the architecture and signing-key fingerprint before adding the repo.
# It never deletes NeoOS, OpenClaw, or Hermes user data.

EXPECTED_FINGERPRINT="C572B5FDD1A29CCFA9A912B6840B0848E139156D"
REPO_URL="https://hermes-assets.nousresearch.com/releases/termux/stable"
KEY_PATH="${PREFIX:?Run inside standard Termux}/etc/apt/keyrings/hermes-agent.asc"
LIST_PATH="$PREFIX/etc/apt/sources.list.d/hermes-agent.list"

die() { printf '\n[ERROR] %s\n' "$*" >&2; exit 1; }

printf '%s\n' "=== Hermes Agent / Termux setup helper ==="
[ "$PREFIX" = "/data/data/com.termux/files/usr" ] || die "Unsupported prefix: ${PREFIX:-unset}"
[ "$(uname -m)" = "aarch64" ] || die "Expected aarch64, got: $(uname -m)"
command -v pkg >/dev/null 2>&1 || die "pkg not found; run this in Termux base shell, not Debian/proot."

printf '[OK] Architecture: %s\n' "$(uname -m)"
printf '[OK] Prefix: %s\n' "$PREFIX"
printf '\n[WARNING] Official guide currently says the Termux package is broken; a fix is in progress.\n'
printf 'Guide: https://hermes-agent.nousresearch.com/docs/getting-started/termux\n'
read -r -p 'Type CHECK-AND-INSTALL to continue: ' answer
[ "$answer" = "CHECK-AND-INSTALL" ] || { echo "Cancelled; no repository changes made."; exit 0; }

pkg install -y curl gnupg
mkdir -p "$PREFIX/etc/apt/keyrings" "$PREFIX/etc/apt/sources.list.d"
tmp_key="$(mktemp)"
trap 'rm -f "$tmp_key"' EXIT
curl -fsSL "$REPO_URL/key.asc" -o "$tmp_key"

fingerprint="$(gpg --batch --show-keys --with-colons "$tmp_key" | awk -F: '$1=="fpr" {print toupper($10); exit}')"
printf 'Signing key fingerprint: %s\n' "${fingerprint:-unreadable}"
[ "$fingerprint" = "$EXPECTED_FINGERPRINT" ] || die "Fingerprint mismatch. Stopped; do not bypass signature verification."

install -m 0644 "$tmp_key" "$KEY_PATH"
printf '%s\n' "deb [signed-by=$KEY_PATH] $REPO_URL hermes-stable main" > "$LIST_PATH"
echo "[OK] Fingerprint matched; repository configured."
pkg update

echo
echo "[WARNING] Official docs currently report the Termux package as broken."
read -r -p 'Type INSTALL-ANYWAY only if you want to attempt installation despite this warning: ' answer2
[ "$answer2" = "INSTALL-ANYWAY" ] || { echo "Stopped before installing Hermes. Repository remains configured."; exit 0; }

pkg install hermes-agent
echo
echo "Verify: hermes --version"
echo "Diagnose: hermes doctor"
echo "Configure provider: hermes setup"
echo "Start TUI: hermes --tui"
