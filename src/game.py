"""
游戏核心逻辑模块
"""
import pygame
from .config import (
    SPEED_MAP, BOMB_CONFIG, RED_SNAKE_CONFIG, COLORS,
    DIFFICULTY_LABELS, DIFFICULTY_COLORS,
    WINDOW_WIDTH, CELL_SIZE, CELL_NUMBER_Y
)
from .entities import Snake, Food, Bomb, RedSnake, ExpBall
from .managers import FontManager


class Game:
    """游戏主类 - 协调所有游戏逻辑"""
    
    def __init__(self):
        # 游戏实体
        self.snake = Snake()
        self.food = Food()
        self.bomb = None
        self.red_snake = None      # 红蛇
        self.exp_balls = []        # 经验球列表
        
        # 游戏状态
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.paused = False
        self.difficulty = 1
        self.speed = SPEED_MAP[1]
        
        # 计时器
        self._bomb_timer = 0
        self._red_snake_timer = 0  # 红蛇生成计时器
        
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
        self._update_red_snake()  # 更新红蛇
        self._update_exp_balls()  # 更新经验球
        self._update_animations()
    
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
        
        # 红蛇相关
        if self.red_snake and self.red_snake.alive:
            # 绿蛇碰到红蛇
            if self.snake.body[0] in self.red_snake.body:
                self._trigger_game_over()
                return
        
        # 经验球相关
        for ball in self.exp_balls[:]:
            if self.snake.check_collision_with(ball.pos):
                # 吃掉经验球，快速变长（增长3段）
                for _ in range(3):
                    self.snake.grow()
                self.exp_balls.remove(ball)
                self.score += 1
                if self.audio:
                    self.audio.play_eat_sound()
    
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
    
    def _update_red_snake(self):
        """更新红蛇逻辑"""
        # 更新现有红蛇
        if self.red_snake and self.red_snake.alive:
            alive = self.red_snake.update(self.snake.body)
            if not alive:
                # 红蛇死亡，生成经验球
                self.exp_balls.extend(self.red_snake.get_exp_balls())
                self.red_snake = None
        
        # 生成新红蛇
        if self.red_snake is None:
            self._red_snake_timer += 1
            if self._red_snake_timer >= RED_SNAKE_CONFIG['interval']:
                self._red_snake_timer = 0
                self.red_snake = RedSnake()
    
    def _update_exp_balls(self):
        """更新经验球"""
        for ball in self.exp_balls[:]:
            alive = ball.update()
            if not alive:
                self.exp_balls.remove(ball)
    
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
        self.red_snake = None
        self.exp_balls = []
        self._bomb_timer = 0
        self._red_snake_timer = 0
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
        # 绘制经验球
        for ball in self.exp_balls:
            ball.draw(screen)
        # 绘制红蛇
        if self.red_snake and self.red_snake.alive:
            self.red_snake.draw(screen)
        self.snake.draw(screen)
    
    def _draw_ui(self, screen):
        """绘制UI"""
        bar_y = CELL_NUMBER_Y * CELL_SIZE
        
        # 状态栏背景（渐变效果）
        bar_rect = pygame.Rect(0, bar_y, WINDOW_WIDTH, 60)
        pygame.draw.rect(screen, COLORS['PANEL'], bar_rect)
        
        # 顶部高光线
        pygame.draw.line(screen, COLORS['BORDER'], (0, bar_y), (WINDOW_WIDTH, bar_y), 2)
        
        # 底部装饰线
        pygame.draw.line(screen, COLORS['BORDER'][:3], (0, bar_y + 58), (WINDOW_WIDTH, bar_y + 58), 1)
        
        cy = bar_y + 30
        f = self.fonts
        
        # 分数区域（带图标效果）
        # 分数图标 - 小星星
        star_x = 80
        self._draw_mini_icon(screen, star_x, cy, 'star', COLORS['ACCENT'])
        self._draw_text(screen, f"{self.score:04d}",
                       f.normal_font, COLORS['ACCENT'], (160, cy))
        
        # 分隔符
        pygame.draw.line(screen, COLORS['BORDER'], (280, bar_y + 15), (280, bar_y + 45), 1)
        
        # 最高分区域
        crown_x = 320
        self._draw_mini_icon(screen, crown_x, cy, 'crown', COLORS['DIM'])
        self._draw_text(screen, f"{self.high_score:04d}",
                       f.normal_font, COLORS['DIM'], (380, cy))
        
        # 分隔符
        pygame.draw.line(screen, COLORS['BORDER'], (500, bar_y + 15), (500, bar_y + 45), 1)
        
        # 难度区域
        diff_color = DIFFICULTY_COLORS[self.difficulty]
        self._draw_mini_icon(screen, 540, cy, 'speed', diff_color)
        diff_text = DIFFICULTY_LABELS[self.difficulty]
        self._draw_text(screen, diff_text, f.normal_font, diff_color, (620, cy))
    
    def _draw_mini_icon(self, screen, x, y, icon_type, color):
        """绘制迷你图标"""
        if icon_type == 'star':
            # 小星星图标
            points = []
            for i in range(5):
                angle = i * 72 - 90
                import math
                px = x + 8 * math.cos(math.radians(angle))
                py = y + 8 * math.sin(math.radians(angle))
                points.append((px, py))
                angle2 = angle + 36
                px2 = x + 4 * math.cos(math.radians(angle2))
                py2 = y + 4 * math.sin(math.radians(angle2))
                points.append((px2, py2))
            pygame.draw.polygon(screen, color, points)
        elif icon_type == 'crown':
            # 小皇冠图标
            pygame.draw.polygon(screen, color, [
                (x - 8, y + 5), (x - 8, y - 3), (x - 4, y),
                (x, y - 6), (x + 4, y), (x + 8, y - 3), (x + 8, y + 5)
            ])
        elif icon_type == 'speed':
            # 速度图标（闪电）
            pygame.draw.polygon(screen, color, [
                (x + 4, y - 8), (x - 4, y + 1), (x + 1, y + 1),
                (x - 4, y + 8), (x + 6, y - 2), (x + 1, y - 2)
            ])
    
    def draw_start_screen(self, screen):
        """绘制开始界面"""
        self._draw_background(screen)
        
        cx, cy = WINDOW_WIDTH // 2, 620 // 2
        f = self.fonts
        
        # 装饰性蛇形图案（动态）
        self._draw_decorative_snake(screen, self._frame)
        
        # 主面板（带阴影效果）
        panel = pygame.Rect(cx - 280, cy - 200, 560, 380)
        # 阴影
        shadow_surf = pygame.Surface((panel.width + 10, panel.height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect(), border_radius=16)
        screen.blit(shadow_surf, (panel.x + 5, panel.y + 5))
        # 主面板
        self._draw_panel(screen, panel, radius=16)
        
        # 标题（带发光效果）
        glow_offset = abs(30 - (self._frame % 60)) / 30 * 0.3 + 0.7
        title_color = tuple(int(c * glow_offset) for c in COLORS['TITLE'])
        self._draw_text(screen, "贪 吃 蛇", f.title_font, title_color, (cx, cy - 130))
        
        # 标题下划线装饰
        pygame.draw.line(screen, COLORS['BORDER'], (cx - 150, cy - 85), (cx + 150, cy - 85), 2)
        pygame.draw.circle(screen, COLORS['ACCENT'], (cx - 150, cy - 85), 4)
        pygame.draw.circle(screen, COLORS['ACCENT'], (cx + 150, cy - 85), 4)
        
        # 操作提示区域
        hints = [
            ("空格键", "开始游戏", 'play'),
            ("方向键", "控制移动", 'arrow'),
            ("空格键", "暂停 / 继续", 'pause'),
        ]
        
        for i, (key, desc, icon) in enumerate(hints):
            y = cy - 50 + i * 48
            # 按键背景
            key_rect = pygame.Rect(cx - 200, y - 14, 100, 28)
            pygame.draw.rect(screen, (*COLORS['BG'], 150), key_rect, border_radius=6)
            pygame.draw.rect(screen, COLORS['BORDER'], key_rect, 1, border_radius=6)
            self._draw_text(screen, key, f.small_font, COLORS['ACCENT'], (cx - 150, y))
            self._draw_text(screen, desc, f.small_font, COLORS['TEXT'], (cx + 60, y))
        
        # 难度选择区域
        pygame.draw.line(screen, COLORS['BORDER'], (cx - 220, cy + 100), (cx + 220, cy + 100), 1)
        
        # 难度按钮
        difficulties = [(1, "简单", COLORS['TITLE']), (2, "普通", (255, 180, 50)), (3, "困难", (255, 80, 80))]
        btn_y = cy + 130
        for level, name, color in difficulties:
            btn_x = cx - 150 + (level - 1) * 150
            btn_rect = pygame.Rect(btn_x - 45, btn_y - 18, 90, 36)
            
            # 选中状态
            if self.difficulty == level:
                # 半透明背景
                bg_surf = pygame.Surface((btn_rect.width, btn_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(bg_surf, (*color, 60), bg_surf.get_rect(), border_radius=8)
                screen.blit(bg_surf, btn_rect.topleft)
                pygame.draw.rect(screen, color, btn_rect, 2, border_radius=8)
                text_color = color
            else:
                pygame.draw.rect(screen, COLORS['BG'], btn_rect, border_radius=8)
                pygame.draw.rect(screen, COLORS['DIM'], btn_rect, 1, border_radius=8)
                text_color = COLORS['DIM']
            
            self._draw_text(screen, f"{level} {name}", f.small_font, text_color, (btn_x, btn_y))
        
        # 左右箭头指示
        arrow_y = btn_y
        # 左箭头（如果当前难度 > 1）
        if self.difficulty > 1:
            left_x = cx - 150 - 60
            pygame.draw.polygon(screen, COLORS['DIM'], [
                (left_x - 8, arrow_y), (left_x + 8, arrow_y - 10), (left_x + 8, arrow_y + 10)
            ])
        # 右箭头（如果当前难度 < 3）
        if self.difficulty < 3:
            right_x = cx + 150 + 60
            pygame.draw.polygon(screen, COLORS['DIM'], [
                (right_x + 8, arrow_y), (right_x - 8, arrow_y - 10), (right_x - 8, arrow_y + 10)
            ])
        
        # 底部提示
        pulse = 0.5 + 0.5 * abs(30 - (self._frame % 60)) / 30
        hint_color = tuple(int(c * pulse) for c in COLORS['DIM'])
        self._draw_text(screen, "按数字键或方向键选择难度",
                       f.small_font, hint_color, (cx, cy + 175))
    
    def _draw_decorative_snake(self, screen, frame):
        """绘制装饰性蛇形图案"""
        import math
        # 左上角装饰蛇
        for i in range(8):
            t = frame * 0.05 + i * 0.5
            x = 50 + i * 15 + math.sin(t) * 10
            y = 80 + math.cos(t) * 20
            size = 12 - i * 0.5
            alpha = 255 - i * 25
            color = (*COLORS['SNAKE_BODY'][:3], alpha)
            surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (int(size), int(size)), int(size))
            screen.blit(surf, (int(x - size), int(y - size)))
        
        # 右下角装饰蛇
        for i in range(8):
            t = frame * 0.05 + i * 0.5 + math.pi
            x = WINDOW_WIDTH - 50 - i * 15 + math.sin(t) * 10
            y = 620 - 80 + math.cos(t) * 20
            size = 12 - i * 0.5
            alpha = 255 - i * 25
            color = (*COLORS['RED_SNAKE_BODY'][:3], alpha)
            surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (int(size), int(size)), int(size))
            screen.blit(surf, (int(x - size), int(y - size)))
    
    def _draw_game_over(self, screen):
        """绘制游戏结束画面"""
        import math
        cx = WINDOW_WIDTH // 2
        cy = CELL_NUMBER_Y * CELL_SIZE // 2
        f = self.fonts
        
        # 遮罩（带动画）
        overlay = pygame.Surface((WINDOW_WIDTH, CELL_NUMBER_Y * CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # 面板阴影
        panel = pygame.Rect(cx - 240, cy - 150, 480, 320)
        shadow_surf = pygame.Surface((panel.width + 20, panel.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), shadow_surf.get_rect(), border_radius=16)
        screen.blit(shadow_surf, (panel.x + 10, panel.y + 10))
        
        # 主面板
        self._draw_panel(screen, panel, alpha=245, radius=16)
        
        # 标题（带脉冲效果）
        pulse = 0.8 + 0.2 * abs(30 - (self._frame % 60)) / 30
        title_color = tuple(int(c * pulse) for c in COLORS['WARN'])
        self._draw_text(screen, "游戏结束", f.title_font, title_color, (cx, cy - 95))
        
        # 分隔线装饰
        pygame.draw.line(screen, COLORS['BORDER'], (cx - 180, cy - 45), (cx + 180, cy - 45), 2)
        pygame.draw.circle(screen, COLORS['WARN'], (cx - 180, cy - 45), 4)
        pygame.draw.circle(screen, COLORS['WARN'], (cx + 180, cy - 45), 4)
        
        # 得分区域
        # 本局得分
        score_y = cy + 5
        self._draw_text(screen, "本局得分", f.small_font, COLORS['DIM'], (cx - 60, score_y))
        # 大号分数显示
        score_text = f"{self.score}"
        score_color = COLORS['ACCENT'] if self.score >= self.high_score else COLORS['TEXT']
        self._draw_text(screen, score_text, f.title_font, score_color, (cx + 80, score_y))
        
        # 最高记录
        high_y = cy + 65
        self._draw_text(screen, "最高记录", f.small_font, COLORS['DIM'], (cx - 60, high_y))
        self._draw_text(screen, f"{self.high_score}", f.normal_font, COLORS['ACCENT'], (cx + 80, high_y))
        
        # 新纪录标识
        if self.score >= self.high_score and self.score > 0:
            new_y = cy + 105
            # 闪烁效果
            alpha = int(180 + 75 * math.sin(self._frame * 0.15))
            new_surf = f.normal_font.render("★ 新纪录 ★", True, COLORS['WARN'])
            new_rect = new_surf.get_rect(center=(cx, new_y))
            new_surf.set_alpha(alpha)
            screen.blit(new_surf, new_rect)
        
        # 重新开始提示按钮
        hint_y = cy + 150
        hint_rect = pygame.Rect(cx - 100, hint_y - 16, 200, 32)
        
        # 按钮背景（带闪烁）
        hint_alpha = int(100 + 50 * abs(30 - (self._frame % 60)) / 30)
        btn_surf = pygame.Surface((hint_rect.width, hint_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (*COLORS['ACCENT'], hint_alpha), btn_surf.get_rect(), border_radius=8)
        pygame.draw.rect(btn_surf, (*COLORS['ACCENT'], 150), btn_surf.get_rect(), 1, border_radius=8)
        screen.blit(btn_surf, hint_rect.topleft)
        
        # 按钮文字
        text_alpha = int(180 + 75 * abs(30 - (self._frame % 60)) / 30)
        hint_text = f.small_font.render("按 空格键 重新开始", True, COLORS['TEXT'])
        hint_text.set_alpha(text_alpha)
        text_rect = hint_text.get_rect(center=(cx, hint_y))
        screen.blit(hint_text, text_rect)
    
    def _draw_pause(self, screen):
        """绘制暂停画面"""
        cx = WINDOW_WIDTH // 2
        cy = CELL_NUMBER_Y * CELL_SIZE // 2
        f = self.fonts
        
        # 遮罩
        overlay = pygame.Surface((WINDOW_WIDTH, CELL_NUMBER_Y * CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        
        # 面板阴影
        panel = pygame.Rect(cx - 200, cy - 100, 400, 200)
        shadow_surf = pygame.Surface((panel.width + 15, panel.height + 15), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect(), border_radius=14)
        screen.blit(shadow_surf, (panel.x + 8, panel.y + 8))
        
        # 主面板
        self._draw_panel(screen, panel, radius=14)
        
        # 暂停图标（两个竖条）
        bar_color = COLORS['ACCENT']
        pygame.draw.rect(screen, bar_color, pygame.Rect(cx - 25, cy - 40, 15, 50), border_radius=4)
        pygame.draw.rect(screen, bar_color, pygame.Rect(cx + 10, cy - 40, 15, 50), border_radius=4)
        
        # 文字
        self._draw_text(screen, "已 暂 停", f.normal_font, COLORS['TEXT'], (cx, cy + 40))
        
        # 继续提示（带闪烁）
        hint_alpha = int(150 + 105 * abs(30 - (self._frame % 60)) / 30)
        hint_surf = f.small_font.render("按  空格键  继续", True, COLORS['DIM'])
        hint_rect = hint_surf.get_rect(center=(cx, cy + 75))
        hint_surf.set_alpha(hint_alpha)
        screen.blit(hint_surf, hint_rect)
    
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
