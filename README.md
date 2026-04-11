# ovpn-launcher

Multi-version OpenVPN connection manager for Linux with a **PyQt6 GUI** (KDE Plasma system tray) and a **CLI** companion.

Manage multiple VPN connections, each pinned to a specific OpenVPN version compiled from source. Credentials are optionally pulled from a KeePass database via `keepassxc-cli`.

![License](https://img.shields.io/badge/license-GPL--3.0-blue)

## Features

- **Multi-version OpenVPN** — run different OpenVPN versions per connection (compiled to `/opt/openvpn-<version>/`)
- **GUI** — PyQt6 app with system tray, profile list, connection log, keyboard shortcuts
- **CLI** — `ovpn-connect` bash script for headless/terminal use
- **KeePass integration** — auto-fetch VPN credentials from a KeePass database
- **Build script** — automated download and compilation of any OpenVPN release

## Requirements

- Python 3.10+
- PyQt6
- `keepassxc-cli` (optional, for credential lookup)
- Build tools for compiling OpenVPN (gcc, make, libssl-dev, liblzo2-dev)

## Installation

```bash
git clone https://github.com/YOURUSER/ovpn-launcher.git
cd ovpn-launcher

# Install the app and CLI
sudo make install

# Create initial config (only if it doesn't exist yet)
make install-config
```

For development:

```bash
make dev  # pip install -e .
```

## Building OpenVPN Versions

```bash
sudo ./scripts/build-openvpn.sh 2.6.14
sudo ./scripts/build-openvpn.sh 2.5.11
```

This downloads, compiles, and installs to `/opt/openvpn-<version>/`.

## Configuration

Profiles live in `~/.config/ovpn-launcher/connections.conf`:

```
# Format: alias|version|config_file|auth_mode
client-a|2.6.14|/home/user/.config/ovpn-launcher/configs/client-a.ovpn|keepass
client-b|2.5.11|/home/user/.config/ovpn-launcher/configs/client-b.ovpn|prompt
office|system|/home/user/.config/ovpn-launcher/configs/office.ovpn
```

- Use `system` as version to use `/usr/bin/openvpn`
- Place `.ovpn` config files in `~/.config/ovpn-launcher/configs/` or anywhere you prefer
- `auth_mode` is optional (defaults to `none`):
  - `none` — connect without credentials
  - `keepass` — fetch credentials from KeePass database
  - `prompt` — ask for username and password interactively

### KeePass Integration

Set `OVPN_KEEPASS_DB` to point to your KeePass database, or it defaults to `~/Document/Keepass/keepass.kdbx`. The entry title in KeePass must match the profile alias.

## Usage

### GUI

```bash
ovpn-app
```

- Double-click or `Ctrl+Enter` to connect
- `Ctrl+D` to disconnect
- Minimizes to system tray on close

### CLI

```bash
ovpn-connect <alias>                  # connect using a profile
ovpn-connect <version> <config.ovpn>  # direct mode
ovpn-connect --list                   # list versions and profiles
ovpn-connect --add                    # add a new profile interactively
ovpn-connect --status                 # check if openvpn is running
```

## Project Structure

```
ovpn-launcher/
├── src/ovpn_launcher/
│   ├── __init__.py
│   ├── app.py          # PyQt6 GUI application
│   ├── paths.py        # XDG-compliant path definitions
│   └── profiles.py     # Profile loading logic
├── scripts/
│   ├── ovpn-connect    # CLI bash script
│   └── build-openvpn.sh # OpenVPN build automation
├── config/
│   └── connections.conf.example
├── share/applications/
│   └── ovpn-launcher.desktop
├── pyproject.toml
├── Makefile
└── README.md
```

## Uninstall

```bash
sudo make uninstall
```

## License

GPL-3.0-or-later
