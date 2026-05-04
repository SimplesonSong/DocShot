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

datas = []
binaries = []
hiddenimports = []

# =========================
# 基础资源文件
# =========================
assets_dir = PROJECT_DIR / "assets"
if assets_dir.exists():
    datas.append((str(assets_dir), "assets"))

# =========================
# Python 3.13 imghdr 兼容
# =========================
# 如果你使用 Python 3.13，请先执行：
# python -m pip install standard-imghdr
hiddenimports += [
    "imghdr",
]

try:
    import imghdr

    imghdr_file = getattr(imghdr, "__file__", None)
    if imghdr_file and os.path.exists(imghdr_file):
        datas.append((imghdr_file, "."))
except Exception:
    pass

# =========================
# 需要完整收集的重型依赖
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
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(package)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hiddenimports
    except Exception as e:
        print(f"[WARN] collect_all failed for {package}: {e}")

# =========================
# 额外收集 Cython Utility
# 解决 _internal\Cython\Utility\CppSupport.cpp 缺失问题
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
# package metadata
# 解决 No package metadata was found for imageio
# =========================

metadata_packages = [
    "imageio",
    "imageio-ffmpeg",
    "paddleocr",
    "paddlepaddle",
    "paddlex",
]

for package in metadata_packages:
    try:
        datas += copy_metadata(package)
    except Exception as e:
        print(f"[WARN] copy_metadata failed for {package}: {e}")

# =========================
# Paddle / PaddleOCR 额外隐藏导入
# =========================
extra_hiddenimports = [
    "paddle",
    "paddle.base",
    "paddle.framework",
    "paddle.utils",
    "paddleocr",
    "paddleocr.paddleocr",
    "paddleocr.tools",
    "paddleocr.ppocr",
    "paddleocr.ppocr.data",
    "paddleocr.ppocr.modeling",
    "paddleocr.ppocr.postprocess",
    "paddleocr.ppocr.utils",
    "paddleocr.ppstructure",
    "paddleocr.ppstructure.table",
    "paddleocr.ppstructure.layout",
    "paddlex",
    "cv2",
    "PIL",
    "PIL.Image",
    "PIL.ImageFile",
    "numpy",
    "fitz",
    "docx",
    "pdf2docx",
    "lxml",
    "lxml.etree",
    "bs4",
    "apted",
    "premailer",
    "openpyxl",
    "imageio",
    "imageio.v2",
    "imageio_ffmpeg",
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
# 补充包元数据
# 解决 No package metadata was found for imageio 等问题
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
]

for package in metadata_packages:
    try:
        datas += copy_metadata(package)
    except Exception as e:
        print(f"[WARN] copy_metadata failed for {package}: {e}")

# =========================
# 去重
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DocShot",
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
    icon=(
        str(assets_dir / "icon.ico")
        if (assets_dir / "icon.ico").exists()
        else str(assets_dir / "icon.png")
        if (assets_dir / "icon.png").exists()
        else None
    ),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="DocShot",
)
