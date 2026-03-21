import pygame
import random
import os


class AudioManager:
    """音效管理器"""
    def __init__(self):
        self.enabled = False
        self.bg_music_path = None
        self.eat_sound_path = None
        self.game_over_sound_path = None
        self._check_assets()
    
    def _check_assets(self):
        """检查 assets 目录下的音乐文件"""
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        if not os.path.exists(assets_dir):
            return
        
        # 支持的音频格式
        exts = ['.mp3', '.wav', '.ogg']
        
        # 查找背景音乐
        for name in ['bgm', 'background', 'music', 'theme']:
            for ext in exts:
                path = os.path.join(assets_dir, f'{name}{ext}')
                if os.path.exists(path):
                    self.bg_music_path = path
                    break
            if self.bg_music_path:
                break
        
        # 查找吃食物音效
        for name in ['eat', 'eat_food', 'coin', 'pickup']:
            for ext in exts:
                path = os.path.join(assets_dir, f'{name}{ext}')
                if os.path.exists(path):
                    self.eat_sound_path = path
                    break
            if self.eat_sound_path:
                break
        
        # 查找游戏结束音效
        for name in ['gameover', 'game_over', 'die', 'fail']:
            for ext in exts:
                path = os.path.join(assets_dir, f'{name}{ext}')
                if os.path.exists(path):
                    self.game_over_sound_path = path
                    break
            if self.game_over_sound_path:
                break
    
    def init_audio(self):
        """初始化音频系统"""
        try:
            pygame.mixer.init()
            self.enabled = True
        except Exception:
            self.enabled = False
    
    def play_bg_music(self, loops=-1, volume=0.5):
        """播放背景音乐"""
        if not self.enabled or not self.bg_music_path:
            print(f"[Audio] 无法播放: enabled={self.enabled}, path={self.bg_music_path}")
            return
        try:
            pygame.mixer.music.load(self.bg_music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            print(f"[Audio] 开始播放背景音乐: {self.bg_music_path}")
        except Exception as e:
            print(f"[Audio] 播放失败: {e}")
            # 尝试用 Sound 方式播放
            try:
                sound = pygame.mixer.Sound(self.bg_music_path)
                sound.set_volume(volume)
                sound.play(loops)
                print("[Audio] 使用 Sound 方式播放成功")
            except Exception as e2:
                print(f"[Audio] Sound 方式也失败: {e2}")
    
    def stop_bg_music(self):
        """停止背景音乐"""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
    
    def pause_bg_music(self):
        """暂停背景音乐"""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass
    
    def resume_bg_music(self):
        """恢复背景音乐"""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.unpause()
        except Exception:
            pass
    
    def _generate_beep(self, frequency, duration, volume=0.5):
        """生成简单蜂鸣音效"""
        try:
            sample_rate = 44100
            samples = int(sample_rate * duration)
            buf = bytearray()
            import math
            for i in range(samples):
                t = i / sample_rate
                # 正弦波 + 衰减
                val = int(127 + 127 * math.sin(2 * math.pi * frequency * t) * (1 - i / samples))
                buf.append(val)
            sound = pygame.mixer.Sound(buffer=bytes(buf))
            sound.set_volume(volume)
            return sound
        except Exception:
            return None
    
    def play_eat_sound(self, volume=0.6, max_duration=500):
        """播放吃食物音效（使用文件或生成），限制最大播放时长(毫秒)"""
        if not self.enabled:
            return
        try:
            if self.eat_sound_path:
                sound = pygame.mixer.Sound(self.eat_sound_path)
                sound.set_volume(volume)
                # 限制播放时长
                channel = sound.play(maxtime=max_duration)
            else:
                # 生成清脆的"叮"声（短促）
                sound = self._generate_beep(880, 0.08, volume)
                if sound:
                    sound.play()
        except Exception:
            pass
    
    def play_game_over_sound(self, volume=0.7):
        """播放游戏结束音效（使用文件或生成）"""
        if not self.enabled:
            return
        try:
            if self.game_over_sound_path:
                sound = pygame.mixer.Sound(self.game_over_sound_path)
                sound.set_volume(volume)
                sound.play()
            else:
                # 生成低沉的"咚"声
                sound = self._generate_beep(220, 0.4, volume)
                if sound:
                    sound.play()
        except Exception:
            pass

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

# 炸弹
BOMB_COLOR   = (100,  60,  70)   # 炸弹主体（偏红）
BOMB_FUSE    = (255,  80,  40)   # 引线火焰
BOMB_SPARK   = (255, 200,  50)   # 火花

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


class Bomb:
    """炸弹 - 蛇碰到会游戏结束，一段时间后会自动消失"""
    def __init__(self, lifetime=180):  # 默认3秒消失 (60fps * 3)
        self.pos = Point(0, 0)
        self.lifetime = lifetime
        self._tick = 0
        self._glow_tick = 0
        self.active = True

    def randomize(self, exclude=None):
        """随机位置，排除 exclude 列表中的点"""
        exclude = exclude or []
        while True:
            p = Point(random.randint(0, CELL_NUMBER_X - 1),
                      random.randint(0, CELL_NUMBER_Y - 1))
            if p not in exclude:
                self.pos = p
                break

    def update(self):
        """更新炸弹状态，返回是否还存活"""
        if not self.active:
            return False
        self._tick += 1
        self._glow_tick = (self._glow_tick + 1) % 30
        if self._tick >= self.lifetime:
            self.active = False
            return False
        return True

    def draw_bomb(self, screen):
        """绘制炸弹"""
        if not self.active:
            return

        cx = self.pos.x * CELL_SIZE + CELL_SIZE // 2
        cy = self.pos.y * CELL_SIZE + CELL_SIZE // 2
        r = CELL_SIZE // 2 - 2

        # 倒计时闪烁效果（快消失时闪烁更快）
        remaining = self.lifetime - self._tick
        flash_speed = 10 if remaining > 60 else 5 if remaining > 30 else 2
        is_visible = (self._tick // flash_speed) % 2 == 0

        # 外圈警告光环（红色）
        if is_visible:
            glow_surf = pygame.Surface((CELL_SIZE * 3, CELL_SIZE * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 0, 0, 60),
                              (CELL_SIZE * 1.5, CELL_SIZE * 1.5), r + 6)
            screen.blit(glow_surf, (cx - CELL_SIZE * 1.5, cy - CELL_SIZE * 1.5))

        # 光晕
        glow_surf = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
        glow_r = int(4 + 3 * abs(15 - self._glow_tick) / 15)
        pygame.draw.circle(glow_surf, (*BOMB_FUSE, 50),
                          (CELL_SIZE, CELL_SIZE), r + glow_r + 2)
        screen.blit(glow_surf, (cx - CELL_SIZE, cy - CELL_SIZE))

        # 炸弹主体（圆形）- 深红色
        pygame.draw.circle(screen, BOMB_COLOR, (cx, cy), r)
        # 边框
        pygame.draw.circle(screen, (150, 80, 90), (cx, cy), r, 2)
        # 高光
        pygame.draw.circle(screen, (140, 100, 110),
                          (cx - r // 3, cy - r // 3), max(3, r // 3))

        # 引线
        fuse_end = (cx + r // 2 - 2, cy - r // 2 + 2)
        pygame.draw.line(screen, (180, 180, 180), (cx + 2, cy - 2), fuse_end, 2)

        # 火焰（闪烁）
        if is_visible:
            pygame.draw.circle(screen, BOMB_FUSE, fuse_end, 5)
            pygame.draw.circle(screen, BOMB_SPARK, fuse_end, 3)
            pygame.draw.circle(screen, (255, 255, 200), fuse_end, 1)


class Game:
    """游戏主类"""
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.food.randomize(self.snake.body)
        self.bomb = None           # 当前炸弹
        self.bomb_timer = 0        # 炸弹生成计时器
        self.bomb_interval = 180   # 每3秒生成一个炸弹 (60fps * 3)
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
        self._update_bomb()
        self._check_fail()
        self._frame += 1

    def _check_eat(self):
        if self.snake.body[0] == self.food.pos:
            self.snake.add_block()
            self.score += 1
            if self.score > self.high_score:
                self.high_score = self.score
            self.food.randomize(self.snake.body)
            # 播放吃食物音效
            if hasattr(self, 'audio') and self.audio:
                self.audio.play_eat_sound()

    def _update_bomb(self):
        """更新炸弹逻辑：生成、消失、碰撞检测"""
        # 更新现有炸弹
        if self.bomb:
            alive = self.bomb.update()
            if not alive:
                self.bomb = None

        # 生成新炸弹
        if self.bomb is None:
            self.bomb_timer += 1
            if self.bomb_timer >= self.bomb_interval:
                self.bomb_timer = 0
                self.bomb = Bomb()
                # 排除蛇身和食物位置
                exclude = list(self.snake.body) + [self.food.pos]
                self.bomb.randomize(exclude)

    def _check_bomb_collision(self):
        """检查是否碰到炸弹"""
        if self.bomb and self.bomb.active:
            if self.snake.body[0] == self.bomb.pos:
                return True
        return False

    def _check_fail(self):
        if self.snake.check_wall_collision() or self.snake.check_self_collision() or self._check_bomb_collision():
            self.game_over_flag = True
            # 播放游戏结束音效并停止背景音乐
            if hasattr(self, 'audio') and self.audio:
                self.audio.stop_bg_music()
                self.audio.play_game_over_sound()

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
        self.bomb = None
        self.bomb_timer = 0
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
        if self.bomb:
            self.bomb.draw_bomb(screen)
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
