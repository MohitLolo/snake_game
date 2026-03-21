"""
UI 渲染器
负责游戏界面和 HUD 的渲染
"""
import pygame
import math
from .base import BaseRenderer
from ..config import COLORS, WINDOW_WIDTH, CELL_SIZE, CELL_NUMBER_Y, DIFFICULTY_COLORS, DIFFICULTY_LABELS


class UIRenderer(BaseRenderer):
    """UI 渲染器"""
    
    def draw(self, screen, game_state):
        """绘制 UI"""
        self._draw_status_bar(screen, game_state)
    
    def _draw_status_bar(self, screen, state):
        """绘制状态栏"""
        bar_y = CELL_NUMBER_Y * CELL_SIZE
        
        # 状态栏背景
        bar_rect = pygame.Rect(0, bar_y, WINDOW_WIDTH, 60)
        pygame.draw.rect(screen, COLORS['PANEL'], bar_rect)
        
        # 顶部高光线
        pygame.draw.line(screen, COLORS['BORDER'], (0, bar_y), (WINDOW_WIDTH, bar_y), 2)
        
        # 底部装饰线
        pygame.draw.line(screen, COLORS['BORDER'][:3], (0, bar_y + 58), (WINDOW_WIDTH, bar_y + 58), 1)
        
        cy = bar_y + 30
        
        # 分数区域
        star_x = 80
        self._draw_mini_icon(screen, star_x, cy, 'star', COLORS['ACCENT'])
        self._draw_text(screen, f"{state.score:04d}",
                       self.fonts.normal_font, COLORS['ACCENT'], (160, cy))
        
        # 分隔符
        pygame.draw.line(screen, COLORS['BORDER'], (280, bar_y + 15), (280, bar_y + 45), 1)
        
        # 最高分区域
        crown_x = 320
        self._draw_mini_icon(screen, crown_x, cy, 'crown', COLORS['DIM'])
        self._draw_text(screen, f"{state.high_score:04d}",
                       self.fonts.normal_font, COLORS['DIM'], (380, cy))
        
        # 分隔符
        pygame.draw.line(screen, COLORS['BORDER'], (500, bar_y + 15), (500, bar_y + 45), 1)
        
        # 难度区域
        diff_color = DIFFICULTY_COLORS[state.difficulty]
        self._draw_mini_icon(screen, 540, cy, 'speed', diff_color)
        diff_text = DIFFICULTY_LABELS[state.difficulty]
        self._draw_text(screen, diff_text, self.fonts.normal_font, diff_color, (620, cy))
    
    def _draw_mini_icon(self, screen, x, y, icon_type, color):
        """绘制迷你图标"""
        if icon_type == 'star':
            points = []
            for i in range(5):
                angle = i * 72 - 90
                px = x + 8 * math.cos(math.radians(angle))
                py = y + 8 * math.sin(math.radians(angle))
                points.append((px, py))
                angle2 = angle + 36
                px2 = x + 4 * math.cos(math.radians(angle2))
                py2 = y + 4 * math.sin(math.radians(angle2))
                points.append((px2, py2))
            pygame.draw.polygon(screen, color, points)
        
        elif icon_type == 'crown':
            pygame.draw.polygon(screen, color, [
                (x - 8, y + 5), (x - 8, y - 3), (x - 4, y),
                (x, y - 6), (x + 4, y), (x + 8, y - 3), (x + 8, y + 5)
            ])
        
        elif icon_type == 'speed':
            pygame.draw.polygon(screen, color, [
                (x + 4, y - 8), (x - 4, y + 1), (x + 1, y + 1),
                (x - 4, y + 8), (x + 6, y - 2), (x + 1, y - 2)
            ])
