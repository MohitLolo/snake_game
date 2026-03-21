"""
食物实体模块
"""
import random
import pygame
from ..config import CELL_SIZE, CELL_NUMBER_X, CELL_NUMBER_Y, COLORS
from ..utils import Point


class Food:
    """食物实体"""
    
    def __init__(self):
        self.pos = Point(0, 0)
        self._glow_tick = 0
    
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
        """更新动画"""
        self._glow_tick = (self._glow_tick + 1) % 60
    
    def draw(self, screen):
        """绘制食物"""
        cx = self.pos.x * CELL_SIZE + CELL_SIZE // 2
        cy = self.pos.y * CELL_SIZE + CELL_SIZE // 2
        r = CELL_SIZE // 2 - 1
        
        glow_r = int(3 + 2 * abs(30 - self._glow_tick) / 30)
        glow_surf = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLORS['FOOD'], 40),
                          (CELL_SIZE, CELL_SIZE), r + glow_r + 3)
        screen.blit(glow_surf, (cx - CELL_SIZE, cy - CELL_SIZE))
        
        pygame.draw.circle(screen, COLORS['FOOD'], (cx, cy), r)
        pygame.draw.circle(screen, COLORS['FOOD_SHINE'],
                          (cx - r // 3, cy - r // 3), max(2, r // 3))
        stem_rect = pygame.Rect(cx - 1, cy - r - 3, 3, 5)
        pygame.draw.rect(screen, COLORS['FOOD_STEM'], stem_rect, border_radius=1)
