"""
经验球实体模块
"""
import pygame
from ..config import CELL_SIZE, COLORS
from ..utils import Point


class ExpBall:
    """经验球"""
    
    def __init__(self, pos=None):
        self.pos = pos or Point(0, 0)
        self._glow_tick = 0
        self.lifetime = 600
        self._tick = 0
    
    def update(self):
        """更新状态"""
        self._tick += 1
        self._glow_tick = (self._glow_tick + 1) % 30
        return self._tick < self.lifetime
    
    def draw(self, screen):
        """绘制经验球"""
        cx = self.pos.x * CELL_SIZE + CELL_SIZE // 2
        cy = self.pos.y * CELL_SIZE + CELL_SIZE // 2
        r = CELL_SIZE // 2 - 2
        
        glow_r = int(4 + 2 * abs(15 - self._glow_tick) / 15)
        glow_surf = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLORS['EXP_BALL_GLOW'], 60),
                          (CELL_SIZE, CELL_SIZE), r + glow_r + 3)
        screen.blit(glow_surf, (cx - CELL_SIZE, cy - CELL_SIZE))
        
        pygame.draw.circle(screen, COLORS['EXP_BALL'], (cx, cy), r)
        pygame.draw.circle(screen, COLORS['EXP_BALL_GLOW'],
                          (cx - r // 3, cy - r // 3), max(2, r // 3))
