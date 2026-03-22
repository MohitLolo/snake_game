"""
游戏画面渲染器
负责游戏主体画面的渲染
"""
import pygame
from .base import BaseRenderer
from ..config import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, CELL_SIZE, CELL_NUMBER_Y


class GameRenderer(BaseRenderer):
    """游戏画面渲染器"""
    
    def draw(self, screen, snake, food, spawner, is_invincible=False):
        """绘制游戏画面"""
        self._draw_background(screen)
        self._draw_entities(screen, snake, food, spawner, is_invincible)
    
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
    
    def _draw_entities(self, screen, snake, food, spawner, is_invincible=False):
        """绘制游戏实体"""
        # 食物
        food.draw(screen)
        
        # 蓝色食物（无敌道具）
        if spawner.blue_food and spawner.blue_food.active:
            spawner.blue_food.draw(screen)
        
        # 炸弹
        if spawner.bomb:
            spawner.bomb.draw(screen)
        
        # 经验球
        for ball in spawner.exp_balls:
            ball.draw(screen)
        
        # 红蛇（无敌状态下不绘制）
        if spawner.red_snake and spawner.red_snake.alive and not is_invincible:
            spawner.red_snake.draw(screen)
        
        # 黄蛇（无敌状态下不绘制）
        if spawner.yellow_snake and spawner.yellow_snake.alive and not is_invincible:
            spawner.yellow_snake.draw(screen)
        
        # 玩家蛇
        snake.draw(screen)
    
    def draw_flashbang(self, screen, is_active):
        """绘制闪光弹效果"""
        if not is_active:
            return
        
        flash_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        flash_surf.fill((255, 255, 255, 160))
        screen.blit(flash_surf, (0, 0))
