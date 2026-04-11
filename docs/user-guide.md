# User Guide

## Description

VPN Launcher is a multi-version OpenVPN connection manager for Linux. It lets you manage multiple VPN profiles, each pinned to a specific OpenVPN version, with optional KeePass credential integration.

## Getting Started

1. Launch the app: `ovpn-app` or from your application menu (VPN Launcher)
2. Add a profile: click **Add Profile** in the toolbar
3. Select a profile and click **Connect** (or double-click)

## Main Window

The main window has:
- **Menu bar** — Help → About
- **Toolbar** — Connect, Disconnect, Reload, Clear Log, Add, Import, Edit, Remove, Quit
- **Filter** — Text field to filter profiles by name
- **Profile list** — Table with columns: Profile, OpenVPN Version, Config File, Auth
- **Connection log** — Real-time output from OpenVPN
- **Status bar** — Current connection state with icon

## Managing Profiles

### Add a Profile
1. Click **Add Profile** in the toolbar
2. Fill in: Alias, OpenVPN Version (dropdown with detected versions, or type manually), Config File (use Browse), Auth Mode
3. Click OK

### Import an .ovpn File
1. Click **Import .ovpn** in the toolbar
2. Select the .ovpn file — it gets copied to `~/.config/ovpn-launcher/configs/`
3. Review the pre-filled profile dialog and click OK

### Edit a Profile
1. Select a profile in the list
2. Click **Edit Profile** in the toolbar
3. Modify fields and click OK

### Remove a Profile
1. Select a profile in the list
2. Click **Remove Profile** in the toolbar
3. Confirm the deletion

### Reorder Profiles
Drag and drop profiles in the list to change their order. The new order is saved automatically.

## Connecting

1. Select a profile
2. Click **Connect** or press `Ctrl+Enter` (or double-click the profile)
3. Depending on the auth mode:
   - **none** — connects directly
   - **keepass** — prompts for your KeePass master password, then fetches credentials
   - **prompt** — asks for username and password
4. The connection log shows OpenVPN output in real-time
5. Status bar and tray icon update to show connection state

### Connection Timeout
If the connection doesn't complete within 30 seconds, a warning dialog appears asking if you want to disconnect or keep waiting.

### Auto-Reconnect
If the VPN connection drops unexpectedly (not a manual disconnect), the app automatically reconnects after 5 seconds.

## Disconnecting

Click **Disconnect** or press `Ctrl+D`. You can also disconnect from the system tray menu.

## System Tray

- The app minimizes to the system tray when you close the window
- Left-click the tray icon to show/hide the window
- Right-click for a menu with: profile quick-connect, Show/Hide, Disconnect, Quit
- Desktop notifications appear on connect and disconnect

## Configuration

### Config File

Profiles are stored in `~/.config/ovpn-launcher/connections.conf`:

```
# Format: alias|version|config_file|auth_mode
client-a|2.6.14|/home/user/.config/ovpn-launcher/configs/client-a.ovpn|keepass
client-b|2.5.11|/home/user/.config/ovpn-launcher/configs/client-b.ovpn|prompt
office|system|/home/user/.config/ovpn-launcher/configs/office.ovpn
```

### Auth Modes

| Mode | Description |
|------|-------------|
| `none` | Connect without credentials (default) |
| `keepass` | Fetch credentials from KeePass database |
| `prompt` | Ask for username and password interactively |

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `OVPN_KEEPASS_DB` | `~/Document/Keepass/keepass.kdbx` | KeePass database path |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Connect to selected profile |
| `Ctrl+D` | Disconnect |
| `F5` | Reload profiles |
| `Ctrl+L` | Clear log |
| `Ctrl+Q` | Quit |

## CLI Companion

```bash
ovpn-connect <alias>                  # connect using a profile
ovpn-connect <version> <config.ovpn>  # direct mode
ovpn-connect --list                   # list versions and profiles
ovpn-connect --add                    # add a new profile interactively
ovpn-connect --status                 # check if openvpn is running
```

## Troubleshooting

### OpenVPN binary not found
Make sure the version is compiled: `sudo ./scripts/build-openvpn.sh <version>`, or use `system` to use `/usr/bin/openvpn`.

### KeePass credentials not found
The KeePass entry title must match the profile alias exactly. Ensure `OVPN_KEEPASS_DB` points to the correct database.

### Connection hangs
If the connection doesn't complete in 30 seconds, the app will prompt you. Check the connection log for errors. Common causes: wrong server address, firewall blocking, incorrect config.

### Tray icon not showing
Ensure your desktop environment supports system tray icons. On KDE Plasma this works out of the box. On GNOME you may need the AppIndicator extension.
