# 贪吃蛇游戏

基于 Python + Pygame 开发的贪吃蛇游戏，支持中文界面、难度选择、加速操控。

## 项目结构

```
snake_game/
├── env/              # Conda 虚拟环境（Python 3.9）
├── main.py           # 游戏主入口
├── snake.py          # 游戏核心逻辑（Point / Snake / Food / Game）
├── requirements.txt  # pip 依赖列表
├── environment.yml   # Conda 环境配置
├── start_game.bat    # Windows 一键启动脚本
└── README.md
```

## 环境要求

- Python 3.9
- Miniconda / Anaconda
- pygame 2.5+


## 运行方式

```bash
# 方式一：双击启动（Windows）
start_game.bat

# 方式二：命令行
env\python.exe main.py

# 方式三：激活环境后运行
conda activate ./env
python main.py
```

## 打包
```bash
# 标准打包（推荐）
python build.py

# 单文件版本（体积更大，但只有一个文件）
python build.py --onefile

# 清理构建文件
python build.py --clean
```


## 操作说明

| 场景 | 按键 | 功能 |
|------|------|------|
| 开始界面 | 空格 | 开始游戏 |
| 开始界面 | 1 / 2 / 3 | 切换难度（简单 / 普通 / 困难） |
| 游戏中 | WASD 或方向键 | 控制移动方向 |
| 游戏中 | 按住同方向键 | 加速前进（速度提升至 3 倍） |
| 游戏中 | 空格 | 暂停 / 继续 |
| 游戏中 | ESC | 返回开始界面 |
| 游戏结束 | 空格 | 重新开始 |

## 功能特点

- 深色 UI + 网格背景，蛇身渐变色 + 高光，食物脉动发光
- 三级难度（简单 200ms / 普通 140ms / 困难 90ms）
- 按住同方向键加速，松开恢复正常速度
- 最高分跨局保留
- 状态栏实时显示分数 / 最高分 / 当前难度
- 支持任意输入法状态下的 WASD 控制（通过禁用窗口 IME 实现）

## 常见问题

**import pygame 报红 / 运行报错 ModuleNotFoundError**
> IDE 解释器未指向项目 `env\python.exe`，在 PyCharm 中将解释器切换为 `D:\...\snake_game\env\python.exe` 即可。

**WASD 在中文输入法下无响应**
> 已通过 `ImmAssociateContext` 禁用游戏窗口的 IME 上下文解决，无需手动切换输入法。

## 许可证

MIT License
