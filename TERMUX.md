# Hermes Agent + OpenClaw — Android Termux helper

This repository includes an install/update helper for standard Android Termux on **aarch64**.

## Run it

Download `scripts/termux-hermes-setup.sh` into Termux and run:

```bash
bash ~/termux-hermes-setup.sh
```

Choose an action:
- **1** — attempt Hermes Agent install/update
- **2** — install/update OpenClaw
- **3** — attempt both
- **4** — check installed versions

The script asks for confirmation before installing or updating either agent. It does not intentionally delete existing projects or user data.

## Hermes Agent

The official Hermes Termux guide has reported that its package is broken and a fix is in progress. The script preserves this warning, checks the repository signing-key fingerprint (`C572 B5FD D1A2 9CCF A9A9 12B6 840B 0848 E139 156D`), and keeps APT signature verification enabled.

Official guide: https://hermes-agent.nousresearch.com/docs/getting-started/termux  
Upstream: https://github.com/NousResearch/hermes-agent

If installation succeeds, check with:

```bash
hermes --version
hermes doctor
hermes setup
hermes --tui
```

## OpenClaw

The script installs Node.js LTS through Termux if `npm` is missing, then runs `npm install -g openclaw@latest` to install or update OpenClaw.

Upstream: https://github.com/openclaw/openclaw

Android/Termux compatibility can vary, so this is an install/update attempt rather than a guarantee that OpenClaw will run. After a first successful install, run:

```bash
openclaw onboard
openclaw --version
```

## Limitations

- Run in the main Termux shell, not Debian/proot.
- Requires an ARM64/aarch64 Android environment.
- The script has not been run on the user's phone; actual installation and runtime are unverified.
- Android may stop background processes, and some integrations may not work on mobile.
