"""Profile loading, saving, version detection, and settings (YAML config)."""

from pathlib import Path
import subprocess

import yaml

from .paths import CONNECTIONS_CONF, CONFIG_YAML, OPENVPN_PREFIX, OPENVPN_GLOB, openvpn_binary

VALID_AUTH_MODES = ("none", "keepass", "prompt")

DEFAULT_SETTINGS = {
    "openvpn_prefix": str(OPENVPN_PREFIX),
    "keepass_db": "~/Document/Keepass/keepass.kdbx",
    "connection_timeout": 30,
    "reconnect_delay": 5,
    "ip_service": "https://api.ipify.org",
    "log_level": "WARNING",
}


def _load_yaml(conf_path=None):
    conf = conf_path or CONFIG_YAML
    if not conf.exists():
        return {}
    return yaml.safe_load(conf.read_text()) or {}


def _save_yaml(data, conf_path=None):
    conf = conf_path or CONFIG_YAML
    conf.parent.mkdir(parents=True, exist_ok=True)
    if conf.exists():
        import shutil
        shutil.copy2(conf, conf.with_suffix(".yaml.bak"))
    conf.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True))


def load_settings(conf_path=None):
    data = _load_yaml(conf_path)
    settings = dict(DEFAULT_SETTINGS)
    settings.update(data.get("settings", {}))
    return settings


def save_settings(settings, conf_path=None):
    data = _load_yaml(conf_path)
    data["settings"] = settings
    _save_yaml(data, conf_path)


def load_profiles(conf_path=None):
    conf = conf_path or CONFIG_YAML
    if not conf.exists() and CONNECTIONS_CONF.exists():
        migrate_legacy_config()
    data = _load_yaml(conf)
    profiles = []
    for p in data.get("profiles", []):
        auth_mode = str(p.get("auth_mode", "none")).strip().lower()
        if auth_mode not in VALID_AUTH_MODES:
            auth_mode = "none"
        profiles.append({
            "alias": str(p.get("alias", "")),
            "version": str(p.get("version", "system")),
            "config": str(p.get("config", "")),
            "auth_mode": auth_mode,
            "keepass_entry": str(p.get("keepass_entry", "")),
            "last_connected": str(p.get("last_connected", "")),
        })
    return profiles


def save_profiles(profiles, conf_path=None):
    data = _load_yaml(conf_path)
    yaml_profiles = []
    for p in profiles:
        entry = {"alias": p["alias"], "version": p["version"], "config": p["config"]}
        if p.get("auth_mode", "none") != "none":
            entry["auth_mode"] = p["auth_mode"]
        if p.get("keepass_entry", ""):
            entry["keepass_entry"] = p["keepass_entry"]
        if p.get("last_connected", ""):
            entry["last_connected"] = p["last_connected"]
        yaml_profiles.append(entry)
    data["profiles"] = yaml_profiles
    _save_yaml(data, conf_path)


def migrate_legacy_config(legacy_path=None, yaml_path=None):
    legacy = legacy_path or CONNECTIONS_CONF
    if not legacy.exists():
        return
    profiles = []
    for line in legacy.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) < 3:
            continue
        auth_mode = parts[3].strip().lower() if len(parts) >= 4 else "none"
        if auth_mode not in VALID_AUTH_MODES:
            auth_mode = "none"
        keepass_entry = parts[4].strip() if len(parts) >= 5 else ""
        entry = {"alias": parts[0], "version": parts[1], "config": parts[2]}
        if auth_mode != "none":
            entry["auth_mode"] = auth_mode
        if keepass_entry:
            entry["keepass_entry"] = keepass_entry
        profiles.append(entry)
    data = {"settings": dict(DEFAULT_SETTINGS), "profiles": profiles}
    _save_yaml(data, yaml_path)


def detect_versions(prefix=None):
    p = Path(prefix) if prefix else OPENVPN_PREFIX
    versions = []
    system_bin = openvpn_binary("system")
    if system_bin.is_file():
        try:
            ver = subprocess.run(
                [str(system_bin), "--version"], capture_output=True, text=True, timeout=3,
            ).stdout.split()[1]
        except Exception:
            ver = "?"
        versions.append(f"system ({ver})")
    for d in sorted(p.glob(OPENVPN_GLOB)):
        if d.is_file():
            versions.append(d.parent.parent.name.removeprefix("openvpn-"))
    return versions
