# -*- mode: python ; coding: utf-8 -*-
# One-folder build (used for the Windows installer/zip and the Debian package).
# Build with `poetry run installer ...` or directly with `pyinstaller --clean --noconfirm islandr.spec`.

import os
import sys

import webview

IS_WINDOWS = sys.platform == "win32"

# Automatically find the path to the pywebview library (contains the WebView2 loader on Windows)
webview_lib_path = os.path.join(os.path.dirname(webview.__file__), "lib")

datas = [
    (os.path.join("rss_islandr", "templates", "report_template.xlsx"), "templates"),
    (os.path.join("rss_islandr", "data"), "data"),
    (os.path.join("rss_islandr", "static"), "static"),
    (os.path.join("rss_islandr", "maps"), "maps"),
]
if os.path.isdir(webview_lib_path):
    datas.append((webview_lib_path, os.path.join("webview", "lib")))

hiddenimports = ["bottle", "PIL._tkinter_finder"]  # The latter is needed by ImageTk (ttkbootstrap)
if IS_WINDOWS:
    hiddenimports += ["clr", "webview.platforms.winforms", "webview.platforms.edgechromium"]
else:
    hiddenimports += ["qtpy", "webview.platforms.qt"]

a = Analysis(
    ["main.py"],
    pathex=[".", os.path.join("rss_islandr", "ui")],  # The ui modules import each other without a package prefix
    hiddenimports=hiddenimports,
    datas=datas,
    binaries=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[os.path.join("build_installer", "pyi_rth_tcl_modules.py")],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="islandr",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join("rss_islandr", "static", "islandr.ico") if IS_WINDOWS else None,
    version="version_info.txt" if IS_WINDOWS else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="islandr",
)
