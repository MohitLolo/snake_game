# 环境配置说明

## 环境要求

- Python 3.9
- Miniconda 或 Anaconda

## 创建环境步骤

1. 下载并安装 Miniconda (如果尚未安装)
   访问 https://docs.conda.io/en/latest/miniconda.html 下载适用于Windows的Miniconda

2. 打开命令提示符或PowerShell

3. 导航到项目目录
   ```bash
   cd snake_game
   ```

4. 创建conda环境
   ```bash
   conda create --prefix ./env python=3.9 -y
   ```

5. 激活环境
   ```bash
   conda activate ./env
   ```

6. 安装pygame依赖
   ```bash
   pip install pygame
   ```

## 验证环境

1. 检查Python版本
   ```bash
   python --version
   ```

2. 检查pygame是否正确安装
   ```bash
   python -c "import pygame; print('Pygame version:', pygame.version.ver)"
   ```

## 常见问题解决

### 1. Conda激活错误
如果遇到 `CondaError: Run 'conda init' before 'conda activate'` 错误：

解决方法：
- 直接使用环境中的Python运行游戏：`env\python.exe main.py`
- 或者先初始化conda：`conda init`，然后重新打开终端

### 2. ModuleNotFoundError: No module named 'pygame'
如果遇到模块导入错误：

解决方法：
1. 确保已在环境中安装pygame：
   ```bash
   conda activate ./env
   pip install pygame
   ```

2. 或者检查环境路径是否正确

### 3. 环境路径问题
如果环境路径包含空格或特殊字符，可能会导致问题。

解决方法：
- 将项目移动到不包含空格和特殊字符的路径下
- 或者使用引号包围路径

## 环境管理命令

- 查看所有环境：`conda env list`
- 删除环境：`conda env remove --prefix ./env`
- 导出环境配置：`conda env export > environment.yml`
- 从配置文件创建环境：`conda env create -f environment.yml`