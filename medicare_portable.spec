# -*- mode: python ; coding: utf-8 -*-
# medicare_portable.spec — PyInstaller ONEFILE spec for MEDICARE_PORTABLE.exe
# Output: dist\MEDICARE_PORTABLE.exe  (single self-extracting file)
#
# Build command (run from MEDICARE_OFFLINE directory):
#   $env:KIVY_HOME = "$PWD\.kivy_home"
#   $env:KIVY_NO_CONSOLELOG = "1"
#   python -m PyInstaller --clean --noconfirm medicare_portable.spec

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

project_dir = Path.cwd()

# ── Bundled read-only data (extracted to sys._MEIPASS at runtime) ──────────
datas = [
    (str(project_dir / 'data'),   'data'),
    (str(project_dir / 'native'), 'native'),
    (str(project_dir / 'assets'), 'assets'),
]
datas += collect_data_files('pypdfium2')
# Kivy's own hook collects its data; collect_data_files adds any extras.
datas += collect_data_files('kivy', includes=['**/*.kv', '**/*.png', '**/*.ttf', '**/*.atlas'])

# ── Hidden imports ─────────────────────────────────────────────────────────
hiddenimports = [
    # Kivy core
    'kivy', 'kivy.core.window', 'kivy.core.text', 'kivy.core.image',
    'kivy.core.audio', 'kivy.core.clipboard',
    'kivy.uix.screenmanager', 'kivy.uix.boxlayout', 'kivy.uix.gridlayout',
    'kivy.uix.scrollview', 'kivy.uix.slider', 'kivy.uix.textinput',
    'kivy.uix.popup', 'kivy.uix.widget', 'kivy.uix.image',
    'kivy.uix.label', 'kivy.uix.button', 'kivy.uix.togglebutton',
    'kivy.uix.floatlayout', 'kivy.uix.relativelayout',
    'kivy.uix.anchorlayout', 'kivy.uix.stacklayout',
    'kivy.graphics', 'kivy.graphics.texture', 'kivy.graphics.context_instructions',
    'kivy.graphics.vertex_instructions', 'kivy.graphics.transformation',
    'kivy.app', 'kivy.clock', 'kivy.properties',
    'kivy.lang', 'kivy.lang.builder',
    'kivy.uix.behaviors', 'kivy.uix.behaviors.button',
    # Standard library
    'sqlite3', 'json', 'csv', 'pathlib', 'os', 'sys', 'io',
    'urllib.request', 'urllib.parse', 'webbrowser',
    'ctypes', 'ctypes.util', 'tempfile', 'logging', 'logging.handlers',
    'datetime', 'traceback',
    # PDF / imaging
    'pypdfium2', 'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont',
    # Reporting
    'reportlab', 'reportlab.lib', 'reportlab.lib.colors',
    'reportlab.lib.styles', 'reportlab.lib.pagesizes', 'reportlab.lib.units',
    'reportlab.platypus', 'reportlab.platypus.paragraph',
    'reportlab.platypus.tables', 'reportlab.platypus.flowables',
    'reportlab.pdfgen', 'reportlab.pdfgen.canvas',
    # Crypto
    'cryptography', 'cryptography.fernet', 'cryptography.hazmat',
    'cryptography.hazmat.primitives', 'cryptography.hazmat.backends',
    'cryptography.hazmat.primitives.hashes',
    'cryptography.hazmat.primitives.kdf.pbkdf2',
    # App modules — core
    'app', 'app.main',
    'app.core.config', 'app.core.database', 'app.core.app_controller',
    'app.core.logger', 'app.core.native_loader',
    # App modules — data
    'app.datasets.dataset_loader',
    # App modules — services
    'app.patients.patient_service',
    'app.history.history_service',
    'app.history.handover_document_service',
    'app.security.encryption',
    'app.security.india_validation',
    'app.healthcare.location_service',
    'app.healthcare.maps_service',
    'app.healthcare.native_map_loader',
    'app.healthcare.offline_map_service',
    'app.synchronization.sync_service',
    # App modules — triage
    'app.triage.question_engine', 'app.triage.engine',
    'app.triage.result', 'app.triage.explainer',
    # App modules — reports
    'app.reports.handover_pdf',
    # App modules — UI
    'app.ui.theme', 'app.ui.components',
    'app.ui.screens', 'app.ui.app',
]

a = Analysis(
    ['main.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['rthook_medicare.py'],
    excludes=[
        'PySide6', 'PyQt5', 'PyQt6', 'tkinter', 'wx',
        'matplotlib', 'pandas', 'numpy', 'scipy',
        'jupyter', 'notebook', 'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,       # <-- binaries embedded (onefile)
    a.zipfiles,
    a.datas,          # <-- datas embedded (onefile)
    [],
    exclude_binaries=False,   # Must be False for onefile
    name='MEDICARE_PORTABLE',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    runtime_tmpdir=None,
    icon=None,
)
# NOTE: No COLLECT block — onefile builds embed everything in the EXE.
