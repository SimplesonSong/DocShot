# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_all,
    collect_data_files,
    collect_dynamic_libs,
    collect_submodules,
    copy_metadata,
)

block_cipher = None

PROJECT_DIR = Path(os.getcwd()).resolve()
ASSETS_DIR = PROJECT_DIR / "assets"
ICON_PATH = ASSETS_DIR / "icon.png"

if not ICON_PATH.exists():
    raise FileNotFoundError(f"找不到图标文件：{ICON_PATH}")

datas = []
binaries = []
hiddenimports = []

# =========================
# 项目资源文件
# =========================

if ASSETS_DIR.exists():
    datas.append((str(ASSETS_DIR), "assets"))

# =========================
# Python 3.13 imghdr 兼容
# 如果你使用 Python 3.13，需要先执行：
# python -m pip install standard-imghdr
# 但更推荐 Python 3.10 / 3.11
# =========================

hiddenimports += [
    "imghdr",
]

try:
    import imghdr

    imghdr_file = getattr(imghdr, "__file__", None)
    if imghdr_file and os.path.exists(imghdr_file):
        datas.append((imghdr_file, "."))
except Exception as e:
    print(f"[WARN] imghdr collect failed: {e}")

# =========================
# 需要完整收集的依赖包
# =========================

collect_packages = [
    "Cython",
    "paddle",
    "paddleocr",
    "paddlex",
    "cv2",
    "PIL",
    "numpy",
    "scipy",
    "skimage",
    "fitz",
    "docx",
    "pdf2docx",
    "lxml",
    "bs4",
    "openpyxl",
    "apted",
    "premailer",
    "imageio",
    "imageio_ffmpeg",
]

for package in collect_packages:
    try:
        package_datas, package_binaries, package_hiddenimports = collect_all(package)
        datas += package_datas
        binaries += package_binaries
        hiddenimports += package_hiddenimports
    except Exception as e:
        print(f"[WARN] collect_all failed for {package}: {e}")

# =========================
# Cython Utility
# 解决：
# _internal\\Cython\\Utility\\CppSupport.cpp 缺失
# =========================

try:
    import Cython

    cython_dir = Path(Cython.__file__).resolve().parent
    cython_utility_dir = cython_dir / "Utility"

    if cython_utility_dir.exists():
        datas.append((str(cython_utility_dir), "Cython/Utility"))
except Exception as e:
    print(f"[WARN] failed to collect Cython Utility: {e}")

try:
    datas += collect_data_files("Cython", include_py_files=True)
    hiddenimports += collect_submodules("Cython")
except Exception as e:
    print(f"[WARN] failed to collect Cython data/submodules: {e}")

# =========================
# 补充包元数据
# 解决：
# No package metadata was found for imageio
# No package metadata was found for xxx
# =========================

metadata_packages = [
    "imageio",
    "imageio-ffmpeg",
    "paddleocr",
    "paddlepaddle",
    "paddlex",
    "Pillow",
    "opencv-python",
    "numpy",
    "scipy",
    "scikit-image",
    "PyMuPDF",
    "pdf2docx",
    "python-docx",
    "lxml",
    "beautifulsoup4",
    "openpyxl",
    "apted",
    "premailer",
    "standard-imghdr",
]

for package in metadata_packages:
    try:
        datas += copy_metadata(package)
    except Exception as e:
        print(f"[WARN] copy_metadata failed for {package}: {e}")

# =========================
# Paddle / PaddleOCR 隐藏导入
# =========================

extra_hiddenimports = [
    "imghdr",
    "imageio",
    "imageio.v2",
    "imageio_ffmpeg",

    "paddle",
    "paddle.base",
    "paddle.framework",
    "paddle.utils",
    "paddle.nn",
    "paddle.nn.functional",
    "paddle.io",
    "paddle.static",
    "paddle.inference",

    "paddleocr",
    "paddleocr.paddleocr",
    "paddleocr.tools",
    "paddleocr.ppocr",
    "paddleocr.ppocr.data",
    "paddleocr.ppocr.modeling",
    "paddleocr.ppocr.postprocess",
    "paddleocr.ppocr.utils",
    "paddleocr.ppocr.utils.logging",
    "paddleocr.ppstructure",
    "paddleocr.ppstructure.table",
    "paddleocr.ppstructure.layout",
    "paddleocr.ppstructure.recovery",

    "paddlex",

    "cv2",
    "PIL",
    "PIL.Image",
    "PIL.ImageFile",
    "PIL.ImageQt",

    "numpy",
    "scipy",
    "skimage",

    "fitz",
    "docx",
    "pdf2docx",

    "lxml",
    "lxml.etree",
    "bs4",
    "openpyxl",
    "apted",
    "premailer",
]

hiddenimports += extra_hiddenimports

# =========================
# 动态库补充
# =========================

dynamic_lib_packages = [
    "paddle",
    "cv2",
    "numpy",
    "scipy",
]

for package in dynamic_lib_packages:
    try:
        binaries += collect_dynamic_libs(package)
    except Exception as e:
        print(f"[WARN] collect_dynamic_libs failed for {package}: {e}")

# =========================
# 去重函数
# =========================

def unique_list(items):
    seen = set()
    result = []
    for item in items:
        key = repr(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


datas = unique_list(datas)
binaries = unique_list(binaries)
hiddenimports = sorted(set(hiddenimports))

# =========================
# Analysis
# =========================

a = Analysis(
    ["main.py"],
    pathex=[str(PROJECT_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib.tests",
        "numpy.tests",
        "scipy.tests",
        "pandas.tests",
        "tkinter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

# =========================
# 单文件模式 EXE
# 注意：
# 1. 单文件模式不要使用 COLLECT
# 2. 不要使用 exclude_binaries=True
# 3. 必须把 a.binaries / a.zipfiles / a.datas 放进 EXE
# =========================

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="DocShot",
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
    icon=str(ICON_PATH),
)