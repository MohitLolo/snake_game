"""
游戏实体模块
包含：蛇、食物、炸弹等游戏对象
"""
import random
import pygame
from .config import (
    CELL_SIZE, CELL_NUMBER_X, CELL_NUMBER_Y, 
    COLORS, BOMB_CONFIG, RED_SNAKE_CONFIG
)
from .utils import Point


class Snake:
    """贪吃蛇实体"""
    
    def __init__(self, start_pos=None):
        if start_pos is None:
            start_pos = Point(10, 14)
        
        self.body = [
            start_pos,
            Point(start_pos.x - 1, start_pos.y),
            Point(start_pos.x - 2, start_pos.y)
        ]
        self.direction = Point(1, 0)  # 初始向右
        self.new_block = False
        self._dir_queue = []
    
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
    
    def queue_direction(self, direction):
        """添加方向到队列（防止高速操作丢指令）"""
        last = self._dir_queue[-1] if self._dir_queue else self.direction
        
        # 忽略反向和重复
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
        total = len(self.body)
        for i, block in enumerate(self.body):
            x = block.x * CELL_SIZE
            y = block.y * CELL_SIZE
            rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
            
            if i == 0:
                # 蛇头
                pygame.draw.rect(screen, COLORS['SNAKE_HEAD'], rect, border_radius=6)
                self._draw_eyes(screen, rect)
            else:
                # 蛇身（渐暗效果）
                ratio = max(0.35, 1 - i / total)
                color = (
                    int(COLORS['SNAKE_BODY'][0] * ratio),
                    int(COLORS['SNAKE_BODY'][1] * ratio),
                    int(COLORS['SNAKE_BODY'][2] * ratio),
                )
                pygame.draw.rect(screen, color, rect, border_radius=4)
                # 高光条
                highlight = pygame.Rect(x + 3, y + 3, CELL_SIZE - 8, 3)
                hl_color = (
                    min(255, color[0] + 40),
                    min(255, color[1] + 40),
                    min(255, color[2] + 40),
                )
                pygame.draw.rect(screen, hl_color, highlight, border_radius=2)
    
    def _draw_eyes(self, screen, head_rect):
        """绘制眼睛"""
        d = self.direction
        es = max(2, CELL_SIZE // 5)
        cx, cy = head_rect.centerx, head_rect.centery
        offset = CELL_SIZE // 4
        
        if d.x == 1:    # 右
            p1, p2 = (cx + offset, cy - offset), (cx + offset, cy + offset)
        elif d.x == -1: # 左
            p1, p2 = (cx - offset, cy - offset), (cx - offset, cy + offset)
        elif d.y == -1: # 上
            p1, p2 = (cx - offset, cy - offset), (cx + offset, cy - offset)
        else:           # 下
            p1, p2 = (cx - offset, cy + offset), (cx + offset, cy + offset)
        
        for p in (p1, p2):
            pygame.draw.circle(screen, COLORS['SNAKE_EYE'], p, es)
            pygame.draw.circle(screen, COLORS['SNAKE_PUPIL'], p, max(1, es // 2))


class Food:
    """食物实体"""
    
    def __init__(self):
        self.pos = Point(0, 0)
        self._glow_tick = 0
    
    def spawn(self, exclude=None):
        """在随机位置生成，排除指定位置"""
        exclude = exclude or []
        while True:
            p = Point(
                random.randint(0, CELL_NUMBER_X - 1),
                random.randint(0, CELL_NUMBER_Y - 1)
            )
            if p not in exclude:
                self.pos = p
                break
    
    def update(self):
        """更新动画"""
        self._glow_tick = (self._glow_tick + 1) % 60
    
    def draw(self, screen):
        """绘制食物"""
        cx = self.pos.x * CELL_SIZE + CELL_SIZE // 2
        cy = self.pos.y * CELL_SIZE + CELL_SIZE // 2
        r = CELL_SIZE // 2 - 1
        
        # 光晕
        glow_r = int(3 + 2 * abs(30 - self._glow_tick) / 30)
        glow_surf = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLORS['FOOD'], 40),
                          (CELL_SIZE, CELL_SIZE), r + glow_r + 3)
        screen.blit(glow_surf, (cx - CELL_SIZE, cy - CELL_SIZE))
        
        # 苹果主体
        pygame.draw.circle(screen, COLORS['FOOD'], (cx, cy), r)
        # 高光
        pygame.draw.circle(screen, COLORS['FOOD_SHINE'],
                          (cx - r // 3, cy - r // 3), max(2, r // 3))
        # 果梗
        stem_rect = pygame.Rect(cx - 1, cy - r - 3, 3, 5)
        pygame.draw.rect(screen, COLORS['FOOD_STEM'], stem_rect, border_radius=1)


class Bomb:
    """炸弹实体 - 时间到会在周围爆炸"""
    
    def __init__(self):
        self.pos = Point(0, 0)
        self.lifetime = BOMB_CONFIG['lifetime']
        self._tick = 0
        self._glow_tick = 0
        self.active = True
        self.exploding = False
        self.explosion_frame = 0
        self.radius = BOMB_CONFIG['explosion_radius']
    
    def spawn(self, exclude=None):
        """在随机位置生成"""
        exclude = exclude or []
        while True:
            p = Point(
                random.randint(0, CELL_NUMBER_X - 1),
                random.randint(0, CELL_NUMBER_Y - 1)
            )
            if p not in exclude:
                self.pos = p
                break
    
    def update(self):
        """更新状态，返回是否还存活"""
        if not self.active:
            return False
        
        if self.exploding:
            self.explosion_frame += 1
            if self.explosion_frame >= BOMB_CONFIG['explosion_duration']:
                self.active = False
                return False
            return True
        
        self._tick += 1
        self._glow_tick = (self._glow_tick + 1) % 30
        
        if self._tick >= self.lifetime:
            self.exploding = True
        
        return True
    
    def get_explosion_range(self):
        """获取爆炸范围的所有格子"""
        if not self.exploding:
            return []
        
        cells = []
        for dx in range(-self.radius, self.radius + 1):
            for dy in range(-self.radius, self.radius + 1):
                if abs(dx) + abs(dy) > 0:  # 不包括中心
                    nx, ny = self.pos.x + dx, self.pos.y + dy
                    if 0 <= nx < CELL_NUMBER_X and 0 <= ny < CELL_NUMBER_Y:
                        cells.append(Point(nx, ny))
        return cells
    
    def draw(self, screen):
        """绘制"""
        if not self.active:
            return
        
        cx = self.pos.x * CELL_SIZE + CELL_SIZE // 2
        cy = self.pos.y * CELL_SIZE + CELL_SIZE // 2
        
        if self.exploding:
            self._draw_explosion(screen, cx, cy)
            return
        
        self._draw_bomb(screen, cx, cy)
    
    def _draw_bomb(self, screen, cx, cy):
        """绘制炸弹本体"""
        r = CELL_SIZE // 2 - 2
        remaining = self.lifetime - self._tick
        flash_speed = 10 if remaining > 60 else 5 if remaining > 30 else 2
        is_visible = (self._tick // flash_speed) % 2 == 0
        
        # 警告光环
        if is_visible:
            surf = pygame.Surface((CELL_SIZE * 3, CELL_SIZE * 3), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 0, 0, 60),
                              (CELL_SIZE * 1.5, CELL_SIZE * 1.5), r + 6)
            screen.blit(surf, (cx - CELL_SIZE * 1.5, cy - CELL_SIZE * 1.5))
        
        # 炸弹主体
        pygame.draw.circle(screen, COLORS['BOMB'], (cx, cy), r)
        pygame.draw.circle(screen, (150, 80, 90), (cx, cy), r, 2)
        pygame.draw.circle(screen, (140, 100, 110),
                          (cx - r // 3, cy - r // 3), max(3, r // 3))
        
        # 引线和火焰
        fuse_end = (cx + r // 2 - 2, cy - r // 2 + 2)
        pygame.draw.line(screen, (180, 180, 180), (cx + 2, cy - 2), fuse_end, 2)
        
        if is_visible:
            pygame.draw.circle(screen, COLORS['BOMB_FUSE'], fuse_end, 5)
            pygame.draw.circle(screen, COLORS['BOMB_SPARK'], fuse_end, 3)
    
    def _draw_explosion(self, screen, cx, cy):
        """绘制爆炸效果"""
        progress = self.explosion_frame / BOMB_CONFIG['explosion_duration']
        
        # 周围格子爆炸
        for cell in self.get_explosion_range():
            cell_cx = cell.x * CELL_SIZE + CELL_SIZE // 2
            cell_cy = cell.y * CELL_SIZE + CELL_SIZE // 2
            
            max_r = CELL_SIZE // 2 + 5
            current_r = int(max_r * (1 - progress))
            alpha = int(255 * (1 - progress))
            
            surf = pygame.Surface((CELL_SIZE + 10, CELL_SIZE + 10), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 100, 0, alpha),
                              (CELL_SIZE // 2 + 5, CELL_SIZE // 2 + 5), current_r)
            screen.blit(surf, (cell_cx - CELL_SIZE // 2 - 5, cell_cy - CELL_SIZE // 2 - 5))
        
        # 中心爆炸
        center_r = int((CELL_SIZE + 10) * (1 - progress * 0.5))
        alpha = int(255 * (1 - progress))
        
        surf = pygame.Surface((CELL_SIZE * 3, CELL_SIZE * 3), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 50, 0, alpha), (CELL_SIZE * 1.5, CELL_SIZE * 1.5), center_r)
        pygame.draw.circle(surf, (255, 200, 0, alpha), (CELL_SIZE * 1.5, CELL_SIZE * 1.5), center_r // 2)
        pygame.draw.circle(surf, (255, 255, 255, alpha), (CELL_SIZE * 1.5, CELL_SIZE * 1.5), center_r // 4)
        screen.blit(surf, (cx - CELL_SIZE * 1.5, cy - CELL_SIZE * 1.5))


class RedSnake:
    """红蛇 - 敌对蛇，碰到边界或绿蛇身体死亡，变成经验球"""
    
    def __init__(self, start_pos=None, length=None):
        if start_pos is None:
            # 随机生成在远离绿蛇的位置
            start_pos = self._random_spawn_pos()
        
        if length is None:
            length = random.randint(RED_SNAKE_CONFIG['min_length'], 
                                   RED_SNAKE_CONFIG['max_length'])
        
        # 初始化身体
        self.body = [Point(start_pos.x - i, start_pos.y) for i in range(length)]
        self.direction = Point(1, 0)  # 初始向右
        self.alive = True
        self._move_timer = 0
    
    def _random_spawn_pos(self):
        """随机生成位置（远离边界）"""
        return Point(
            random.randint(5, CELL_NUMBER_X - 6),
            random.randint(5, CELL_NUMBER_Y - 6)
        )
    
    def update(self, green_snake_body):
        """更新红蛇状态，返回是否还存活"""
        if not self.alive:
            return False
        
        self._move_timer += 1
        if self._move_timer >= RED_SNAKE_CONFIG['speed'] // 20:  # 根据速度调整
            self._move_timer = 0
            self._auto_move(green_snake_body)
        
        # 检查死亡条件
        if self._check_death(green_snake_body):
            self.alive = False
            return False
        
        return True
    
    def _auto_move(self, green_snake_body):
        """自动移动（简单的随机转向）"""
        head = self.body[0]
        
        # 随机决定是否转向
        if random.random() < 0.3:
            # 随机选择一个方向
            directions = [Point(0, -1), Point(0, 1), Point(-1, 0), Point(1, 0)]
            # 排除反向
            valid_dirs = [d for d in directions 
                         if not (d.x == -self.direction.x and d.y == -self.direction.y)]
            if valid_dirs:
                self.direction = random.choice(valid_dirs)
        
        # 移动
        new_head = Point(head.x + self.direction.x, head.y + self.direction.y)
        self.body = [new_head] + self.body[:-1]
    
    def _check_death(self, green_snake_body):
        """检查是否死亡（撞墙或撞到绿蛇身体）"""
        head = self.body[0]
        
        # 撞墙
        if not (0 <= head.x < CELL_NUMBER_X and 0 <= head.y < CELL_NUMBER_Y):
            return True
        
        # 撞到绿蛇身体（不包括头部）
        if head in green_snake_body[1:]:
            return True
        
        return False
    
    def get_exp_balls(self):
        """死亡后变成经验球，每个身体段一个"""
        return [ExpBall(pos=p) for p in self.body]
    
    def draw(self, screen):
        """绘制红蛇"""
        for i, block in enumerate(self.body):
            x = block.x * CELL_SIZE
            y = block.y * CELL_SIZE
            rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
            
            if i == 0:
                # 蛇头
                pygame.draw.rect(screen, COLORS['RED_SNAKE_HEAD'], rect, border_radius=6)
            else:
                # 蛇身
                pygame.draw.rect(screen, COLORS['RED_SNAKE_BODY'], rect, border_radius=4)


class ExpBall:
    """经验球 - 绿蛇吃掉后快速变长"""
    
    def __init__(self, pos=None):
        self.pos = pos or Point(0, 0)
        self._glow_tick = 0
        self.lifetime = 600  # 10秒后消失 (60fps * 10)
        self._tick = 0
    
    def update(self):
        """更新状态，返回是否还存活"""
        self._tick += 1
        self._glow_tick = (self._glow_tick + 1) % 30
        return self._tick < self.lifetime
    
    def draw(self, screen):
        """绘制经验球"""
        cx = self.pos.x * CELL_SIZE + CELL_SIZE // 2
        cy = self.pos.y * CELL_SIZE + CELL_SIZE // 2
        r = CELL_SIZE // 2 - 2
        
        # 发光效果
        glow_r = int(4 + 2 * abs(15 - self._glow_tick) / 15)
        glow_surf = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLORS['EXP_BALL_GLOW'], 60),
                          (CELL_SIZE, CELL_SIZE), r + glow_r + 3)
        screen.blit(glow_surf, (cx - CELL_SIZE, cy - CELL_SIZE))
        
        # 主体
        pygame.draw.circle(screen, COLORS['EXP_BALL'], (cx, cy), r)
        # 高光
        pygame.draw.circle(screen, COLORS['EXP_BALL_GLOW'],
                          (cx - r // 3, cy - r // 3), max(2, r // 3))
