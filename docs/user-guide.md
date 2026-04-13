# User Guide

## Description

VPN Launcher is a multi-version OpenVPN connection manager for Linux and Windows. It lets you manage multiple VPN profiles, each pinned to a specific OpenVPN version, with optional KeePass credential integration.

## Getting Started

### Linux
1. Launch the app: `ovpn-app` or from your application menu (VPN Launcher)
2. Add a profile: click **Add Profile** in the toolbar (or `Ctrl+N`)
3. Select a profile and click **Connect** (or double-click)

### Windows
1. Run the installer (`ovpn-launcher-setup.exe`) or the standalone `ovpn-launcher.exe`
2. The app requests Administrator privileges on launch (required for OpenVPN routing)
3. Add a profile and connect as above

## Main Window

The main window has:
- **Toolbar** — icons for: Connect, Disconnect, Add, Edit, Remove, Import .ovpn, Import Profile, Export Profile, Build OpenVPN, Reload, Clear Log, Copy Log, and ☰ hamburger menu
- **Filter** — text field to filter profiles by name
- **Profile list** — table with columns: Profile, OpenVPN Version, Config File, Auth, KeePass Entry, Last Connected
- **Connection log** — real-time output from OpenVPN with color coding (errors in red, warnings in orange, success in green)
- **Search bar** — `Ctrl+F` to search in the log
- **Status bar** — connection state with timer, profile count, and public IP

## Hamburger Menu (☰)

All actions are accessible from the hamburger menu at the right end of the toolbar:
- Connect / Disconnect
- Add, Edit, Remove profiles
- Import .ovpn, Import Profile (.zip), Export Profile
- Ping Server, DNS Check, List Adapters (Windows), Build OpenVPN
- Open Configs Folder, Open Logs Folder
- Reload, Clear Log, Copy Log
- Start at Login, Settings
- About, Quit

## Managing Profiles

### Add a Profile
1. Click **Add Profile** or press `Ctrl+N`
2. Fill in: Alias, OpenVPN Version (dropdown with detected versions + system, or type manually), Config File (use Browse), Auth Mode
3. If auth mode is `keepass`, optionally set a KeePass Entry name (defaults to alias)
4. Click OK

### Import an .ovpn File
1. Click **Import .ovpn** in the toolbar
2. Select the .ovpn file — it gets copied to `~/.config/ovpn-launcher/configs/`
3. Review the pre-filled profile dialog and click OK

### Import a Profile (.zip)
1. Click **Import Profile** in the toolbar
2. Select a .zip file previously exported from the app
3. The .ovpn is extracted and the profile dialog is pre-filled

### Export a Profile
1. Select a profile in the list
2. Click **Export Profile** — saves a .zip with the .ovpn and profile metadata

### Edit a Profile
1. Select a profile and click **Edit Profile** or press `Ctrl+E`
2. Modify fields and click OK

### Remove a Profile
1. Select a profile and press `Delete` or click **Remove Profile**
2. Confirm the deletion

### Reorder Profiles
Drag and drop profiles in the list to change their order. The new order is saved automatically.

## Connecting

1. Select a profile
2. Click **Connect** or press `Ctrl+Enter` (or double-click the profile)
3. Depending on the auth mode:
   - **none** — connects directly
   - **keepass** — prompts for your KeePass master password, then fetches credentials
   - **prompt** — asks for username and password
4. The connection log shows OpenVPN output in real-time with color coding
5. Status bar shows connection state, elapsed time, and public IP
6. The connected profile is highlighted in bold in the tree and tray menu

### Connection Timeout
If the connection doesn't complete within the configured timeout (default 30s), a warning dialog appears asking if you want to disconnect or keep waiting.

### Auto-Reconnect
If the VPN connection drops unexpectedly (not a manual disconnect), the app automatically reconnects with exponential backoff: 5s, 10s, 20s, 60s. It gives up after 5 attempts.

### Switching Profiles
If you're connected and try to connect to a different profile, the app asks for confirmation before disconnecting and reconnecting.

## Disconnecting

Click **Disconnect** or press `Ctrl+D`. You can also disconnect from the system tray menu.

## Building OpenVPN Versions

1. Click **Build OpenVPN** in the toolbar (or ☰ → Build OpenVPN)
2. Select a version from the dropdown (fetched from GitHub) or type one manually
3. Click **Build** — the app downloads, compiles, and installs the version
4. Versions already installed are marked in the dropdown

## System Tray

- The app minimizes to the system tray when you close the window
- Left-click the tray icon to show/hide the window
- Right-click for a menu with: profile quick-connect (active profile marked with ▶), Show/Hide, Disconnect, Quit
- Desktop notifications appear on connect (with IP) and disconnect

## Settings

Accessible from ☰ → Settings:

| Setting | Description | Default |
|---------|-------------|---------|
| OpenVPN Prefix | Directory for compiled OpenVPN versions | /opt |
| KeePass DB | Path to KeePass database | ~/Document/Keepass/keepass.kdbx |
| Connection Timeout | Seconds before timeout warning | 30 |
| Reconnect Delay | Base delay for auto-reconnect | 5 |
| IP Service URL | Service for public IP lookup | https://api.ipify.org |
| Log Level | Application log level | WARNING |

Settings are stored in `~/.config/ovpn-launcher/config.yaml`.

## Network Tools

- **Ping Server** (☰ menu): pings the VPN server from the .ovpn config and shows latency in the log
- **DNS Check** (☰ menu): shows the current DNS resolver IP to detect DNS leaks
- **List Adapters** (☰ menu, Windows only): lists virtual network adapters (wintun/TAP) via `tapctl.exe`
- **Public IP**: displayed in the status bar, updates on connect/disconnect

## Connection Log

- Color coded: errors (red), warnings (orange), success (green), internal messages (muted)
- `Ctrl+F` to search in the log
- `Ctrl+Shift+C` to copy entire log to clipboard
- Double-click a line to copy it to clipboard
- Logs are saved to `~/.config/ovpn-launcher/logs/{alias}_{timestamp}.log`

## Configuration

### Config File Location

| Platform | Path |
|----------|------|
| Linux | `~/.config/ovpn-launcher/config.yaml` |
| Windows | `%APPDATA%\ovpn-launcher\config.yaml` |

### Config File (YAML)

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

### Auth Modes

| Mode | Description |
|------|-------------|
| `none` | Connect without credentials (default) |
| `keepass` | Fetch credentials from KeePass database |
| `prompt` | Ask for username and password interactively |

### Autostart

Enable from ☰ → Start at Login.
- **Linux**: creates a `.desktop` file in `~/.config/autostart/`
- **Windows**: creates a `.vbs` script in the Startup folder

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Connect to selected profile |
| `Ctrl+D` | Disconnect |
| `Ctrl+N` | Add profile |
| `Ctrl+E` | Edit profile |
| `Delete` | Remove profile |
| `F5` | Reload profiles |
| `Ctrl+L` | Clear log |
| `Ctrl+Shift+C` | Copy log to clipboard |
| `Ctrl+F` | Search in log |
| `Escape` | Close search bar |
| `Ctrl+Q` | Quit |

## CLI Companion

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

## Troubleshooting

### OpenVPN binary not found
Build the version from the GUI (Build OpenVPN button) or use `system` to use the system-installed OpenVPN.
- **Linux**: system binary at `/usr/bin/openvpn`, compiled versions at `/opt/openvpn-<ver>/sbin/openvpn`
- **Windows**: system binary at `C:\Program Files\OpenVPN\bin\openvpn.exe`, extracted versions at `%LOCALAPPDATA%\ovpn-launcher\openvpn\openvpn-<ver>\bin\openvpn.exe`

### KeePass credentials not found
The KeePass entry title must match the `keepass_entry` field (or the alias if not set). Ensure the KeePass DB path is correct in Settings.

### Connection hangs
Check the connection log for errors. The app will prompt after the configured timeout. Common causes: wrong server address, firewall blocking, incorrect config.

### Config validation warnings
If a profile shows a ⚠ warning icon, hover over it to see what's missing (binary not found, config file not found).

### Tray icon not showing
Ensure your desktop environment supports system tray icons. On KDE Plasma this works out of the box. On GNOME you may need the AppIndicator extension.

### Windows: Access denied / routes not working
The app must run as Administrator for OpenVPN to modify routing tables. The installer and PyInstaller exe request admin automatically via UAC. If running from source, right-click → Run as Administrator.

### Windows: Adapter in use
If you see "All wintun adapters are currently in use", another OpenVPN instance (e.g. OpenVPN GUI) is using the adapter. The app creates a dedicated `ovpn-launcher` adapter on startup to avoid conflicts. If it fails, close other OpenVPN instances first.

### Windows: Interactive Service warning
If you see a warning about the OpenVPN Interactive Service, install OpenVPN fully via its official MSI installer to set up the service and drivers.
