"""
碰撞检测处理器
"""
import math
from ..config import CELL_SIZE


class CollisionHandler:
    """碰撞检测处理器"""
    
    def __init__(self, game_state):
        self.state = game_state
    
    def check_all(self, snake, food, bomb, red_snake, yellow_snake, blue_food, exp_balls, 
                  on_eat_food, on_eat_blue_food, on_eat_exp, on_game_over):
        """检查所有碰撞"""
        # 吃食物
        if self._check_food_collision(snake, food):
            on_eat_food()
        
        # 吃蓝色食物（无敌道具）
        if blue_food and blue_food.active:
            if self._check_blue_food_collision(snake, blue_food):
                on_eat_blue_food()
        
        # 无敌状态下忽略所有致命碰撞
        if self.state.is_invincible:
            # 经验球仍然可以吃
            self._check_exp_balls(snake, exp_balls, on_eat_exp)
            return
        
        # 撞墙或撞自己（非新手模式）
        if self.state.difficulty == 0:
            # 新手模式：检测黄蛇碰撞
            if yellow_snake and yellow_snake.alive:
                if yellow_snake.check_collision_with_player(snake.smooth_body):
                    on_game_over()
                    return
                # 检测玩家蛇头是否碰到黄蛇身体，黄蛇死亡
                if self._check_player_hit_yellow_snake(snake, yellow_snake):
                    yellow_snake.alive = False
                    return
        else:
            if snake.check_wall_collision() or snake.check_self_collision():
                on_game_over()
                return
        
        # 炸弹相关（新手模式跳过）
        if self.state.difficulty != 0 and bomb and bomb.active:
            if self._check_bomb_collision(snake, bomb, on_game_over):
                return
        
        # 红蛇相关（新手模式跳过）
        if self.state.difficulty != 0 and red_snake and red_snake.alive:
            if snake.body[0] in red_snake.body:
                on_game_over()
                return
        
        # 经验球
        self._check_exp_balls(snake, exp_balls, on_eat_exp)
    
    def _check_food_collision(self, snake, food):
        """检查食物碰撞"""
        if self.state.difficulty == 0:
            # 新手模式：像素级碰撞
            if snake.smooth_body:
                head_x, head_y = snake.smooth_body[0]
                food_x = food.pos.x * CELL_SIZE + CELL_SIZE // 2
                food_y = food.pos.y * CELL_SIZE + CELL_SIZE // 2
                dist = ((head_x - food_x) ** 2 + (head_y - food_y) ** 2) ** 0.5
                return dist < CELL_SIZE
        else:
            return snake.check_collision_with(food.pos)
        return False
    
    def _check_blue_food_collision(self, snake, blue_food):
        """检查蓝色食物碰撞"""
        if self.state.difficulty == 0:
            # 新手模式：像素级碰撞
            if snake.smooth_body:
                head_x, head_y = snake.smooth_body[0]
                food_x = blue_food.pos.x * CELL_SIZE + CELL_SIZE // 2
                food_y = blue_food.pos.y * CELL_SIZE + CELL_SIZE // 2
                dist = ((head_x - food_x) ** 2 + (head_y - food_y) ** 2) ** 0.5
                return dist < CELL_SIZE
        else:
            return snake.check_collision_with(blue_food.pos)
        return False
    
    def _check_bomb_collision(self, snake, bomb, on_game_over):
        """检查炸弹碰撞"""
        # 直接碰到炸弹
        if snake.check_collision_with(bomb.pos):
            on_game_over()
            return True
        # 被爆炸波及
        if bomb.exploding:
            explosion_range = bomb.get_explosion_range()
            if snake.body[0] in explosion_range:
                on_game_over()
                return True
        return False
    
    def _check_player_hit_yellow_snake(self, snake, yellow_snake):
        """检测玩家蛇头是否碰到黄蛇（包括头部和身体）"""
        if not snake.smooth_body or not yellow_snake.smooth_body:
            return False
        
        player_head = snake.smooth_body[0]
        
        # 遍历黄蛇所有部分（包括头部），检测碰撞
        for seg in yellow_snake.smooth_body:
            dx = player_head[0] - seg[0]
            dy = player_head[1] - seg[1]
            dist = (dx * dx + dy * dy) ** 0.5
            if dist < CELL_SIZE:
                return True
        return False
    
    def _check_exp_balls(self, snake, exp_balls, on_eat_exp):
        """检查经验球碰撞"""
        for ball in exp_balls[:]:
            if self.state.difficulty == 0:
                # 新手模式：像素级碰撞
                if snake.smooth_body:
                    head_x, head_y = snake.smooth_body[0]
                    ball_x = ball.pos.x * CELL_SIZE + CELL_SIZE // 2
                    ball_y = ball.pos.y * CELL_SIZE + CELL_SIZE // 2
                    dist = ((head_x - ball_x) ** 2 + (head_y - ball_y) ** 2) ** 0.5
                    if dist < CELL_SIZE:
                        on_eat_exp(ball)
            else:
                if snake.check_collision_with(ball.pos):
                    on_eat_exp(ball)
