"""Tests for ovpn_launcher.services (pure logic, no Qt)."""

import subprocess
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml

from ovpn_launcher.services import (
    log_color, validate_ovpn, extract_remote_host,
    export_profile_zip, import_profile_zip, fetch_keepass_creds,
)


class TestLogColor:
    def test_error_red(self):
        assert log_color("ERROR: something failed") == "#e74c3c"

    def test_fatal_red(self):
        assert log_color("FATAL: crash") == "#e74c3c"

    def test_warn_orange(self):
        assert log_color("WARNING: something") == "#e67e22"

    def test_success_green(self):
        assert log_color("Initialization Sequence Completed") == "#27ae60"

    def test_internal_uses_muted(self):
        assert log_color("-- Reconnecting --", muted_color="#888") == "#888"

    def test_command_uses_muted(self):
        assert log_color("$ /opt/openvpn", muted_color="#999") == "#999"

    def test_internal_no_muted_returns_none(self):
        assert log_color("-- internal --") is None

    def test_normal_returns_none(self):
        assert log_color("some regular output") is None


class TestValidateOvpn:
    def test_valid_config(self, tmp_path):
        f = tmp_path / "test.ovpn"
        f.write_text("remote vpn.example.com 1194\ndev tun\n")
        assert validate_ovpn(f) == []

    def test_missing_remote(self, tmp_path):
        f = tmp_path / "test.ovpn"
        f.write_text("dev tun\n")
        assert validate_ovpn(f) == ["remote"]

    def test_missing_dev(self, tmp_path):
        f = tmp_path / "test.ovpn"
        f.write_text("remote vpn.example.com 1194\n")
        assert validate_ovpn(f) == ["dev"]

    def test_missing_both(self, tmp_path):
        f = tmp_path / "test.ovpn"
        f.write_text("# empty config\n")
        assert validate_ovpn(f) == ["remote", "dev"]


class TestExtractRemoteHost:
    def test_extracts_host(self, tmp_path):
        f = tmp_path / "test.ovpn"
        f.write_text("client\nremote vpn.example.com 1194\ndev tun\n")
        assert extract_remote_host(f) == "vpn.example.com"

    def test_no_remote(self, tmp_path):
        f = tmp_path / "test.ovpn"
        f.write_text("client\ndev tun\n")
        assert extract_remote_host(f) is None

    def test_first_remote_wins(self, tmp_path):
        f = tmp_path / "test.ovpn"
        f.write_text("remote first.com 1194\nremote second.com 1194\n")
        assert extract_remote_host(f) == "first.com"


class TestExportProfileZip:
    def test_basic_export(self, tmp_path):
        ovpn = tmp_path / "test.ovpn"
        ovpn.write_text("remote vpn.example.com\ndev tun\n")
        dest = tmp_path / "export.zip"
        profile = {"alias": "vpn1", "version": "2.6.14", "config": str(ovpn), "auth_mode": "none"}
        export_profile_zip(profile, dest)
        with zipfile.ZipFile(dest) as zf:
            assert "profile.yaml" in zf.namelist()
            assert "test.ovpn" in zf.namelist()
            meta = yaml.safe_load(zf.read("profile.yaml"))
            assert meta["alias"] == "vpn1"
            assert meta["version"] == "2.6.14"
            assert meta["config"] == "test.ovpn"
            assert "auth_mode" not in meta  # none is omitted

    def test_export_with_keepass(self, tmp_path):
        ovpn = tmp_path / "test.ovpn"
        ovpn.write_text("remote vpn.example.com\n")
        dest = tmp_path / "export.zip"
        profile = {"alias": "vpn1", "version": "system", "config": str(ovpn),
                    "auth_mode": "keepass", "keepass_entry": "My VPN"}
        export_profile_zip(profile, dest)
        with zipfile.ZipFile(dest) as zf:
            meta = yaml.safe_load(zf.read("profile.yaml"))
            assert meta["auth_mode"] == "keepass"
            assert meta["keepass_entry"] == "My VPN"

    def test_export_missing_ovpn(self, tmp_path):
        dest = tmp_path / "export.zip"
        profile = {"alias": "vpn1", "version": "system", "config": "/nonexistent.ovpn", "auth_mode": "none"}
        export_profile_zip(profile, dest)
        with zipfile.ZipFile(dest) as zf:
            assert "profile.yaml" in zf.namelist()
            assert len(zf.namelist()) == 1  # only profile.yaml


class TestImportProfileZip:
    def test_basic_import(self, tmp_path):
        ovpn_content = b"remote vpn.example.com\ndev tun\n"
        zpath = tmp_path / "import.zip"
        with zipfile.ZipFile(zpath, "w") as zf:
            zf.writestr("profile.yaml", yaml.dump({"alias": "vpn1", "version": "2.6.14", "config": "test.ovpn"}))
            zf.writestr("test.ovpn", ovpn_content)
        meta, ovpn_bytes = import_profile_zip(zpath)
        assert meta["alias"] == "vpn1"
        assert ovpn_bytes == ovpn_content

    def test_import_with_keepass(self, tmp_path):
        zpath = tmp_path / "import.zip"
        with zipfile.ZipFile(zpath, "w") as zf:
            zf.writestr("profile.yaml", yaml.dump({
                "alias": "vpn1", "version": "system", "config": "test.ovpn",
                "auth_mode": "keepass", "keepass_entry": "My VPN",
            }))
            zf.writestr("test.ovpn", b"remote x\n")
        meta, _ = import_profile_zip(zpath)
        assert meta["auth_mode"] == "keepass"
        assert meta["keepass_entry"] == "My VPN"

    def test_import_no_ovpn_file(self, tmp_path):
        zpath = tmp_path / "import.zip"
        with zipfile.ZipFile(zpath, "w") as zf:
            zf.writestr("profile.yaml", yaml.dump({"alias": "vpn1", "version": "system", "config": "missing.ovpn"}))
        meta, ovpn_bytes = import_profile_zip(zpath)
        assert meta["alias"] == "vpn1"
        assert ovpn_bytes is None

    def test_import_missing_profile_yaml(self, tmp_path):
        zpath = tmp_path / "import.zip"
        with zipfile.ZipFile(zpath, "w") as zf:
            zf.writestr("test.ovpn", b"remote x\n")
        with pytest.raises(ValueError, match="No profile.yaml"):
            import_profile_zip(zpath)

    def test_import_invalid_yaml(self, tmp_path):
        zpath = tmp_path / "import.zip"
        with zipfile.ZipFile(zpath, "w") as zf:
            zf.writestr("profile.yaml", yaml.dump({"alias": "vpn1"}))  # missing version, config
        with pytest.raises(ValueError, match="Invalid profile.yaml"):
            import_profile_zip(zpath)

    def test_import_bad_zip(self, tmp_path):
        bad = tmp_path / "bad.zip"
        bad.write_text("not a zip")
        with pytest.raises(zipfile.BadZipFile):
            import_profile_zip(bad)


class TestFetchKeepassCreds:
    def test_db_not_found(self, tmp_path):
        user, pwd = fetch_keepass_creds("entry", tmp_path / "nonexistent.kdbx", "pass")
        assert user is None and pwd is None

    @patch("ovpn_launcher.services.subprocess.run")
    def test_success(self, mock_run, tmp_path):
        db = tmp_path / "test.kdbx"
        db.write_bytes(b"fake")
        mock_run.side_effect = [
            MagicMock(stdout="myuser\n", returncode=0),
            MagicMock(stdout="mypass\n", returncode=0),
        ]
        user, pwd = fetch_keepass_creds("entry", str(db), "master")
        assert user == "myuser"
        assert pwd == "mypass"

    @patch("ovpn_launcher.services.subprocess.run")
    def test_empty_creds(self, mock_run, tmp_path):
        db = tmp_path / "test.kdbx"
        db.write_bytes(b"fake")
        mock_run.side_effect = [
            MagicMock(stdout="", returncode=1, stderr="not found"),
            MagicMock(stdout="", returncode=1, stderr="not found"),
        ]
        user, pwd = fetch_keepass_creds("entry", str(db), "master")
        assert user is None and pwd is None

    @patch("ovpn_launcher.services.subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 10))
    def test_timeout(self, mock_run, tmp_path):
        import subprocess
        db = tmp_path / "test.kdbx"
        db.write_bytes(b"fake")
        user, pwd = fetch_keepass_creds("entry", str(db), "master")
        assert user is None and pwd is None
