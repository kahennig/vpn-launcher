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
