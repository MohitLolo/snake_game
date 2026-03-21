"""
游戏核心逻辑模块
"""
import pygame
from .config import (
    SPEED_MAP, BOMB_CONFIG, COLORS,
    DIFFICULTY_LABELS, DIFFICULTY_COLORS,
    WINDOW_WIDTH, CELL_SIZE, CELL_NUMBER_Y
)
from .entities import Snake, Food, Bomb
from .managers import FontManager


class Game:
    """游戏主类 - 协调所有游戏逻辑"""
    
    def __init__(self):
        # 游戏实体
        self.snake = Snake()
        self.food = Food()
        self.bomb = None
        
        # 游戏状态
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.paused = False
        self.difficulty = 1
        self.speed = SPEED_MAP[1]
        
        # 炸弹计时器
        self._bomb_timer = 0
        
        # 动画帧计数
        self._frame = 0
        
        # 字体管理器
        self.fonts = FontManager()
        
        # 音频管理器（外部注入）
        self.audio = None
        
        # 初始化
        self._init_level()
    
    def _init_level(self):
        """初始化关卡"""
        self.food.spawn(self.snake.body)
        self.fonts.load()
    
    def update(self):
        """更新游戏状态"""
        if self.game_over or self.paused:
            return
        
        self.snake.move()
        self._check_collisions()
        self._update_bomb()
        self._update_animations()
        self._frame += 1
    
    def _check_collisions(self):
        """检查所有碰撞"""
        # 吃食物
        if self.snake.check_collision_with(self.food.pos):
            self.snake.grow()
            self.score += 1
            self.high_score = max(self.high_score, self.score)
            self.food.spawn(self.snake.body)
            if self.audio:
                self.audio.play_eat_sound()
        
        # 撞墙或撞自己
        if self.snake.check_wall_collision() or self.snake.check_self_collision():
            self._trigger_game_over()
            return
        
        # 炸弹相关
        if self.bomb and self.bomb.active:
            # 直接碰到炸弹
            if self.snake.check_collision_with(self.bomb.pos):
                self._trigger_game_over()
                return
            # 被爆炸波及
            if self.bomb.exploding:
                explosion_range = self.bomb.get_explosion_range()
                if self.snake.body[0] in explosion_range:
                    self._trigger_game_over()
                    return
    
    def _update_bomb(self):
        """更新炸弹逻辑"""
        # 更新现有炸弹
        if self.bomb:
            alive = self.bomb.update()
            if not alive:
                self.bomb = None
        
        # 生成新炸弹
        if self.bomb is None:
            self._bomb_timer += 1
            if self._bomb_timer >= BOMB_CONFIG['interval']:
                self._bomb_timer = 0
                self.bomb = Bomb()
                exclude = list(self.snake.body) + [self.food.pos]
                self.bomb.spawn(exclude)
    
    def _update_animations(self):
        """更新动画"""
        self.food.update()
    
    def _trigger_game_over(self):
        """触发游戏结束"""
        self.game_over = True
        if self.audio:
            self.audio.stop_bg_music()
            self.audio.play_game_over_sound()
    
    def set_direction(self, direction):
        """设置蛇的方向"""
        if not self.game_over and not self.paused:
            self.snake.queue_direction(direction)
    
    def toggle_pause(self):
        """切换暂停状态"""
        if not self.game_over:
            self.paused = not self.paused
            if self.audio:
                if self.paused:
                    self.audio.pause_bg_music()
                else:
                    self.audio.resume_bg_music()
    
    def set_difficulty(self, level):
        """设置难度"""
        if 1 <= level <= 3:
            self.difficulty = level
            self.speed = SPEED_MAP[level]
    
    def restart(self):
        """重新开始"""
        self.snake = Snake()
        self.food.spawn(self.snake.body)
        self.bomb = None
        self._bomb_timer = 0
        self.score = 0
        self.game_over = False
        self.paused = False
    
    # ========== 绘制方法 ==========
    
    def draw(self, screen):
        """绘制游戏画面"""
        self._draw_background(screen)
        self._draw_entities(screen)
        self._draw_ui(screen)
        
        if self.game_over:
            self._draw_game_over(screen)
        elif self.paused:
            self._draw_pause(screen)
    
    def _draw_background(self, screen):
        """绘制背景"""
        screen.fill(COLORS['BG'])
        
        # 网格
        game_h = CELL_NUMBER_Y * CELL_SIZE
        for x in range(0, WINDOW_WIDTH + 1, CELL_SIZE):
            pygame.draw.line(screen, COLORS['GRID'], (x, 0), (x, game_h))
        for y in range(0, game_h + 1, CELL_SIZE):
            pygame.draw.line(screen, COLORS['GRID'], (0, y), (WINDOW_WIDTH, y))
        
        # 边框
        pygame.draw.rect(screen, COLORS['BORDER'],
                        pygame.Rect(0, 0, WINDOW_WIDTH, game_h), 2)
    
    def _draw_entities(self, screen):
        """绘制游戏实体"""
        self.food.draw(screen)
        if self.bomb:
            self.bomb.draw(screen)
        self.snake.draw(screen)
    
    def _draw_ui(self, screen):
        """绘制UI"""
        bar_y = CELL_NUMBER_Y * CELL_SIZE
        bar_rect = pygame.Rect(0, bar_y, WINDOW_WIDTH, 60)
        pygame.draw.rect(screen, COLORS['PANEL'], bar_rect)
        pygame.draw.line(screen, COLORS['BORDER'], (0, bar_y), (WINDOW_WIDTH, bar_y), 2)
        
        cy = bar_y + 30
        f = self.fonts
        
        # 分数
        self._draw_text(screen, f"分数  {self.score:04d}",
                       f.normal_font, COLORS['ACCENT'], (160, cy))
        # 最高分
        self._draw_text(screen, f"最高  {self.high_score:04d}",
                       f.normal_font, COLORS['DIM'], (380, cy))
        # 难度
        diff_text = f"难度  {DIFFICULTY_LABELS[self.difficulty]}"
        self._draw_text(screen, diff_text, f.normal_font,
                       DIFFICULTY_COLORS[self.difficulty], (620, cy))
    
    def draw_start_screen(self, screen):
        """绘制开始界面"""
        self._draw_background(screen)
        
        cx, cy = WINDOW_WIDTH // 2, 620 // 2
        f = self.fonts
        
        # 面板
        panel = pygame.Rect(cx - 260, cy - 180, 520, 340)
        self._draw_panel(screen, panel)
        
        # 标题
        self._draw_text(screen, "贪 吃 蛇", f.title_font, COLORS['TITLE'], (cx, cy - 120))
        
        # 分隔线
        pygame.draw.line(screen, COLORS['BORDER'], (cx - 200, cy - 68), (cx + 200, cy - 68), 1)
        
        # 操作提示
        hints = [
            ("空格键", "开始游戏"),
            ("方向键", "控制移动"),
            ("空格键", "暂停 / 继续"),
        ]
        for i, (key, desc) in enumerate(hints):
            y = cy - 40 + i * 40
            self._draw_text(screen, key, f.small_font, COLORS['ACCENT'], (cx - 70, y))
            self._draw_text(screen, desc, f.small_font, COLORS['TEXT'], (cx + 50, y))
        
        # 难度选择
        pygame.draw.line(screen, COLORS['BORDER'], (cx - 200, cy + 82), (cx + 200, cy + 82), 1)
        self._draw_text(screen, "1 简单   2 普通   3 困难",
                       f.small_font, COLORS['DIM'], (cx, cy + 110))
        
        cur_text = f"当前难度：{DIFFICULTY_LABELS[self.difficulty]}"
        self._draw_text(screen, cur_text, f.small_font,
                       DIFFICULTY_COLORS[self.difficulty], (cx, cy + 140))
    
    def _draw_game_over(self, screen):
        """绘制游戏结束画面"""
        cx = WINDOW_WIDTH // 2
        cy = CELL_NUMBER_Y * CELL_SIZE // 2
        f = self.fonts
        
        # 遮罩
        overlay = pygame.Surface((WINDOW_WIDTH, CELL_NUMBER_Y * CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        # 面板
        panel = pygame.Rect(cx - 220, cy - 130, 440, 270)
        self._draw_panel(screen, panel, alpha=240)
        
        self._draw_text(screen, "游戏结束", f.title_font, COLORS['WARN'], (cx, cy - 75))
        
        pygame.draw.line(screen, COLORS['BORDER'], (cx - 170, cy - 28), (cx + 170, cy - 28), 1)
        
        self._draw_text(screen, f"本局得分    {self.score}",
                       f.normal_font, COLORS['TEXT'], (cx, cy + 10))
        self._draw_text(screen, f"最高记录    {self.high_score}",
                       f.normal_font, COLORS['ACCENT'], (cx, cy + 55))
        
        pygame.draw.line(screen, COLORS['BORDER'], (cx - 170, cy + 88), (cx + 170, cy + 88), 1)
        self._draw_text(screen, "按  空格键  重新开始",
                       f.small_font, COLORS['DIM'], (cx, cy + 112))
    
    def _draw_pause(self, screen):
        """绘制暂停画面"""
        cx = WINDOW_WIDTH // 2
        cy = CELL_NUMBER_Y * CELL_SIZE // 2
        f = self.fonts
        
        overlay = pygame.Surface((WINDOW_WIDTH, CELL_NUMBER_Y * CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))
        
        panel = pygame.Rect(cx - 180, cy - 80, 360, 160)
        self._draw_panel(screen, panel)
        
        self._draw_text(screen, "已 暂 停", f.title_font, COLORS['ACCENT'], (cx, cy - 25))
        self._draw_text(screen, "按  空格键  继续",
                       f.small_font, COLORS['DIM'], (cx, cy + 45))
    
    def _draw_text(self, screen, text, font, color, center):
        """绘制文字"""
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=center)
        screen.blit(surf, rect)
    
    def _draw_panel(self, screen, rect, alpha=210, radius=12):
        """绘制半透明面板"""
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*COLORS['PANEL'], alpha), surf.get_rect(), border_radius=radius)
        pygame.draw.rect(surf, (*COLORS['BORDER'], 180), surf.get_rect(), 2, border_radius=radius)
        screen.blit(surf, rect.topleft)
