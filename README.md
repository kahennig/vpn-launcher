# ovpn-launcher

Multi-version OpenVPN connection manager for **Linux** and **Windows** with a **PyQt6 GUI** and a **Python CLI** companion.

Manage multiple VPN connections, each pinned to a specific OpenVPN version. Credentials are optionally pulled from a KeePass database via `keepassxc-cli`.

![License](https://img.shields.io/badge/license-GPL--3.0-blue)

## Features

- **Multi-version OpenVPN** — run different OpenVPN versions per connection
- **Cross-platform** — Linux (KDE Plasma tray) and Windows (Fusion style, NSIS installer)
- **GUI** — PyQt6 app with system tray, hamburger menu, profile management, connection log with colors and search
- **CLI** — `ovpn-connect` Python CLI for headless/terminal use
- **KeePass integration** — auto-fetch VPN credentials from a KeePass database (configurable entry name per profile)
- **Build / Install from GUI** — compile OpenVPN from source (Linux) or extract from official MSI (Windows)
- **Settings** — configurable timeouts, reconnect delay, IP service, log level, OpenVPN prefix, KeePass DB path
- **Auto-reconnect** — exponential backoff (5s, 10s, 20s, 60s) on unexpected disconnection
- **Import/Export** — import .ovpn files or profile .zip archives, export profiles for sharing

## Installation

### Linux

```bash
git clone https://github.com/kahennig/vpn-launcher.git
cd vpn-launcher
sudo make install
make install-config  # creates initial config (only if it doesn't exist)
```

Requirements: Python 3.10+, PyQt6, PyYAML, build tools for compiling OpenVPN (gcc, make, libssl-dev, liblzo2-dev).

### Windows

Download from [Releases](https://github.com/kahennig/vpn-launcher/releases):
- **`ovpn-launcher-setup.exe`** — installer with Start Menu shortcut, Desktop shortcut, and uninstaller
- **`ovpn-launcher.exe`** — standalone portable executable

The app requests Administrator privileges on launch (required for OpenVPN routing).

For development:
```bash
make dev  # Linux: pip install -e .
pip install -e .  # Windows
```

## Configuration

Configuration file location:

| Platform | Path |
|----------|------|
| Linux | `~/.config/ovpn-launcher/config.yaml` |
| Windows | `%APPDATA%\ovpn-launcher\config.yaml` |

```yaml
settings:
  openvpn_prefix: /opt
  keepass_db: ~/Document/Keepass/keepass.kdbx
  connection_timeout: 30
  reconnect_delay: 5
  ip_service: https://api.ipify.org
  log_level: WARNING

profiles:
  - alias: client-a
    version: "2.6.14"
    config: /home/user/.config/ovpn-launcher/configs/client-a.ovpn
    auth_mode: keepass
    keepass_entry: VPN Client A

  - alias: office
    version: system
    config: /home/user/.config/ovpn-launcher/configs/office.ovpn
```

- Use `system` as version to use the system-installed OpenVPN
- `auth_mode`: `none` (default), `keepass`, `prompt`
- Settings are editable from the GUI via ☰ → Settings

## Usage

### GUI

```bash
ovpn-app
```

- Double-click or `Ctrl+Enter` to connect
- `Ctrl+D` to disconnect
- `Ctrl+N` to add profile, `Ctrl+E` to edit, `Delete` to remove
- `Ctrl+F` to search in log, `Ctrl+Shift+C` to copy log
- Minimizes to system tray on close

### CLI

```bash
ovpn-connect <alias>                  # connect using a profile
ovpn-connect <version> <config.ovpn>  # direct mode
ovpn-connect --list                   # list versions and profiles
ovpn-connect --add                    # add a new profile interactively
ovpn-connect --edit <alias>           # edit a profile
ovpn-connect --remove <alias>         # remove a profile
ovpn-connect --status                 # check if openvpn is running
ovpn-connect --version                # show version
```

## Building OpenVPN Versions

From the GUI: click **Build OpenVPN** in the toolbar — it fetches available versions from GitHub.

- **Linux**: downloads source, compiles, and installs to `/opt/openvpn-<version>/`
- **Windows**: downloads official MSI, extracts `openvpn.exe` + required DLLs to `%LOCALAPPDATA%\ovpn-launcher\openvpn\openvpn-<version>\`

## Project Structure

```
ovpn-launcher/
├── src/ovpn_launcher/
│   ├── __init__.py       # Version string
│   ├── app.py            # PyQt6 GUI application
│   ├── cli.py            # Python CLI companion
│   ├── dialogs.py        # GUI dialogs (Profile, Settings, Build)
│   ├── services.py       # Business logic (no Qt dependency)
│   ├── builder.py        # OpenVPN download, compilation, MSI extraction
│   ├── paths.py          # Cross-platform path definitions
│   └── profiles.py       # YAML config loading/saving, settings, migration
├── scripts/
│   ├── ovpn-connect      # Legacy bash CLI (kept for reference)
│   └── build-openvpn.sh  # OpenVPN build script (bash)
├── tests/                # 105 tests (pytest + pytest-qt)
├── config/               # Example config files
├── share/
│   ├── applications/ovpn-launcher.desktop
│   └── icons/            # App icon (SVG, ICO) + bundled Breeze themes
├── docs/                 # Architecture, development, user guide
├── installer.nsi         # NSIS installer script (Windows)
├── ovpn-launcher.spec    # PyInstaller spec (Windows)
├── .github/workflows/    # CI + Windows build pipeline
├── pyproject.toml
├── Makefile
└── README.md
```

## Uninstall

### Linux
```bash
sudo make uninstall
```

### Windows
Use Add/Remove Programs, or run the uninstaller from the Start Menu.

## License

GPL-3.0-or-later — © 2026 Andreas Hennig
