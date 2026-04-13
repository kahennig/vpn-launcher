# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for ovpn-launcher Windows build."""

import os
import sys

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('share/icons/ovpn-launcher.svg', 'share/icons'),
        ('share/icons/breeze', 'share/icons/breeze'),
        ('share/icons/breeze-dark', 'share/icons/breeze-dark'),
    ],
    hiddenimports=['ovpn_launcher', 'ovpn_launcher.app', 'ovpn_launcher.cli',
                   'ovpn_launcher.builder', 'ovpn_launcher.paths', 'ovpn_launcher.profiles'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ovpn-launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='share/icons/ovpn-launcher.ico',
    uac_admin=True,
)
