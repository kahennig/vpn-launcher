# Development Guide

## Prerequisites

### Linux
- Python 3.10+ (system has 3.14)
- PyQt6, PyYAML
- `keepassxc-cli` (optional, for KeePass integration)
- KDE Plasma desktop (for system tray icons; works on other DEs but icons may differ)

### Windows
- Python 3.10+
- PyQt6, PyYAML
- PyInstaller (for building the exe)
- NSIS (for building the installer)

## Setup

```bash
cd ~/source/personal/ovpn-launcher
make dev  # pip install -e . (editable mode)
make install-config  # creates ~/.config/ovpn-launcher/ with example config
```

On Windows (no Makefile):
```powershell
pip install -e .
pip install pyinstaller
```

## Running

```bash
# GUI
ovpn-app

# CLI
ovpn-connect --list
ovpn-connect <alias>
ovpn-connect --add
ovpn-connect --edit <alias>
ovpn-connect --remove <alias>
ovpn-connect --status
ovpn-connect --version
```

## Testing

```bash
pip install pytest pytest-qt
python -m pytest tests/ -v
```

105 tests covering:
- `test_profiles.py` — YAML load/save, settings, migration, detect_versions, backup, last_connected
- `test_paths.py` — openvpn_binary, path constants, custom prefix, Windows paths
- `test_services.py` — elevation, kill command, public IP, DNS, log colors, ovpn validation, import/export, autostart, KeePass
- `test_app.py` — ProfileDialog, SettingsDialog, VPNLauncher (reload_profiles), log colors

CI runs on push/PR via GitHub Actions (`.github/workflows/ci.yml`) on both Ubuntu and Windows.

## Building for Windows

### Standalone exe
```powershell
pyinstaller ovpn-launcher.spec
# Output: dist/ovpn-launcher.exe
```

### NSIS installer
```powershell
makensis installer.nsi
# Output: dist/ovpn-launcher-setup.exe
```

Both are built automatically by CI (`.github/workflows/build-windows.yml`) on tags or manual dispatch.

## Building OpenVPN Versions

From the GUI: **Build OpenVPN** button fetches versions from GitHub and handles everything.

From the command line:
```bash
sudo ./scripts/build-openvpn.sh 2.6.14
```

Build dependencies (Fedora):
```bash
sudo dnf install gcc make openssl-devel lzo-devel pam-devel lz4-devel
```

Build dependencies (Debian/Ubuntu):
```bash
sudo apt install build-essential libssl-dev liblzo2-dev libpam0g-dev liblz4-dev
```

## Install / Uninstall

```bash
sudo make install    # pip install + .desktop + icon
sudo make uninstall  # removes everything
```

## Project Structure

```
src/ovpn_launcher/
  __init__.py       # version string
  app.py            # PyQt6 GUI — VPNLauncher, main(), splash, auto-elevation
  cli.py            # Python CLI — argparse, connect, add, edit, remove, list, status
  dialogs.py        # GUI dialogs — ProfileDialog, SettingsDialog, BuildDialog
  services.py       # Business logic — elevation, KeePass, IP/DNS, import/export, adapters
  builder.py        # OpenVPN build — fetch versions, compile (Linux) / extract MSI (Windows)
  paths.py          # Path constants, XDG/APPDATA config, openvpn_binary(), IS_WINDOWS
  profiles.py       # YAML config: load/save profiles, settings, migration, detect_versions

scripts/
  ovpn-connect      # legacy bash CLI (kept for reference)
  build-openvpn.sh  # OpenVPN build script (bash, still usable standalone)

tests/
  test_app.py       # GUI tests (ProfileDialog, SettingsDialog, VPNLauncher, log colors)
  test_paths.py     # path and binary resolution tests (Linux + Windows)
  test_profiles.py  # YAML config, settings, migration, backup tests
  test_services.py  # elevation, kill, IP, DNS, log colors, validation, import/export

config/
  config.yaml.example       # YAML config template
  connections.conf.example   # legacy format reference

share/
  applications/ovpn-launcher.desktop
  icons/ovpn-launcher.svg    # custom app icon (shield + lock)
  icons/ovpn-launcher.ico    # Windows icon (multi-size)
  icons/breeze/              # bundled Breeze icon theme (light)
  icons/breeze-dark/         # bundled Breeze icon theme (dark)

.github/workflows/
  ci.yml                    # CI: pytest on Ubuntu + Windows
  build-windows.yml         # Windows build: PyInstaller exe + NSIS installer

installer.nsi               # NSIS installer script
ovpn-launcher.spec          # PyInstaller spec (uac_admin=True)

openspec/
  backlog.md        # task index with Windows port roadmap
  done/             # completed task specs
  active/           # tasks in progress

docs/
  architecture.md   # component diagram, connection flow, config format
  development.md    # this file
  migration.md      # history of migration from ~/bin + ~/vpn
  user-guide.md     # end-user guide
  varios/           # reference documents
```

## TODO / Future Ideas

- [ ] W015: Management Interface (--management TCP socket) for reliable monitoring
- [ ] W016: Base install of first OpenVPN via MSI (drivers + Interactive Service)
- [ ] L016: Flatpak packaging for Linux
- [ ] Add a LICENSE file (GPL-3.0 full text)
