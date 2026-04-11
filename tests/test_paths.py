"""Tests for ovpn_launcher.paths."""

from pathlib import Path

from ovpn_launcher.paths import CONFIG_DIR, CONNECTIONS_CONF, CONFIG_YAML, openvpn_binary


class TestOpenvpnBinary:
    def test_system_version(self):
        assert openvpn_binary("system") == Path("/usr/bin/openvpn")

    def test_specific_version(self):
        assert openvpn_binary("2.6.14") == Path("/opt/openvpn-2.6.14/sbin/openvpn")

    def test_another_version(self):
        assert openvpn_binary("2.5.11") == Path("/opt/openvpn-2.5.11/sbin/openvpn")

    def test_custom_prefix(self):
        assert openvpn_binary("2.6.14", Path("/custom")) == Path("/custom/openvpn-2.6.14/sbin/openvpn")

    def test_system_ignores_prefix(self):
        assert openvpn_binary("system", Path("/custom")) == Path("/usr/bin/openvpn")


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
