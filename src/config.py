"""
游戏配置常量模块
集中管理所有游戏参数，便于调整和扩展
"""

# ========== 窗口配置 ==========
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 620
CELL_SIZE = 20
CELL_NUMBER_X = WINDOW_WIDTH // CELL_SIZE       # 40
CELL_NUMBER_Y = (WINDOW_HEIGHT - 60) // CELL_SIZE  # 28 (留出底部状态栏)
FPS = 60

# ========== 游戏速度配置 ==========
SPEED_MAP = {
    0: 100,   # 新手: 100ms (鼠标跟随模式)
    1: 200,   # 简单: 200ms
    2: 140,   # 普通: 140ms
    3: 110    # 困难: 110ms (比之前慢一点)
}

# ========== 闪光弹配置（普通和困难模式） ==========
FLASHBANG_CONFIG = {
    'interval': 480,        # 生成间隔 (帧数, 60fps * 10秒)
    'duration': 60,        # 白屏持续时间 (帧数, 60fps * 3秒)
}

# ========== 新手模式配置 ==========
BEGINNER_CONFIG = {
    'snake_speed': 3,      # 蛇跟随鼠标的速度（像素/帧）
    'min_distance': 10,    # 蛇头到鼠标的最小距离（开始移动）
    'boost_speed': 8,      # 加速时的速度
    'boost_duration': 30,  # 加速持续时间（帧数，约0.5秒）
    'double_click_time': 300,  # 双击间隔（毫秒）
}

# ========== 黄蛇配置（新手模式） ==========
YELLOW_SNAKE_CONFIG = {
    'interval': 400,        # 生成间隔 (帧数, 60fps * 6.7秒)
    'min_length': 4,        # 最小长度
    'max_length': 10,       # 最大长度
    'speed': 150,           # 黄蛇移动速度 (ms)
}

# ========== 炸弹配置 ==========
BOMB_CONFIG = {
    'lifetime': 180,        # 炸弹存在时间 (帧数, 60fps * 3秒)
    'interval': 180,        # 生成间隔 (帧数, 60fps * 3秒)
    'explosion_radius': 1,  # 爆炸范围 (格数)
    'explosion_duration': 20  # 爆炸动画持续时间 (帧数)
}

# ========== 红蛇配置 ==========
RED_SNAKE_CONFIG = {
    'interval': 300,        # 生成间隔 (帧数, 60fps * 5秒)
    'min_length': 3,        # 最小长度
    'max_length': 8,        # 最大长度
    'speed': 120,           # 红蛇移动速度 (ms)
}

# ========== 颜色配置 ==========
COLORS = {
    # 基础
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    
    # 背景
    'BG': (15, 20, 30),         # 深蓝黑背景
    'GRID': (25, 32, 44),       # 网格线
    'PANEL': (20, 26, 38),      # 状态栏背景
    'BORDER': (60, 80, 120),    # 边框
    
    # 蛇
    'SNAKE_HEAD': (50, 220, 80),
    'SNAKE_BODY': (30, 160, 60),
    'SNAKE_DARK': (10, 90, 30),
    'SNAKE_EYE': (255, 255, 255),
    'SNAKE_PUPIL': (0, 0, 0),
    
    # 食物
    'FOOD': (255, 60, 80),
    'FOOD_SHINE': (255, 160, 170),
    'FOOD_STEM': (120, 60, 20),
    
    # 炸弹
    'BOMB': (100, 60, 70),
    'BOMB_FUSE': (255, 80, 40),
    'BOMB_SPARK': (255, 200, 50),
    
    # 红蛇
    'RED_SNAKE_HEAD': (220, 50, 50),
    'RED_SNAKE_BODY': (180, 40, 40),
    
    # 黄蛇（新手模式）
    'YELLOW_SNAKE_HEAD': (255, 200, 50),
    'YELLOW_SNAKE_BODY': (220, 180, 40),
    
    # 经验球
    'EXP_BALL': (255, 215, 0),
    'EXP_BALL_GLOW': (255, 255, 150),
    
    # UI
    'TITLE': (80, 200, 130),
    'TEXT': (200, 210, 230),
    'DIM': (100, 115, 140),
    'ACCENT': (80, 180, 255),
    'WARN': (255, 120, 60),
}

# ========== 音频配置 ==========
AUDIO_CONFIG = {
    'bg_volume': 0.5,
    'eat_volume': 0.6,
    'game_over_volume': 0.7,
    'eat_max_duration': 500,  # 毫秒
}

# ========== 难度配置 ==========
DIFFICULTY_LABELS = {0: "新手", 1: "简单", 2: "普通", 3: "困难"}
DIFFICULTY_COLORS = {
    0: (100, 180, 255),  # 新手 - 浅蓝色
    1: (80, 200, 130),
    2: (255, 180, 50),
    3: (255, 80, 80)
}
