# Architecture

## Component Overview

```
┌─────────────────────────────────────────────────┐
│                  User                            │
│         ┌──────────┐  ┌──────────────┐          │
│         │ ovpn-app │  │ ovpn-connect │          │
│         │  (GUI)   │  │ (Python CLI) │          │
│         └────┬─────┘  └──────┬───────┘          │
│              │               │                   │
│    ┌─────────▼───────────────▼──────────┐       │
│    │  paths.py + profiles.py + builder.py│       │
│    │  (shared config, loading, building) │       │
│    └─────────────────┬──────────────────┘       │
│                      │                           │
│         ┌────────────▼───────────────┐          │
│         │ ~/.config/ovpn-launcher/   │          │
│         │  config.yaml               │          │
│         │  configs/*.ovpn            │          │
│         │  logs/*.log                │          │
│         └────────────────────────────┘          │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ /opt/openvpn-<ver>/sbin/openvpn           │  │
│  │ /usr/bin/openvpn (system)                 │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ keepassxc-cli (optional)                  │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Modules

| Module | Responsibility |
|--------|---------------|
| `app.py` | PyQt6 GUI: VPNLauncher, ProfileDialog, SettingsDialog, BuildDialog |
| `cli.py` | Python CLI: argparse, connect, add, edit, remove, list, status |
| `profiles.py` | YAML config: load/save profiles, load/save settings, migration, detect_versions |
| `paths.py` | Path constants: CONFIG_DIR, CONFIG_YAML, LOG_DIR, AUTOSTART, openvpn_binary() |
| `builder.py` | OpenVPN build: fetch_available_versions (GitHub API), build_openvpn (download, compile, install) |

## Connection Flow

### GUI (ovpn-app)

1. User selects a profile from the tree widget
2. App validates .ovpn (checks for `remote` and `dev` directives)
3. App resolves the OpenVPN binary path via `paths.openvpn_binary(version, prefix)`
4. Based on `auth_mode`:
   - `none` — no credentials, connect directly
   - `keepass` — prompts for master password, fetches user/pass from KeePass via `keepassxc-cli` (uses `keepass_entry` or alias)
   - `prompt` — shows two QInputDialog prompts for username and password
5. Writes credentials to a temp file (0600 permissions) if obtained
6. Launches `pkexec <openvpn-binary> --config <file> [--auth-user-pass <authfile>]` via QProcess
7. Starts connection timeout timer (configurable, default 30s)
8. Opens log file in `~/.config/ovpn-launcher/logs/`
9. Monitors stdout for "Initialization Sequence Completed" to update state
10. On connect: saves `last_connected` timestamp, fetches public IP, shows notification with IP
11. On disconnect: sends kill via `pkexec kill <pid>`, cleans up auth file and log file
12. On unexpected process exit: auto-reconnects with exponential backoff (5s, 10s, 20s, 60s, max 5 attempts)

### CLI (ovpn-connect)

1. Resolves profile from config.yaml (alias mode) or takes version+config directly
2. Same auth_mode logic: `none` (direct), `keepass` (getpass), `prompt` (input)
3. Launches `sudo <openvpn-binary> --config <file> [--auth-user-pass <authfile>]`
4. atexit cleans up auth file

## Config Format (YAML)

`~/.config/ovpn-launcher/config.yaml`:

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
    config: /path/to/client-a.ovpn
    auth_mode: keepass
    keepass_entry: VPN Client A
    last_connected: "2026-04-10 15:30"
```

Legacy `connections.conf` (pipe-delimited) is auto-migrated on first load.

## Privilege Escalation

- GUI uses `pkexec` (Polkit) — required because sudo doesn't work well with graphical apps
- CLI uses `sudo` — standard for terminal usage

## GUI Features

- **Hamburger menu** — all actions in one place (KDE Dolphin/Kate style)
- **Profile management** — Add, Edit, Remove, Import .ovpn, Import/Export .zip
- **Build OpenVPN** — download and compile versions from GUI (fetches from GitHub API)
- **Profile filter** — QLineEdit for quick filtering by name
- **Drag & drop** — reorder profiles
- **Config validation** — warning icon if binary or config missing
- **Connection timeout** — configurable timer with warning dialog
- **Auto-reconnect** — exponential backoff, max 5 attempts
- **Log colors** — errors red, warnings orange, success green
- **Log search** — Ctrl+F with find next
- **Log copy** — Ctrl+Shift+C or double-click line
- **Persistent logs** — saved to `~/.config/ovpn-launcher/logs/`
- **Tray notifications** — connect (with IP), disconnect
- **System tray** — minimize to tray, quick-connect menu with active profile indicator
- **Connection timer** — elapsed time in status bar
- **Public IP** — displayed in status bar, updates on state change
- **Profile counter** — "N profiles" in status bar
- **Last connected** — timestamp per profile
- **Settings dialog** — all settings editable from GUI
- **Autostart** — toggle from hamburger menu
- **About dialog** — version, features, author, license
- **Custom icon** — SVG shield with lock
- **Splash screen** — shown during startup

## OpenVPN Version Management

Versions are compiled from source to isolated prefixes:

```
/opt/openvpn-2.6.14/
├── sbin/openvpn
├── lib/
├── include/
└── share/
```

Available versions are fetched from GitHub API (`OpenVPN/openvpn` tags). The `--disable-dco` flag is used during compilation.

## Settings

All configurable via GUI (☰ → Settings) or `config.yaml`:

| Setting | Default | Description |
|---------|---------|-------------|
| `openvpn_prefix` | `/opt` | Directory for compiled OpenVPN versions |
| `keepass_db` | `~/Document/Keepass/keepass.kdbx` | KeePass database path |
| `connection_timeout` | `30` | Seconds before timeout warning |
| `reconnect_delay` | `5` | Base delay for auto-reconnect backoff |
| `ip_service` | `https://api.ipify.org` | Public IP lookup service |
| `log_level` | `WARNING` | Python logging level (overridable via `OVPN_LOG_LEVEL` env var) |
