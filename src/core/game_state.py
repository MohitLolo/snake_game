"""
游戏状态管理
集中管理所有游戏状态变量
"""
from ..config import SPEED_MAP, BEGINNER_CONFIG


class GameState:
    """游戏状态管理器"""
    
    def __init__(self):
        # 游戏状态
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.paused = False
        self.difficulty = 1
        self.speed = SPEED_MAP[1]
        
        # 动画帧计数
        self.frame = 0
        
        # 鼠标位置（新手模式用）
        self.mouse_x = 0
        self.mouse_y = 0
        
        # 加速状态（新手模式）
        self.boost_timer = 0
        self.is_boosting = False
        
        # 闪光弹状态
        self.flashbang_timer = 0
        self.flashbang_active = False
        self.flashbang_frame = 0
        
        # 实体计时器
        self.bomb_timer = 0
        self.red_snake_timer = 0
        self.yellow_snake_timer = 0
    
    def reset(self, difficulty):
        """重置游戏状态"""
        self.score = 0
        self.game_over = False
        self.paused = False
        self.difficulty = difficulty
        self.speed = SPEED_MAP[difficulty]
        self.frame = 0
        
        # 重置加速状态
        self.boost_timer = 0
        self.is_boosting = False
        
        # 重置闪光弹状态
        self.flashbang_timer = 0
        self.flashbang_active = False
        self.flashbang_frame = 0
        
        # 重置实体计时器
        self.bomb_timer = 0
        self.red_snake_timer = 0
        self.yellow_snake_timer = 0
    
    def update_frame(self):
        """更新帧计数"""
        self.frame += 1
    
    def update_boost(self):
        """更新加速状态"""
        if self.is_boosting:
            self.boost_timer -= 1
            if self.boost_timer <= 0:
                self.is_boosting = False
    
    def trigger_boost(self):
        """触发加速"""
        if not self.game_over and not self.paused:
            self.is_boosting = True
            self.boost_timer = BEGINNER_CONFIG['boost_duration']
    
    def set_mouse_position(self, x, y):
        """设置鼠标位置"""
        self.mouse_x = x
        self.mouse_y = y
    
    def add_score(self, points=1):
        """增加分数"""
        self.score += points
        self.high_score = max(self.high_score, self.score)
    
    def trigger_game_over(self):
        """触发游戏结束"""
        self.game_over = True
    
    def toggle_pause(self):
        """切换暂停状态"""
        if not self.game_over:
            self.paused = not self.paused
    
    def set_difficulty(self, level):
        """设置难度"""
        if 0 <= level <= 3:
            self.difficulty = level
            self.speed = SPEED_MAP[level]
