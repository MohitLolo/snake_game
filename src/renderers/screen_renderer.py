"""
屏幕渲染器
负责开始界面、游戏结束、暂停等全屏画面的渲染
"""
import pygame
import math
from .base import BaseRenderer
from ..config import COLORS, WINDOW_WIDTH, CELL_NUMBER_Y, CELL_SIZE, DIFFICULTY_COLORS


class ScreenRenderer(BaseRenderer):
    """屏幕渲染器"""
    
    def __init__(self, font_manager):
        super().__init__(font_manager)
        self.frame = 0
    
    def update_frame(self, frame):
        """更新帧计数"""
        self.frame = frame
    
    def draw_start_screen(self, screen, difficulty):
        """绘制开始界面"""
        self._draw_background(screen)
        
        cx, cy = WINDOW_WIDTH // 2, 620 // 2
        
        # 装饰性蛇形图案
        self._draw_decorative_snake(screen)
        
        # 主面板
        panel = pygame.Rect(cx - 280, cy - 200, 560, 380)
        shadow_surf = pygame.Surface((panel.width + 10, panel.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect(), border_radius=16)
        screen.blit(shadow_surf, (panel.x + 5, panel.y + 5))
        self._draw_panel(screen, panel, radius=16)
        
        # 标题
        glow_offset = abs(30 - (self.frame % 60)) / 30 * 0.3 + 0.7
        title_color = tuple(int(c * glow_offset) for c in COLORS['TITLE'])
        self._draw_text(screen, "贪 吃 蛇", self.fonts.title_font, title_color, (cx, cy - 130))
        
        # 标题下划线
        pygame.draw.line(screen, COLORS['BORDER'], (cx - 150, cy - 85), (cx + 150, cy - 85), 2)
        pygame.draw.circle(screen, COLORS['ACCENT'], (cx - 150, cy - 85), 4)
        pygame.draw.circle(screen, COLORS['ACCENT'], (cx + 150, cy - 85), 4)
        
        # 操作提示
        hints = [
            ("空格键", "开始游戏", 'play'),
            ("方向键", "控制移动", 'arrow'),
            ("空格键", "暂停 / 继续", 'pause'),
        ]
        
        for i, (key, desc, icon) in enumerate(hints):
            y = cy - 50 + i * 48
            key_rect = pygame.Rect(cx - 200, y - 14, 100, 28)
            pygame.draw.rect(screen, (*COLORS['BG'], 150), key_rect, border_radius=6)
            pygame.draw.rect(screen, COLORS['BORDER'], key_rect, 1, border_radius=6)
            self._draw_text(screen, key, self.fonts.small_font, COLORS['ACCENT'], (cx - 150, y))
            self._draw_text(screen, desc, self.fonts.small_font, COLORS['TEXT'], (cx + 60, y))
        
        # 难度选择
        pygame.draw.line(screen, COLORS['BORDER'], (cx - 220, cy + 100), (cx + 220, cy + 100), 1)
        
        difficulties = [
            (0, "新手", DIFFICULTY_COLORS[0]),
            (1, "简单", DIFFICULTY_COLORS[1]),
            (2, "普通", DIFFICULTY_COLORS[2]),
            (3, "困难", DIFFICULTY_COLORS[3])
        ]
        btn_y = cy + 130
        btn_width = 80
        btn_spacing = 100
        start_x = cx - (len(difficulties) - 1) * btn_spacing // 2
        
        for level, name, color in difficulties:
            btn_x = start_x + level * btn_spacing
            btn_rect = pygame.Rect(btn_x - btn_width // 2, btn_y - 18, btn_width, 36)
            
            if difficulty == level:
                bg_surf = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(bg_surf, (*color, 60), bg_surf.get_rect(), border_radius=8)
                screen.blit(bg_surf, btn_rect.topleft)
                pygame.draw.rect(screen, color, btn_rect, 2, border_radius=8)
                text_color = color
            else:
                pygame.draw.rect(screen, COLORS['BG'], btn_rect, border_radius=8)
                pygame.draw.rect(screen, COLORS['DIM'], btn_rect, 1, border_radius=8)
                text_color = COLORS['DIM']
            
            self._draw_text(screen, name, self.fonts.small_font, text_color, (btn_x, btn_y))
        
        # 箭头指示
        if difficulty > 0:
            left_x = start_x - 50
            pygame.draw.polygon(screen, COLORS['DIM'], [
                (left_x - 8, btn_y), (left_x + 8, btn_y - 10), (left_x + 8, btn_y + 10)
            ])
        if difficulty < 3:
            right_x = start_x + 3 * btn_spacing + 50
            pygame.draw.polygon(screen, COLORS['DIM'], [
                (right_x + 8, btn_y), (right_x - 8, btn_y - 10), (right_x - 8, btn_y + 10)
            ])
        
        # 底部提示
        pulse = 0.5 + 0.5 * abs(30 - (self.frame % 60)) / 30
        hint_color = tuple(int(c * pulse) for c in COLORS['DIM'])
        self._draw_text(screen, "按数字键或方向键选择难度",
                       self.fonts.small_font, hint_color, (cx, cy + 175))
    
    def draw_game_over(self, screen, score, high_score):
        """绘制游戏结束画面"""
        cx = WINDOW_WIDTH // 2
        cy = CELL_NUMBER_Y * CELL_SIZE // 2
        
        # 遮罩
        overlay = pygame.Surface((WINDOW_WIDTH, CELL_NUMBER_Y * CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 面板
        panel = pygame.Rect(cx - 240, cy - 150, 480, 320)
        shadow_surf = pygame.Surface((panel.width + 20, panel.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect(), border_radius=16)
        screen.blit(shadow_surf, (panel.x + 10, panel.y + 10))
        self._draw_panel(screen, panel, alpha=245, radius=16)
        
        # 标题
        pulse = 0.8 + 0.2 * abs(30 - (self.frame % 60)) / 30
        title_color = tuple(int(c * pulse) for c in COLORS['WARN'])
        self._draw_text(screen, "游戏结束", self.fonts.title_font, title_color, (cx, cy - 95))
        
        # 分隔线
        pygame.draw.line(screen, COLORS['BORDER'], (cx - 180, cy - 45), (cx + 180, cy - 45), 2)
        pygame.draw.circle(screen, COLORS['WARN'], (cx - 180, cy - 45), 4)
        pygame.draw.circle(screen, COLORS['WARN'], (cx + 180, cy - 45), 4)
        
        # 得分
        score_y = cy + 5
        self._draw_text(screen, "本局得分", self.fonts.small_font, COLORS['DIM'], (cx - 60, score_y))
        score_color = COLORS['ACCENT'] if score >= high_score else COLORS['TEXT']
        self._draw_text(screen, str(score), self.fonts.title_font, score_color, (cx + 80, score_y))
        
        # 最高记录
        high_y = cy + 65
        self._draw_text(screen, "最高记录", self.fonts.small_font, COLORS['DIM'], (cx - 60, high_y))
        self._draw_text(screen, str(high_score), self.fonts.normal_font, COLORS['ACCENT'], (cx + 80, high_y))
        
        # 新纪录
        if score >= high_score and score > 0:
            new_y = cy + 105
            alpha = int(180 + 75 * math.sin(self.frame * 0.15))
            new_surf = self.fonts.normal_font.render("★ 新纪录 ★", True, COLORS['WARN'])
            new_rect = new_surf.get_rect(center=(cx, new_y))
            new_surf.set_alpha(alpha)
            screen.blit(new_surf, new_rect)
        
        # 重新开始按钮
        hint_y = cy + 150
        hint_rect = pygame.Rect(cx - 100, hint_y - 16, 200, 32)
        hint_alpha = int(100 + 50 * abs(30 - (self.frame % 60)) / 30)
        btn_surf = pygame.Surface((hint_rect.width, hint_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (*COLORS['ACCENT'], hint_alpha), btn_surf.get_rect(), border_radius=8)
        pygame.draw.rect(btn_surf, (*COLORS['ACCENT'], 150), btn_surf.get_rect(), 1, border_radius=8)
        screen.blit(btn_surf, hint_rect.topleft)
        
        text_alpha = int(180 + 75 * abs(30 - (self.frame % 60)) / 30)
        hint_text = self.fonts.small_font.render("按 空格键 重新开始", True, COLORS['TEXT'])
        hint_text.set_alpha(text_alpha)
        text_rect = hint_text.get_rect(center=(cx, hint_y))
        screen.blit(hint_text, text_rect)
    
    def draw_pause(self, screen):
        """绘制暂停画面"""
        cx = WINDOW_WIDTH // 2
        cy = CELL_NUMBER_Y * CELL_SIZE // 2
        
        # 遮罩
        overlay = pygame.Surface((WINDOW_WIDTH, CELL_NUMBER_Y * CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        # 面板
        panel = pygame.Rect(cx - 200, cy - 100, 400, 200)
        shadow_surf = pygame.Surface((panel.width + 15, panel.height + 15), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect(), border_radius=14)
        screen.blit(shadow_surf, (panel.x + 8, panel.y + 8))
        self._draw_panel(screen, panel, radius=14)
        
        # 暂停图标
        bar_color = COLORS['ACCENT']
        pygame.draw.rect(screen, bar_color, pygame.Rect(cx - 25, cy - 40, 15, 50), border_radius=4)
        pygame.draw.rect(screen, bar_color, pygame.Rect(cx + 10, cy - 40, 15, 50), border_radius=4)
        
        # 文字
        self._draw_text(screen, "已 暂 停", self.fonts.normal_font, COLORS['TEXT'], (cx, cy + 40))
        
        # 继续提示
        hint_alpha = int(150 + 105 * abs(30 - (self.frame % 60)) / 30)
        hint_surf = self.fonts.small_font.render("按  空格键  继续", True, COLORS['DIM'])
        hint_rect = hint_surf.get_rect(center=(cx, cy + 75))
        hint_surf.set_alpha(hint_alpha)
        screen.blit(hint_surf, hint_rect)
    
    def _draw_background(self, screen):
        """绘制背景"""
        screen.fill(COLORS['BG'])
        
        game_h = CELL_NUMBER_Y * CELL_SIZE
        for x in range(0, WINDOW_WIDTH + 1, CELL_SIZE):
            pygame.draw.line(screen, COLORS['GRID'], (x, 0), (x, game_h))
        for y in range(0, game_h + 1, CELL_SIZE):
            pygame.draw.line(screen, COLORS['GRID'], (0, y), (WINDOW_WIDTH, y))
        
        pygame.draw.rect(screen, COLORS['BORDER'],
                        pygame.Rect(0, 0, WINDOW_WIDTH, game_h), 2)
    
    def _draw_decorative_snake(self, screen):
        """绘制装饰性蛇形图案"""
        # 左上角
        for i in range(8):
            t = self.frame * 0.05 + i * 0.5
            x = 50 + i * 15 + math.sin(t) * 10
            y = 80 + math.cos(t) * 20
            size = 12 - i * 0.5
            alpha = 255 - i * 25
            color = (*COLORS['SNAKE_BODY'][:3], alpha)
            surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (int(size), int(size)), int(size))
            screen.blit(surf, (int(x - size), int(y - size)))
        
        # 右下角
        for i in range(8):
            t = self.frame * 0.05 + i * 0.5 + math.pi
            x = WINDOW_WIDTH - 50 - i * 15 + math.sin(t) * 10
            y = 620 - 80 + math.cos(t) * 20
            size = 12 - i * 0.5
            alpha = 255 - i * 25
            color = (*COLORS['RED_SNAKE_BODY'][:3], alpha)
            surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (int(size), int(size)), int(size))
            screen.blit(surf, (int(x - size), int(y - size)))
