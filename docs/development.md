# Development Guide

## Prerequisites

- Python 3.10+ (system has 3.14)
- PyQt6 (`pip install PyQt6` or system package)
- `keepassxc-cli` (optional, for KeePass integration)
- KDE Plasma desktop (for system tray icons; works on other DEs but icons may differ)

## Setup

```bash
cd ~/source/personal/ovpn-launcher
make dev  # pip install -e . (editable mode)
make install-config  # creates ~/.config/ovpn-launcher/ with example config
```

## Running

```bash
# GUI
ovpn-app
# or directly:
python -m ovpn_launcher.app

# CLI
./scripts/ovpn-connect --list
./scripts/ovpn-connect <alias>
./scripts/ovpn-connect --add
./scripts/ovpn-connect --status
```

## Testing

```bash
pip install pytest pytest-qt
python -m pytest tests/ -v
```

Tests cover `profiles.py`: load, save, detect_versions, auth_mode parsing, header preservation.

CI runs automatically on push/PR via GitHub Actions (`.github/workflows/ci.yml`).

## Building OpenVPN Versions

```bash
sudo ./scripts/build-openvpn.sh 2.6.14
sudo ./scripts/build-openvpn.sh 2.5.11
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
sudo make install    # installs to /usr/local/bin + .desktop file
sudo make uninstall  # removes everything
```

## Project Structure

```
src/ovpn_launcher/
  __init__.py      # version string
  paths.py         # all path constants, XDG config, openvpn_binary() helper
  profiles.py      # load/save profiles, detect_versions()
  app.py           # PyQt6 GUI — ProfileDialog, VPNLauncher, main()

scripts/
  ovpn-connect     # bash CLI (installed to /usr/local/bin/)
  build-openvpn.sh # compile any OpenVPN version from source

tests/
  test_profiles.py # pytest tests for profiles.py

config/
  connections.conf.example  # template copied during make install-config

share/applications/
  ovpn-launcher.desktop     # freedesktop .desktop entry

.github/workflows/
  ci.yml           # GitHub Actions CI (pytest + xvfb)

docs/
  architecture.md  # component diagram, connection flow, config format
  migration.md     # history of migration from ~/bin + ~/vpn
  development.md   # this file
  user-guide.md    # end-user guide
```

## TODO / Future Ideas

- [ ] Add a LICENSE file (GPL-3.0 full text)
- [ ] Publish to GitHub and update YOURUSER in pyproject.toml and README.md
- [ ] Multiple simultaneous VPN connections
- [ ] KeePass master password caching with timeout
- [ ] Packaging as RPM/Flatpak
- [ ] Custom app icon instead of relying on theme icons
