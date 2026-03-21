"""
黄蛇实体模块
"""
import math
import random
import pygame
from ..config import CELL_SIZE, COLORS, YELLOW_SNAKE_CONFIG, WINDOW_WIDTH, CELL_NUMBER_Y
from ..utils import Point
from .exp_ball import ExpBall


class YellowSnake:
    """黄蛇 - 新手模式敌对蛇"""
    
    def __init__(self, start_pos=None, length=None):
        if start_pos is None:
            start_pos = self._random_spawn_pos()
        
        if length is None:
            length = random.randint(YELLOW_SNAKE_CONFIG['min_length'], 
                                   YELLOW_SNAKE_CONFIG['max_length'])
        
        self.smooth_body = []
        self._init_smooth_body(start_pos, length)
        self.direction = Point(1, 0)
        self.alive = True
        self._move_timer = 0
    
    def _random_spawn_pos(self):
        """随机生成位置"""
        game_height = CELL_NUMBER_Y * CELL_SIZE
        return (
            random.randint(100, WINDOW_WIDTH - 100),
            random.randint(100, game_height - 100)
        )
    
    def _init_smooth_body(self, start_pos, length):
        """初始化平滑位置"""
        x, y = start_pos
        self.smooth_body = [(x - i * CELL_SIZE, y) for i in range(length)]
    
    def update(self):
        """更新黄蛇状态"""
        if not self.alive:
            return False
        
        self._move_timer += 1
        if self._move_timer >= YELLOW_SNAKE_CONFIG['speed'] // 16:
            self._move_timer = 0
            self._auto_move()
        
        return True
    
    def _auto_move(self):
        """自动移动"""
        head_x, head_y = self.smooth_body[0]
        
        if random.random() < 0.25:
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            valid_dirs = [d for d in directions 
                         if not (d[0] == -self.direction.x and d[1] == -self.direction.y)]
            if valid_dirs:
                d = random.choice(valid_dirs)
                self.direction = Point(d[0], d[1])
        
        speed = 2
        new_head_x = head_x + self.direction.x * speed
        new_head_y = head_y + self.direction.y * speed
        
        new_smooth_body = [(new_head_x, new_head_y)]
        for i in range(1, len(self.smooth_body)):
            prev_x, prev_y = new_smooth_body[i - 1]
            curr_x, curr_y = self.smooth_body[i]
            
            seg_dx = prev_x - curr_x
            seg_dy = prev_y - curr_y
            seg_dist = math.sqrt(seg_dx * seg_dx + seg_dy * seg_dy)
            
            if seg_dist > CELL_SIZE:
                ratio = CELL_SIZE / seg_dist
                new_x = prev_x - seg_dx * ratio
                new_y = prev_y - seg_dy * ratio
                new_smooth_body.append((new_x, new_y))
            else:
                new_smooth_body.append((curr_x, curr_y))
        
        self.smooth_body = new_smooth_body
    
    def check_collision_with_player(self, player_smooth_body):
        """检查是否与玩家蛇碰撞"""
        if not self.alive or not self.smooth_body or not player_smooth_body:
            return False
        
        player_head = player_smooth_body[0]
        
        for seg in self.smooth_body:
            dx = player_head[0] - seg[0]
            dy = player_head[1] - seg[1]
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < CELL_SIZE:
                return True
        return False
    
    def get_exp_balls(self):
        """死亡后变成经验球"""
        balls = []
        for x, y in self.smooth_body:
            grid_x = int(x // CELL_SIZE)
            grid_y = int(y // CELL_SIZE)
            balls.append(ExpBall(pos=Point(grid_x, grid_y)))
        return balls
    
    def draw(self, screen):
        """绘制黄蛇"""
        total = len(self.smooth_body)
        
        for i, (x, y) in enumerate(self.smooth_body):
            size = CELL_SIZE // 2 - 1
            
            if i == 0:
                pygame.draw.circle(screen, COLORS['YELLOW_SNAKE_HEAD'], (int(x), int(y)), size + 2)
            else:
                ratio = max(0.4, 1 - i / total)
                color = (
                    int(COLORS['YELLOW_SNAKE_BODY'][0] * ratio),
                    int(COLORS['YELLOW_SNAKE_BODY'][1] * ratio),
                    int(COLORS['YELLOW_SNAKE_BODY'][2] * ratio),
                )
                pygame.draw.circle(screen, color, (int(x), int(y)), size)
