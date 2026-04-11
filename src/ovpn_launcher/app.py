#!/usr/bin/env python3
"""VPN Launcher - Multi-version OpenVPN connection manager (KDE Plasma)."""

import os
import sys
import signal
import subprocess
import tempfile
import logging
import zipfile
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, QProcess, QSettings, QSize, QTimer, QEvent
from PyQt6.QtGui import QIcon, QAction, QTextCursor, QKeySequence, QPalette, QFont, QPixmap, QPainter, QColor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, QSystemTrayIcon,
    QMenu, QInputDialog, QLineEdit, QMessageBox, QTextEdit, QSplitter,
    QToolBar, QStatusBar, QHeaderView, QStyle, QDialog, QTabWidget,
    QFormLayout, QComboBox, QFileDialog, QDialogButtonBox, QToolButton,
    QSpinBox, QSplashScreen, QTextBrowser,
)

from .paths import CONNECTIONS_CONF, openvpn_binary
from .paths import CONFIG_DIR, LOG_DIR, AUTOSTART_DIR, AUTOSTART_DESKTOP, OPENVPN_PREFIX
from .profiles import load_profiles, save_profiles, detect_versions, load_settings, save_settings, VALID_AUTH_MODES
from . import __version__

from .builder import fetch_available_versions, installed_versions, build_openvpn

log = logging.getLogger(__name__)


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
        self.build_btn = QPushButton("Build")
        self.build_btn.clicked.connect(self._start_build)
        row.addWidget(self.build_btn)
        layout.addLayout(row)

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

        import threading
        def run():
            build_openvpn(version, self.prefix, on_output=self._append_output)
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


class VPNLauncher(QMainWindow):
    STATE_DISCONNECTED = 0
    STATE_CONNECTING = 1
    STATE_CONNECTED = 2

    def __init__(self):
        super().__init__()
        self.process = None
        self.auth_file = None
        self._log_file = None
        self.connected_alias = None
        self._last_profile = None
        self._user_disconnected = False
        self._reconnect_attempt = 0
        self._reconnect_delays = [5, 10, 20, 60]
        self._reconnect_max = 5
        self.state = self.STATE_DISCONNECTED
        self.connect_timer = QTimer(self)
        self.connect_timer.setSingleShot(True)
        self.connect_timer.timeout.connect(self._on_connection_timeout)
        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.setSingleShot(True)
        self.reconnect_timer.timeout.connect(self._on_reconnect)
        self._elapsed_timer = QTimer(self)
        self._elapsed_timer.timeout.connect(self._update_elapsed)
        self._elapsed_seconds = 0
        self.settings = QSettings("ovpn-launcher", "ovpn-launcher")
        self._app_settings = load_settings()

        self.setWindowTitle("VPN Launcher")
        self.setWindowIcon(_app_icon())
        self.setMinimumSize(580, 460)

        self._setup_actions()
        self._setup_toolbar()
        self._setup_ui()
        self._setup_tray()
        self._setup_statusbar()
        self._restore_geometry()

        self.reload_profiles()
        self._update_state(self.STATE_DISCONNECTED)

    # ── Actions ──────────────────────────────────────────────────────

    def _setup_actions(self):
        self.action_connect = QAction(QIcon.fromTheme("network-connect"), "&Connect", self)
        self.action_connect.setShortcut(QKeySequence("Ctrl+Return"))
        self.action_connect.setToolTip("Connect to selected profile (Ctrl+Enter)")
        self.action_connect.triggered.connect(self.on_connect)

        self.action_disconnect = QAction(QIcon.fromTheme("network-disconnect"), "&Disconnect", self)
        self.action_disconnect.setShortcut(QKeySequence("Ctrl+D"))
        self.action_disconnect.setToolTip("Disconnect (Ctrl+D)")
        self.action_disconnect.triggered.connect(self.on_disconnect)

        self.action_reload = QAction(QIcon.fromTheme("view-refresh"), "&Reload Profiles", self)
        self.action_reload.setShortcut(QKeySequence.StandardKey.Refresh)
        self.action_reload.setToolTip("Reload profiles from connections.conf")
        self.action_reload.triggered.connect(self.reload_profiles)

        self.action_clear_log = QAction(QIcon.fromTheme("edit-clear-history"), "Clear &Log", self)
        self.action_clear_log.setShortcut(QKeySequence("Ctrl+L"))
        self.action_clear_log.triggered.connect(lambda: self.log_output.clear())

        self.action_copy_log = QAction(QIcon.fromTheme("edit-copy"), "Copy Lo&g", self)
        self.action_copy_log.setShortcut(QKeySequence("Ctrl+Shift+C"))
        self.action_copy_log.setToolTip("Copy log to clipboard (Ctrl+Shift+C)")
        self.action_copy_log.triggered.connect(
            lambda: QApplication.clipboard().setText(self.log_output.toPlainText())
        )

        self.action_add = QAction(QIcon.fromTheme("list-add"), "&Add Profile", self)
        self.action_add.setShortcut(QKeySequence("Ctrl+N"))
        self.action_add.setToolTip("Add a new VPN profile (Ctrl+N)")
        self.action_add.triggered.connect(self.on_add_profile)

        self.action_import = QAction(QIcon.fromTheme("document-import"), "&Import .ovpn", self)
        self.action_import.setToolTip("Import an .ovpn file as a new profile")
        self.action_import.triggered.connect(self.on_import_ovpn)

        self.action_import_zip = QAction(QIcon.fromTheme("package-x-generic"), "I&mport Profile", self)
        self.action_import_zip.setToolTip("Import a profile from exported .zip")
        self.action_import_zip.triggered.connect(self.on_import_zip)

        self.action_edit = QAction(QIcon.fromTheme("document-edit"), "&Edit Profile", self)
        self.action_edit.setShortcut(QKeySequence("Ctrl+E"))
        self.action_edit.setToolTip("Edit selected profile (Ctrl+E)")
        self.action_edit.triggered.connect(self.on_edit_profile)

        self.action_remove = QAction(QIcon.fromTheme("list-remove"), "&Remove Profile", self)
        self.action_remove.setShortcut(QKeySequence("Delete"))
        self.action_remove.setToolTip("Remove selected profile (Delete)")
        self.action_remove.triggered.connect(self.on_remove_profile)

        self.action_export = QAction(QIcon.fromTheme("document-export"), "E&xport Profile", self)
        self.action_export.setToolTip("Export selected profile as .zip")
        self.action_export.triggered.connect(self.on_export_profile)

        self.action_ping = QAction(QIcon.fromTheme("network-wired"), "&Ping Server", self)
        self.action_ping.setToolTip("Ping VPN server to check latency")
        self.action_ping.triggered.connect(self.on_ping_profile)

        self.action_dns_check = QAction(QIcon.fromTheme("network-server"), "&DNS Check", self)
        self.action_dns_check.setToolTip("Check DNS resolver (leak test)")
        self.action_dns_check.triggered.connect(self.on_dns_check)

        self.action_build = QAction(QIcon.fromTheme("run-build"), "Build Open&VPN", self)
        self.action_build.setToolTip("Download and compile an OpenVPN version")
        self.action_build.triggered.connect(self._show_build_dialog)

        self.action_open_configs = QAction(QIcon.fromTheme("folder-open"), "Open Configs Folder", self)
        self.action_open_configs.triggered.connect(lambda: self._open_folder(CONFIG_DIR / "configs"))

        self.action_open_logs = QAction(QIcon.fromTheme("folder-open"), "Open Logs Folder", self)
        self.action_open_logs.triggered.connect(lambda: self._open_folder(LOG_DIR))

        self.action_about = QAction(QIcon.fromTheme("help-about"), "&About VPN Launcher", self)
        self.action_about.triggered.connect(self._show_about)

        self.action_settings = QAction(QIcon.fromTheme("configure"), "&Settings", self)
        self.action_settings.triggered.connect(self._show_settings)

        self.action_search_log = QAction("Find in Log", self)
        self.action_search_log.setShortcut(QKeySequence.StandardKey.Find)
        self.action_search_log.triggered.connect(self._toggle_search_bar)
        self.addAction(self.action_search_log)

        self.action_quit = QAction(QIcon.fromTheme("application-exit"), "&Quit", self)
        self.action_quit.setShortcut(QKeySequence.StandardKey.Quit)
        self.action_quit.triggered.connect(self.quit_app)

    # ── About ─────────────────────────────────────────────────────────

    def _show_about(self, _checked=False):
        if not hasattr(self, '_about_dlg'):
            self._about_dlg = self._create_about_dialog()
        self._about_dlg.exec()

    def _create_about_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("About VPN Launcher")
        dlg.setFixedSize(460, 420)
        layout = QVBoxLayout(dlg)

        # Header: icon + name + version
        header = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(_app_icon().pixmap(64, 64))
        header.addWidget(icon_label)

        title_block = QVBoxLayout()
        name_label = QLabel("VPN Launcher")
        name_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title_block.addWidget(name_label)
        ver_label = QLabel(f"Version {__version__}")
        pal = dlg.palette()
        muted = pal.color(QPalette.ColorRole.PlaceholderText).name()
        ver_label.setStyleSheet(f"font-size: 10pt; color: {muted};")
        title_block.addWidget(ver_label)
        title_block.addStretch()
        header.addLayout(title_block)
        header.addStretch()
        layout.addLayout(header)

        desc = QLabel("Multi-version OpenVPN connection manager for Linux\nwith KDE Plasma system tray integration.")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Tabs
        tabs = QTabWidget()

        about_tab = QTextEdit()
        about_tab.setReadOnly(True)
        about_tab.setStyleSheet("font-size: 10pt;")
        about_tab.setHtml(
            "<p>Manage multiple VPN connections, each pinned to a specific "
            "OpenVPN version compiled from source. Credentials are "
            "optionally pulled from a KeePass database via keepassxc-cli.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Multi-version OpenVPN support</li>"
            "<li>PyQt6 GUI with system tray</li>"
            "<li>CLI companion (ovpn-connect)</li>"
            "<li>KeePass integration</li>"
            "<li>Profile management (add, edit, remove, import, export)</li>"
            "<li>Auto-reconnect with backoff</li>"
            "<li>Connection timeout detection</li>"
            "<li>Log search, copy, and persistent logging</li>"
            "<li>Public IP and DNS leak check</li>"
            "<li>Build script for OpenVPN compilation</li>"
            "</ul>"
        )
        tabs.addTab(about_tab, "About")

        author_tab = QTextBrowser()
        author_tab.setStyleSheet("font-size: 10pt;")
        author_tab.setHtml(
            "<p><b>Andreas Hennig</b><br>Author &amp; Maintainer</p>"
            '<p><a href="mailto:kahennig.work@gmail.com">kahennig.work@gmail.com</a></p>'
            '<p><a href="https://github.com/kahennig/vpn-launcher">github.com/kahennig/vpn-launcher</a></p>'
            "<p>© 2026</p>"
        )
        author_tab.setOpenExternalLinks(True)
        tabs.addTab(author_tab, "Author")

        license_tab = QTextEdit()
        license_tab.setReadOnly(True)
        license_tab.setStyleSheet("font-family: monospace; font-size: 9pt;")
        license_tab.setPlainText(
            "This program is free software: you can redistribute it and/or modify\n"
            "it under the terms of the GNU General Public License as published by\n"
            "the Free Software Foundation, either version 3 of the License, or\n"
            "(at your option) any later version.\n\n"
            "This program is distributed in the hope that it will be useful,\n"
            "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
            "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\n"
            "GNU General Public License for more details.\n\n"
            "You should have received a copy of the GNU General Public License\n"
            "along with this program. If not, see <https://www.gnu.org/licenses/>."
        )
        tabs.addTab(license_tab, "License")

        layout.addWidget(tabs)

        link = QLabel('<a href="https://github.com/kahennig/vpn-launcher">github.com/kahennig/vpn-launcher</a>')
        link.setOpenExternalLinks(True)
        layout.addWidget(link)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        return dlg

    def _show_settings(self):
        dlg = SettingsDialog(self, self._app_settings)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._app_settings = dlg.get_settings()
            save_settings(self._app_settings)
            self.reload_profiles()

    def _show_build_dialog(self, _checked=False):
        prefix = self._app_settings.get("openvpn_prefix", "/opt")
        dlg = BuildDialog(self, prefix=prefix)
        dlg.exec()
        self.reload_profiles()

    # ── Toolbar ──────────────────────────────────────────────────────

    def _setup_toolbar(self):
        toolbar = QToolBar("Main")
        toolbar.setObjectName("main_toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(22, 22))
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        toolbar.addAction(self.action_connect)
        toolbar.addAction(self.action_disconnect)
        toolbar.addSeparator()
        toolbar.addAction(self.action_add)
        toolbar.addAction(self.action_edit)
        toolbar.addAction(self.action_remove)
        toolbar.addSeparator()
        toolbar.addAction(self.action_import)
        toolbar.addAction(self.action_import_zip)
        toolbar.addAction(self.action_export)
        toolbar.addSeparator()
        toolbar.addAction(self.action_build)
        toolbar.addSeparator()
        toolbar.addAction(self.action_reload)
        toolbar.addAction(self.action_clear_log)
        toolbar.addAction(self.action_copy_log)
        spacer = QWidget()
        spacer.setSizePolicy(spacer.sizePolicy().horizontalPolicy().Expanding,
                             spacer.sizePolicy().verticalPolicy().Preferred)
        toolbar.addWidget(spacer)
        hamburger_menu = QMenu(self)
        hamburger_menu.addAction(self.action_connect)
        hamburger_menu.addAction(self.action_disconnect)
        hamburger_menu.addSeparator()
        hamburger_menu.addAction(self.action_add)
        hamburger_menu.addAction(self.action_edit)
        hamburger_menu.addAction(self.action_remove)
        hamburger_menu.addSeparator()
        hamburger_menu.addAction(self.action_import)
        hamburger_menu.addAction(self.action_import_zip)
        hamburger_menu.addAction(self.action_export)
        hamburger_menu.addSeparator()
        hamburger_menu.addAction(self.action_ping)
        hamburger_menu.addAction(self.action_dns_check)
        hamburger_menu.addAction(self.action_build)
        hamburger_menu.addAction(self.action_open_configs)
        hamburger_menu.addAction(self.action_open_logs)
        hamburger_menu.addSeparator()
        hamburger_menu.addAction(self.action_reload)
        hamburger_menu.addAction(self.action_clear_log)
        hamburger_menu.addAction(self.action_copy_log)
        hamburger_menu.addSeparator()
        self.action_autostart = QAction("Start at &Login", self)
        self.action_autostart.setCheckable(True)
        self.action_autostart.setChecked(AUTOSTART_DESKTOP.is_file())
        self.action_autostart.triggered.connect(self._toggle_autostart)
        hamburger_menu.addAction(self.action_autostart)
        hamburger_menu.addAction(self.action_settings)
        hamburger_menu.addSeparator()
        hamburger_menu.addAction(self.action_about)
        hamburger_menu.addAction(self.action_quit)
        hamburger_btn = QToolButton(self)
        hamburger_btn.setIcon(QIcon.fromTheme("application-menu", QIcon.fromTheme("open-menu-symbolic")))
        hamburger_btn.setMenu(hamburger_menu)
        hamburger_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        hamburger_btn.setToolTip("Menu")
        toolbar.addWidget(hamburger_btn)
        self.addToolBar(toolbar)

    # ── Central UI ───────────────────────────────────────────────────

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setObjectName("main_splitter")

        self.profile_filter = QLineEdit()
        self.profile_filter.setPlaceholderText("Filter profiles…")
        self.profile_filter.setClearButtonEnabled(True)
        self.profile_filter.textChanged.connect(self._filter_profiles)
        splitter.addWidget(self.profile_filter)

        self.profile_tree = QTreeWidget()
        self.profile_tree.setHeaderLabels(["Profile", "OpenVPN Version", "Config File", "Auth", "KeePass Entry", "Last Connected"])
        self.profile_tree.setRootIsDecorated(False)
        self.profile_tree.setAlternatingRowColors(True)
        self.profile_tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.profile_tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.profile_tree.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.profile_tree.model().rowsMoved.connect(self._on_profiles_reordered)
        self.profile_tree.header().setStretchLastSection(True)
        self.profile_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.profile_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.profile_tree.header().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.profile_tree.header().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.profile_tree.itemDoubleClicked.connect(lambda: self.on_connect())
        self.profile_tree.setAccessibleName("VPN Profiles")
        splitter.addWidget(self.profile_tree)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("font-family: monospace; font-size: 9pt;")
        self.log_output.setPlaceholderText("Connection log will appear here…")
        self.log_output.setAccessibleName("Connection Log")
        self.log_output.viewport().installEventFilter(self)
        splitter.addWidget(self.log_output)

        self._search_bar = QLineEdit()
        self._search_bar.setPlaceholderText("Search log… (Enter = next, Escape = close)")
        self._search_bar.setClearButtonEnabled(True)
        self._search_bar.returnPressed.connect(self._search_log_next)
        self._search_bar.hide()
        splitter.addWidget(self._search_bar)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 2)
        splitter.setStretchFactor(3, 0)

        if self.settings.contains("splitter_state"):
            splitter.restoreState(self.settings.value("splitter_state"))
        self.splitter = splitter

        layout.addWidget(splitter)

    def _on_profiles_reordered(self):
        reordered = []
        for i in range(self.profile_tree.topLevelItemCount()):
            item = self.profile_tree.topLevelItem(i)
            reordered.append(item.data(0, Qt.ItemDataRole.UserRole))
        self.profiles = reordered
        save_profiles(self.profiles)

    def _filter_profiles(self, text):
        text = text.lower()
        for i in range(self.profile_tree.topLevelItemCount()):
            item = self.profile_tree.topLevelItem(i)
            item.setHidden(text not in item.text(0).lower())

    def _toggle_search_bar(self):
        if self._search_bar.isVisible():
            self._search_bar.hide()
        else:
            self._search_bar.show()
            self._search_bar.setFocus()
            self._search_bar.selectAll()

    def _search_log_next(self):
        text = self._search_bar.text()
        if text:
            if not self.log_output.find(text):
                self.log_output.moveCursor(QTextCursor.MoveOperation.Start)
                self.log_output.find(text)

    def _toggle_autostart(self, checked):
        if checked:
            AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
            desktop = (
                "[Desktop Entry]\nType=Application\nName=VPN Launcher\n"
                "Exec=ovpn-app\nIcon=ovpn-launcher\nTerminal=false\n"
                "X-GNOME-Autostart-enabled=true\n"
            )
            AUTOSTART_DESKTOP.write_text(desktop)
        else:
            try:
                AUTOSTART_DESKTOP.unlink()
            except FileNotFoundError:
                pass

    def _open_folder(self, path):
        path.mkdir(parents=True, exist_ok=True)
        from PyQt6.QtGui import QDesktopServices
        from PyQt6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self._search_bar.isVisible():
            self._search_bar.hide()
            return
        super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        if obj is self.log_output.viewport() and event.type() == QEvent.Type.MouseButtonDblClick:
            cursor = self.log_output.cursorForPosition(event.pos())
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            line = cursor.selectedText().strip()
            if line:
                QApplication.clipboard().setText(line)
            return True
        return super().eventFilter(obj, event)

    # ── Log Helpers ──────────────────────────────────────────────────

    def _log_color(self, text):
        t = text.lower()
        if "error" in t or "fatal" in t:
            return "#e74c3c"
        if "warn" in t:
            return "#e67e22"
        if "initialization sequence completed" in t:
            return "#27ae60"
        if text.startswith("--") or text.startswith("---") or text.startswith("$"):
            return self.palette().color(QPalette.ColorRole.PlaceholderText).name()
        return None

    def _log_append(self, text):
        color = self._log_color(text)
        if color:
            self.log_output.append(f'<span style="color:{color}">{text}</span>')
        else:
            self.log_output.append(text)

    # ── Status Bar ───────────────────────────────────────────────────

    def _setup_statusbar(self):
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(16, 16)
        self.status_text = QLabel("Disconnected")
        self._ip_label = QLabel("IP: —")
        self._profile_count = QLabel()
        bar = QStatusBar()
        bar.addWidget(self.status_icon)
        bar.addWidget(self.status_text)
        bar.addPermanentWidget(self._profile_count)
        bar.addPermanentWidget(self._ip_label)
        self.setStatusBar(bar)
        self._fetch_public_ip()

    # ── System Tray ──────────────────────────────────────────────────

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(_app_icon(), self)
        self._rebuild_tray_menu()
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _rebuild_tray_menu(self):
        menu = QMenu()
        is_connected = self.state != self.STATE_DISCONNECTED
        for p in getattr(self, "profiles", []):
            label = f"{p['alias']}  (v{p['version']})"
            is_active = is_connected and p["alias"] == self.connected_alias
            if is_active:
                label = f"▶ {label}"
            action = QAction(label, self)
            action.setData(p)
            if is_active:
                action.setIcon(_app_icon())
            action.triggered.connect(lambda checked, a=action: self._tray_connect(a.data()))
            menu.addAction(action)
        if getattr(self, "profiles", []):
            menu.addSeparator()
        show_action = QAction(QIcon.fromTheme("window"), "Show / Hide", self)
        show_action.triggered.connect(self._toggle_window)
        menu.addAction(show_action)
        self.tray_disconnect_action = QAction(QIcon.fromTheme("network-disconnect"), "Disconnect", self)
        self.tray_disconnect_action.triggered.connect(self.on_disconnect)
        self.tray_disconnect_action.setEnabled(is_connected)
        menu.addAction(self.tray_disconnect_action)
        menu.addSeparator()
        menu.addAction(self.action_quit)
        self.tray.setContextMenu(menu)

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            try:
                self._toggle_window()
            except Exception:
                pass

    def _toggle_window(self):
        if self.isVisible() and not self.isMinimized():
            self.hide()
        else:
            self.show()
            self.setWindowState(self.windowState() & ~Qt.WindowType.WindowMinimized)
            self.raise_()
            self.activateWindow()

    def _tray_connect(self, profile):
        if not profile:
            return
        for i in range(self.profile_tree.topLevelItemCount()):
            item = self.profile_tree.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole)["alias"] == profile["alias"]:
                self.profile_tree.setCurrentItem(item)
                break
        self.on_connect()

    # ── Profile Management ────────────────────────────────────────────

    def on_add_profile(self):
        dlg = ProfileDialog(self, existing_aliases=[p["alias"] for p in self.profiles])
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.profiles.append(dlg.get_profile())
            save_profiles(self.profiles)
            self.reload_profiles()

    def on_import_ovpn(self):
        src, _ = QFileDialog.getOpenFileName(
            self, "Import OpenVPN Config", "",
            "OpenVPN Config (*.ovpn *.conf);;All Files (*)",
        )
        if not src:
            return
        src_path = Path(src)
        configs_dir = CONFIG_DIR / "configs"
        configs_dir.mkdir(parents=True, exist_ok=True)
        dest = configs_dir / src_path.name
        if dest.exists():
            ans = QMessageBox.question(
                self, "File Exists",
                f"{dest.name} already exists in configs.\nOverwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if ans != QMessageBox.StandardButton.Yes:
                return
        import shutil
        shutil.copy2(src, dest)
        alias = src_path.stem
        profile = {"alias": alias, "version": "system", "config": str(dest), "auth_mode": "none"}
        dlg = ProfileDialog(self, profile=profile, existing_aliases=[p["alias"] for p in self.profiles])
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.profiles.append(dlg.get_profile())
            save_profiles(self.profiles)
            self.reload_profiles()

    def on_import_zip(self):
        src, _ = QFileDialog.getOpenFileName(
            self, "Import Profile Zip", "",
            "Zip Archive (*.zip);;All Files (*)",
        )
        if not src:
            return
        try:
            with zipfile.ZipFile(src, "r") as zf:
                if "profile.conf" not in zf.namelist():
                    QMessageBox.warning(self, "Import", "No profile.conf found in zip.")
                    return
                conf_line = zf.read("profile.conf").decode().strip()
                parts = conf_line.split("|")
                if len(parts) < 3:
                    QMessageBox.warning(self, "Import", "Invalid profile.conf format.")
                    return
                alias, version, ovpn_name = parts[0], parts[1], parts[2]
                auth_mode = parts[3] if len(parts) >= 4 else "none"
                configs_dir = CONFIG_DIR / "configs"
                configs_dir.mkdir(parents=True, exist_ok=True)
                dest = configs_dir / ovpn_name
                if ovpn_name in zf.namelist():
                    if dest.exists():
                        ans = QMessageBox.question(
                            self, "File Exists",
                            f"{ovpn_name} already exists in configs.\nOverwrite?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        )
                        if ans != QMessageBox.StandardButton.Yes:
                            return
                    dest.write_bytes(zf.read(ovpn_name))
                profile = {"alias": alias, "version": version, "config": str(dest), "auth_mode": auth_mode}
                dlg = ProfileDialog(self, profile=profile, existing_aliases=[p["alias"] for p in self.profiles])
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    self.profiles.append(dlg.get_profile())
                    save_profiles(self.profiles)
                    self.reload_profiles()
        except zipfile.BadZipFile:
            QMessageBox.critical(self, "Import", "Invalid zip file.")

    def on_edit_profile(self):
        item = self.profile_tree.currentItem()
        if not item:
            return
        profile = item.data(0, Qt.ItemDataRole.UserRole)
        other_aliases = [p["alias"] for p in self.profiles if p["alias"] != profile["alias"]]
        dlg = ProfileDialog(self, profile=profile, existing_aliases=other_aliases)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            idx = next(i for i, p in enumerate(self.profiles) if p["alias"] == profile["alias"])
            self.profiles[idx] = dlg.get_profile()
            save_profiles(self.profiles)
            self.reload_profiles()

    def on_remove_profile(self):
        item = self.profile_tree.currentItem()
        if not item:
            return
        alias = item.data(0, Qt.ItemDataRole.UserRole)["alias"]
        ans = QMessageBox.question(
            self, "Remove Profile",
            f"Remove profile '{alias}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if ans == QMessageBox.StandardButton.Yes:
            self.profiles = [p for p in self.profiles if p["alias"] != alias]
            save_profiles(self.profiles)
            self.reload_profiles()

    def on_export_profile(self):
        item = self.profile_tree.currentItem()
        if not item:
            return
        profile = item.data(0, Qt.ItemDataRole.UserRole)
        dest, _ = QFileDialog.getSaveFileName(
            self, "Export Profile", f"{profile['alias']}.zip",
            "Zip Archive (*.zip)",
        )
        if not dest:
            return
        config_path = Path(profile["config"])
        parts = [profile["alias"], profile["version"], config_path.name]
        if profile.get("auth_mode", "none") != "none":
            parts.append(profile["auth_mode"])
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
            if config_path.is_file():
                zf.write(config_path, config_path.name)
            zf.writestr("profile.conf", "|".join(parts) + "\n")

    def on_ping_profile(self):
        item = self.profile_tree.currentItem()
        if not item:
            return
        profile = item.data(0, Qt.ItemDataRole.UserRole)
        config_path = Path(profile["config"])
        if not config_path.is_file():
            self._log_append(f"-- Config file not found: {config_path} --")
            return
        host = None
        for line in config_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("remote "):
                parts = line.split()
                if len(parts) >= 2:
                    host = parts[1]
                break
        if not host:
            self._log_append(f"-- No 'remote' directive found in {config_path.name} --")
            return
        self._log_append(f"-- Pinging {host}... --")
        proc = QProcess(self)
        proc.setProgram("ping")
        proc.setArguments(["-c", "1", "-W", "3", host])
        proc.finished.connect(lambda code, _s, p=proc, h=host: self._on_ping_finished(p, code, h))
        proc.start()

    def _on_ping_finished(self, proc, exit_code, host):
        output = proc.readAllStandardOutput().data().decode(errors="replace")
        if exit_code == 0:
            import re
            m = re.search(r"time[=<](\d+\.?\d*)", output)
            ms = m.group(1) if m else "?"
            self._log_append(f"-- Ping {host}: {ms}ms --")
        else:
            self._log_append(f"-- Ping {host}: unreachable --")
        proc.deleteLater()

    def on_dns_check(self):
        self._log_append("-- Checking DNS resolver... --")
        proc = QProcess(self)
        proc.setProgram("dig")
        proc.setArguments(["+short", "whoami.akamai.net", "@ns1-1.akamaitech.net"])
        proc.finished.connect(lambda code, _s, p=proc: self._on_dns_check_finished(p, code))
        proc.start()

    def _on_dns_check_finished(self, proc, exit_code):
        if exit_code == 0:
            ip = proc.readAllStandardOutput().data().decode().strip()
            self._log_append(f"-- DNS resolver: {ip or 'unknown'} --")
        else:
            self._log_append("-- DNS check failed (is 'dig' installed?) --")
        proc.deleteLater()

    # ── Profile Loading ──────────────────────────────────────────────

    def reload_profiles(self):
        self.profiles = load_profiles()
        log.info("Loaded %d profiles", len(self.profiles))
        self.profile_tree.clear()
        for p in self.profiles:
            kp_display = ""
            if p["auth_mode"] == "keepass":
                kp_display = p.get("keepass_entry", "") or f"({p['alias']})"
            item = QTreeWidgetItem([p["alias"], p["version"], Path(p["config"]).name, p["auth_mode"], kp_display, p.get("last_connected", "")])
            item.setToolTip(2, p["config"])
            item.setData(0, Qt.ItemDataRole.UserRole, p)
            # Validate binary and config
            warnings = []
            binary = openvpn_binary(p["version"], Path(self._app_settings.get("openvpn_prefix", "/opt")))
            if not binary.is_file():
                warnings.append(f"Binary not found: {binary}")
            if not Path(p["config"]).is_file():
                warnings.append(f"Config not found: {p['config']}")
            if warnings:
                item.setIcon(0, QIcon.fromTheme("dialog-warning"))
                item.setToolTip(0, "\n".join(warnings))
            else:
                item.setIcon(0, _app_icon())
            self.profile_tree.addTopLevelItem(item)
        if self.profiles:
            self.profile_tree.setCurrentItem(self.profile_tree.topLevelItem(0))
        self._rebuild_tray_menu()
        n = len(self.profiles)
        self._profile_count.setText(f"{n} profile{'s' if n != 1 else ''}")

    # ── KeePass ──────────────────────────────────────────────────

    def _get_keepass_creds(self, alias, keepass_entry=""):
        entry = keepass_entry or alias
        keepass_db = Path(self._app_settings.get("keepass_db", "~/Document/Keepass/keepass.kdbx")).expanduser()
        log.debug("KeePass lookup: entry='%s', db='%s', exists=%s", entry, keepass_db, keepass_db.exists())
        if not keepass_db.exists():
            log.warning("KeePass DB not found: %s", keepass_db)
            return None, None
        password, ok = QInputDialog.getText(
            self, "KeePass", f"Master password for '{entry}':",
            QLineEdit.EchoMode.Password,
        )
        if not ok or not password:
            return None, None
        try:
            r_user = subprocess.run(
                ["keepassxc-cli", "show", "-q", "-s", "-a", "Username", str(keepass_db), entry],
                input=password, capture_output=True, text=True, timeout=10,
            )
            r_pwd = subprocess.run(
                ["keepassxc-cli", "show", "-q", "-s", "-a", "Password", str(keepass_db), entry],
                input=password, capture_output=True, text=True, timeout=10,
            )
            user = r_user.stdout.strip()
            pwd = r_pwd.stdout.strip()
            if not user or not pwd:
                log.warning("KeePass lookup failed for '%s': user_rc=%d pwd_rc=%d stderr=%s",
                            entry, r_user.returncode, r_pwd.returncode,
                            (r_user.stderr or r_pwd.stderr).strip())
            else:
                log.debug("KeePass credentials obtained for '%s'", entry)
        except subprocess.TimeoutExpired:
            return None, None
        finally:
            password = None  # noqa: F841
        return (user, pwd) if user and pwd else (None, None)

    # ── Prompt Credentials ────────────────────────────────────────

    def _get_prompt_creds(self, alias):
        user, ok = QInputDialog.getText(
            self, "VPN Credentials", f"Username for '{alias}':",
        )
        if not ok or not user:
            return None, None
        pwd, ok = QInputDialog.getText(
            self, "VPN Credentials", f"Password for '{alias}':",
            QLineEdit.EchoMode.Password,
        )
        if not ok or not pwd:
            return None, None
        return user, pwd

    # ── Connect / Disconnect ─────────────────────────────────────────

    def on_connect(self):
        item = self.profile_tree.currentItem()
        if not item:
            return
        profile = item.data(0, Qt.ItemDataRole.UserRole)
        alias = profile["alias"]

        if self.state != self.STATE_DISCONNECTED:
            if alias == self.connected_alias:
                return
            ans = QMessageBox.question(
                self, "Switch Profile",
                f"Disconnect from '{self.connected_alias}' and connect to '{alias}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if ans != QMessageBox.StandardButton.Yes:
                return
            self.on_disconnect()

        version, config = profile["version"], profile["config"]

        binary = str(openvpn_binary(version, Path(self._app_settings.get("openvpn_prefix", "/opt"))))
        if not os.path.isfile(binary):
            QMessageBox.critical(self, "Error", f"OpenVPN {version} not found at:\n{binary}")
            return
        if not os.path.isfile(config):
            QMessageBox.critical(self, "Error", f"Config file not found:\n{config}")
            return

        ovpn_text = Path(config).read_text(errors="replace")
        missing = [d for d in ("remote", "dev") if not any(l.strip().startswith(d) for l in ovpn_text.splitlines())]
        if missing:
            ans = QMessageBox.warning(
                self, "Config Warning",
                f"Config file may be incomplete.\nMissing directives: {', '.join(missing)}\n\nConnect anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if ans != QMessageBox.StandardButton.Yes:
                return

        args = ["--config", config]
        auth_mode = profile["auth_mode"]

        user, pwd = None, None
        if auth_mode == "keepass":
            user, pwd = self._get_keepass_creds(alias, profile.get("keepass_entry", ""))
        elif auth_mode == "prompt":
            user, pwd = self._get_prompt_creds(alias)

        if auth_mode in ("keepass", "prompt") and not user:
            self._log_append("-- No credentials obtained, connection aborted --")
            return

        if user and pwd:
            self.auth_file = tempfile.NamedTemporaryFile(mode="w", prefix="ovpn-auth-", delete=False)
            self.auth_file.write(f"{user}\n{pwd}\n")
            self.auth_file.close()
            os.chmod(self.auth_file.name, 0o600)
            args += ["--auth-user-pass", self.auth_file.name]

        self.process = QProcess(self)
        self.process.setProgram("pkexec")
        self.process.setArguments([binary] + args)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._on_read_output)
        self.process.finished.connect(self._on_process_finished)
        self.log_output.clear()
        self._log_append(f"$ {binary} {' '.join(args)}")
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self._log_file = open(LOG_DIR / f"{alias}_{ts}.log", "w")
        self._log_file.write(f"$ {binary} {' '.join(args)}\n")
        self.process.start()

        log.info("Connecting to %s (version %s)", alias, version)
        self.connected_alias = alias
        self._last_profile = profile
        self._user_disconnected = False
        self._reconnect_attempt = 0
        self._update_state(self.STATE_CONNECTING)
        self.connect_timer.start(int(self._app_settings.get("connection_timeout", 30)) * 1000)

    def on_disconnect(self):
        if self.state == self.STATE_DISCONNECTED:
            return
        log.info("Disconnecting from %s", self.connected_alias)
        self._user_disconnected = True
        self._reconnect_attempt = 0
        self.reconnect_timer.stop()
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            pid = self.process.processId()
            if pid:
                subprocess.run(["pkexec", "kill", str(pid)], capture_output=True)
            self.process.kill()
            self.process.waitForFinished(3000)
        self._cleanup()

    def _on_connection_timeout(self):
        if self.state != self.STATE_CONNECTING:
            return
        log.warning("Connection timeout for %s", self.connected_alias)
        ans = QMessageBox.warning(
            self, "Connection Timeout",
            f"Connection to '{self.connected_alias}' is taking longer than expected.\n\nDisconnect?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if ans == QMessageBox.StandardButton.Yes:
            self.on_disconnect()

    def _on_read_output(self):
        data = self.process.readAllStandardOutput().data().decode(errors="replace")
        for line in data.splitlines(keepends=True):
            stripped = line.rstrip()
            color = self._log_color(stripped)
            self.log_output.moveCursor(QTextCursor.MoveOperation.End)
            if color:
                self.log_output.insertHtml(f'<span style="color:{color}">{stripped}</span><br>')
            else:
                self.log_output.insertPlainText(line)
            self.log_output.moveCursor(QTextCursor.MoveOperation.End)
        if self._log_file:
            self._log_file.write(data)
            self._log_file.flush()
        if "Initialization Sequence Completed" in data:
            self.connect_timer.stop()
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            for i, p in enumerate(self.profiles):
                if p["alias"] == self.connected_alias:
                    p["last_connected"] = ts
                    item = self.profile_tree.topLevelItem(i)
                    if item:
                        item.setText(5, ts)
                        item.setData(0, Qt.ItemDataRole.UserRole, p)
                    break
            save_profiles(self.profiles)
            self._update_state(self.STATE_CONNECTED)

    def _on_process_finished(self, exit_code, _exit_status):
        self._log_append(f"\n--- Process exited (code {exit_code}) ---")
        should_reconnect = (
            not self._user_disconnected
            and exit_code != 0
            and self._last_profile is not None
        )
        self._cleanup()
        if should_reconnect:
            self._reconnect_attempt += 1
            if self._reconnect_attempt > self._reconnect_max:
                self._log_append(f"-- Auto-reconnect gave up after {self._reconnect_max} attempts --")
                return
            idx = min(self._reconnect_attempt - 1, len(self._reconnect_delays) - 1)
            delay = self._reconnect_delays[idx]
            self._log_append(f"-- Reconnecting in {delay}s (attempt {self._reconnect_attempt}/{self._reconnect_max})... --")
            self.reconnect_timer.start(delay * 1000)

    def _on_reconnect(self):
        if self.state != self.STATE_DISCONNECTED or not self._last_profile:
            return
        alias = self._last_profile["alias"]
        for i in range(self.profile_tree.topLevelItemCount()):
            item = self.profile_tree.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole)["alias"] == alias:
                self.profile_tree.setCurrentItem(item)
                break
        self._log_append(f"-- Auto-reconnecting to {alias}... --")
        self.on_connect()

    def _cleanup(self):
        self.connect_timer.stop()
        if self._log_file:
            try:
                self._log_file.close()
            except OSError:
                pass
            self._log_file = None
        if self.auth_file:
            try:
                os.unlink(self.auth_file.name)
            except OSError:
                pass
            self.auth_file = None
        self.connected_alias = None
        self._update_state(self.STATE_DISCONNECTED)

    # ── State Management ─────────────────────────────────────────────

    def _update_state(self, state):
        prev_state = self.state
        self.state = state
        pal = self.palette()

        if state == self.STATE_DISCONNECTED:
            label = "Disconnected"
            color = pal.color(QPalette.ColorRole.PlaceholderText)
            tray_icon = "network-vpn-disconnected"
            tray_tip = "VPN Launcher — Disconnected"
            self._elapsed_timer.stop()
        elif state == self.STATE_CONNECTING:
            label = f"Connecting: {self.connected_alias}…"
            color = pal.color(QPalette.ColorRole.Link)
            tray_icon = "network-vpn-acquiring"
            tray_tip = f"VPN Launcher — Connecting: {self.connected_alias}"
        else:
            label = f"Connected: {self.connected_alias}"
            color = pal.color(QPalette.ColorRole.Link)
            tray_icon = "network-vpn"
            tray_tip = f"VPN Launcher — Connected: {self.connected_alias}"
            self._elapsed_seconds = 0
            self._elapsed_timer.start(1000)

        self.status_text.setText(label)
        self.status_text.setStyleSheet(f"color: {color.name()};")

        icon = QIcon.fromTheme(tray_icon, _app_icon())
        self.status_icon.setPixmap(icon.pixmap(16, 16))

        self.tray.setIcon(icon)
        self.tray.setToolTip(tray_tip)

        if state == self.STATE_CONNECTED:
            self._fetch_public_ip(notify=True)
        elif state == self.STATE_DISCONNECTED and prev_state != self.STATE_DISCONNECTED:
            self.tray.showMessage(
                "VPN Disconnected", "VPN connection closed.",
                QSystemTrayIcon.MessageIcon.Information, 3000,
            )
            self._fetch_public_ip()

        connected = state != self.STATE_DISCONNECTED
        self.action_connect.setEnabled(not connected)
        self.action_disconnect.setEnabled(connected)
        self.profile_tree.setEnabled(not connected)
        self.action_add.setEnabled(not connected)
        self.action_import.setEnabled(not connected)
        self.action_import_zip.setEnabled(not connected)
        self.action_edit.setEnabled(not connected)
        self.action_remove.setEnabled(not connected)
        self.action_export.setEnabled(not connected)

        QTimer.singleShot(0, self._rebuild_tray_menu)

        # Highlight active profile in tree
        for i in range(self.profile_tree.topLevelItemCount()):
            item = self.profile_tree.topLevelItem(i)
            alias = item.data(0, Qt.ItemDataRole.UserRole)["alias"]
            is_active = connected and alias == self.connected_alias
            font = item.font(0)
            font.setBold(is_active)
            for col in range(item.columnCount()):
                item.setFont(col, font)
            if is_active and state == self.STATE_CONNECTING:
                item.setIcon(0, QIcon.fromTheme("network-vpn-acquiring"))
            else:
                item.setIcon(0, _app_icon())

    # ── Window Lifecycle ─────────────────────────────────────────────

    def _update_elapsed(self):
        self._elapsed_seconds += 1
        h, rem = divmod(self._elapsed_seconds, 3600)
        m, s = divmod(rem, 60)
        self.status_text.setText(f"Connected: {self.connected_alias} — {h:02d}:{m:02d}:{s:02d}")

    def _fetch_public_ip(self, notify=False):
        proc = QProcess(self)
        proc.setProgram("curl")
        ip_service = self._app_settings.get("ip_service", "https://api.ipify.org")
        proc.setArguments(["-s", "--max-time", "5", ip_service])
        proc.finished.connect(lambda code, _status, p=proc, n=notify: self._on_ip_fetched(p, code, n))
        proc.start()

    def _on_ip_fetched(self, proc, exit_code, notify=False):
        if exit_code == 0:
            ip = proc.readAllStandardOutput().data().decode().strip()
            self._ip_label.setText(f"IP: {ip}" if ip else "IP: —")
        else:
            ip = ""
            self._ip_label.setText("IP: —")
        if notify and self.state == self.STATE_CONNECTED:
            msg = f"Connected to {self.connected_alias}"
            if ip:
                msg += f" — IP: {ip}"
            self.tray.showMessage("VPN Connected", msg, QSystemTrayIcon.MessageIcon.Information, 3000)
        proc.deleteLater()

    def _restore_geometry(self):
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.contains("window_state"):
            self.restoreState(self.settings.value("window_state"))

    def _save_geometry(self):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())
        self.settings.setValue("splitter_state", self.splitter.saveState())

    def closeEvent(self, event):
        event.ignore()
        self._save_geometry()
        self.hide()
        self.tray.showMessage(
            "VPN Launcher", "Still running in the system tray.",
            QSystemTrayIcon.MessageIcon.Information, 2000,
        )

    def quit_app(self):
        self._save_geometry()
        self._user_disconnected = True
        self.reconnect_timer.stop()
        self.on_disconnect()
        self.tray.hide()
        QApplication.quit()


def _app_icon():
    custom = Path(__file__).parent.parent.parent / "share" / "icons" / "ovpn-launcher.svg"
    if custom.is_file():
        return QIcon(str(custom))
    installed = Path("/usr/local/share/icons/ovpn-launcher.svg")
    if installed.is_file():
        return QIcon(str(installed))
    return QIcon.fromTheme("ovpn-launcher", QIcon.fromTheme("network-vpn"))


def main():
    def _excepthook(exc_type, exc_value, exc_tb):
        log.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_tb))
    sys.excepthook = _excepthook

    logging.basicConfig(
        level=getattr(logging, os.environ.get("OVPN_LOG_LEVEL", "").upper() or load_settings().get("log_level", "WARNING"), logging.WARNING),
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    app = QApplication(sys.argv)
    app.setApplicationName("VPN Launcher")
    app.setOrganizationName("ovpn-launcher")
    app.setDesktopFileName("ovpn-launcher")
    app.setWindowIcon(_app_icon())
    app.setQuitOnLastWindowClosed(False)

    icon_pixmap = _app_icon().pixmap(96, 96)
    splash_w, splash_h = 320, 200
    pixmap = QPixmap(splash_w, splash_h)
    pixmap.fill(QColor("#1a2332"))
    painter = QPainter(pixmap)
    painter.drawPixmap((splash_w - 96) // 2, 20, icon_pixmap)
    painter.setPen(QColor("white"))
    font = painter.font()
    font.setPointSize(16)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(0, 130, splash_w, 30, Qt.AlignmentFlag.AlignCenter, "VPN Launcher")
    font.setPointSize(10)
    font.setBold(False)
    painter.setFont(font)
    painter.setPen(QColor("#7f8c8d"))
    painter.drawText(0, 158, splash_w, 20, Qt.AlignmentFlag.AlignCenter, f"v{__version__}")
    painter.end()
    splash = QSplashScreen(pixmap)
    splash.show()
    splash.showMessage("Loading…", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, QColor("#7f8c8d"))
    app.processEvents()

    window = VPNLauncher()
    splash.finish(window)

    def handle_signal(*_):
        window.quit_app()
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(200)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
