"""
X = Wall
. = Pellet
O = Power Pellet
G = Ghost House
"""

from constants import (CELL_SIZE, MAZE_GRID_ROWS, MAZE_GRID_COLUMNS, MAZE_LEVEL_START_X, MAZE_LEVEL_START_Y)

maze_level_1 = [
    "XXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXX",
    "X..............................OX",
    "X.XXX.XXX.XXXXXX.XXXXXX.XXX.XXX.X",
    "X.X X.X X.X    X.X    X.X X.X X.X",
    "X.XXX.X X.XXXXXX.XXXXXX.X X.XXX.X",
    "X.....XXX.X....X.X....X.XXX.....X",
    "XXXXX.......XX.X.X.XX.......XXXXX",
    "X.....XXXXX...........XXXXX.....X",
    "X.XXX.......XXXXXXXXX.......XXX.X",
    "X.....XXXXX...........XXXXX.....X",
    "X.XXX...O...X       X.......XXX.X",
    "X.X X.XXXXX.X G G G X.XXXXX.X X.X",
    "X.X X.X   X.X G   G X.X   X.X X.X",
    "X.X X.X   X.X G   G X.X   X.X X.X",
    "X.X X.XXXXX.X G G G X.XXXXX.X X.X",
    "X.XXX.......XXXX.XXXX...O...XXX.X",
    "X.....XXXXX...........XXXXX.....X",
    "X.XXX.......XXXXXXXXX.......XXX.X",
    "X.....XXXXX...........XXXXX.....X",
    "XXXXX.......XX.X.X.XX.......XXXXX",
    "X.....XXX.X....X.X....X.XXX.....X",
    "X.XXX.X X.XXXXXX.XXXXXX.X X.XXX.X",
    "X.X X.X X.X    X.X    X.X X.X X.X",
    "X.XXX.XXX.XXXXXX.XXXXXX.XXX.XXX.X",
    "XO..............................X",
    "XXXXXXXXXXXXXXXX.XXXXXXXXXXXXXXXX"
]



def calculate_maze_data(maze_level):
    """Phân tích lưới dạng list các chuỗi và trả về danh sách tọa độ chi tiết của tường, hạt thức ăn, hạt sức mạnh, vị trí hồi sinh và các ô có thể đi lại."""
    walls = []
    pellets = []
    power_pellets = []
    ghost_spawns = [] 
    valid_cells = [] # Lưu các ô đi được cho thuật toán Dijkstra
    
    for row in range(MAZE_GRID_ROWS):
        for column in range(MAZE_GRID_COLUMNS):
            character = maze_level[row][column]
            character_x = round(MAZE_LEVEL_START_X + CELL_SIZE * column)
            character_y = round(MAZE_LEVEL_START_Y - CELL_SIZE * row)
            
            if character == "X":
                walls.append((character_x, character_y))
            else:
                valid_cells.append((character_x, character_y))
                if character == ".":
                    pellets.append((character_x, character_y))
                elif character == "O":
                    power_pellets.append((character_x, character_y))
                elif character == "G":
                    ghost_spawns.append((character_x, character_y))
                
    return walls, pellets, power_pellets, ghost_spawns, valid_cells

R_BEST_SCORE = 0
C_BEST_SCORE = 0