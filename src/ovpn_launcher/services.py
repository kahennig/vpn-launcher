"""Pure business logic for VPN Launcher (no Qt dependency)."""

import logging
import subprocess
import zipfile
from pathlib import Path

import yaml

log = logging.getLogger(__name__)


def log_color(text, muted_color=None):
    """Return a hex color for a log line, or None for default."""
    t = text.lower()
    if "error" in t or "fatal" in t:
        return "#e74c3c"
    if "warn" in t:
        return "#e67e22"
    if "initialization sequence completed" in t:
        return "#27ae60"
    if text.startswith("--") or text.startswith("---") or text.startswith("$"):
        return muted_color
    return None


def validate_ovpn(config_path):
    """Return list of missing critical directives in an .ovpn file."""
    text = Path(config_path).read_text(errors="replace")
    return [d for d in ("remote", "dev")
            if not any(line.strip().startswith(d) for line in text.splitlines())]


def extract_remote_host(config_path):
    """Extract the first 'remote' host from an .ovpn file, or None."""
    for line in Path(config_path).read_text(errors="replace").splitlines():
        line = line.strip()
        if line.startswith("remote "):
            parts = line.split()
            if len(parts) >= 2:
                return parts[1]
    return None


def export_profile_zip(profile, dest):
    """Write a profile zip containing profile.yaml and the .ovpn file."""
    config_path = Path(profile["config"])
    meta = {"alias": profile["alias"], "version": profile["version"], "config": config_path.name}
    if profile.get("auth_mode", "none") != "none":
        meta["auth_mode"] = profile["auth_mode"]
    if profile.get("keepass_entry"):
        meta["keepass_entry"] = profile["keepass_entry"]
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
        if config_path.is_file():
            zf.write(config_path, config_path.name)
        zf.writestr("profile.yaml", yaml.dump(meta, default_flow_style=False))


def import_profile_zip(src):
    """Read a profile zip. Returns (meta_dict, ovpn_bytes_or_None).

    Raises ValueError if the zip is invalid or missing profile.yaml.
    Raises zipfile.BadZipFile if the file is not a valid zip.
    """
    with zipfile.ZipFile(src, "r") as zf:
        if "profile.yaml" not in zf.namelist():
            raise ValueError("No profile.yaml found in zip.")
        meta = yaml.safe_load(zf.read("profile.yaml").decode())
        if not meta or not all(k in meta for k in ("alias", "version", "config")):
            raise ValueError("Invalid profile.yaml format.")
        ovpn_name = meta["config"]
        ovpn_bytes = zf.read(ovpn_name) if ovpn_name in zf.namelist() else None
    return meta, ovpn_bytes


def fetch_keepass_creds(entry, db_path, master_password):
    """Fetch username/password from KeePass via keepassxc-cli.

    Returns (user, password) or (None, None) on failure.
    """
    db = Path(db_path).expanduser()
    log.debug("KeePass lookup: entry='%s', db='%s', exists=%s", entry, db, db.exists())
    if not db.exists():
        log.warning("KeePass DB not found: %s", db)
        return None, None
    try:
        r_user = subprocess.run(
            ["keepassxc-cli", "show", "-q", "-s", "-a", "Username", str(db), entry],
            input=master_password, capture_output=True, text=True, timeout=10,
        )
        r_pwd = subprocess.run(
            ["keepassxc-cli", "show", "-q", "-s", "-a", "Password", str(db), entry],
            input=master_password, capture_output=True, text=True, timeout=10,
        )
        user = r_user.stdout.strip()
        pwd = r_pwd.stdout.strip()
        if not user or not pwd:
            log.warning("KeePass lookup failed for '%s': user_rc=%d pwd_rc=%d stderr=%s",
                        entry, r_user.returncode, r_pwd.returncode,
                        (r_user.stderr or r_pwd.stderr).strip())
            return None, None
        log.debug("KeePass credentials obtained for '%s'", entry)
        return user, pwd
    except subprocess.TimeoutExpired:
        return None, None
