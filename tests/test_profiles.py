"""Tests for ovpn_launcher.profiles (YAML config)."""

import pytest
from pathlib import Path

from ovpn_launcher.profiles import (
    load_profiles, save_profiles, detect_versions, load_settings,
    save_settings, migrate_legacy_config, VALID_AUTH_MODES, DEFAULT_SETTINGS,
)


@pytest.fixture
def conf_file(tmp_path):
    return tmp_path / "config.yaml"


@pytest.fixture
def legacy_file(tmp_path):
    return tmp_path / "connections.conf"


class TestLoadProfiles:
    def test_empty_file(self, conf_file):
        conf_file.write_text("")
        assert load_profiles(conf_file) == []

    def test_missing_file(self, tmp_path):
        assert load_profiles(tmp_path / "nonexistent.yaml") == []

    def test_basic_profile(self, conf_file):
        conf_file.write_text(
            "profiles:\n"
            "  - alias: myalias\n"
            "    version: '2.6.14'\n"
            "    config: /path/to/config.ovpn\n"
        )
        profiles = load_profiles(conf_file)
        assert len(profiles) == 1
        assert profiles[0] == {
            "alias": "myalias", "version": "2.6.14",
            "config": "/path/to/config.ovpn", "auth_mode": "none",
            "keepass_entry": "", "last_connected": "",
        }

    def test_auth_mode_keepass(self, conf_file):
        conf_file.write_text(
            "profiles:\n"
            "  - alias: vpn\n"
            "    version: system\n"
            "    config: /etc/vpn.ovpn\n"
            "    auth_mode: keepass\n"
        )
        assert load_profiles(conf_file)[0]["auth_mode"] == "keepass"

    def test_invalid_auth_mode_defaults_to_none(self, conf_file):
        conf_file.write_text(
            "profiles:\n"
            "  - alias: vpn\n"
            "    version: system\n"
            "    config: /etc/vpn.ovpn\n"
            "    auth_mode: bogus\n"
        )
        assert load_profiles(conf_file)[0]["auth_mode"] == "none"

    def test_keepass_entry(self, conf_file):
        conf_file.write_text(
            "profiles:\n"
            "  - alias: vpn\n"
            "    version: system\n"
            "    config: /etc/vpn.ovpn\n"
            "    auth_mode: keepass\n"
            "    keepass_entry: My VPN Entry\n"
        )
        assert load_profiles(conf_file)[0]["keepass_entry"] == "My VPN Entry"

    def test_multiple_profiles(self, conf_file):
        conf_file.write_text(
            "profiles:\n"
            "  - alias: a\n"
            "    version: '2.6.14'\n"
            "    config: /a.ovpn\n"
            "    auth_mode: keepass\n"
            "  - alias: b\n"
            "    version: system\n"
            "    config: /b.ovpn\n"
            "    auth_mode: prompt\n"
            "  - alias: c\n"
            "    version: '2.5.11'\n"
            "    config: /c.ovpn\n"
        )
        profiles = load_profiles(conf_file)
        assert len(profiles) == 3
        assert profiles[0]["auth_mode"] == "keepass"
        assert profiles[1]["auth_mode"] == "prompt"
        assert profiles[2]["auth_mode"] == "none"


class TestSaveProfiles:
    def test_save_and_reload(self, conf_file):
        profiles = [
            {"alias": "a", "version": "2.6.14", "config": "/a.ovpn", "auth_mode": "keepass", "keepass_entry": ""},
            {"alias": "b", "version": "system", "config": "/b.ovpn", "auth_mode": "none", "keepass_entry": ""},
        ]
        save_profiles(profiles, conf_file)
        loaded = load_profiles(conf_file)
        assert len(loaded) == 2
        assert loaded[0]["auth_mode"] == "keepass"
        assert loaded[1]["auth_mode"] == "none"

    def test_none_auth_mode_omitted(self, conf_file):
        profiles = [{"alias": "x", "version": "system", "config": "/x.ovpn", "auth_mode": "none", "keepass_entry": ""}]
        save_profiles(profiles, conf_file)
        content = conf_file.read_text()
        assert "auth_mode" not in content

    def test_keepass_entry_omitted_if_empty(self, conf_file):
        profiles = [{"alias": "x", "version": "system", "config": "/x.ovpn", "auth_mode": "keepass", "keepass_entry": ""}]
        save_profiles(profiles, conf_file)
        content = conf_file.read_text()
        assert "keepass_entry" not in content

    def test_preserves_settings(self, conf_file):
        conf_file.write_text("settings:\n  connection_timeout: 60\nprofiles: []\n")
        profiles = [{"alias": "new", "version": "system", "config": "/new.ovpn", "auth_mode": "none", "keepass_entry": ""}]
        save_profiles(profiles, conf_file)
        settings = load_settings(conf_file)
        assert settings["connection_timeout"] == 60

    def test_creates_parent_dirs(self, tmp_path):
        conf = tmp_path / "sub" / "dir" / "config.yaml"
        profiles = [{"alias": "a", "version": "system", "config": "/a.ovpn", "auth_mode": "none", "keepass_entry": ""}]
        save_profiles(profiles, conf)
        assert conf.exists()

    def test_roundtrip_preserves_order(self, conf_file):
        profiles = [
            {"alias": "z", "version": "system", "config": "/z.ovpn", "auth_mode": "none", "keepass_entry": ""},
            {"alias": "a", "version": "2.6.14", "config": "/a.ovpn", "auth_mode": "keepass", "keepass_entry": ""},
            {"alias": "m", "version": "2.5.11", "config": "/m.ovpn", "auth_mode": "prompt", "keepass_entry": ""},
        ]
        save_profiles(profiles, conf_file)
        loaded = load_profiles(conf_file)
        assert [p["alias"] for p in loaded] == ["z", "a", "m"]


class TestSettings:
    def test_defaults(self, conf_file):
        conf_file.write_text("")
        settings = load_settings(conf_file)
        assert settings == DEFAULT_SETTINGS

    def test_override(self, conf_file):
        conf_file.write_text("settings:\n  connection_timeout: 60\n")
        settings = load_settings(conf_file)
        assert settings["connection_timeout"] == 60
        assert settings["reconnect_delay"] == 5  # default preserved

    def test_save_and_reload(self, conf_file):
        settings = dict(DEFAULT_SETTINGS)
        settings["connection_timeout"] = 45
        save_settings(settings, conf_file)
        loaded = load_settings(conf_file)
        assert loaded["connection_timeout"] == 45


class TestMigrateLegacy:
    def test_basic_migration(self, legacy_file, conf_file):
        legacy_file.write_text("# Header\nclient-a|2.6.14|/a.ovpn|keepass\noffice|system|/b.ovpn\n")
        migrate_legacy_config(legacy_file, conf_file)
        profiles = load_profiles(conf_file)
        assert len(profiles) == 2
        assert profiles[0]["alias"] == "client-a"
        assert profiles[0]["auth_mode"] == "keepass"
        assert profiles[1]["alias"] == "office"
        assert profiles[1]["auth_mode"] == "none"

    def test_migration_with_keepass_entry(self, legacy_file, conf_file):
        legacy_file.write_text("vpn|system|/vpn.ovpn|keepass|My Entry\n")
        migrate_legacy_config(legacy_file, conf_file)
        profiles = load_profiles(conf_file)
        assert profiles[0]["keepass_entry"] == "My Entry"

    def test_migration_creates_settings(self, legacy_file, conf_file):
        legacy_file.write_text("vpn|system|/vpn.ovpn\n")
        migrate_legacy_config(legacy_file, conf_file)
        settings = load_settings(conf_file)
        assert settings == DEFAULT_SETTINGS

    def test_missing_legacy_does_nothing(self, tmp_path, conf_file):
        migrate_legacy_config(tmp_path / "nonexistent.conf", conf_file)
        assert not conf_file.exists()


class TestDetectVersions:
    def test_returns_list(self):
        versions = detect_versions()
        assert isinstance(versions, list)

    def test_system_included_if_exists(self):
        versions = detect_versions()
        if Path("/usr/bin/openvpn").is_file():
            assert any(v.startswith("system") for v in versions)


class TestSaveProfilesLastConnected:
    def test_save_and_load_last_connected(self, conf_file):
        profiles = [
            {"alias": "a", "version": "system", "config": "/a.ovpn",
             "auth_mode": "none", "keepass_entry": "", "last_connected": "2026-04-10 15:30"},
        ]
        save_profiles(profiles, conf_file)
        loaded = load_profiles(conf_file)
        assert loaded[0]["last_connected"] == "2026-04-10 15:30"

    def test_empty_last_connected_omitted(self, conf_file):
        profiles = [
            {"alias": "a", "version": "system", "config": "/a.ovpn",
             "auth_mode": "none", "keepass_entry": "", "last_connected": ""},
        ]
        save_profiles(profiles, conf_file)
        content = conf_file.read_text()
        assert "last_connected" not in content


class TestSaveBackup:
    def test_creates_backup(self, conf_file):
        conf_file.write_text("profiles: []\n")
        profiles = [{"alias": "a", "version": "system", "config": "/a.ovpn",
                      "auth_mode": "none", "keepass_entry": "", "last_connected": ""}]
        save_profiles(profiles, conf_file)
        bak = conf_file.with_suffix(".yaml.bak")
        assert bak.exists()
        assert "profiles: []" in bak.read_text()


class TestAutoMigration:
    def test_auto_migrates_on_load(self, tmp_path):
        legacy = tmp_path / "connections.conf"
        legacy.write_text("vpn|system|/vpn.ovpn|keepass\n")
        yaml_path = tmp_path / "config.yaml"
        # Monkey-patch the module constants temporarily
        import ovpn_launcher.profiles as mod
        orig_yaml = mod.CONFIG_YAML
        orig_conf = mod.CONNECTIONS_CONF
        mod.CONFIG_YAML = yaml_path
        mod.CONNECTIONS_CONF = legacy
        try:
            profiles = load_profiles(yaml_path)
            assert len(profiles) == 1
            assert profiles[0]["alias"] == "vpn"
            assert yaml_path.exists()
        finally:
            mod.CONFIG_YAML = orig_yaml
            mod.CONNECTIONS_CONF = orig_conf
