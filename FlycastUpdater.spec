# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# ==========================================
# 1. COLOQUE O BLOCO DA VERSÃO AQUI
# ==========================================
vs_version_info = VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(4, 0, 0, 0), 
    prodvers=(4, 0, 0, 0), 
    mask=0x3f, 
    flags=0x0, 
    OS=0x40004, 
    fileType=0x1, 
    subtype=0x0, 
    date=(0, 0) 
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0', 
        [StringStruct('CompanyName', 'DaniboySan'), 
         StringStruct('FileDescription', 'Flycast Updater - Launcher'), 
         StringStruct('FileVersion', '4.0.0.0'), 
         StringStruct('InternalName', 'FlycastUpdater'), 
         StringStruct('LegalCopyright', 'Copyright (C) 2026 DaniboySan'), 
         StringStruct('OriginalFilename', 'FlycastUpdater.exe'), 
         StringStruct('ProductName', 'Flycast Updater'), 
         StringProductVersion('ProductVersion', '4.0.0.0')])
      ]
    ), 
    VarFileInfo([VarStruct('Translation', [1033, 1204])])
  ]
)


a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='FlycastUpdater',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=vs_version_info,  # <--- 2. ADICIONE ESTA LINHA AQUI NO FINAL DO EXE
)