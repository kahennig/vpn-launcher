"""Pure business logic for VPN Launcher (no Qt dependency)."""

import logging
import os
import shutil
import socket
import subprocess
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

import yaml

from .paths import IS_WINDOWS, AUTOSTART_DIR, AUTOSTART_FILE

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


def keepassxc_cli_path():
    """Find keepassxc-cli binary. Returns path string or None."""
    found = shutil.which("keepassxc-cli")
    if found:
        return found
    if IS_WINDOWS:
        for base in [os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                     os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")]:
            candidate = Path(base) / "KeePassXC" / "keepassxc-cli.exe"
            if candidate.is_file():
                return str(candidate)
    return None


def fetch_keepass_creds(entry, db_path, master_password):
    """Fetch username/password from KeePass via keepassxc-cli.

    Returns (user, password) or (None, None) on failure.
    """
    db = Path(db_path).expanduser()
    log.debug("KeePass lookup: entry='%s', db='%s', exists=%s", entry, db, db.exists())
    if not db.exists():
        log.warning("KeePass DB not found: %s", db)
        return None, None
    cli = keepassxc_cli_path()
    if not cli:
        log.warning("keepassxc-cli not found")
        return None, None
    try:
        r_user = subprocess.run(
            [cli, "show", "-q", "-s", "-a", "Username", str(db), entry],
            input=master_password, capture_output=True, text=True, timeout=10,
        )
        r_pwd = subprocess.run(
            [cli, "show", "-q", "-s", "-a", "Password", str(db), entry],
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


ADAPTER_NAME = "ovpn-launcher"


def _find_tapctl():
    """Find tapctl.exe. Returns path string or None."""
    if not IS_WINDOWS:
        return None
    found = shutil.which("tapctl")
    if found:
        return found
    for base in [Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")),
                 Path(os.environ.get("LOCALAPPDATA", "")) / "ovpn-launcher" / "openvpn"]:
        for p in base.rglob("tapctl.exe"):
            if p.is_file():
                return str(p)
    return None


def ensure_adapter():
    """Ensure a dedicated wintun adapter exists for ovpn-launcher (Windows only).

    Returns True if the adapter is available, False otherwise.
    """
    if not IS_WINDOWS:
        return False
    # Check if adapter already exists
    for _guid, name in list_tap_adapters():
        if name == ADAPTER_NAME:
            return True
    # Create it
    tapctl = _find_tapctl()
    if not tapctl:
        log.warning("tapctl.exe not found, cannot create adapter")
        return False
    try:
        r = subprocess.run(
            [tapctl, "create", "--hwid", "wintun", "--name", ADAPTER_NAME],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0:
            log.info("Created wintun adapter '%s'", ADAPTER_NAME)
            return True
        log.warning("tapctl create failed: %s", r.stderr.strip())
    except Exception as e:
        log.warning("Failed to create adapter: %s", e)
    return False


def windows_driver_args():
    """Return extra OpenVPN args to use the dedicated adapter on Windows."""
    if not IS_WINDOWS:
        return []
    # Use our dedicated adapter if available
    for _guid, name in list_tap_adapters():
        if name == ADAPTER_NAME:
            return ["--windows-driver", "wintun", "--dev-node", ADAPTER_NAME]
    return []


_system_version_cache = None


def get_system_version(binary=None):
    """Get the version string of the system OpenVPN binary (cached).

    Returns version string (e.g. '2.6.14') or '' if not found.
    """
    global _system_version_cache
    if _system_version_cache is not None:
        return _system_version_cache
    if binary is None:
        from .paths import openvpn_binary
        binary = openvpn_binary("system")
    try:
        if not Path(str(binary)).is_file():
            _system_version_cache = ""
            return ""
        r = subprocess.run(
            [str(binary), "--version"], capture_output=True, text=True, timeout=5,
        )
        _system_version_cache = r.stdout.split()[1] if r.stdout else ""
    except Exception:
        _system_version_cache = ""
    return _system_version_cache


def is_interactive_service_running():
    """Check if OpenVPN Interactive Service is running (Windows only).

    Returns True on Linux (not needed), or True/False on Windows.
    """
    if not IS_WINDOWS:
        return True
    for svc_name in ("OpenVPNServiceInteractive", "OpenVPNService", "openvpnserv2"):
        try:
            r = subprocess.run(
                ["sc", "query", svc_name],
                capture_output=True, text=True, timeout=5,
            )
            if "RUNNING" in r.stdout:
                return True
        except Exception:
            pass
    return False


def list_tap_adapters():
    """List virtual network adapters via tapctl.exe (Windows only).

    Returns list of (guid, name) tuples, or empty list on Linux/error.
    """
    if not IS_WINDOWS:
        return []
    tapctl = _find_tapctl()
    if not tapctl:
        return []
    try:
        r = subprocess.run(
            [tapctl, "list"], capture_output=True, text=True, timeout=10,
        )
        adapters = []
        for line in r.stdout.strip().splitlines():
            # Format: {GUID} AdapterName
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                adapters.append((parts[0], parts[1]))
        return adapters
    except Exception:
        return []


def _is_admin():
    """Check if the current process has admin privileges (Windows only)."""
    if not IS_WINDOWS:
        return False
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def elevate_command(command, gui=False):
    """Wrap a command list with privilege escalation for the current platform."""
    if IS_WINDOWS:
        # On Windows, OpenVPN needs admin for netsh route changes.
        # If already admin or Interactive Service handles it, run directly.
        return list(command)
    return ["pkexec" if gui else "sudo"] + list(command)


def needs_admin_warning():
    """Return True if the user should be warned about missing admin rights.

    On Windows, OpenVPN needs admin to modify routes unless the
    Interactive Service is running and handles it.
    """
    if not IS_WINDOWS:
        return False
    if _is_admin():
        return False
    if is_interactive_service_running():
        return False
    return True


def kill_command(pid, gui=False):
    """Build a command to kill a process with elevated privileges."""
    if IS_WINDOWS:
        return ["taskkill", "/F", "/PID", str(pid)]
    return ["pkexec" if gui else "sudo", "kill", str(pid)]


def fetch_public_ip(url="https://api.ipify.org", timeout=5):
    """Fetch public IP address. Returns IP string or empty string on failure."""
    try:
        with urlopen(Request(url), timeout=timeout) as resp:
            return resp.read().decode().strip()
    except (URLError, OSError, ValueError):
        return ""


def dns_resolver_ip(timeout=5):
    """Check DNS resolver via Akamai whoami. Returns IP string or empty string."""
    try:
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        result = socket.getaddrinfo("whoami.akamai.net", None)
        socket.setdefaulttimeout(old_timeout)
        if result:
            return result[0][4][0]
    except (socket.gaierror, OSError):
        pass
    return ""


def is_autostart_enabled():
    """Check if autostart is enabled."""
    return AUTOSTART_FILE.is_file()


def enable_autostart():
    """Enable autostart at login."""
    AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
    if IS_WINDOWS:
        AUTOSTART_FILE.write_text(
            'CreateObject("WScript.Shell").Run '
            '"pythonw -m ovpn_launcher.app", 0, False\n'
        )
    else:
        AUTOSTART_FILE.write_text(
            "[Desktop Entry]\nType=Application\nName=VPN Launcher\n"
            "Exec=ovpn-app\nIcon=ovpn-launcher\nTerminal=false\n"
            "X-GNOME-Autostart-enabled=true\n"
        )


def disable_autostart():
    """Disable autostart at login."""
    try:
        AUTOSTART_FILE.unlink()
    except FileNotFoundError:
        pass
