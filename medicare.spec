# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

project_dir = Path.cwd()

datas = [
    (str(project_dir / 'data'), 'data'),
    (str(project_dir / 'native'), 'native'),
    (str(project_dir / 'assets'), 'assets'),
]

hiddenimports = [
    'kivy',
    'kivy.core.window',
    'kivy.core.text',
    'kivy.uix.screenmanager',
    'kivy.uix.boxlayout',
    'kivy.uix.gridlayout',
    'kivy.uix.scrollview',
    'kivy.uix.slider',
    'kivy.uix.textinput',
    'kivy.uix.popup',
    'kivy.uix.widget',
    'kivy.graphics',
    'sqlite3',
    'reportlab',
    'reportlab.lib.colors',
    'reportlab.platypus',
    'reportlab.lib.styles',
    'cryptography',
    'cryptography.fernet',
    'urllib.request',
    'urllib.parse',
    'webbrowser',
    'app.healthcare.location_service',
    'app.healthcare.maps_service',
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6', 'PyQt5', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MEDICARE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MEDICARE',
)
