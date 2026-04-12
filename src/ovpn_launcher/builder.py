"""OpenVPN version fetching and building/installing."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.request import urlopen, Request

from .paths import IS_WINDOWS, OPENVPN_GLOB


GITHUB_TAGS_URL = "https://api.github.com/repos/OpenVPN/openvpn/tags?per_page=50"
DOWNLOAD_URL = "https://swupdate.openvpn.net/community/releases/openvpn-{version}.tar.gz"
MSI_URL = "https://swupdate.openvpn.net/community/releases/OpenVPN-{version}-I001-amd64.msi"
STABLE_RE = re.compile(r"^v(\d+\.\d+\.\d+)$")


def fetch_available_versions():
    try:
        with urlopen(GITHUB_TAGS_URL, timeout=10) as resp:
            tags = json.loads(resp.read())
        versions = []
        for t in tags:
            m = STABLE_RE.match(t["name"])
            if m:
                versions.append(m.group(1))
        return versions
    except Exception:
        return []


def installed_versions(prefix="/opt"):
    p = Path(prefix)
    versions = []
    for d in sorted(p.glob(OPENVPN_GLOB)):
        if d.is_file():
            versions.append(d.parent.parent.name.removeprefix("openvpn-"))
    return versions


def has_tap_driver():
    """Check if a TAP/TUN driver is installed (Windows only)."""
    if not IS_WINDOWS:
        return True
    candidates = [
        Path(os.environ.get("SYSTEMROOT", "C:\\Windows")) / "System32" / "drivers" / "tap0901.sys",
        Path(os.environ.get("SYSTEMROOT", "C:\\Windows")) / "System32" / "wintun.dll",
        Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "TAP-Windows",
        Path(os.environ.get("PROGRAMFILES", "C:\\Program Files")) / "OpenVPN" / "bin" / "openvpn.exe",
    ]
    return any(p.exists() for p in candidates)


def _install_openvpn_windows(version, prefix, on_output=None, full_install=False):
    """Download and install OpenVPN on Windows from official MSI."""
    def log(msg):
        if on_output:
            on_output(msg)

    prefix = os.path.expandvars(str(prefix))
    dest = Path(prefix) / f"openvpn-{version}"
    binary = dest / "bin" / "openvpn.exe"
    if binary.is_file():
        log(f"OpenVPN {version} already installed at {dest}")
        return True

    url = MSI_URL.format(version=version)
    build_dir = Path(tempfile.mkdtemp(prefix="openvpn-install-"))
    msi_path = build_dir / f"OpenVPN-{version}.msi"
    extract_dir = build_dir / "extracted"

    try:
        log(f"==> Downloading OpenVPN {version} MSI...")
        req = Request(url, headers={"User-Agent": "ovpn-launcher"})
        with urlopen(req, timeout=120) as resp, open(msi_path, "wb") as f:
            f.write(resp.read())
        if not msi_path.exists() or msi_path.stat().st_size < 10000:
            log("ERROR: Download failed or file too small")
            return False

        log(f"==> Extracting OpenVPN {version} binary...")
        extract_dir.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(
            ["msiexec", "/a", str(msi_path), "/qn",
             f"TARGETDIR={extract_dir}"],
            capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            log(f"ERROR: Extract failed (code {r.returncode})")
            return False

        # msiexec /a creates nested structure — find openvpn.exe anywhere
        found = list(extract_dir.rglob("openvpn.exe"))
        if not found:
            log("ERROR: openvpn.exe not found in extracted MSI")
            log(f"Extracted contents: {[str(p.relative_to(extract_dir)) for p in extract_dir.rglob('*') if p.is_file()][:20]}")
            return False

        import shutil
        dest.mkdir(parents=True, exist_ok=True)
        binary.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(found[0]), str(binary))
        log(f"Found openvpn.exe at: {found[0].relative_to(extract_dir)}")

        if binary.is_file():
            log(f"==> Done! OpenVPN {version} installed at {dest}")
            return True
        else:
            log("ERROR: Failed to copy openvpn.exe")
            return False

    except subprocess.TimeoutExpired:
        log("ERROR: Install timed out")
        return False
    except Exception as e:
        log(f"ERROR: {e}")
        return False
    finally:
        import shutil
        shutil.rmtree(build_dir, ignore_errors=True)


def build_openvpn(version, prefix="/opt", on_output=None, full_install=False):
    """Build (Linux) or install (Windows) an OpenVPN version."""
    if IS_WINDOWS:
        return _install_openvpn_windows(version, prefix, on_output, full_install)
    return _build_openvpn_linux(version, prefix, on_output)


def _build_openvpn_linux(version, prefix="/opt", on_output=None):
    def log(msg):
        if on_output:
            on_output(msg)

    dest = Path(prefix) / f"openvpn-{version}"
    if (dest / "sbin" / "openvpn").is_file():
        log(f"OpenVPN {version} already installed at {dest}")
        return True

    url = DOWNLOAD_URL.format(version=version)
    build_dir = Path(tempfile.mkdtemp(prefix="openvpn-build-"))
    tarball = build_dir / f"openvpn-{version}.tar.gz"
    src_dir = build_dir / f"openvpn-{version}"

    try:
        log(f"==> Downloading OpenVPN {version}...")
        req = Request(url, headers={"User-Agent": "ovpn-launcher"})
        with urlopen(req, timeout=60) as resp, open(tarball, "wb") as f:
            f.write(resp.read())
        if not tarball.exists() or tarball.stat().st_size < 1000:
            log(f"ERROR: Download failed or file too small")
            return False

        log("==> Extracting...")
        r = subprocess.run(["tar", "xzf", str(tarball)], cwd=str(build_dir), capture_output=True, text=True)
        if r.returncode != 0:
            log(f"ERROR: Extract failed: {r.stderr}")
            return False

        if not src_dir.is_dir():
            log(f"ERROR: Source directory not found: {src_dir}")
            return False

        log(f"==> Configuring (prefix={dest}, --disable-dco)...")
        r = subprocess.run(
            ["./configure", f"--prefix={dest}", "--disable-dco", "--quiet"],
            cwd=str(src_dir), capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            log(f"ERROR: Configure failed:\n{r.stderr[-500:]}")
            return False

        log("==> Building (this may take a few minutes)...")
        nproc = subprocess.run(["nproc"], capture_output=True, text=True).stdout.strip() or "2"
        r = subprocess.run(
            ["make", f"-j{nproc}", "--quiet"],
            cwd=str(src_dir), capture_output=True, text=True, timeout=600,
        )
        if r.returncode != 0:
            log(f"ERROR: Build failed:\n{r.stderr[-500:]}")
            return False

        log(f"==> Installing to {dest} (requires privileges)...")
        r = subprocess.run(
            ["pkexec", "make", "-C", str(src_dir), "install", "--quiet"],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0:
            log(f"ERROR: Install failed:\n{r.stderr[-500:]}")
            return False

        binary = dest / "sbin" / "openvpn"
        if binary.is_file():
            ver_out = subprocess.run([str(binary), "--version"], capture_output=True, text=True).stdout.split("\n")[0]
            log(f"==> Done! {ver_out}")
            return True
        else:
            log("ERROR: Binary not found after install")
            return False

    except subprocess.TimeoutExpired:
        log("ERROR: Build timed out")
        return False
    except Exception as e:
        log(f"ERROR: {e}")
        return False
    finally:
        import shutil
        shutil.rmtree(build_dir, ignore_errors=True)
