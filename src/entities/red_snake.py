"""
红蛇实体模块
"""
import random
import pygame
from ..config import CELL_SIZE, CELL_NUMBER_X, CELL_NUMBER_Y, COLORS, RED_SNAKE_CONFIG
from ..utils import Point
from .exp_ball import ExpBall


class RedSnake:
    """红蛇 - 敌对蛇"""
    
    def __init__(self, start_pos=None, length=None):
        if start_pos is None:
            start_pos = self._random_spawn_pos()
        
        if length is None:
            length = random.randint(RED_SNAKE_CONFIG['min_length'], 
                                   RED_SNAKE_CONFIG['max_length'])
        
        self.body = [Point(start_pos.x - i, start_pos.y) for i in range(length)]
        self.direction = Point(1, 0)
        self.alive = True
        self._move_timer = 0
    
    def _random_spawn_pos(self):
        """随机生成位置"""
        return Point(
            random.randint(5, CELL_NUMBER_X - 6),
            random.randint(5, CELL_NUMBER_Y - 6)
        )
    
    def update(self, green_snake_body):
        """更新红蛇状态"""
        if not self.alive:
            return False
        
        self._move_timer += 1
        if self._move_timer >= RED_SNAKE_CONFIG['speed'] // 20:
            self._move_timer = 0
            self._auto_move(green_snake_body)
        
        if self._check_death(green_snake_body):
            self.alive = False
            return False
        
        return True
    
    def _auto_move(self, green_snake_body):
        """自动移动"""
        head = self.body[0]
        
        if random.random() < 0.3:
            directions = [Point(0, -1), Point(0, 1), Point(-1, 0), Point(1, 0)]
            valid_dirs = [d for d in directions 
                         if not (d.x == -self.direction.x and d.y == -self.direction.y)]
            if valid_dirs:
                self.direction = random.choice(valid_dirs)
        
        new_head = Point(head.x + self.direction.x, head.y + self.direction.y)
        self.body = [new_head] + self.body[:-1]
    
    def _check_death(self, green_snake_body):
        """检查是否死亡"""
        head = self.body[0]
        
        if not (0 <= head.x < CELL_NUMBER_X and 0 <= head.y < CELL_NUMBER_Y):
            return True
        
        if head in green_snake_body[1:]:
            return True
        
        return False
    
    def get_exp_balls(self):
        """死亡后变成经验球"""
        return [ExpBall(pos=p) for p in self.body]
    
    def draw(self, screen):
        """绘制红蛇"""
        for i, block in enumerate(self.body):
            x = block.x * CELL_SIZE
            y = block.y * CELL_SIZE
            rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
            
            if i == 0:
                pygame.draw.rect(screen, COLORS['RED_SNAKE_HEAD'], rect, border_radius=6)
            else:
                pygame.draw.rect(screen, COLORS['RED_SNAKE_BODY'], rect, border_radius=4)
