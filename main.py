"""
贪吃蛇游戏主入口
重构后的结构化版本
"""
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

import pygame
import sys
import ctypes

# 添加 src 到路径
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, SPEED_MAP, BEGINNER_CONFIG
from src.utils import Point
from src.game import Game
from src.managers import AudioManager


def disable_ime(hwnd):
    """禁用窗口 IME 输入法"""
    try:
        imm32 = ctypes.WinDLL('imm32')
        himc = imm32.ImmGetContext(hwnd)
        if himc:
            imm32.ImmAssociateContext(hwnd, 0)
            imm32.ImmReleaseContext(hwnd, himc)
    except Exception:
        pass


class GameApp:
    """游戏应用程序 - 负责游戏循环和事件处理"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("贪吃蛇")
        self.clock = pygame.time.Clock()
        
        # 初始化管理器
        self.audio = AudioManager()
        self.audio.init()
        
        # 初始化游戏
        self.game = Game()
        self.game.audio = self.audio
        
        # 游戏状态
        self.started = False
        self.current_speed = self.game.speed
        
        # 双击检测（新手模式加速）
        self._last_click_time = 0
        
        # 设置定时器
        self.SCREEN_UPDATE = pygame.USEREVENT
        pygame.time.set_timer(self.SCREEN_UPDATE, self.game.speed)
        
        # 方向映射
        self.DIR_MAP = {
            pygame.K_UP:    Point(0, -1),
            pygame.K_DOWN:  Point(0,  1),
            pygame.K_LEFT:  Point(-1, 0),
            pygame.K_RIGHT: Point(1,  0),
            pygame.K_w:     Point(0, -1),
            87:             Point(0, -1),  # 大写 W
            pygame.K_s:     Point(0,  1),
            83:             Point(0,  1),  # 大写 S
            pygame.K_a:     Point(-1, 0),
            65:             Point(-1, 0),  # 大写 A
            pygame.K_d:     Point(1,  0),
            68:             Point(1,  0),  # 大写 D
        }
        
        # 禁用 IME
        self._setup_ime()
    
    def _setup_ime(self):
        """设置输入法"""
        hwnd = pygame.display.get_wm_info().get('window', 0)
        if hwnd:
            disable_ime(hwnd)
    
    def run(self):
        """主游戏循环"""
        while True:
            self._handle_events()
            self._handle_input()
            self._update()
            self._render()
            self.clock.tick(FPS)
    
    def _update(self):
        """更新游戏状态"""
        # 更新音频（处理淡入淡出）
        self.audio.update()
        # 更新帧计数（用于动画）
        self.game._frame += 1
    
    def _handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == self.SCREEN_UPDATE:
                self.game.update()
            
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
            
            if event.type == pygame.MOUSEMOTION:
                # 新手模式：更新鼠标位置
                if self.started and self.game.difficulty == 0:
                    self.game.update_mouse_position(*event.pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 新手模式：双击加速
                if event.button == 1:  # 左键
                    self._handle_mouse_click()
    
    def _handle_keydown(self, key):
        """处理按键"""
        if not self.started:
            self._handle_start_screen_keys(key)
        else:
            self._handle_game_keys(key)
    
    def _handle_mouse_click(self):
        """处理鼠标点击（双击加速）"""
        if not self.started or self.game.difficulty != 0:
            return
        
        current_time = pygame.time.get_ticks()
        double_click_time = BEGINNER_CONFIG['double_click_time']
        
        # 检测双击
        if current_time - self._last_click_time < double_click_time:
            # 双击成功，触发加速
            self.game.trigger_boost()
            self._last_click_time = 0  # 重置，避免三击被识别为双击
        else:
            self._last_click_time = current_time
    
    def _handle_start_screen_keys(self, key):
        """处理开始界面按键"""
        if key == pygame.K_SPACE:
            self.started = True
            self.audio.play_bg_music()
        elif key in (pygame.K_0, pygame.K_KP0):
            self._set_difficulty(0)
        elif key in (pygame.K_1, pygame.K_KP1):
            self._set_difficulty(1)
        elif key in (pygame.K_2, pygame.K_KP2):
            self._set_difficulty(2)
        elif key in (pygame.K_3, pygame.K_KP3):
            self._set_difficulty(3)
        elif key in (pygame.K_LEFT, pygame.K_a, 65):  # 65 是大写 A
            # 左键：降低难度
            new_level = max(0, self.game.difficulty - 1)
            self._set_difficulty(new_level)
        elif key in (pygame.K_RIGHT, pygame.K_d, 68):  # 68 是大写 D
            # 右键：提高难度
            new_level = min(3, self.game.difficulty + 1)
            self._set_difficulty(new_level)
    
    def _handle_game_keys(self, key):
        """处理游戏按键"""
        if key in self.DIR_MAP:
            self.game.set_direction(self.DIR_MAP[key])
        elif key == pygame.K_SPACE:
            if self.game.game_over:
                self._restart_game()
            else:
                self.game.toggle_pause()
        elif key == pygame.K_ESCAPE:
            self._return_to_menu()
    
    def _handle_input(self):
        """处理持续按键（WASD加速）和新手模式鼠标跟随"""
        if not self.started or self.game.game_over or self.game.paused:
            return
        
        # 新手模式：每帧更新（跟随鼠标）
        if self.game.difficulty == 0:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.game.update_mouse_position(mouse_x, mouse_y)
            self.game.update()  # 新手模式每帧更新
            return
        
        keys = pygame.key.get_pressed()
        pressed_dir = None
        
        if keys[pygame.K_w] or keys[87] or keys[pygame.K_UP]:
            pressed_dir = Point(0, -1)
        elif keys[pygame.K_s] or keys[83] or keys[pygame.K_DOWN]:
            pressed_dir = Point(0, 1)
        elif keys[pygame.K_a] or keys[65] or keys[pygame.K_LEFT]:
            pressed_dir = Point(-1, 0)
        elif keys[pygame.K_d] or keys[68] or keys[pygame.K_RIGHT]:
            pressed_dir = Point(1, 0)
        
        if pressed_dir:
            self.game.set_direction(pressed_dir)
            self._handle_boost(pressed_dir)
        else:
            # 没有按键时恢复普通速度
            if self.current_speed != self.game.speed:
                pygame.time.set_timer(self.SCREEN_UPDATE, self.game.speed)
                self.current_speed = self.game.speed
    
    def _handle_boost(self, direction):
        """处理加速逻辑 - 只有按住同方向才加速"""
        cur = self.game.snake.direction
        is_same = (direction.x == cur.x and direction.y == cur.y)
        
        if is_same:
            # 同方向加速
            boost_speed = max(40, self.game.speed // 3)
            if self.current_speed != boost_speed:
                pygame.time.set_timer(self.SCREEN_UPDATE, boost_speed)
                self.current_speed = boost_speed
        else:
            # 不同方向恢复正常速度
            if self.current_speed != self.game.speed:
                pygame.time.set_timer(self.SCREEN_UPDATE, self.game.speed)
                self.current_speed = self.game.speed
    
    def _set_difficulty(self, level):
        """设置难度"""
        self.game.set_difficulty(level)
        pygame.time.set_timer(self.SCREEN_UPDATE, self.game.speed)
        self.current_speed = self.game.speed
    
    def _restart_game(self):
        """重新开始"""
        self.game.restart()
        pygame.time.set_timer(self.SCREEN_UPDATE, self.game.speed)
        self.current_speed = self.game.speed
        self.audio.play_bg_music()
    
    def _return_to_menu(self):
        """返回主菜单"""
        self.game.restart()
        self.started = False
        self.audio.stop_bg_music()
    
    def _render(self):
        """渲染画面"""
        if not self.started:
            self.game.draw_start_screen(self.screen)
        else:
            self.game.draw(self.screen)
        
        pygame.display.update()


def main():
    app = GameApp()
    app.run()


if __name__ == '__main__':
    main()
