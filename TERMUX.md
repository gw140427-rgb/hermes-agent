# Hermes Agent — Android Termux helper

This repository includes a cautious helper script for the official Hermes Agent APT package on standard Android Termux (aarch64).

## Important current status

The official guide currently warns that **the Termux package is broken and a fix is in progress**. The script does not claim the package is currently working and asks for confirmation before attempting installation.

Official guide: https://hermes-agent.nousresearch.com/docs/getting-started/termux  
Upstream source: https://github.com/NousResearch/hermes-agent

## Use

Download `scripts/termux-hermes-setup.sh` into Termux, then run:

```bash
bash ~/termux-hermes-setup.sh
```

The script checks the standard Termux prefix and `aarch64`, downloads the official repository key, verifies its fingerprint (`C572 B5FD D1A2 9CCF A9A9 12B6 840B 0848 E139 156D`), adds the official stable APT source, and asks again before installing the package.

Do not run this in Debian/proot. Do not disable APT signature verification. This helper does not remove existing files or user data.

After a successful install, try:

```bash
hermes --version
hermes doctor
hermes setup
hermes --tui
```

Actual installation and runtime have not been tested on every Android device. Termux background processes can be stopped by Android, and some desktop-only integrations are unavailable.
