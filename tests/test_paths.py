"""Tests for ovpn_launcher.paths."""

import sys
from pathlib import Path

from ovpn_launcher.paths import (
    IS_WINDOWS, CONFIG_DIR, CONNECTIONS_CONF, CONFIG_YAML, LOG_DIR,
    OPENVPN_PREFIX, AUTOSTART_DIR, AUTOSTART_FILE, openvpn_binary,
)


class TestOpenvpnBinary:
    def test_system_version_linux(self):
        if IS_WINDOWS:
            return
        assert openvpn_binary("system") == Path("/usr/bin/openvpn")

    def test_system_version_windows(self):
        if not IS_WINDOWS:
            return
        result = openvpn_binary("system")
        assert result.name == "openvpn.exe"
        assert "OpenVPN" in str(result)

    def test_specific_version(self):
        result = openvpn_binary("2.6.14")
        assert "openvpn-2.6.14" in str(result)
        if IS_WINDOWS:
            assert result.name == "openvpn.exe"
        else:
            assert result.name == "openvpn"

    def test_custom_prefix(self):
        result = openvpn_binary("2.6.14", Path("/custom"))
        assert "openvpn-2.6.14" in str(result)
        assert "custom" in str(result)

    def test_system_ignores_prefix(self):
        result = openvpn_binary("system", Path("/custom"))
        assert "/custom" not in str(result)


class TestConstants:
    def test_config_dir_ends_with_ovpn_launcher(self):
        assert CONFIG_DIR.name == "ovpn-launcher"

    def test_connections_conf_name(self):
        assert CONNECTIONS_CONF.name == "connections.conf"

    def test_connections_conf_inside_config_dir(self):
        assert CONNECTIONS_CONF.parent == CONFIG_DIR

    def test_config_yaml_name(self):
        assert CONFIG_YAML.name == "config.yaml"

    def test_config_yaml_inside_config_dir(self):
        assert CONFIG_YAML.parent == CONFIG_DIR

    def test_log_dir_inside_config_dir(self):
        assert LOG_DIR.parent == CONFIG_DIR

    def test_platform_detection(self):
        assert IS_WINDOWS == (sys.platform == "win32")

    def test_openvpn_prefix_is_path(self):
        assert isinstance(OPENVPN_PREFIX, Path)
