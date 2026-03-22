"""
游戏配置模块
从 YAML 文件加载配置
"""
import os
import yaml

# 获取配置文件路径
_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(os.path.dirname(_current_dir), 'config.yaml')

# 加载 YAML 配置
with open(_config_path, 'r', encoding='utf-8') as f:
    _cfg = yaml.safe_load(f)

# ========== 窗口配置 ==========
WINDOW_WIDTH = _cfg['window']['width']
WINDOW_HEIGHT = _cfg['window']['height']
CELL_SIZE = _cfg['window']['cell_size']
FPS = _cfg['window']['fps']
CELL_NUMBER_X = WINDOW_WIDTH // CELL_SIZE
CELL_NUMBER_Y = (WINDOW_HEIGHT - 60) // CELL_SIZE

# ========== 游戏速度配置 ==========
SPEED_MAP = _cfg['speed_map']

# ========== 闪光弹配置 ==========
FLASHBANG_CONFIG = _cfg['flashbang']

# ========== 新手模式配置 ==========
BEGINNER_CONFIG = _cfg['beginner']

# ========== 黄蛇配置 ==========
YELLOW_SNAKE_CONFIG = _cfg['yellow_snake']

# ========== 炸弹配置 ==========
BOMB_CONFIG = _cfg['bomb']

# ========== 蓝色食物配置 ==========
BLUE_FOOD_CONFIG = _cfg['blue_food']

# ========== 红蛇配置 ==========
RED_SNAKE_CONFIG = _cfg['red_snake']

# ========== 颜色配置 ==========
COLORS = {k: tuple(v) for k, v in _cfg['colors'].items()}

# ========== 音频配置 ==========
AUDIO_CONFIG = _cfg['audio']

# ========== 难度配置 ==========
DIFFICULTY_LABELS = _cfg['difficulty']['labels']
DIFFICULTY_COLORS = {int(k): tuple(v) for k, v in _cfg['difficulty']['colors'].items()}
