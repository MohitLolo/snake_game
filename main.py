import pygame
import sys
import ctypes
from snake import Game, Point, WINDOW_WIDTH, WINDOW_HEIGHT, SPEED_MAP, AudioManager


def disable_ime(hwnd):
    """禁用窗口 IME 输入法，让 pygame 直接接收原始按键"""
    try:
        imm32 = ctypes.WinDLL('imm32')
        himc = imm32.ImmGetContext(hwnd)
        if himc:
            imm32.ImmAssociateContext(hwnd, 0)
            imm32.ImmReleaseContext(hwnd, himc)
    except Exception:
        pass


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("贪吃蛇")
    clock = pygame.time.Clock()

    # 初始化音效系统
    audio = AudioManager()
    audio.init_audio()

    game = Game()
    game.init_fonts()
    game.audio = audio  # 将音效管理器传递给游戏对象

    # 禁用 IME，确保 WASD 任意输入法状态下都能正常接收
    hwnd = pygame.display.get_wm_info().get('window', 0)
    if hwnd:
        disable_ime(hwnd)

    game_started = False
    current_timer_speed = game.speed  # 追踪当前计时器速度

    SCREEN_UPDATE = pygame.USEREVENT
    pygame.time.set_timer(SCREEN_UPDATE, game.speed)

    DIR_MAP = {
        pygame.K_UP:    Point(0, -1),
        pygame.K_DOWN:  Point(0,  1),
        pygame.K_LEFT:  Point(-1, 0),
        pygame.K_RIGHT: Point(1,  0),
        pygame.K_w:     Point(0, -1),  # 小写 w
        87:             Point(0, -1),  # 大写 W
        pygame.K_s:     Point(0,  1),  # 小写 s
        83:             Point(0,  1),  # 大写 S
        pygame.K_a:     Point(-1, 0),  # 小写 a
        65:             Point(-1, 0),  # 大写 A
        pygame.K_d:     Point(1,  0),  # 小写 d
        68:             Point(1,  0),  # 大写 D
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == SCREEN_UPDATE:
                game.update()

            if event.type == pygame.KEYDOWN:
                if not game_started:
                    # 开始界面：空格开始，1/2/3 切换难度
                    if event.key == pygame.K_SPACE:
                        game_started = True
                        audio.stop_bg_music()  # 先停止之前的音乐
                        audio.play_bg_music()  # 开始播放背景音乐
                    elif event.key in (pygame.K_1, pygame.K_KP1):
                        game.set_difficulty(1)
                        pygame.time.set_timer(SCREEN_UPDATE, game.speed)
                        current_timer_speed = game.speed
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        game.set_difficulty(2)
                        pygame.time.set_timer(SCREEN_UPDATE, game.speed)
                        current_timer_speed = game.speed
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        game.set_difficulty(3)
                        pygame.time.set_timer(SCREEN_UPDATE, game.speed)
                        current_timer_speed = game.speed
                else:
                    # 游戏中：方向键（事件方式，不受输入法影响）
                    if event.key in DIR_MAP:
                        game.update_direction(DIR_MAP[event.key])
                    elif event.key == pygame.K_SPACE:
                        if game.game_over_flag:
                            game.restart()
                            pygame.time.set_timer(SCREEN_UPDATE, game.speed)
                            current_timer_speed = game.speed
                            audio.stop_bg_music()  # 先停止之前的音乐
                            audio.play_bg_music()  # 重新开始时播放背景音乐
                        else:
                            game.toggle_pause()
                            if game.paused:
                                audio.pause_bg_music()
                            else:
                                audio.resume_bg_music()
                    elif event.key == pygame.K_ESCAPE:
                        # ESC 返回开始界面
                        game.restart()
                        game_started = False
                        audio.stop_bg_music()  # 停止背景音乐

        # WASD 轮询检测（同时检测大小写，绕开输入法拦截）
        if game_started and not game.game_over_flag:
            keys = pygame.key.get_pressed()
            pressed_dir = None
            # pygame.K_w=119(w), pygame.K_W 不存在，大写W的扫描码索引为87
            if keys[pygame.K_w] or keys[87] or keys[pygame.K_UP]:
                pressed_dir = Point(0, -1)
            elif keys[pygame.K_s] or keys[83] or keys[pygame.K_DOWN]:
                pressed_dir = Point(0, 1)
            elif keys[pygame.K_a] or keys[65] or keys[pygame.K_LEFT]:
                pressed_dir = Point(-1, 0)
            elif keys[pygame.K_d] or keys[68] or keys[pygame.K_RIGHT]:
                pressed_dir = Point(1, 0)

            if pressed_dir is not None:
                game.update_direction(pressed_dir)
                # 按住同方向加速
                cur = game.snake.direction
                is_same_dir = (pressed_dir.x == cur.x and pressed_dir.y == cur.y)
                boost_speed = max(40, game.speed // 3)
                target_speed = boost_speed if is_same_dir else game.speed
            else:
                target_speed = game.speed

            # 只在速度实际变化时才重置计时器
            if target_speed != current_timer_speed:
                pygame.time.set_timer(SCREEN_UPDATE, target_speed)
                current_timer_speed = target_speed

        if not game_started:
            game.draw_start_screen(screen)
        else:
            game.draw_elements(screen)

        pygame.display.update()
        clock.tick(60)


if __name__ == '__main__':
    main()
