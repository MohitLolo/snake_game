"""
实体生成管理器
管理炸弹、红蛇、黄蛇、经验球等实体的生成和更新
"""
from ..config import (
    BOMB_CONFIG, RED_SNAKE_CONFIG, YELLOW_SNAKE_CONFIG, FLASHBANG_CONFIG, BLUE_FOOD_CONFIG
)
from ..entities import Bomb, RedSnake, YellowSnake, BlueFood


class EntitySpawner:
    """实体生成管理器"""
    
    def __init__(self, game_state):
        self.state = game_state
        self.bomb = None
        self.red_snake = None
        self.yellow_snake = None
        self.exp_balls = []
        self.blue_food = None
    
    def reset(self):
        """重置所有实体"""
        self.bomb = None
        self.red_snake = None
        self.yellow_snake = None
        self.exp_balls = []
        self.blue_food = None
    
    def update(self, snake_body, food_pos, audio=None):
        """更新所有实体"""
        self._update_bomb(snake_body, food_pos)
        self._update_red_snake()
        self._update_yellow_snake()
        self._update_blue_food(snake_body, food_pos)
        self._update_exp_balls()
        self._update_flashbang(audio)
    
    def _update_bomb(self, snake_body, food_pos):
        """更新炸弹"""
        if self.state.difficulty == 0:
            return
        
        # 更新现有炸弹
        if self.bomb:
            alive = self.bomb.update()
            if not alive:
                self.bomb = None
        
        # 生成新炸弹
        if self.bomb is None:
            self.state.bomb_timer += 1
            if self.state.bomb_timer >= BOMB_CONFIG['interval']:
                self.state.bomb_timer = 0
                self.bomb = Bomb()
                exclude = list(snake_body) + [food_pos]
                self.bomb.spawn(exclude)
    
    def _update_red_snake(self):
        """更新红蛇"""
        if self.state.difficulty == 0:
            return
        
        # 更新现有红蛇
        if self.red_snake and self.red_snake.alive:
            # 注意：需要传入玩家蛇身体，这里简化处理
            alive = self.red_snake.update([])
            if not alive:
                self.exp_balls.extend(self.red_snake.get_exp_balls())
                self.red_snake = None
        
        # 生成新红蛇
        if self.red_snake is None:
            self.state.red_snake_timer += 1
            if self.state.red_snake_timer >= RED_SNAKE_CONFIG['interval']:
                self.state.red_snake_timer = 0
                self.red_snake = RedSnake()
    
    def _update_yellow_snake(self):
        """更新黄蛇"""
        if self.state.difficulty != 0:
            return
        
        # 更新现有黄蛇
        if self.yellow_snake:
            if self.yellow_snake.alive:
                self.yellow_snake.update()
            else:
                # 黄蛇死亡，生成经验球
                self.exp_balls.extend(self.yellow_snake.get_exp_balls())
                self.yellow_snake = None
        
        # 生成新黄蛇
        if self.yellow_snake is None:
            self.state.yellow_snake_timer += 1
            if self.state.yellow_snake_timer >= YELLOW_SNAKE_CONFIG['interval']:
                self.state.yellow_snake_timer = 0
                self.yellow_snake = YellowSnake()
    
    def _update_exp_balls(self):
        """更新经验球"""
        for ball in self.exp_balls[:]:
            alive = ball.update()
            if not alive:
                self.exp_balls.remove(ball)
    
    def _update_blue_food(self, snake_body, food_pos):
        """更新蓝色食物（无敌道具）"""
        # 更新现有蓝色食物动画
        if self.blue_food and self.blue_food.active:
            self.blue_food.update()
        
        # 无敌状态下不生成新的蓝色食物
        if self.state.is_invincible:
            return
        
        # 生成新蓝色食物
        if self.blue_food is None or not self.blue_food.active:
            self.state.blue_food_timer += 1
            if self.state.blue_food_timer >= BLUE_FOOD_CONFIG['interval']:
                self.state.blue_food_timer = 0
                self.blue_food = BlueFood()
                exclude = list(snake_body) + [food_pos]
                self.blue_food.spawn(exclude)
    
    def _update_flashbang(self, audio):
        """更新闪光弹"""
        # 普通模式(2)和困难模式(3)有闪光弹
        if self.state.difficulty not in (2, 3):
            return
        
        if self.state.flashbang_active:
            self.state.flashbang_frame += 1
            if self.state.flashbang_frame >= FLASHBANG_CONFIG['duration']:
                self.state.flashbang_active = False
                self.state.flashbang_frame = 0
            return
        
        self.state.flashbang_timer += 1
        if self.state.flashbang_timer >= FLASHBANG_CONFIG['interval']:
            self.state.flashbang_timer = 0
            self.state.flashbang_active = True
            self.state.flashbang_frame = 0
            if audio:
                audio.play_flashbang_sound()
