# Migration from ~/bin + ~/vpn

This project was originally a set of loose scripts created with Kiro, living in the user's home directory. This document captures the original layout and migration steps.

## Original Layout

```
~/bin/ovpn-app          # PyQt6 GUI script (standalone, no package)
~/bin/ovpn-connect      # Bash CLI script
~/vpn/connections.conf  # Profile definitions (pipe-delimited)
~/vpn/*.ovpn            # OpenVPN config files
~/vpn/README.md         # Usage notes
/opt/openvpn-2.6.14/    # Compiled OpenVPN 2.6.14
/usr/bin/openvpn        # System OpenVPN 2.7.1
```

The original scripts hardcoded paths:
- `CONF = Path.home() / "vpn" / "connections.conf"`
- `KPDB = Path.home() / "Document" / "Keepass" / "keepass.kdbx"`

## What Changed

| Aspect | Before | After |
|--------|--------|-------|
| GUI script | `~/bin/ovpn-app` (standalone) | `src/ovpn_launcher/app.py` (Python package) |
| CLI script | `~/bin/ovpn-connect` | `scripts/ovpn-connect` |
| Config dir | `~/vpn/` | `~/.config/ovpn-launcher/` (XDG) |
| Hardcoded paths | In each script | Centralized in `paths.py` |
| OpenVPN build | Manual (documented in README) | `scripts/build-openvpn.sh` |
| Installation | Copy to ~/bin manually | `make install` → `/usr/local/bin/` |
| Desktop entry | None | `share/applications/ovpn-launcher.desktop` |
| Package format | None | `pyproject.toml` with setuptools |

## Migration Steps (for the user's own system)

```bash
# 1. Install the new project
cd ~/source/personal/ovpn-launcher
sudo make install
make install-config

# 2. Copy existing config and .ovpn files
cp ~/vpn/connections.conf ~/.config/ovpn-launcher/connections.conf
cp ~/vpn/*.ovpn ~/.config/ovpn-launcher/configs/

# 3. Update paths inside connections.conf to point to new config location
# Old: IdRetail|2.6.14|/home/andi/vpn/pfSense1-UDP4-1197-config.ovpn
# New: IdRetail|2.6.14|/home/andi/.config/ovpn-launcher/configs/pfSense1-UDP4-1197-config.ovpn

# 4. Remove old files (once verified working)
rm ~/bin/ovpn-app ~/bin/ovpn-connect
# Optionally keep ~/vpn/ as backup or remove it

# 5. Verify
ovpn-connect --list
ovpn-app
```

## Existing Compiled OpenVPN Versions

The user's system already has:
- **2.7.1** (system) at `/usr/bin/openvpn`
- **2.6.14** (compiled) at `/opt/openvpn-2.6.14/sbin/openvpn`

To add more versions: `sudo ./scripts/build-openvpn.sh <version>`
