"""
管理器模块
包含：音频管理、资源管理、字体管理等
"""
import os
import pygame
from .config import AUDIO_CONFIG
from .utils import generate_beep


class AudioManager:
    """音效管理器 - 统一管理所有音频"""
    
    # 淡入淡出配置
    FADE_DURATION = 60  # 淡入淡出帧数（约1秒）
    
    def __init__(self, assets_dir=None):
        self.enabled = False
        self._music_playing = False
        self._music_started = False  # 是否已经开始播放过
        self._fade_frame = 0  # 淡入淡出进度
        self._fade_mode = None  # 'in', 'out', None
        
        # 确定 assets 目录路径
        if assets_dir is None:
            # 获取项目根目录（main.py 所在目录）
            current_file = os.path.abspath(__file__)
            src_dir = os.path.dirname(current_file)
            root_dir = os.path.dirname(src_dir)
            self.assets_dir = os.path.join(root_dir, 'assets')
            print(f"[Audio] 当前文件: {current_file}")
            print(f"[Audio] src目录: {src_dir}")
            print(f"[Audio] 根目录: {root_dir}")
        else:
            self.assets_dir = assets_dir
        
        print(f"[Audio] Assets目录: {self.assets_dir}")
        print(f"[Audio] 目录存在: {os.path.exists(self.assets_dir)}")
        
        # 音频文件路径
        self.bg_music_path = None
        self.eat_sound_path = None
        self.game_over_sound_path = None
        
        self._scan_assets()
    
    def _scan_assets(self):
        """扫描 assets 目录下的音频文件"""
        if not os.path.exists(self.assets_dir):
            print(f"[Audio] 目录不存在: {self.assets_dir}")
            return
        
        exts = ['.mp3', '.wav', '.ogg']
        
        # 背景音乐
        for name in ['bgm', 'background', 'music', 'theme']:
            for ext in exts:
                path = os.path.join(self.assets_dir, f'{name}{ext}')
                if os.path.exists(path):
                    self.bg_music_path = path
                    print(f"[Audio] 找到背景音乐: {path}")
                    break
            if self.bg_music_path:
                break
        
        # 吃食物音效
        for name in ['eat', 'eat_food', 'coin', 'pickup']:
            for ext in exts:
                path = os.path.join(self.assets_dir, f'{name}{ext}')
                if os.path.exists(path):
                    self.eat_sound_path = path
                    break
            if self.eat_sound_path:
                break
        
        # 游戏结束音效
        for name in ['gameover', 'game_over', 'die', 'fail']:
            for ext in exts:
                path = os.path.join(self.assets_dir, f'{name}{ext}')
                if os.path.exists(path):
                    self.game_over_sound_path = path
                    break
            if self.game_over_sound_path:
                break
    
    def init(self):
        """初始化音频系统"""
        try:
            pygame.mixer.init()
            self.enabled = True
        except Exception as e:
            print(f"[Audio] 初始化失败: {e}")
            self.enabled = False
    
    def update(self):
        """更新音频状态（需要在游戏循环中每帧调用）"""
        if not self.enabled or not self._music_playing:
            return
        
        # 处理淡入淡出
        if self._fade_mode == 'in':
            self._fade_frame += 1
            progress = min(1.0, self._fade_frame / self.FADE_DURATION)
            volume = AUDIO_CONFIG['bg_volume'] * progress
            pygame.mixer.music.set_volume(volume)
            if progress >= 1.0:
                self._fade_mode = None
        
        elif self._fade_mode == 'out':
            self._fade_frame += 1
            progress = min(1.0, self._fade_frame / self.FADE_DURATION)
            volume = AUDIO_CONFIG['bg_volume'] * (1 - progress)
            pygame.mixer.music.set_volume(volume)
            if progress >= 1.0:
                pygame.mixer.music.pause()
                self._fade_mode = None
    
    def play_bg_music(self, loops=-1):
        """播放背景音乐（整个游戏周期只播放一次，循环使用）"""
        print(f"[Audio] 尝试播放BGM...")
        print(f"[Audio] enabled={self.enabled}, path={self.bg_music_path}")
        
        if not self.enabled:
            print("[Audio] 音频未启用")
            return
        if not self.bg_music_path:
            print("[Audio] 无背景音乐文件")
            return
        
        # 如果已经在播放，不做任何操作（保持循环）
        if self._music_playing:
            print("[Audio] 已经在播放中")
            return
        
        try:
            print(f"[Audio] 加载文件: {self.bg_music_path}")
            pygame.mixer.music.load(self.bg_music_path)
            pygame.mixer.music.set_volume(0)  # 初始音量为0，淡入
            pygame.mixer.music.play(loops)
            self._music_playing = True
            self._music_started = True
            self._fade_mode = 'in'
            self._fade_frame = 0
            print("[Audio] BGM开始播放（淡入中）")
        except Exception as e:
            print(f"[Audio] BGM播放失败: {e}")
            print("[Audio] 尝试使用 Sound 方式播放...")
            try:
                # 尝试用 Sound 方式播放
                sound = pygame.mixer.Sound(self.bg_music_path)
                sound.set_volume(AUDIO_CONFIG['bg_volume'])
                # Sound 不能循环播放长音乐，需要特殊处理
                sound.play(-1)  # 循环播放
                self._music_playing = True
                self._music_started = True
                print("[Audio] Sound方式播放成功")
            except Exception as e2:
                print(f"[Audio] Sound方式也失败: {e2}")
                self._music_playing = False
    
    def stop_bg_music(self):
        """停止背景音乐（渐出效果）"""
        if self.enabled and self._music_playing:
            self._fade_mode = 'out'
            self._fade_frame = 0
    
    def pause_bg_music(self):
        """暂停背景音乐（渐出效果）"""
        if self.enabled and self._music_playing:
            self._fade_mode = 'out'
            self._fade_frame = 0
    
    def resume_bg_music(self):
        """恢复背景音乐（渐入效果）"""
        if self.enabled and self._music_playing:
            self._fade_mode = 'in'
            self._fade_frame = 0
    
    def play_eat_sound(self):
        """播放吃食物音效"""
        if not self.enabled:
            return
        try:
            if self.eat_sound_path:
                sound = pygame.mixer.Sound(self.eat_sound_path)
                sound.set_volume(AUDIO_CONFIG['eat_volume'])
                sound.play(maxtime=AUDIO_CONFIG['eat_max_duration'])
            else:
                # 生成默认音效
                buf = generate_beep(44100, 880, 0.08, AUDIO_CONFIG['eat_volume'])
                if buf:
                    sound = pygame.mixer.Sound(buffer=buf)
                    sound.play()
        except Exception as e:
            print(f"[Audio] 吃食物音效失败: {e}")
    
    def play_game_over_sound(self):
        """播放游戏结束音效"""
        if not self.enabled:
            return
        try:
            if self.game_over_sound_path:
                sound = pygame.mixer.Sound(self.game_over_sound_path)
                sound.set_volume(AUDIO_CONFIG['game_over_volume'])
                sound.play()
            else:
                buf = generate_beep(44100, 220, 0.4, AUDIO_CONFIG['game_over_volume'])
                if buf:
                    sound = pygame.mixer.Sound(buffer=buf)
                    sound.play()
        except Exception as e:
            print(f"[Audio] 游戏结束音效失败: {e}")


class FontManager:
    """字体管理器"""
    
    def __init__(self):
        self.title_font = None
        self.normal_font = None
        self.small_font = None
        self._loaded = False
    
    def load(self):
        """加载字体"""
        if self._loaded:
            return
        
        chinese_fonts = ['msyh.ttc', 'simhei.ttf', 'simsun.ttc', 'simkai.ttf']
        font_paths = ['C:/Windows/Fonts/', 'C:/Windows/System32/Fonts/']
        
        for name in chinese_fonts:
            for path in font_paths:
                full = os.path.join(path, name)
                if os.path.exists(full):
                    try:
                        self.title_font = pygame.font.Font(full, 64)
                        self.normal_font = pygame.font.Font(full, 32)
                        self.small_font = pygame.font.Font(full, 22)
                        self._loaded = True
                        return
                    except Exception:
                        continue
        
        # 使用默认字体
        self.title_font = pygame.font.Font(None, 72)
        self.normal_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 26)
        self._loaded = True
