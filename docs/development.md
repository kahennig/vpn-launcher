# Development Guide

## Prerequisites

- Python 3.10+ (system has 3.14)
- PyQt6, PyYAML
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

58 tests covering:
- `test_profiles.py` — YAML load/save, settings, migration, detect_versions, backup, last_connected
- `test_paths.py` — openvpn_binary, path constants, custom prefix
- `test_app.py` — ProfileDialog (validation, keepass_entry visibility, get_profile), SettingsDialog (prefill, get_settings, defaults), VPNLauncher (reload_profiles), log colors

CI runs automatically on push/PR via GitHub Actions (`.github/workflows/ci.yml`).

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
  app.py            # PyQt6 GUI — BuildDialog, SettingsDialog, ProfileDialog, VPNLauncher, main()
  cli.py            # Python CLI — argparse, connect, add, edit, remove, list, status
  builder.py        # OpenVPN build — fetch versions (GitHub API), download, compile, install
  paths.py          # path constants, XDG config, openvpn_binary()
  profiles.py       # YAML config: load/save profiles, settings, migration, detect_versions

scripts/
  ovpn-connect      # legacy bash CLI (kept for reference)
  build-openvpn.sh  # OpenVPN build script (bash, still usable standalone)

tests/
  test_app.py       # GUI tests (ProfileDialog, SettingsDialog, VPNLauncher, log colors)
  test_paths.py     # path and binary resolution tests
  test_profiles.py  # YAML config, settings, migration, backup tests

config/
  config.yaml.example       # YAML config template
  connections.conf.example   # legacy format reference

share/
  applications/ovpn-launcher.desktop
  icons/ovpn-launcher.svg    # custom app icon

.github/workflows/
  ci.yml            # GitHub Actions CI (pytest + xvfb)

openspec/
  backlog.md        # task index with Windows port roadmap
  done/             # completed task specs
  active/           # tasks in progress

docs/
  architecture.md   # component diagram, connection flow, config format
  development.md    # this file
  migration.md      # history of migration from ~/bin + ~/vpn
  user-guide.md     # end-user guide
```

## TODO / Future Ideas

- [ ] Add a LICENSE file (GPL-3.0 full text)
- [ ] Packaging as RPM/Flatpak (L016)
- [ ] Windows port (see openspec/backlog.md for roadmap: T064-T069, W001-W010)
