import pygame
import os
import sys
from mazes import calculate_maze_data, maze_level_1
from constants import CELL_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH

def to_pygame(x, y):
    """Chuyển đổi từ hệ tọa độ chuẩn sang hệ tọa độ Pygame."""
    return (int(x + SCREEN_WIDTH / 2), int(SCREEN_HEIGHT / 2 - y))

def _res(filename):
    """Trả về đường dẫn tuyệt đối đến file tài nguyên (ảnh)"""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)

class Pen:
    def __init__(self):
        self.walls, self.pellets, self.power_pellets, self.ghost_spawns, self.valid_cells = calculate_maze_data(maze_level_1)

class Wall(Pen):
    def __init__(self):
        super().__init__()
        self.shape_name = _res("wall.gif")  # Đường dẫn tuyệt đối

class Pellet(Pen):
    def __init__(self):
        super().__init__()
        self.stamps = {}

    def draw(self):
        stamp_id = 0
        for x, y in self.pellets:
            self.stamps[(x, y)] = stamp_id
            stamp_id += 1

class PowerPellet(Pen):
    def __init__(self):
        super().__init__()
        self.stamps = {}

    def draw(self):
        stamp_id = 0
        for x, y in self.power_pellets:
            self.stamps[(x, y)] = stamp_id
            stamp_id += 1

class UiPen(Pen):
    def __init__(self):
        super().__init__()
        pygame.font.init()
        self.font = pygame.font.SysFont("Courier", 30, bold=False)