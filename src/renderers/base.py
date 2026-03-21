"""
渲染器基类
"""
import pygame
from ..config import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, CELL_SIZE, CELL_NUMBER_Y


class BaseRenderer:
    """渲染器基类"""
    
    def __init__(self, font_manager):
        self.fonts = font_manager
    
    def _draw_text(self, screen, text, font, color, center):
        """绘制居中文字"""
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=center)
        screen.blit(surf, rect)
    
    def _draw_panel(self, screen, rect, alpha=210, radius=12):
        """绘制半透明面板"""
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*COLORS['PANEL'], alpha), surf.get_rect(), border_radius=radius)
        pygame.draw.rect(surf, (*COLORS['BORDER'], 180), surf.get_rect(), 2, border_radius=radius)
        screen.blit(surf, rect.topleft)
