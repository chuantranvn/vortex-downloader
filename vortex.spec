# -*- mode: python ; coding: utf-8 -*-
import os
import glob
import imageio_ffmpeg

block_cipher = None

BASE_DIR = os.path.abspath(os.getcwd())
FFMPEG_DIR = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())

added_datas = [
    (os.path.join(BASE_DIR, 'client', 'desktop_gui', 'assets'), os.path.join('client', 'desktop_gui', 'assets')),
    (FFMPEG_DIR, os.path.join('imageio_ffmpeg', 'binaries')),
    (os.path.join(BASE_DIR, 'extension'), 'extension'),
]

# Thu thập toàn bộ file nhị phân C/Rust Extension (.pyd) trong môi trường ảo (.venv) hoặc môi trường Python hiện tại
extra_binaries = []
seen_pyds = set()
candidate_sp_dirs = [os.path.join(BASE_DIR, '.venv', 'Lib', 'site-packages')]
try:
    import site
    for sp in site.getsitepackages():
        if os.path.exists(sp) and sp not in candidate_sp_dirs:
            candidate_sp_dirs.append(sp)
except Exception:
    pass

for sp_dir in candidate_sp_dirs:
    if os.path.exists(sp_dir):
        for p in glob.glob(os.path.join(sp_dir, '**', '*.pyd'), recursive=True):
            fname = os.path.basename(p)
            if fname not in seen_pyds:
                seen_pyds.add(fname)
                rel_dir = os.path.dirname(os.path.relpath(p, sp_dir))
                extra_binaries.append((p, rel_dir))

hidden_imports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.asyncio',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
    'fastapi',
    'starlette',
    'starlette.routing',
    'starlette.middleware',
    'starlette.middleware.cors',
    'starlette.responses',
    'aiohttp',
    'httpx',
    'yt_dlp',
    'psutil',
    'websockets',
    'pydantic',
    'pydantic_core',
    'imageio_ffmpeg',
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'services.core_engine.main',
    'services.core_engine.engine',
    'services.media_extractor.main',
    'services.media_extractor.extractor',
    'services.gateway.main',
    'common.database',
    'common.schemas',
    'common.utils',
]

a = Analysis(
    ['run_app.py'],
    pathex=[BASE_DIR],
    binaries=extra_binaries,
    datas=added_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'numpy'],
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
    name='VortexDownloader',
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
    icon=os.path.join(BASE_DIR, 'client', 'desktop_gui', 'assets', 'vortex_icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VortexDownloader',
)
