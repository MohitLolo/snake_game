# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

# 获取项目根目录
base_dir = os.path.abspath('.')

a = Analysis(
    ['main.py'],
    pathex=[base_dir],
    binaries=[],
    datas=[
        ('assets', 'assets'),  # 包含资源文件
        ('config.yaml', '.'),  # 包含配置文件
        ('src', 'src'),        # 包含源代码
    ],
    hiddenimports=[
        'pygame',
        'yaml',
        'src.entities',
        'src.core',
        'src.renderers',
        'src.managers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SnakeGame',  # 使用英文名减少误报
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 禁用 UPX 压缩，减少误报
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
    version='version.txt',  # 添加版本信息
)
