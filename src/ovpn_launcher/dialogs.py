"""Dialog classes for VPN Launcher GUI."""

import threading
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSpinBox,
    QTextEdit, QVBoxLayout,
)

from .builder import fetch_available_versions, installed_versions, build_openvpn, has_tap_driver
from .paths import IS_WINDOWS
from .profiles import detect_versions, VALID_AUTH_MODES


class BuildDialog(QDialog):
    def __init__(self, parent=None, prefix="/opt"):
        super().__init__(parent)
        self.prefix = prefix
        self.setWindowTitle("Build OpenVPN")
        self.setMinimumSize(500, 400)
        layout = QVBoxLayout(self)

        row = QHBoxLayout()
        row.addWidget(QLabel("Version:"))
        self.version_combo = QComboBox()
        self.version_combo.setEditable(True)
        self.version_combo.addItem("Loading versions...")
        row.addWidget(self.version_combo)
        self.build_btn = QPushButton("Install" if IS_WINDOWS else "Build")
        self.build_btn.clicked.connect(self._start_build)
        row.addWidget(self.build_btn)
        layout.addLayout(row)

        self.full_install_cb = None
        if IS_WINDOWS:
            from PyQt6.QtWidgets import QCheckBox
            self.full_install_cb = QCheckBox("Full install (includes TAP/TUN driver)")
            self.full_install_cb.setChecked(not has_tap_driver())
            layout.addWidget(self.full_install_cb)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("font-family: monospace; font-size: 9pt;")
        layout.addWidget(self.output)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

        self._building = False
        QTimer.singleShot(0, self._load_versions)

    def _load_versions(self):
        self.version_combo.clear()
        inst = set(installed_versions(self.prefix))
        available = fetch_available_versions()
        for v in available:
            label = f"{v} (installed)" if v in inst else v
            self.version_combo.addItem(label, v)
        if not available:
            self.version_combo.addItem("(type version manually)")

    def _start_build(self):
        if self._building:
            return
        version = self.version_combo.currentData() or self.version_combo.currentText().strip()
        if not version or version.startswith("("):
            return
        self._building = True
        self.build_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        self.output.clear()

        def run():
            full = self.full_install_cb.isChecked() if self.full_install_cb else False
            build_openvpn(version, self.prefix, on_output=self._append_output, full_install=full)
            self._build_done()
        threading.Thread(target=run, daemon=True).start()

    def _append_output(self, text):
        from PyQt6.QtCore import QMetaObject, Qt as QtConst, Q_ARG
        QMetaObject.invokeMethod(self.output, "append", QtConst.ConnectionType.QueuedConnection, Q_ARG(str, text))

    def _build_done(self):
        self._append_output("\n--- Build process finished ---")
        self._building = False
        QTimer.singleShot(0, self._enable_buttons)

    def _enable_buttons(self):
        self.build_btn.setEnabled(True)
        self.close_btn.setEnabled(True)
        self._load_versions()


class SettingsDialog(QDialog):
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(480)
        s = settings or {}
        layout = QFormLayout(self)

        row = QHBoxLayout()
        self.prefix_edit = QLineEdit(s.get("openvpn_prefix", "/opt"))
        btn = QPushButton("Browse…")
        btn.clicked.connect(lambda: self._browse_dir(self.prefix_edit))
        row.addWidget(self.prefix_edit)
        row.addWidget(btn)
        layout.addRow("OpenVPN Prefix:", row)

        row2 = QHBoxLayout()
        self.keepass_edit = QLineEdit(s.get("keepass_db", ""))
        btn2 = QPushButton("Browse…")
        btn2.clicked.connect(lambda: self._browse_file(self.keepass_edit, "KeePass DB (*.kdbx);;All Files (*)"))
        row2.addWidget(self.keepass_edit)
        row2.addWidget(btn2)
        layout.addRow("KeePass DB:", row2)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setSuffix(" s")
        self.timeout_spin.setValue(int(s.get("connection_timeout", 30)))
        layout.addRow("Connection Timeout:", self.timeout_spin)

        self.reconnect_spin = QSpinBox()
        self.reconnect_spin.setRange(1, 120)
        self.reconnect_spin.setSuffix(" s")
        self.reconnect_spin.setValue(int(s.get("reconnect_delay", 5)))
        layout.addRow("Reconnect Delay:", self.reconnect_spin)

        self.ip_edit = QLineEdit(s.get("ip_service", "https://api.ipify.org"))
        layout.addRow("IP Service URL:", self.ip_edit)

        self.log_combo = QComboBox()
        self.log_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_combo.setCurrentText(s.get("log_level", "WARNING"))
        layout.addRow("Log Level:", self.log_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def _browse_dir(self, line_edit):
        path = QFileDialog.getExistingDirectory(self, "Select Directory", line_edit.text())
        if path:
            line_edit.setText(path)

    def _browse_file(self, line_edit, filter_str):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", line_edit.text(), filter_str)
        if path:
            line_edit.setText(path)

    def get_settings(self):
        return {
            "openvpn_prefix": self.prefix_edit.text().strip(),
            "keepass_db": self.keepass_edit.text().strip(),
            "connection_timeout": self.timeout_spin.value(),
            "reconnect_delay": self.reconnect_spin.value(),
            "ip_service": self.ip_edit.text().strip(),
            "log_level": self.log_combo.currentText(),
        }


class ProfileDialog(QDialog):
    def __init__(self, parent=None, profile=None, existing_aliases=None):
        super().__init__(parent)
        self.existing_aliases = existing_aliases or []
        self.setWindowTitle("Edit Profile" if profile else "Add Profile")
        self.setMinimumWidth(420)

        layout = QFormLayout(self)

        self.alias_edit = QLineEdit()
        layout.addRow("Alias:", self.alias_edit)

        self.version_combo = QComboBox()
        self.version_combo.setEditable(True)
        for v in detect_versions():
            if v.startswith("system"):
                self.version_combo.addItem(v, "system")
            else:
                self.version_combo.addItem(v, v)
        layout.addRow("OpenVPN Version:", self.version_combo)

        config_row = QHBoxLayout()
        self.config_edit = QLineEdit()
        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse_config)
        config_row.addWidget(self.config_edit)
        config_row.addWidget(browse_btn)
        layout.addRow("Config File:", config_row)

        self.auth_combo = QComboBox()
        self.auth_combo.addItems(VALID_AUTH_MODES)
        self.auth_combo.currentTextChanged.connect(self._on_auth_mode_changed)
        layout.addRow("Auth Mode:", self.auth_combo)

        self.keepass_entry_edit = QLineEdit()
        self.keepass_entry_edit.setPlaceholderText("(uses alias if empty)")
        self._keepass_entry_label = QLabel("KeePass Entry:")
        layout.addRow(self._keepass_entry_label, self.keepass_entry_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        if profile:
            self.alias_edit.setText(profile["alias"])
            idx = self.version_combo.findData(profile["version"])
            if idx >= 0:
                self.version_combo.setCurrentIndex(idx)
            else:
                self.version_combo.setCurrentText(profile["version"])
            self.config_edit.setText(profile["config"])
            self.auth_combo.setCurrentText(profile.get("auth_mode", "none"))
            self.keepass_entry_edit.setText(profile.get("keepass_entry", ""))

        self._on_auth_mode_changed(self.auth_combo.currentText())

    def _on_auth_mode_changed(self, mode):
        visible = mode == "keepass"
        self._keepass_entry_label.setVisible(visible)
        self.keepass_entry_edit.setVisible(visible)

    def _browse_config(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select OpenVPN Config", "",
            "OpenVPN Config (*.ovpn *.conf);;All Files (*)",
        )
        if path:
            self.config_edit.setText(path)

    def _validate_and_accept(self):
        alias = self.alias_edit.text().strip()
        if not alias:
            QMessageBox.warning(self, "Validation", "Alias cannot be empty.")
            return
        if alias in self.existing_aliases:
            QMessageBox.warning(self, "Validation", f"Alias '{alias}' already exists.")
            return
        config = self.config_edit.text().strip()
        if not config:
            QMessageBox.warning(self, "Validation", "Config file cannot be empty.")
            return
        if not Path(config).is_file():
            QMessageBox.warning(self, "Warning", f"Config file not found:\n{config}\n\nProfile will be saved anyway.")
        self.accept()

    def get_profile(self):
        return {
            "alias": self.alias_edit.text().strip(),
            "version": self.version_combo.currentData() or self.version_combo.currentText().strip(),
            "config": self.config_edit.text().strip(),
            "auth_mode": self.auth_combo.currentText(),
            "keepass_entry": self.keepass_entry_edit.text().strip(),
        }
