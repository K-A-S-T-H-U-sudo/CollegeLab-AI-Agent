# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/KASTHURI/.gemini/antigravity-ide/scratch/collegelabs_ai_agent/main.py'],
    pathex=['C:/Users/KASTHURI/.gemini/antigravity-ide/scratch/collegelabs_ai_agent'],
    binaries=[],
    datas=[],
    hiddenimports=['psutil', 'sqlite3', 'tkinter', 'tkinter.ttk', 'ctypes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CollegeLabAI',
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
