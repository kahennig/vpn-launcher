"""OpenVPN version fetching and building."""

import json
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.request import urlopen, Request


GITHUB_TAGS_URL = "https://api.github.com/repos/OpenVPN/openvpn/tags?per_page=50"
DOWNLOAD_URL = "https://swupdate.openvpn.net/community/releases/openvpn-{version}.tar.gz"
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
    for d in sorted(p.glob("openvpn-*/sbin/openvpn")):
        if d.is_file():
            versions.append(d.parent.parent.name.removeprefix("openvpn-"))
    return versions


def build_openvpn(version, prefix="/opt", on_output=None):
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
