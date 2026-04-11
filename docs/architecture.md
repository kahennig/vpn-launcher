# Architecture

## Component Overview

```
┌─────────────────────────────────────────────────┐
│                  User                            │
│         ┌──────────┐  ┌──────────────┐          │
│         │ ovpn-app │  │ ovpn-connect │          │
│         │  (GUI)   │  │    (CLI)     │          │
│         └────┬─────┘  └──────┬───────┘          │
│              │               │                   │
│         ┌────▼───────────────▼───────┐          │
│         │     paths.py + profiles.py │          │
│         │  (shared config & loading) │          │
│         └────────────┬───────────────┘          │
│                      │                           │
│         ┌────────────▼───────────────┐          │
│         │ ~/.config/ovpn-launcher/   │          │
│         │  connections.conf          │          │
│         │  configs/*.ovpn            │          │
│         └────────────────────────────┘          │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ /opt/openvpn-<ver>/sbin/openvpn           │  │
│  │ /usr/bin/openvpn (system)                 │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  ┌───────────────────────────────────────────┐  │
│  │ keepassxc-cli (optional)                  │  │
│  │ ~/Document/Keepass/keepass.kdbx           │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## Connection Flow

### GUI (ovpn-app)

1. User selects a profile from the tree widget
2. App resolves the OpenVPN binary path via `paths.openvpn_binary(version)`
3. Based on `auth_mode`:
   - `none` — no credentials, connect directly
   - `keepass` — prompts for master password, fetches user/pass from KeePass via `keepassxc-cli`
   - `prompt` — shows two QInputDialog prompts for username and password
4. Writes credentials to a temp file (0600 permissions) if obtained
5. Launches `pkexec <openvpn-binary> --config <file> [--auth-user-pass <authfile>]` via QProcess
6. Starts a 30-second connection timeout timer
7. Monitors stdout for "Initialization Sequence Completed" to update state
8. On disconnect: sends kill via `pkexec kill <pid>`, cleans up auth file
9. On unexpected process exit (crash): auto-reconnects after 5 seconds

### CLI (ovpn-connect)

1. Resolves profile from connections.conf (alias mode) or takes version+config directly
2. Same auth_mode logic: `none` (direct), `keepass` (terminal prompt), `prompt` (read -p)
3. Launches `sudo <openvpn-binary> --config <file> [--auth-user-pass <authfile>]`
4. Trap cleans up auth file on exit

## Privilege Escalation

- GUI uses `pkexec` (Polkit) — required because sudo doesn't work well with graphical apps
- CLI uses `sudo` — standard for terminal usage

## Config Format

`connections.conf` uses a pipe-delimited format:

```
alias|version|config_path|auth_mode
```

- `alias` — human-readable name, also used as KeePass entry lookup key
- `version` — either "system" or a version string like "2.6.14"
- `config_path` — absolute path to the .ovpn file
- `auth_mode` — optional (defaults to `none`): `none`, `keepass`, or `prompt`

## GUI Features

- **Profile management** — Add, Edit, Remove, Import .ovpn from toolbar
- **Profile filter** — QLineEdit above tree for quick filtering by name
- **Drag & drop** — Reorder profiles by dragging in the tree
- **Connection timeout** — 30-second timer with warning dialog
- **Auto-reconnect** — Reconnects after 5 seconds on unexpected disconnection
- **Tray notifications** — Desktop notifications on connect/disconnect
- **System tray** — Minimize to tray, connect from tray menu
- **About dialog** — Version, license, author info (Help → About)

## OpenVPN Version Management

Versions are compiled from source to isolated prefixes:

```
/opt/openvpn-2.6.14/
├── sbin/openvpn      # the binary
├── lib/              # libraries
├── include/          # headers
└── share/            # man pages, docs
```

The `--disable-dco` flag is used during compilation to avoid build conflicts with newer kernel headers.

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|------------|
| `XDG_CONFIG_HOME` | `~/.config` | Base config directory |
| `OVPN_CONF` | `$XDG_CONFIG_HOME/ovpn-launcher/connections.conf` | CLI config path override |
| `OVPN_KEEPASS_DB` | `~/Document/Keepass/keepass.kdbx` | KeePass database path |
| `KPPASS` | (none) | Pre-set KeePass master password for CLI (avoids prompt) |
