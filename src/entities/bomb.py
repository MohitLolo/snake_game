"""
炸弹实体模块
"""
import random
import pygame
from ..config import CELL_SIZE, CELL_NUMBER_X, CELL_NUMBER_Y, COLORS, BOMB_CONFIG
from ..utils import Point


class Bomb:
    """炸弹实体"""
    
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
        """更新状态"""
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
        """获取爆炸范围"""
        if not self.exploding:
            return []
        
        cells = []
        for dx in range(-self.radius, self.radius + 1):
            for dy in range(-self.radius, self.radius + 1):
                if abs(dx) + abs(dy) > 0:
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
        else:
            self._draw_bomb(screen, cx, cy)
    
    def _draw_bomb(self, screen, cx, cy):
        """绘制炸弹"""
        r = CELL_SIZE // 2 - 2
        remaining = self.lifetime - self._tick
        flash_speed = 10 if remaining > 60 else 5 if remaining > 30 else 2
        is_visible = (self._tick // flash_speed) % 2 == 0
        
        if is_visible:
            surf = pygame.Surface((CELL_SIZE * 3, CELL_SIZE * 3), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 0, 0, 60),
                              (CELL_SIZE * 1.5, CELL_SIZE * 1.5), r + 6)
            screen.blit(surf, (cx - CELL_SIZE * 1.5, cy - CELL_SIZE * 1.5))
        
        pygame.draw.circle(screen, COLORS['BOMB'], (cx, cy), r)
        pygame.draw.circle(screen, (150, 80, 90), (cx, cy), r, 2)
        pygame.draw.circle(screen, (140, 100, 110),
                          (cx - r // 3, cy - r // 3), max(3, r // 3))
        
        fuse_end = (cx + r // 2 - 2, cy - r // 2 + 2)
        pygame.draw.line(screen, (180, 180, 180), (cx + 2, cy - 2), fuse_end, 2)
        
        if is_visible:
            pygame.draw.circle(screen, COLORS['BOMB_FUSE'], fuse_end, 5)
            pygame.draw.circle(screen, COLORS['BOMB_SPARK'], fuse_end, 3)
    
    def _draw_explosion(self, screen, cx, cy):
        """绘制爆炸"""
        progress = self.explosion_frame / BOMB_CONFIG['explosion_duration']
        
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
        
        center_r = int((CELL_SIZE + 10) * (1 - progress * 0.5))
        alpha = int(255 * (1 - progress))
        
        surf = pygame.Surface((CELL_SIZE * 3, CELL_SIZE * 3), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 50, 0, alpha), (CELL_SIZE * 1.5, CELL_SIZE * 1.5), center_r)
        pygame.draw.circle(surf, (255, 200, 0, alpha), (CELL_SIZE * 1.5, CELL_SIZE * 1.5), center_r // 2)
        pygame.draw.circle(surf, (255, 255, 255, alpha), (CELL_SIZE * 1.5, CELL_SIZE * 1.5), center_r // 4)
        screen.blit(surf, (cx - CELL_SIZE * 1.5, cy - CELL_SIZE * 1.5))
