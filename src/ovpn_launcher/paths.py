"""Centralized path definitions with platform detection."""

import os
import sys
from pathlib import Path

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    _config_base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    CONFIG_DIR = _config_base / "ovpn-launcher"
    AUTOSTART_DIR = _config_base / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    AUTOSTART_FILE = AUTOSTART_DIR / "ovpn-launcher.vbs"
    OPENVPN_PREFIX = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "ovpn-launcher" / "openvpn"
    KEEPASS_DB = Path(os.environ.get(
        "OVPN_KEEPASS_DB",
        Path.home() / "Documents" / "Keepass" / "keepass.kdbx",
    ))
else:
    XDG_CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    CONFIG_DIR = XDG_CONFIG / "ovpn-launcher"
    AUTOSTART_DIR = XDG_CONFIG / "autostart"
    AUTOSTART_FILE = AUTOSTART_DIR / "ovpn-launcher.desktop"
    OPENVPN_PREFIX = Path("/opt")
    KEEPASS_DB = Path(os.environ.get(
        "OVPN_KEEPASS_DB",
        Path.home() / "Document" / "Keepass" / "keepass.kdbx",
    ))

CONNECTIONS_CONF = CONFIG_DIR / "connections.conf"
CONFIG_YAML = CONFIG_DIR / "config.yaml"
LOG_DIR = CONFIG_DIR / "logs"
OPENVPN_GLOB = "openvpn-*/bin/openvpn.exe" if IS_WINDOWS else "openvpn-*/sbin/openvpn"


def openvpn_binary(version: str, prefix: Path = OPENVPN_PREFIX) -> Path:
    prefix = Path(os.path.expandvars(str(prefix)))
    if version == "system":
        if IS_WINDOWS:
            return Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "OpenVPN" / "bin" / "openvpn.exe"
        return Path("/usr/bin/openvpn")
    if IS_WINDOWS:
        return prefix / f"openvpn-{version}" / "bin" / "openvpn.exe"
    return prefix / f"openvpn-{version}" / "sbin" / "openvpn"
