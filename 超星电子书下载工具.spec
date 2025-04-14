# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['tkinter', 'tkinter.ttk']
hiddenimports += collect_submodules('requests')
hiddenimports += collect_submodules('pypdf')


a = Analysis(
    ['c:\\Users\\qq114\\Desktop\\cxstar-pdf-download\\main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PyQt5', 'PySide2', 'IPython', 'notebook', 'sphinx', 'pytest', 'PIL.ImageQt', 'PIL.ImageTk', 'PIL.ImageGrab', 'PIL.ImageDraw2', 'PIL.ImageCms', 'PIL.ImageMath', 'PIL.ImageGL', 'PIL.ImageColor', 'PIL.ImageFilter', 'PIL.ImageEnhance', 'PIL.ImageOps', 'PIL.ImageWin', 'PIL.ImagePath', 'PIL.ImageShow', 'PIL.ImageMorph', 'PIL.ImageChops', 'PIL.ImageTransform', 'PIL.ImageStat', 'PIL.ImageSequence'],
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
    name='超星电子书下载工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
