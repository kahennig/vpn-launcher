"""Tests for ovpn_launcher.app (ProfileDialog)."""

import pytest
from unittest.mock import patch

from ovpn_launcher.app import ProfileDialog


class TestProfileDialogAdd:
    def test_fields_empty_by_default(self, qtbot):
        dlg = ProfileDialog()
        qtbot.addWidget(dlg)
        assert dlg.alias_edit.text() == ""
        assert dlg.config_edit.text() == ""
        assert dlg.auth_combo.currentText() == "none"

    def test_get_profile(self, qtbot):
        dlg = ProfileDialog()
        qtbot.addWidget(dlg)
        dlg.alias_edit.setText("test")
        dlg.version_combo.setCurrentText("system")
        dlg.config_edit.setText("/tmp/test.ovpn")
        dlg.auth_combo.setCurrentText("keepass")
        p = dlg.get_profile()
        assert p == {
            "alias": "test", "version": "system",
            "config": "/tmp/test.ovpn", "auth_mode": "keepass",
            "keepass_entry": "",
        }

    def test_get_profile_strips_whitespace(self, qtbot):
        dlg = ProfileDialog()
        qtbot.addWidget(dlg)
        dlg.alias_edit.setText("  test  ")
        dlg.version_combo.setCurrentText("  system  ")
        dlg.config_edit.setText("  /tmp/test.ovpn  ")
        p = dlg.get_profile()
        assert p["alias"] == "test"
        assert p["version"] == "system"
        assert p["config"] == "/tmp/test.ovpn"


class TestProfileDialogEdit:
    def test_fields_prefilled(self, qtbot):
        profile = {"alias": "vpn1", "version": "2.6.14", "config": "/etc/vpn.ovpn", "auth_mode": "prompt"}
        dlg = ProfileDialog(profile=profile)
        qtbot.addWidget(dlg)
        assert dlg.alias_edit.text() == "vpn1"
        assert dlg.version_combo.currentText() == "2.6.14"
        assert dlg.config_edit.text() == "/etc/vpn.ovpn"
        assert dlg.auth_combo.currentText() == "prompt"


class TestProfileDialogValidation:
    def test_empty_alias_rejected(self, qtbot):
        dlg = ProfileDialog()
        qtbot.addWidget(dlg)
        dlg.alias_edit.setText("")
        dlg.config_edit.setText("/tmp/test.ovpn")
        with patch.object(dlg, "accept") as mock_accept:
            dlg._validate_and_accept()
            mock_accept.assert_not_called()

    def test_duplicate_alias_rejected(self, qtbot):
        dlg = ProfileDialog(existing_aliases=["taken"])
        qtbot.addWidget(dlg)
        dlg.alias_edit.setText("taken")
        dlg.config_edit.setText("/tmp/test.ovpn")
        with patch.object(dlg, "accept") as mock_accept:
            dlg._validate_and_accept()
            mock_accept.assert_not_called()

    def test_empty_config_rejected(self, qtbot):
        dlg = ProfileDialog()
        qtbot.addWidget(dlg)
        dlg.alias_edit.setText("test")
        dlg.config_edit.setText("")
        with patch.object(dlg, "accept") as mock_accept:
            dlg._validate_and_accept()
            mock_accept.assert_not_called()

    def test_valid_profile_accepted(self, qtbot, tmp_path):
        conf = tmp_path / "test.ovpn"
        conf.write_text("client\n")
        dlg = ProfileDialog()
        qtbot.addWidget(dlg)
        dlg.alias_edit.setText("test")
        dlg.version_combo.setCurrentText("system")
        dlg.config_edit.setText(str(conf))
        with patch.object(dlg, "accept") as mock_accept:
            dlg._validate_and_accept()
            mock_accept.assert_called_once()


from ovpn_launcher.app import SettingsDialog, VPNLauncher
from ovpn_launcher.profiles import DEFAULT_SETTINGS


class TestProfileDialogKeepassEntry:
    def test_keepass_entry_hidden_when_none(self, qtbot):
        dlg = ProfileDialog()
        qtbot.addWidget(dlg)
        assert not dlg.keepass_entry_edit.isVisible()

    def test_keepass_entry_visible_when_keepass(self, qtbot):
        dlg = ProfileDialog()
        qtbot.addWidget(dlg)
        dlg.auth_combo.setCurrentText("keepass")
        assert not dlg.keepass_entry_edit.isHidden()

    def test_keepass_entry_hidden_when_prompt(self, qtbot):
        dlg = ProfileDialog()
        qtbot.addWidget(dlg)
        dlg.auth_combo.setCurrentText("keepass")
        dlg.auth_combo.setCurrentText("prompt")
        assert not dlg.keepass_entry_edit.isVisible()

    def test_get_profile_includes_keepass_entry(self, qtbot):
        profile = {"alias": "vpn", "version": "system", "config": "/vpn.ovpn",
                    "auth_mode": "keepass", "keepass_entry": "My VPN"}
        dlg = ProfileDialog(profile=profile)
        qtbot.addWidget(dlg)
        p = dlg.get_profile()
        assert p["keepass_entry"] == "My VPN"


class TestSettingsDialog:
    def test_fields_prefilled(self, qtbot):
        settings = {
            "openvpn_prefix": "/custom",
            "keepass_db": "/my/db.kdbx",
            "connection_timeout": 45,
            "reconnect_delay": 10,
            "ip_service": "https://example.com/ip",
            "log_level": "DEBUG",
        }
        dlg = SettingsDialog(settings=settings)
        qtbot.addWidget(dlg)
        assert dlg.prefix_edit.text() == "/custom"
        assert dlg.keepass_edit.text() == "/my/db.kdbx"
        assert dlg.timeout_spin.value() == 45
        assert dlg.reconnect_spin.value() == 10
        assert dlg.ip_edit.text() == "https://example.com/ip"
        assert dlg.log_combo.currentText() == "DEBUG"

    def test_get_settings(self, qtbot):
        dlg = SettingsDialog(settings=DEFAULT_SETTINGS)
        qtbot.addWidget(dlg)
        dlg.prefix_edit.setText("/opt")
        dlg.timeout_spin.setValue(60)
        s = dlg.get_settings()
        assert s["openvpn_prefix"] == "/opt"
        assert s["connection_timeout"] == 60

    def test_defaults_when_empty(self, qtbot):
        dlg = SettingsDialog(settings={})
        qtbot.addWidget(dlg)
        assert dlg.timeout_spin.value() == 30
        assert dlg.reconnect_spin.value() == 5
        assert dlg.log_combo.currentText() == "WARNING"


class TestVPNLauncherReload:
    def test_reload_populates_tree(self, qtbot, tmp_path):
        import ovpn_launcher.profiles as mod
        conf = tmp_path / "config.yaml"
        conf.write_text(
            "profiles:\n"
            "  - alias: test1\n"
            "    version: system\n"
            "    config: /test1.ovpn\n"
            "  - alias: test2\n"
            "    version: '2.6.14'\n"
            "    config: /test2.ovpn\n"
        )
        orig = mod.CONFIG_YAML
        mod.CONFIG_YAML = conf
        try:
            w = VPNLauncher()
            qtbot.addWidget(w)
            assert w.profile_tree.topLevelItemCount() == 2
            assert w.profile_tree.topLevelItem(0).text(0) == "test1"
            assert w.profile_tree.topLevelItem(1).text(0) == "test2"
        finally:
            mod.CONFIG_YAML = orig


class TestLogColor:
    def test_error_red(self, qtbot):
        w = VPNLauncher()
        qtbot.addWidget(w)
        assert w._log_color("ERROR: something failed") == "#e74c3c"

    def test_fatal_red(self, qtbot):
        w = VPNLauncher()
        qtbot.addWidget(w)
        assert w._log_color("FATAL: crash") == "#e74c3c"

    def test_warn_orange(self, qtbot):
        w = VPNLauncher()
        qtbot.addWidget(w)
        assert w._log_color("WARNING: something") == "#e67e22"

    def test_success_green(self, qtbot):
        w = VPNLauncher()
        qtbot.addWidget(w)
        assert w._log_color("Initialization Sequence Completed") == "#27ae60"

    def test_internal_muted(self, qtbot):
        w = VPNLauncher()
        qtbot.addWidget(w)
        color = w._log_color("-- Reconnecting in 5 seconds... --")
        assert color is not None
        assert color != "#e74c3c"

    def test_normal_none(self, qtbot):
        w = VPNLauncher()
        qtbot.addWidget(w)
        assert w._log_color("some regular openvpn output") is None
