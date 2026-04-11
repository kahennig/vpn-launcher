# ovpn-launcher

Multi-version OpenVPN connection manager for Linux with a **PyQt6 GUI** (KDE Plasma system tray) and a **Python CLI** companion.

Manage multiple VPN connections, each pinned to a specific OpenVPN version compiled from source. Credentials are optionally pulled from a KeePass database via `keepassxc-cli`.

![License](https://img.shields.io/badge/license-GPL--3.0-blue)

## Features

- **Multi-version OpenVPN** — run different OpenVPN versions per connection (compiled to `/opt/openvpn-<version>/`)
- **GUI** — PyQt6 app with system tray, hamburger menu, profile management, connection log with colors and search
- **CLI** — `ovpn-connect` Python CLI for headless/terminal use
- **KeePass integration** — auto-fetch VPN credentials from a KeePass database (configurable entry name per profile)
- **Build from GUI** — download and compile any OpenVPN version directly from the app
- **Settings** — configurable timeouts, reconnect delay, IP service, log level, OpenVPN prefix, KeePass DB path
- **Auto-reconnect** — exponential backoff (5s, 10s, 20s, 60s) on unexpected disconnection
- **Import/Export** — import .ovpn files or profile .zip archives, export profiles for sharing

## Requirements

- Python 3.10+
- PyQt6
- PyYAML
- `keepassxc-cli` (optional, for credential lookup)
- Build tools for compiling OpenVPN (gcc, make, libssl-dev, liblzo2-dev)

## Installation

```bash
git clone https://github.com/kahennig/vpn-launcher.git
cd vpn-launcher

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

From the GUI: click the **Build OpenVPN** button in the toolbar — it fetches available versions from GitHub and handles download, compilation, and installation.

Or from the command line:

```bash
sudo ./scripts/build-openvpn.sh 2.6.14
sudo ./scripts/build-openvpn.sh 2.5.11
```

## Configuration

Configuration lives in `~/.config/ovpn-launcher/config.yaml`:

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

- Use `system` as version to use `/usr/bin/openvpn`
- `auth_mode` is optional (defaults to `none`): `none`, `keepass`, `prompt`
- `keepass_entry` is optional — if omitted, the alias is used as the KeePass entry title
- Settings are also editable from the GUI via ☰ → Settings

Legacy `connections.conf` (pipe-delimited) is auto-migrated to YAML on first load.

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

## Project Structure

```
ovpn-launcher/
├── src/ovpn_launcher/
│   ├── __init__.py       # Version string
│   ├── app.py            # PyQt6 GUI application
│   ├── cli.py            # Python CLI companion
│   ├── builder.py        # OpenVPN download and compilation
│   ├── paths.py          # XDG-compliant path definitions
│   └── profiles.py       # YAML config loading/saving, settings, migration
├── scripts/
│   ├── ovpn-connect      # Legacy bash CLI (kept for reference)
│   └── build-openvpn.sh  # OpenVPN build script (bash)
├── tests/
│   ├── test_app.py       # GUI tests (pytest-qt)
│   ├── test_paths.py     # Path tests
│   └── test_profiles.py  # Profile/settings/migration tests
├── config/
│   ├── config.yaml.example
│   └── connections.conf.example  # Legacy format reference
├── share/
│   ├── applications/ovpn-launcher.desktop
│   └── icons/ovpn-launcher.svg
├── docs/
│   ├── architecture.md
│   ├── development.md
│   ├── migration.md
│   └── user-guide.md
├── .github/workflows/ci.yml
├── pyproject.toml
├── Makefile
└── README.md
```

## Uninstall

```bash
sudo make uninstall
```

## License

GPL-3.0-or-later — © 2026 Andreas Hennig
