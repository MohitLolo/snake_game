import pygame
import random
import os

# 游戏配置
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 620
CELL_SIZE = 20
CELL_NUMBER_X = WINDOW_WIDTH // CELL_SIZE       # 40
CELL_NUMBER_Y = (WINDOW_HEIGHT - 60) // CELL_SIZE  # 28  留出底部状态栏

# 颜色定义
BLACK        = (0,   0,   0)
WHITE        = (255, 255, 255)
BG_COLOR     = (15,  20,  30)    # 深蓝黑背景
GRID_COLOR   = (25,  32,  44)    # 网格线
PANEL_COLOR  = (20,  26,  38)    # 状态栏背景
BORDER_COLOR = (60,  80, 120)    # 边框

# 蛇
SNAKE_HEAD   = (50,  220,  80)
SNAKE_BODY   = (30,  160,  60)
SNAKE_DARK   = (10,   90,  30)
SNAKE_EYE    = (255, 255, 255)
SNAKE_PUPIL  = (0,     0,   0)

# 食物
FOOD_COLOR   = (255,  60,  80)
FOOD_SHINE   = (255, 160, 170)
FOOD_STEM    = (120,  60,  20)

# UI 文字
TITLE_COLOR  = (80,  200, 130)
TEXT_COLOR   = (200, 210, 230)
DIM_COLOR    = (100, 115, 140)
ACCENT       = (80,  180, 255)
WARN_COLOR   = (255, 120,  60)

# 难度对应速度(ms)
SPEED_MAP = {1: 200, 2: 140, 3: 90}


class Point:
    """表示游戏中的一个坐标点"""
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


class Snake:
    """贪吃蛇"""
    def __init__(self):
        self.body = [Point(10, 14), Point(9, 14), Point(8, 14)]
        self.direction = Point(1, 0)
        self.new_block = False
        self._dir_queue = []   # 方向输入队列，防止高速操作丢指令

    # ── 移动 ─────────────────────────────────────────────
    def move_snake(self):
        # 消费队列中的下一个方向
        if self._dir_queue:
            self.direction = self._dir_queue.pop(0)

        head = self.body[0]
        new_head = Point(head.x + self.direction.x, head.y + self.direction.y)
        if self.new_block:
            self.body.insert(0, new_head)
            self.new_block = False
        else:
            self.body = [new_head] + self.body[:-1]

    def add_block(self):
        self.new_block = True

    def queue_direction(self, direction):
        """将新方向加入队列（过滤反向和重复）"""
        last = self._dir_queue[-1] if self._dir_queue else self.direction
        if (direction.x * -1 == last.x and direction.y * -1 == last.y):
            return   # 反向，忽略
        if direction.x == last.x and direction.y == last.y:
            return   # 重复，忽略
        if len(self._dir_queue) < 2:
            self._dir_queue.append(direction)

    # ── 碰撞检测 ──────────────────────────────────────────
    def check_wall_collision(self):
        h = self.body[0]
        return not (0 <= h.x < CELL_NUMBER_X and 0 <= h.y < CELL_NUMBER_Y)

    def check_self_collision(self):
        return self.body[0] in self.body[1:]

    # ── 绘制 ──────────────────────────────────────────────
    def draw_snake(self, screen):
        total = len(self.body)
        for i, block in enumerate(self.body):
            x = block.x * CELL_SIZE
            y = block.y * CELL_SIZE
            rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)

            if i == 0:
                # 蛇头：亮绿色圆角矩形
                pygame.draw.rect(screen, SNAKE_HEAD, rect, border_radius=6)
                self._draw_eyes(screen, rect)
            else:
                # 蛇身：随位置渐暗
                ratio = max(0.35, 1 - i / total)
                color = (
                    int(SNAKE_BODY[0] * ratio),
                    int(SNAKE_BODY[1] * ratio),
                    int(SNAKE_BODY[2] * ratio),
                )
                pygame.draw.rect(screen, color, rect, border_radius=4)
                # 身体高光条
                highlight = pygame.Rect(x + 3, y + 3, CELL_SIZE - 8, 3)
                hl_color = (
                    min(255, color[0] + 40),
                    min(255, color[1] + 40),
                    min(255, color[2] + 40),
                )
                pygame.draw.rect(screen, hl_color, highlight, border_radius=2)

    def _draw_eyes(self, screen, head_rect):
        d = self.direction
        es = max(2, CELL_SIZE // 5)
        cx, cy = head_rect.centerx, head_rect.centery
        offset = CELL_SIZE // 4

        if d.x == 1:    # 右
            p1 = (cx + offset, cy - offset)
            p2 = (cx + offset, cy + offset)
        elif d.x == -1: # 左
            p1 = (cx - offset, cy - offset)
            p2 = (cx - offset, cy + offset)
        elif d.y == -1: # 上
            p1 = (cx - offset, cy - offset)
            p2 = (cx + offset, cy - offset)
        else:           # 下
            p1 = (cx - offset, cy + offset)
            p2 = (cx + offset, cy + offset)

        for p in (p1, p2):
            pygame.draw.circle(screen, SNAKE_EYE, p, es)
            pygame.draw.circle(screen, SNAKE_PUPIL, p, max(1, es // 2))


class Food:
    """食物"""
    def __init__(self):
        self.pos = Point(0, 0)
        self._glow_tick = 0   # 用于发光动画

    def randomize(self, exclude=None):
        """随机位置，排除 exclude 列表中的点"""
        exclude = exclude or []
        while True:
            p = Point(random.randint(0, CELL_NUMBER_X - 1),
                      random.randint(0, CELL_NUMBER_Y - 1))
            if p not in exclude:
                self.pos = p
                break

    def draw_food(self, screen):
        self._glow_tick = (self._glow_tick + 1) % 60
        glow_r = int(3 + 2 * abs(30 - self._glow_tick) / 30)  # 3~5 脉动

        cx = self.pos.x * CELL_SIZE + CELL_SIZE // 2
        cy = self.pos.y * CELL_SIZE + CELL_SIZE // 2
        r  = CELL_SIZE // 2 - 1

        # 光晕
        glow_surf = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*FOOD_COLOR, 40),
                           (CELL_SIZE, CELL_SIZE), r + glow_r + 3)
        screen.blit(glow_surf, (cx - CELL_SIZE, cy - CELL_SIZE))

        # 苹果主体
        pygame.draw.circle(screen, FOOD_COLOR, (cx, cy), r)
        # 高光
        pygame.draw.circle(screen, FOOD_SHINE,
                           (cx - r // 3, cy - r // 3), max(2, r // 3))
        # 果梗
        stem_rect = pygame.Rect(cx - 1, cy - r - 3, 3, 5)
        pygame.draw.rect(screen, FOOD_STEM, stem_rect, border_radius=1)


class Game:
    """游戏主类"""
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.food.randomize(self.snake.body)
        self.score = 0
        self.high_score = 0
        self.font = None
        self.font_sm = None
        self.title_font = None
        self.game_over_flag = False
        self.paused = False
        self.difficulty = 1
        self.speed = SPEED_MAP[1]
        self._frame = 0   # 全局帧计数，用于动画

    # ── 初始化 ────────────────────────────────────────────
    def init_fonts(self):
        chinese_fonts = ['msyh.ttc', 'simhei.ttf', 'simsun.ttc', 'simkai.ttf']
        font_paths = ['C:/Windows/Fonts/', 'C:/Windows/System32/Fonts/']

        for name in chinese_fonts:
            for path in font_paths:
                full = os.path.join(path, name)
                if os.path.exists(full):
                    try:
                        self.title_font = pygame.font.Font(full, 64)
                        self.font       = pygame.font.Font(full, 32)
                        self.font_sm    = pygame.font.Font(full, 22)
                        return
                    except Exception:
                        continue

        self.title_font = pygame.font.Font(None, 72)
        self.font       = pygame.font.Font(None, 36)
        self.font_sm    = pygame.font.Font(None, 26)

    # ── 更新 ──────────────────────────────────────────────
    def update(self):
        if self.game_over_flag or self.paused:
            return
        self.snake.move_snake()
        self._check_eat()
        self._check_fail()
        self._frame += 1

    def _check_eat(self):
        if self.snake.body[0] == self.food.pos:
            self.snake.add_block()
            self.score += 1
            if self.score > self.high_score:
                self.high_score = self.score
            self.food.randomize(self.snake.body)

    def _check_fail(self):
        if self.snake.check_wall_collision() or self.snake.check_self_collision():
            self.game_over_flag = True

    # ── 控制 ──────────────────────────────────────────────
    def update_direction(self, direction):
        if not self.game_over_flag and not self.paused:
            self.snake.queue_direction(direction)

    def toggle_pause(self):
        if not self.game_over_flag:
            self.paused = not self.paused

    def set_difficulty(self, level):
        if 1 <= level <= 3:
            self.difficulty = level
            self.speed = SPEED_MAP[level]

    def restart(self):
        self.snake = Snake()
        self.food.randomize(self.snake.body)
        self.score = 0
        self.game_over_flag = False
        self.paused = False

    # ── 绘制工具 ──────────────────────────────────────────
    def _draw_text(self, screen, text, font, color, center):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=center)
        screen.blit(surf, rect)

    def _draw_panel(self, screen, rect, alpha=210, radius=12):
        """半透明圆角面板"""
        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*PANEL_COLOR, alpha), surf.get_rect(), border_radius=radius)
        pygame.draw.rect(surf, (*BORDER_COLOR, 180), surf.get_rect(), 2, border_radius=radius)
        screen.blit(surf, rect.topleft)

    # ── 主绘制入口 ─────────────────────────────────────────
    def draw_elements(self, screen):
        # 背景 + 网格
        screen.fill(BG_COLOR)
        self._draw_grid(screen)

        self.food.draw_food(screen)
        self.snake.draw_snake(screen)
        self._draw_status_bar(screen)

        if self.game_over_flag:
            self._draw_game_over(screen)
        elif self.paused:
            self._draw_pause(screen)

    def _draw_grid(self, screen):
        game_h = CELL_NUMBER_Y * CELL_SIZE
        for x in range(0, WINDOW_WIDTH + 1, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, game_h))
        for y in range(0, game_h + 1, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))
        # 游戏区域边框
        pygame.draw.rect(screen, BORDER_COLOR,
                         pygame.Rect(0, 0, WINDOW_WIDTH, game_h), 2)

    def _draw_status_bar(self, screen):
        bar_y = CELL_NUMBER_Y * CELL_SIZE
        bar_rect = pygame.Rect(0, bar_y, WINDOW_WIDTH, 60)
        pygame.draw.rect(screen, PANEL_COLOR, bar_rect)
        pygame.draw.line(screen, BORDER_COLOR, (0, bar_y), (WINDOW_WIDTH, bar_y), 2)

        cy = bar_y + 30

        # 分数
        self._draw_text(screen, f"分数  {self.score:04d}",
                        self.font, ACCENT, (160, cy))
        # 最高分
        self._draw_text(screen, f"最高  {self.high_score:04d}",
                        self.font, DIM_COLOR, (380, cy))
        # 难度
        diff_labels = {1: "简单", 2: "普通", 3: "困难"}
        diff_colors = {1: (80, 200, 130), 2: (255, 180, 50), 3: (255, 80, 80)}
        self._draw_text(screen,
                        f"难度  {diff_labels[self.difficulty]}",
                        self.font, diff_colors[self.difficulty], (620, cy))

    def draw_start_screen(self, screen):
        if self.font is None:
            self.init_fonts()

        screen.fill(BG_COLOR)
        self._draw_grid(screen)

        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2

        # 标题面板
        panel = pygame.Rect(cx - 260, cy - 180, 520, 340)
        self._draw_panel(screen, panel, alpha=230, radius=18)

        # 标题
        self._draw_text(screen, "贪 吃 蛇", self.title_font, TITLE_COLOR, (cx, cy - 120))

        # 分隔线
        pygame.draw.line(screen, BORDER_COLOR, (cx - 200, cy - 68), (cx + 200, cy - 68), 1)

        # 操作提示
        hints = [
            ("空格键", "开始游戏"),
            ("方向键", "控制移动"),
            ("空格键", "暂停 / 继续"),
        ]
        for i, (key, desc) in enumerate(hints):
            y = cy - 40 + i * 40
            self._draw_text(screen, key,  self.font_sm, ACCENT,      (cx - 70, y))
            self._draw_text(screen, desc, self.font_sm, TEXT_COLOR,   (cx + 50, y))

        # 分隔线
        pygame.draw.line(screen, BORDER_COLOR, (cx - 200, cy + 82), (cx + 200, cy + 82), 1)

        # 难度选择
        self._draw_text(screen, "1 简单   2 普通   3 困难",
                        self.font_sm, DIM_COLOR, (cx, cy + 110))

        diff_labels = {1: "简单", 2: "普通", 3: "困难"}
        diff_colors = {1: (80, 200, 130), 2: (255, 180, 50), 3: (255, 80, 80)}
        cur_text = f"当前难度：{diff_labels[self.difficulty]}"
        self._draw_text(screen, cur_text, self.font_sm,
                        diff_colors[self.difficulty], (cx, cy + 140))

    def _draw_game_over(self, screen):
        cx = WINDOW_WIDTH // 2
        cy = CELL_NUMBER_Y * CELL_SIZE // 2

        overlay = pygame.Surface((WINDOW_WIDTH, CELL_NUMBER_Y * CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(cx - 220, cy - 130, 440, 270)
        self._draw_panel(screen, panel, alpha=240, radius=16)

        self._draw_text(screen, "游戏结束", self.title_font, WARN_COLOR, (cx, cy - 75))

        pygame.draw.line(screen, BORDER_COLOR,
                         (cx - 170, cy - 28), (cx + 170, cy - 28), 1)

        self._draw_text(screen, f"本局得分    {self.score}",
                        self.font, TEXT_COLOR, (cx, cy + 10))
        self._draw_text(screen, f"最高记录    {self.high_score}",
                        self.font, ACCENT, (cx, cy + 55))

        pygame.draw.line(screen, BORDER_COLOR,
                         (cx - 170, cy + 88), (cx + 170, cy + 88), 1)

        self._draw_text(screen, "按  空格键  重新开始",
                        self.font_sm, DIM_COLOR, (cx, cy + 112))

    def _draw_pause(self, screen):
        cx = WINDOW_WIDTH // 2
        cy = CELL_NUMBER_Y * CELL_SIZE // 2

        overlay = pygame.Surface((WINDOW_WIDTH, CELL_NUMBER_Y * CELL_SIZE), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(cx - 180, cy - 80, 360, 160)
        self._draw_panel(screen, panel, alpha=230, radius=16)

        self._draw_text(screen, "已 暂 停", self.title_font, ACCENT, (cx, cy - 25))
        self._draw_text(screen, "按  空格键  继续",
                        self.font_sm, DIM_COLOR, (cx, cy + 45))
