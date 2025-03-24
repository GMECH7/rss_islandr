# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main\\main_ui.py'],
    pathex=['.'],  # Ensure project directory is included
    hiddenimports=[
        'pywebview',
        'bottle',
        'rss_islandr.core.config_parser',
        'rss_islandr.core.datatypes',
        'rss_islandr.ui.assessment_ui',
        'rss_islandr.ui.excel_writer_btn_ui',
        'rss_islandr.ui.map_ui',
        'rss_islandr.ui.site_info_ui',
    ],
    datas=[
    ('rss_islandr\\core\\settings.json', 'core'),
    ('rss_islandr\\data', 'data'),
    ('rss_islandr\\static', 'static')
    ],
    binaries=[],
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
    name='islandr',
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
    icon=['rss_islandr\\static\\islandr.ico'],
    version='version_info.txt',
)
