@echo off
REM 启动贪吃蛇游戏

REM 设置当前目录为脚本所在目录
cd /d %~dp0

REM 检查环境是否存在
if not exist "env\python.exe" (
    echo 未找到游戏环境，请先创建conda环境：
    echo conda create --prefix ./env python=3.9 -y
    echo 然后安装依赖：
    echo conda activate ./env
    echo pip install pygame
    pause
    exit /b
)

REM 直接使用环境中的Python运行游戏，避免conda激活问题
echo 启动贪吃蛇游戏...
env\python.exe main.py

REM 如果游戏退出，显示错误信息
if %errorlevel% neq 0 (
    echo 游戏运行出错，错误代码: %errorlevel%
    pause
)