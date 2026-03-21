"""
打包脚本 - 使用 PyInstaller 打包游戏为可执行文件
"""
import os
import sys
import shutil
import subprocess


def clean_build():
    """清理构建目录"""
    dirs_to_remove = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name}...")
            shutil.rmtree(dir_name)
    
    # 清理 .pyc 文件
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
        for dir in dirs:
            if dir == '__pycache__':
                path = os.path.join(root, dir)
                if os.path.exists(path):
                    shutil.rmtree(path)


def build():
    """执行打包"""
    print("开始打包贪吃蛇游戏...")
    
    # 确保依赖已安装
    print("检查依赖...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # 执行 PyInstaller
    print("执行 PyInstaller...")
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        'build.spec',
        '--clean',
        '--noconfirm'
    ]
    subprocess.check_call(cmd)
    
    print("\n打包完成！")
    print("可执行文件位于: dist/贪吃蛇.exe")


def build_onefile():
    """打包为单文件版本"""
    print("开始打包单文件版本...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',
        '--name', '贪吃蛇',
        '--add-data', 'assets;assets',
        '--add-data', 'config.yaml;.',
        '--hidden-import', 'pygame',
        '--hidden-import', 'yaml',
        'main.py'
    ]
    
    subprocess.check_call(cmd)
    print("\n单文件版本打包完成！")
    print("可执行文件位于: dist/贪吃蛇.exe")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='打包贪吃蛇游戏')
    parser.add_argument('--clean', action='store_true', help='清理构建文件')
    parser.add_argument('--onefile', action='store_true', help='打包为单文件')
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build()
    elif args.onefile:
        build_onefile()
    else:
        build()
