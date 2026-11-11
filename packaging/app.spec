# -*- mode: python ; coding: utf-8 -*-
# Build from the project root:  pyinstaller packaging/app.spec
# Result: dist/FogProject.exe (single file, no console window)
import os

ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))
ASSETS = os.path.join(ROOT, 'assets')

a = Analysis(
    [os.path.join(ROOT, 'gui', '__main__.py')],
    pathex=[ROOT],
    binaries=[],
    datas=[
        (os.path.join(ASSETS, 'logo.png'), 'assets'),
        (os.path.join(ASSETS, 'icon.png'), 'assets'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Qt modules the application does not use (smaller exe)
    excludes=['tkinter', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets',
              'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.Qt3DCore', 'PySide6.QtMultimedia',
              'PySide6.QtPdf', 'PySide6.QtCharts', 'PySide6.QtDataVisualization'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FogProject',
    icon=os.path.join(ASSETS, 'icon.ico'),
    version=os.path.join(SPECPATH, 'version_info.txt'),
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
)
