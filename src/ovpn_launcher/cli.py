#!/usr/bin/env python3
"""ovpn-connect: CLI companion for ovpn-launcher."""

import argparse
import atexit
import getpass
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from . import __version__
from .paths import openvpn_binary
from .profiles import load_profiles, save_profiles, load_settings, detect_versions, VALID_AUTH_MODES
from .services import elevate_command, fetch_keepass_creds, windows_driver_args


def cmd_list(settings):
    prefix = Path(settings.get("openvpn_prefix", "/opt"))
    print("Installed versions:")
    for v in detect_versions(prefix):
        if v == "system":
            try:
                ver = subprocess.run(
                    ["openvpn", "--version"], capture_output=True, text=True
                ).stdout.split()[1]
            except Exception:
                ver = "?"
            print(f"  system ({ver})")
        else:
            print(f"  {v}")
    print()
    profiles = load_profiles()
    print(f"Configured profiles ({len(profiles)}):")
    for p in profiles:
        auth = f" [{p['auth_mode']}]" if p["auth_mode"] != "none" else ""
        print(f"  {p['alias']} -> version {p['version']} ({Path(p['config']).name}){auth}")


def cmd_add():
    alias = input("Alias: ").strip()
    if not alias:
        print("Alias cannot be empty", file=sys.stderr)
        sys.exit(1)
    profiles = load_profiles()
    if any(p["alias"] == alias for p in profiles):
        print(f"Alias '{alias}' already exists", file=sys.stderr)
        sys.exit(1)
    print("Available versions:")
    for v in detect_versions():
        print(f"  {v}")
    version = input("Version: ").strip()
    config = input("Config file path: ").strip()
    auth_mode = input("Auth mode (none/keepass/prompt) [none]: ").strip() or "none"
    keepass_entry = ""
    if auth_mode == "keepass":
        keepass_entry = input("KeePass entry (empty = use alias): ").strip()
    profiles.append({
        "alias": alias, "version": version, "config": config,
        "auth_mode": auth_mode, "keepass_entry": keepass_entry,
    })
    save_profiles(profiles)
    print(f"Profile '{alias}' added.")


def cmd_status():
    try:
        result = subprocess.run(["pgrep", "-x", "openvpn"], capture_output=True, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().replace("\n", " ")
            print(f"OpenVPN is running (PID: {pids})")
        else:
            print("No OpenVPN process running.")
    except FileNotFoundError:
        print("pgrep not found", file=sys.stderr)


def cmd_remove(alias):
    profiles = load_profiles()
    match = [p for p in profiles if p["alias"] == alias]
    if not match:
        print(f"Profile '{alias}' not found.", file=sys.stderr)
        sys.exit(1)
    confirm = input(f"Remove profile '{alias}'? [y/N]: ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return
    profiles = [p for p in profiles if p["alias"] != alias]
    save_profiles(profiles)
    print(f"Profile '{alias}' removed.")


def cmd_edit(alias):
    profiles = load_profiles()
    profile = next((p for p in profiles if p["alias"] == alias), None)
    if not profile:
        print(f"Profile '{alias}' not found.", file=sys.stderr)
        sys.exit(1)
    print(f"Editing profile '{alias}' (press Enter to keep current value)")
    new_alias = input(f"  Alias [{profile['alias']}]: ").strip() or profile["alias"]
    if new_alias != profile["alias"] and any(p["alias"] == new_alias for p in profiles):
        print(f"Alias '{new_alias}' already exists.", file=sys.stderr)
        sys.exit(1)
    print("  Available versions:")
    for v in detect_versions():
        print(f"    {v}")
    new_version = input(f"  Version [{profile['version']}]: ").strip() or profile["version"]
    new_config = input(f"  Config [{profile['config']}]: ").strip() or profile["config"]
    new_auth = input(f"  Auth mode [{profile['auth_mode']}]: ").strip() or profile["auth_mode"]
    new_kp = profile.get("keepass_entry", "")
    if new_auth == "keepass":
        new_kp = input(f"  KeePass entry [{new_kp or '(alias)'}]: ").strip() or new_kp
    idx = next(i for i, p in enumerate(profiles) if p["alias"] == alias)
    profiles[idx] = {
        "alias": new_alias, "version": new_version, "config": new_config,
        "auth_mode": new_auth, "keepass_entry": new_kp,
        "last_connected": profile.get("last_connected", ""),
    }
    save_profiles(profiles)
    print(f"Profile '{new_alias}' updated.")


def get_credentials(alias, auth_mode, keepass_entry, settings):
    if auth_mode == "keepass":
        keepass_db = settings.get("keepass_db", "~/Document/Keepass/keepass.kdbx")
        if not Path(keepass_db).expanduser().exists():
            print(f"KeePass DB not found: {keepass_db}", file=sys.stderr)
            return None, None
        entry = keepass_entry or alias
        print(f"Looking up credentials for '{entry}' in KeePass...")
        master = os.environ.get("KPPASS") or getpass.getpass("KeePass master password: ")
        user, pwd = fetch_keepass_creds(entry, keepass_db, master)
        master = None  # noqa: F841
        if user and pwd:
            print("Credentials loaded from KeePass.")
            return user, pwd
        print(f"No KeePass entry found for '{entry}'.")
        return None, None
    elif auth_mode == "prompt":
        user = input(f"VPN username for '{alias}': ")
        pwd = getpass.getpass(f"VPN password for '{alias}': ")
        return (user, pwd) if user and pwd else (None, None)
    return None, None


def cmd_connect(alias=None, version=None, config=None):
    settings = load_settings()
    prefix = Path(settings.get("openvpn_prefix", "/opt"))

    if alias and not version:
        profiles = load_profiles()
        profile = next((p for p in profiles if p["alias"] == alias), None)
        if not profile:
            print(f"Profile '{alias}' not found. Run: ovpn-connect --list", file=sys.stderr)
            sys.exit(1)
        version = profile["version"]
        config = profile["config"]
        auth_mode = profile["auth_mode"]
        keepass_entry = profile.get("keepass_entry", "")
    else:
        auth_mode = "none"
        keepass_entry = ""

    binary = openvpn_binary(version, prefix)
    if not binary.is_file():
        print(f"OpenVPN {version} not found at {binary}", file=sys.stderr)
        sys.exit(1)
    if not Path(config).is_file():
        print(f"Config not found: {config}", file=sys.stderr)
        sys.exit(1)

    print(f"Connecting with OpenVPN {version} ({binary})")
    print(f"Config: {config}")

    args = elevate_command([str(binary), "--config", config] + windows_driver_args())
    user, pwd = get_credentials(alias or "", auth_mode, keepass_entry, settings)
    auth_file = None
    if user and pwd:
        auth_file = tempfile.NamedTemporaryFile(mode="w", prefix="ovpn-auth-", delete=False)
        auth_file.write(f"{user}\n{pwd}\n")
        auth_file.close()
        os.chmod(auth_file.name, 0o600)
        atexit.register(lambda f=auth_file.name: os.unlink(f) if os.path.exists(f) else None)
        args += ["--auth-user-pass", auth_file.name]

    try:
        subprocess.run(args)
    except KeyboardInterrupt:
        print("\nDisconnected.")
    finally:
        if auth_file and os.path.exists(auth_file.name):
            os.unlink(auth_file.name)


def main():
    parser = argparse.ArgumentParser(
        prog="ovpn-connect",
        description="CLI companion for ovpn-launcher",
    )
    parser.add_argument("--version", "-v", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--list", "-l", action="store_true", help="List versions and profiles")
    parser.add_argument("--add", action="store_true", help="Add a new profile interactively")
    parser.add_argument("--remove", metavar="ALIAS", help="Remove a profile")
    parser.add_argument("--edit", metavar="ALIAS", help="Edit a profile interactively")
    parser.add_argument("--status", "-s", action="store_true", help="Check if openvpn is running")
    parser.add_argument("args", nargs="*", help="<alias> or <version> <config.ovpn>")

    opts = parser.parse_args()
    settings = load_settings()

    if opts.list:
        cmd_list(settings)
    elif opts.add:
        cmd_add()
    elif opts.remove:
        cmd_remove(opts.remove)
    elif opts.edit:
        cmd_edit(opts.edit)
    elif opts.status:
        cmd_status()
    elif len(opts.args) == 1:
        cmd_connect(alias=opts.args[0])
    elif len(opts.args) == 2:
        cmd_connect(version=opts.args[0], config=opts.args[1])
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
