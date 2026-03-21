"""
蛇实体模块
"""
import math
import pygame
from ..config import CELL_SIZE, CELL_NUMBER_X, CELL_NUMBER_Y, COLORS, BEGINNER_CONFIG
from ..utils import Point


class Snake:
    """贪吃蛇实体"""
    
    def __init__(self, start_pos=None, beginner_mode=False):
        if start_pos is None:
            start_pos = Point(10, 14)
        
        self.body = [
            start_pos,
            Point(start_pos.x - 1, start_pos.y),
            Point(start_pos.x - 2, start_pos.y)
        ]
        self.direction = Point(1, 0)
        self.new_block = False
        self._dir_queue = []
        
        self.beginner_mode = beginner_mode
        self.smooth_body = []
        self._init_smooth_body()
    
    def _init_smooth_body(self):
        """初始化平滑位置"""
        self.smooth_body = [(block.x * CELL_SIZE + CELL_SIZE // 2,
                            block.y * CELL_SIZE + CELL_SIZE // 2)
                           for block in self.body]
    
    def move(self):
        """移动蛇"""
        if self._dir_queue:
            self.direction = self._dir_queue.pop(0)
        
        head = self.body[0]
        new_head = Point(head.x + self.direction.x, head.y + self.direction.y)
        
        if self.new_block:
            self.body.insert(0, new_head)
            self.new_block = False
        else:
            self.body = [new_head] + self.body[:-1]
    
    def grow(self):
        """增长"""
        self.new_block = True
        if self.beginner_mode and self.smooth_body:
            self.smooth_body.append(self.smooth_body[-1])
    
    def move_to_mouse(self, mouse_x, mouse_y, speed=None):
        """新手模式：向鼠标位置移动"""
        if not self.beginner_mode:
            return
        
        head_x, head_y = self.smooth_body[0]
        dx = mouse_x - head_x
        dy = mouse_y - head_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < BEGINNER_CONFIG['min_distance']:
            return
        
        if speed is None:
            speed = BEGINNER_CONFIG['snake_speed']
        
        move_x = (dx / distance) * speed
        move_y = (dy / distance) * speed
        
        if abs(dx) > abs(dy):
            self.direction = Point(1, 0) if dx > 0 else Point(-1, 0)
        else:
            self.direction = Point(0, 1) if dy > 0 else Point(0, -1)
        
        new_head_x = head_x + move_x
        new_head_y = head_y + move_y
        
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
        self.body = [Point(int(x // CELL_SIZE), int(y // CELL_SIZE))
                    for x, y in self.smooth_body]
    
    def queue_direction(self, direction):
        """添加方向到队列"""
        last = self._dir_queue[-1] if self._dir_queue else self.direction
        
        if direction.x == -last.x and direction.y == -last.y:
            return
        if direction.x == last.x and direction.y == last.y:
            return
        
        if len(self._dir_queue) < 2:
            self._dir_queue.append(direction)
    
    def check_wall_collision(self):
        """检查是否撞墙"""
        head = self.body[0]
        return not (0 <= head.x < CELL_NUMBER_X and 0 <= head.y < CELL_NUMBER_Y)
    
    def check_self_collision(self):
        """检查是否撞到自己"""
        return self.body[0] in self.body[1:]
    
    def check_collision_with(self, point):
        """检查头部是否与某点碰撞"""
        return self.body[0] == point
    
    def draw(self, screen):
        """绘制蛇"""
        if self.beginner_mode and self.smooth_body:
            self._draw_smooth(screen)
        else:
            self._draw_grid(screen)
    
    def _draw_grid(self, screen):
        """格子模式绘制"""
        total = len(self.body)
        for i, block in enumerate(self.body):
            x = block.x * CELL_SIZE
            y = block.y * CELL_SIZE
            rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
            
            if i == 0:
                pygame.draw.rect(screen, COLORS['SNAKE_HEAD'], rect, border_radius=6)
                self._draw_eyes(screen, rect)
            else:
                ratio = max(0.35, 1 - i / total)
                color = (
                    int(COLORS['SNAKE_BODY'][0] * ratio),
                    int(COLORS['SNAKE_BODY'][1] * ratio),
                    int(COLORS['SNAKE_BODY'][2] * ratio),
                )
                pygame.draw.rect(screen, color, rect, border_radius=4)
                highlight = pygame.Rect(x + 3, y + 3, CELL_SIZE - 8, 3)
                hl_color = (
                    min(255, color[0] + 40),
                    min(255, color[1] + 40),
                    min(255, color[2] + 40),
                )
                pygame.draw.rect(screen, hl_color, highlight, border_radius=2)
    
    def _draw_smooth(self, screen):
        """新手模式：平滑绘制"""
        total = len(self.smooth_body)
        
        for i, (x, y) in enumerate(self.smooth_body):
            size = CELL_SIZE // 2 - 1
            
            if i == 0:
                pygame.draw.circle(screen, COLORS['SNAKE_HEAD'], (int(x), int(y)), size + 2)
                self._draw_smooth_eyes(screen, x, y, size)
            else:
                ratio = max(0.35, 1 - i / total)
                color = (
                    int(COLORS['SNAKE_BODY'][0] * ratio),
                    int(COLORS['SNAKE_BODY'][1] * ratio),
                    int(COLORS['SNAKE_BODY'][2] * ratio),
                )
                pygame.draw.circle(screen, color, (int(x), int(y)), size)
    
    def _draw_smooth_eyes(self, screen, x, y, size):
        """新手模式：绘制眼睛"""
        d = self.direction
        es = max(2, CELL_SIZE // 5)
        offset = size // 2
        
        if d.x == 1:
            p1, p2 = (x + offset, y - offset), (x + offset, y + offset)
        elif d.x == -1:
            p1, p2 = (x - offset, y - offset), (x - offset, y + offset)
        elif d.y == -1:
            p1, p2 = (x - offset, y - offset), (x + offset, y - offset)
        else:
            p1, p2 = (x - offset, y + offset), (x + offset, y + offset)
        
        for px, py in (p1, p2):
            pygame.draw.circle(screen, COLORS['SNAKE_EYE'], (int(px), int(py)), es)
            pygame.draw.circle(screen, COLORS['SNAKE_PUPIL'], (int(px), int(py)), max(1, es // 2))
    
    def _draw_eyes(self, screen, head_rect):
        """绘制眼睛"""
        d = self.direction
        es = max(2, CELL_SIZE // 5)
        cx, cy = head_rect.centerx, head_rect.centery
        offset = CELL_SIZE // 4
        
        if d.x == 1:
            p1, p2 = (cx + offset, cy - offset), (cx + offset, cy + offset)
        elif d.x == -1:
            p1, p2 = (cx - offset, cy - offset), (cx - offset, cy + offset)
        elif d.y == -1:
            p1, p2 = (cx - offset, cy - offset), (cx + offset, cy - offset)
        else:
            p1, p2 = (cx - offset, cy + offset), (cx + offset, cy + offset)
        
        for p in (p1, p2):
            pygame.draw.circle(screen, COLORS['SNAKE_EYE'], p, es)
            pygame.draw.circle(screen, COLORS['SNAKE_PUPIL'], p, max(1, es // 2))
