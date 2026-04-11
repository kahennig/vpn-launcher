"""Centralized path definitions following XDG conventions."""

from pathlib import Path
import os

XDG_CONFIG = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
AUTOSTART_DIR = XDG_CONFIG / "autostart"
AUTOSTART_DESKTOP = AUTOSTART_DIR / "ovpn-launcher.desktop"
CONFIG_DIR = XDG_CONFIG / "ovpn-launcher"
CONNECTIONS_CONF = CONFIG_DIR / "connections.conf"
CONFIG_YAML = CONFIG_DIR / "config.yaml"
LOG_DIR = CONFIG_DIR / "logs"
OPENVPN_PREFIX = Path("/opt")
KEEPASS_DB = Path(os.environ.get(
    "OVPN_KEEPASS_DB",
    Path.home() / "Document" / "Keepass" / "keepass.kdbx",
))


def openvpn_binary(version: str, prefix: Path = OPENVPN_PREFIX) -> Path:
    if version == "system":
        return Path("/usr/bin/openvpn")
    return prefix / f"openvpn-{version}" / "sbin" / "openvpn"
