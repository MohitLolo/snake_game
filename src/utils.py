"""
工具类和通用功能
"""
import math


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

    def copy(self):
        """创建副本"""
        return Point(self.x, self.y)

    def add(self, other):
        """向量加法"""
        return Point(self.x + other.x, self.y + other.y)


class Vector2:
    """2D向量"""
    __slots__ = ('x', 'y')
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"


def generate_beep(sample_rate, frequency, duration, volume=0.5):
    """生成简单蜂鸣音效"""
    try:
        samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(samples):
            t = i / sample_rate
            val = int(127 + 127 * math.sin(2 * math.pi * frequency * t) * (1 - i / samples))
            buf.append(val)
        return bytes(buf)
    except Exception:
        return None
