"""
游戏核心逻辑模块 - 精简版
协调所有游戏组件
"""
import pygame
from .config import SPEED_MAP, BEGINNER_CONFIG, WINDOW_WIDTH, CELL_NUMBER_Y, CELL_SIZE
from .entities import Snake, Food
from .core import GameState, CollisionHandler, EntitySpawner
from .renderers import GameRenderer, UIRenderer, ScreenRenderer
from .managers import FontManager


class Game:
    """游戏主类 - 精简协调器"""
    
    # 属性代理到 state
    @property
    def speed(self):
        return self.state.speed
    
    @property
    def score(self):
        return self.state.score
    
    @property
    def high_score(self):
        return self.state.high_score
    
    @property
    def game_over(self):
        return self.state.game_over
    
    @property
    def paused(self):
        return self.state.paused
    
    @property
    def difficulty(self):
        return self.state.difficulty
    
    @property
    def _frame(self):
        """帧计数器（兼容旧代码）"""
        return self.state.frame
    
    @_frame.setter
    def _frame(self, value):
        self.state.frame = value
    
    def __init__(self):
        # 游戏实体
        self.snake = Snake(beginner_mode=False)
        self.food = Food()
        
        # 核心组件
        self.state = GameState()
        self.spawner = EntitySpawner(self.state)
        self.collision = CollisionHandler(self.state)
        
        # 渲染器
        self.fonts = FontManager()
        self.game_renderer = GameRenderer(self.fonts)
        self.ui_renderer = UIRenderer(self.fonts)
        self.screen_renderer = ScreenRenderer(self.fonts)
        
        # 音频管理器（外部注入）
        self.audio = None
        
        # 初始化
        self._init_level()
    
    def _init_level(self):
        """初始化关卡"""
        self.food.spawn(self.snake.body)
        self.fonts.load()
        self.state.set_mouse_position(WINDOW_WIDTH // 2, CELL_NUMBER_Y * CELL_SIZE // 2)
    
    # ========== 更新方法 ==========
    
    def update(self):
        """更新游戏状态"""
        if self.state.game_over or self.state.paused:
            return
        
        self.state.update_frame()
        self.state.update_boost()
        
        # 更新蛇位置
        if self.state.difficulty == 0:
            speed = BEGINNER_CONFIG['boost_speed'] if self.state.is_boosting else BEGINNER_CONFIG['snake_speed']
            self.snake.move_to_mouse(self.state.mouse_x, self.state.mouse_y, speed)
        else:
            self.snake.move()
        
        # 碰撞检测
        self.collision.check_all(
            self.snake, self.food, self.spawner.bomb,
            self.spawner.red_snake, self.spawner.yellow_snake, self.spawner.exp_balls,
            on_eat_food=self._on_eat_food,
            on_eat_exp=self._on_eat_exp,
            on_game_over=self._on_game_over
        )
        
        # 更新实体
        self.spawner.update(self.snake.body, self.food.pos, self.audio)
        
        # 更新动画
        self.food.update()
    
    def _on_eat_food(self):
        """吃到食物回调"""
        self.snake.grow()
        self.state.add_score(1)
        self.food.spawn(self.snake.body)
        if self.audio:
            self.audio.play_eat_sound()
    
    def _on_eat_exp(self, ball):
        """吃到经验球回调"""
        for _ in range(3):
            self.snake.grow()
        self.spawner.exp_balls.remove(ball)
        self.state.add_score(1)
        if self.audio:
            self.audio.play_eat_sound()
    
    def _on_game_over(self):
        """游戏结束回调"""
        self.state.trigger_game_over()
        if self.audio:
            self.audio.stop_bg_music()
            self.audio.play_game_over_sound()
    
    # ========== 控制方法 ==========
    
    def set_direction(self, direction):
        """设置蛇的方向"""
        if not self.state.game_over and not self.state.paused and self.state.difficulty != 0:
            self.snake.queue_direction(direction)
    
    def toggle_pause(self):
        """切换暂停状态"""
        was_paused = self.state.paused
        self.state.toggle_pause()
        if self.audio:
            if self.state.paused and not was_paused:
                self.audio.pause_bg_music()
            elif not self.state.paused and was_paused:
                self.audio.resume_bg_music()
    
    def set_difficulty(self, level):
        """设置难度"""
        self.state.set_difficulty(level)
        self.snake = Snake(beginner_mode=(level == 0))
        self.food.spawn(self.snake.body)
    
    def restart(self):
        """重新开始"""
        self.snake = Snake(beginner_mode=(self.state.difficulty == 0))
        self.food.spawn(self.snake.body)
        self.spawner.reset()
        self.state.reset(self.state.difficulty)
    
    def update_mouse_position(self, x, y):
        """更新鼠标位置"""
        self.state.set_mouse_position(x, y)
    
    def trigger_boost(self):
        """触发加速"""
        if self.state.difficulty == 0:
            self.state.trigger_boost()
    
    # ========== 绘制方法 ==========
    
    def draw(self, screen):
        """绘制游戏画面"""
        # 游戏画面
        self.game_renderer.draw(screen, self.snake, self.food, self.spawner)
        
        # UI
        self.ui_renderer.draw(screen, self.state)
        
        # 游戏结束/暂停画面
        if self.state.game_over:
            self.screen_renderer.draw_game_over(screen, self.state.score, self.state.high_score)
        elif self.state.paused:
            self.screen_renderer.draw_pause(screen)
        
        # 闪光弹效果
        self.game_renderer.draw_flashbang(screen, self.state.flashbang_active)
    
    def draw_start_screen(self, screen):
        """绘制开始界面"""
        self.screen_renderer.update_frame(self.state.frame)
        self.screen_renderer.draw_start_screen(screen, self.state.difficulty)
        self.state.update_frame()
