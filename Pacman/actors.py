import math
import random
import heapq
import os
import sys
from constants import CELL_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_MOVE_SPEED, ENEMY_MOVE_SPEED, ENEMY_RADAR

def _res(filename):
    """Trả về đường dẫn tuyệt đối đến file tài nguyên, hỗ trợ cả môi trường thường và PyInstaller."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)

class Actor:
    """Class quản lý vị trí, hướng đi, hình ảnh và khả năng hiển thị của một thực thể trong game."""
    def __init__(self):
        """Khởi tạo tọa độ, hướng, trạng thái hiển thị và hình dạng mặc định của Actor."""
        self._x = 0.0
        self._y = 0.0
        self._heading = 0
        self._is_visible = False
        self._shape = ""

    def hideturtle(self): self._is_visible = False
    def showturtle(self): self._is_visible = True

    def xcor(self): return self._x
    def ycor(self): return self._y
    def setx(self, x): self._x = x
    def sety(self, y): self._y = y
    
    def goto(self, x, y=None):
        """Di chuyển thực thể đến tọa độ cụ thể (x, y) hoặc thông qua một tuple/list."""
        if y is None: 
            self._x, self._y = x[0], x[1]
        else:
            self._x, self._y = x, y
            
    def setheading(self, h): self._heading = h
    def heading(self): return self._heading
    def get_heading(self): return round(self._heading)
    
    def forward(self, distance):
        """Di chuyển thực thể về phía trước theo hướng hiện tại một khoảng cách cho trước."""
        h = self.get_heading()
        if h == 0: self._x += distance       
        elif h == 90: self._y += distance    
        elif h == 180: self._x -= distance   
        elif h == 270: self._y -= distance   
        
    def distance(self, other):
        """Tính toán khoảng cách Euclidean từ thực thể này đến một đối tượng hoặc tọa độ khác."""
        if isinstance(other, Actor):
            ox, oy = other.xcor(), other.ycor()
        else:
            ox, oy = other[0], other[1]
        return math.hypot(self._x - ox, self._y - oy)

    def shape(self, name):
        self._shape = name

class Player(Actor):
    """Pacman class, kế thừa từ Actor."""
    def __init__(self, walls):
        """Khởi tạo trạng thái, tốc độ, mạng sống, điểm số, và bản đồ các bức tường cho người chơi."""
        super().__init__()
        self.showturtle()
        self.shape(_res("pac.gif"))
        self.state = "stop"
        self.move_speed = PLAYER_MOVE_SPEED
        self.lives = 3
        self.score = 0
        self.walls = walls
        
        self.next_heading = None 
        self.is_powered_up = False 

    def move(self):
        """Cập nhật tọa độ di chuyển của Pac-Man, xử lý chuyển hướng, kiểm tra va chạm tường và tính năng đi xuyên qua các cạnh màn hình (screen wraparound)."""
        if self.state == "stop":
            if self.next_heading is not None:
                old_x, old_y = self.xcor(), self.ycor()
                self.setheading(self.next_heading)
                self.state = "move"
                self.forward(self.move_speed)
                self.check_wall_collision()
                if self.state == "stop":
                    self.goto(old_x, old_y)
                else:
                    self.next_heading = None
        else:
            if self.next_heading is not None and self.next_heading != self.get_heading():
                old_x, old_y = self.xcor(), self.ycor()
                old_heading = self.get_heading()

                self.setheading(self.next_heading)
                self.forward(self.move_speed)
                self.check_wall_collision()

                if self.state == "stop":
                    self.goto(old_x, old_y)
                    self.setheading(old_heading)
                    self.state = "move"
                    self.forward(self.move_speed)
                    self.check_wall_collision()
                else:
                    self.next_heading = None
            else:
                self.forward(self.move_speed)
                self.check_wall_collision()

        self.change_shape_directon()
        
        if round(self.ycor()) > SCREEN_HEIGHT / 2 - 2 * CELL_SIZE: self.sety(-SCREEN_HEIGHT / 2)
        elif round(self.ycor()) < -SCREEN_HEIGHT / 2: self.sety(SCREEN_HEIGHT / 2 - 2 * CELL_SIZE)
        elif round(self.xcor()) < -SCREEN_WIDTH / 2: self.setx(SCREEN_WIDTH / 2)
        elif round(self.xcor()) > SCREEN_WIDTH / 2: self.setx(-SCREEN_WIDTH / 2)

    def check_wall_collision(self):
        """Kiểm tra và xử lý giới hạn di chuyển nếu xảy ra va chạm với tường, đồng thời dừng nhân vật (nếu có)."""
        round_x = round(self.xcor())
        round_y = round(self.ycor())
        heading = self.get_heading()
        half_cell = round(CELL_SIZE / 2)
        for x, y in self.walls:
            dx = round_x - x
            dy = round_y - y

            if heading == 0:
                if -half_cell < dx + half_cell < half_cell and -half_cell <= dy <= half_cell:
                    self.setx(x - CELL_SIZE)
                    self.state = "stop"
                elif -half_cell < dx + half_cell < half_cell and dy > half_cell and abs(dy) < CELL_SIZE:
                    self.sety(y + CELL_SIZE)
                elif -half_cell < dx + half_cell < half_cell and dy < -half_cell and abs(dy) < CELL_SIZE:
                    self.sety(y - CELL_SIZE)
            elif heading == 180:
                if -half_cell < dx - half_cell < half_cell and -half_cell <= dy <= half_cell:
                    self.setx(x + CELL_SIZE)
                    self.state = "stop"
                elif -half_cell < dx - half_cell < half_cell and dy > half_cell and abs(dy) < CELL_SIZE:
                    self.sety(y + CELL_SIZE)
                elif -half_cell < dx - half_cell < half_cell and dy < -half_cell and abs(dy) < CELL_SIZE:
                    self.sety(y - CELL_SIZE)
            elif heading == 90:
                if -half_cell <= dx <= half_cell and -half_cell < dy + half_cell < half_cell:
                    self.sety(y - CELL_SIZE)
                    self.state = "stop"
                elif dx > half_cell and abs(dx) < CELL_SIZE and -half_cell < dy + half_cell < half_cell:
                    self.setx(x + CELL_SIZE)
                elif dx < -half_cell and abs(dx) < CELL_SIZE and -half_cell < dy + half_cell < half_cell:
                    self.setx(x - CELL_SIZE)
            elif heading == 270:
                if -half_cell <= dx <= half_cell and -half_cell < dy - half_cell < half_cell:
                    self.sety(y + CELL_SIZE)
                    self.state = "stop"
                elif dx > half_cell and abs(dx) < CELL_SIZE and -half_cell < dy - half_cell < half_cell:
                    self.setx(x + CELL_SIZE)
                elif dx < -half_cell and abs(dx) < CELL_SIZE and -half_cell < dy - half_cell < half_cell:
                    self.setx(x - CELL_SIZE)

    def turn_right(self): self.next_heading = 0
    def turn_left(self): self.next_heading = 180
    def turn_up(self): self.next_heading = 90
    def turn_down(self): self.next_heading = 270

    def activate_power_mode(self):
        """Kích hoạt trạng thái tăng sức mạnh (khi ăn Power Pellet), tăng tốc độ di chuyển."""
        self.is_powered_up = True
        self.move_speed = PLAYER_MOVE_SPEED + 1

    def reset_speed(self):
        """Hủy trạng thái tăng sức mạnh, tốc độ di chuyển trở lại bình thường."""
        self.move_speed = PLAYER_MOVE_SPEED
        self.is_powered_up = False

    def change_shape_directon(self):
        """Cập nhật hình ảnh hiển thị của Pac-Man để phù hợp với hướng di chuyển hiện tại."""
        if self.state != "stop":
            if self.get_heading() == 0: self.shape(_res("right.gif"))
            elif self.get_heading() == 180: self.shape(_res("left.gif"))
            elif self.get_heading() == 90: self.shape(_res("up.gif"))
            elif self.get_heading() == 270: self.shape(_res("down.gif"))
        else:
            self.shape(_res("pac.gif"))

class Enemy(Actor):
    """Ghost class, kế thừa từ Actor."""
    def __init__(self, start_x, start_y, walls, valid_cells, player, game_mode):
        """Khởi tạo tọa độ xuất phát, môi trường, mục tiêu là người chơi, và lưu trữ chế độ game hiện tại cho Ghost."""
        super().__init__()
        self._original_shape = "" 
        self.showturtle()
        self.goto(start_x, start_y)
        self.state = "stop"
        
        self.walls = walls
        self.valid_cells = set(valid_cells)
        self.player = player
        self.game_mode = game_mode
        self.path_recalc_timer = 0
        
        self.spawn_x = start_x
        self.spawn_y = start_y
        self.peers = []  # Danh sách chứa các ghosts

    def set_peers(self, peers):
        """Hàm nhận danh sách tất cả các ghost từ main.py"""
        self.peers = peers

    def shape(self, name):
        """Cập nhật hình dạng của Ghost và lưu lại hình dáng gốc nếu đây không phải là trạng thái bị hù dọa."""
        self._shape = name
        if "scare" not in str(name):
            self._original_shape = name

    def scare(self):
        """Chuyển Ghost sang trạng thái bị hù dọa (thay đổi hình ảnh hiển thị thành chạy trốn)."""
        self._shape = _res("scare1.png")

    def unscare(self):
        """Khôi phục Ghost về hình dạng ban đầu sau khi hết trạng thái bị hù dọa."""
        self._shape = self._original_shape

    def respawn(self):
        """Đưa Ghost trở lại vị trí xuất phát ban đầu và làm mới trạng thái di chuyển."""
        self.goto(self.spawn_x, self.spawn_y)
        self.state = "stop"
        if self.player.is_powered_up:
            self.scare()
        else:
            self.unscare()
        self.start_move()

    def move(self):
        """Cập nhật vị trí của Ghost và xử lý việc di chuyển xuyên lề qua các cạnh màn hình."""
        if self.state != "stop":
            self.forward(ENEMY_MOVE_SPEED)
            if round(self.ycor()) > SCREEN_HEIGHT / 2 - 2 * CELL_SIZE: self.sety(-SCREEN_HEIGHT / 2)
            elif round(self.ycor()) < -SCREEN_HEIGHT / 2: self.sety(SCREEN_HEIGHT / 2 - 2 * CELL_SIZE)
            elif round(self.xcor()) < -SCREEN_WIDTH / 2: self.setx(SCREEN_WIDTH / 2)
            elif round(self.xcor()) > SCREEN_WIDTH / 2: self.setx(-SCREEN_WIDTH / 2)
    
    def check_wall_collision(self):
        """Kiểm tra và sửa vị trí nếu Ghost đi vào tường, thực hiện chuyển động mới."""
        round_x = round(self.xcor())
        round_y = round(self.ycor())
        heading = self.get_heading()
        half_cell = round(CELL_SIZE / 2)
        for x, y in self.walls:
            dx = round_x - x
            dy = round_y - y

            if heading == 0:
                if -half_cell < dx + half_cell < half_cell and -half_cell <= dy <= half_cell:
                    self.setx(x - CELL_SIZE); self.start_move() 
                elif -half_cell < dx + half_cell < half_cell and dy > half_cell and abs(dy) < CELL_SIZE:
                    self.sety(y + CELL_SIZE)
                elif -half_cell < dx + half_cell < half_cell and dy < -half_cell and abs(dy) < CELL_SIZE:
                    self.sety(y - CELL_SIZE)
            elif heading == 180:
                if -half_cell < dx - half_cell < half_cell and -half_cell <= dy <= half_cell:
                    self.setx(x + CELL_SIZE); self.start_move()
                elif -half_cell < dx - half_cell < half_cell and dy > half_cell and abs(dy) < CELL_SIZE:
                    self.sety(y + CELL_SIZE)
                elif -half_cell < dx - half_cell < half_cell and dy < -half_cell and abs(dy) < CELL_SIZE:
                    self.sety(y - CELL_SIZE)
            elif heading == 90:
                if -half_cell <= dx <= half_cell and -half_cell < dy + half_cell < half_cell:
                    self.sety(y - CELL_SIZE); self.start_move()
                elif dx > half_cell and abs(dx) < CELL_SIZE and -half_cell < dy + half_cell < half_cell:
                    self.setx(x + CELL_SIZE)
                elif dx < -half_cell and abs(dx) < CELL_SIZE and -half_cell < dy + half_cell < half_cell:
                    self.setx(x - CELL_SIZE)
            elif heading == 270:
                if -half_cell <= dx <= half_cell and -half_cell < dy - half_cell < half_cell:
                    self.sety(y + CELL_SIZE); self.start_move()
                elif dx > half_cell and abs(dx) < CELL_SIZE and -half_cell < dy - half_cell < half_cell:
                    self.setx(x + CELL_SIZE)
                elif dx < -half_cell and abs(dx) < CELL_SIZE and -half_cell < dy - half_cell < half_cell:
                    self.setx(x - CELL_SIZE)

    def _random_fallback_move(self):
        """Lựa chọn một hướng di chuyển ngẫu nhiên hợp lệ làm phương án dự phòng khi Ghost bị kẹt hoặc không tìm thấy đường."""
        right_cell = round(self.xcor()) + CELL_SIZE, round(self.ycor())
        left_cell = round(self.xcor()) - CELL_SIZE, round(self.ycor())
        top_cell = round(self.xcor()), round(self.ycor()) + CELL_SIZE
        bottom_cell = round(self.xcor()), round(self.ycor()) - CELL_SIZE
        next_possibile_cell = [right_cell, left_cell, top_cell, bottom_cell]
        
        for cell in next_possibile_cell[:]:
            if cell in self.walls: next_possibile_cell.remove(cell)
                
        if next_possibile_cell:
            next_cell = random.choice(next_possibile_cell)
            if next_cell == right_cell: self.setheading(0)
            elif next_cell == left_cell: self.setheading(180)
            elif next_cell == top_cell: self.setheading(90)
            elif next_cell == bottom_cell: self.setheading(270)
        self.state = "move"

    def start_move(self):
        """Kích hoạt bước di chuyển đầu tiên cho Ghost (sử dụng Dijkstra nếu ở chế độ Classic, nếu không dùng ngẫu nhiên)."""
        if self.game_mode == "classic" and self.state != "stop":
            px, py = round(self.player.xcor()), round(self.player.ycor())
            self.dijkstra_step(px, py) 
            self.state = "move"
            return
        self._random_fallback_move()
    
    def _build_peer_penalty_map(self):
        """
        Xây dựng bản đồ penalty cho các ô lân cận ghost đồng đội như sau:
        - Cell peer đang đứng: penalty = 50 (tránh trực tiếp)
        - Cell kề cạnh peer (vùng đệm 1 bước): penalty = 25
        - Cell là hướng tiếp theo peer đang di chuyển tới: penalty thêm 30
        Trả về dict: {(x, y): penalty_value}
        """
        penalty_map = {}
        for p in getattr(self, 'peers', []):
            if p is self:
                continue
            px, py = round(p.xcor()), round(p.ycor())
            peer_cell = (px, py)
            
            penalty_map[peer_cell] = penalty_map.get(peer_cell, 0) + 50

            for ddx, ddy in [(CELL_SIZE, 0), (-CELL_SIZE, 0), (0, CELL_SIZE), (0, -CELL_SIZE)]:
                neighbor = (px + ddx, py + ddy)
                if neighbor in self.valid_cells:
                    penalty_map[neighbor] = penalty_map.get(neighbor, 0) + 25
            
            ph = p.get_heading()
            dir_map = {0: (CELL_SIZE, 0), 180: (-CELL_SIZE, 0), 90: (0, CELL_SIZE), 270: (0, -CELL_SIZE)}
            if ph in dir_map:
                ddx, ddy = dir_map[ph]
                next_peer_cell = (px + ddx, py + ddy)
                if next_peer_cell in self.valid_cells:
                    penalty_map[next_peer_cell] = penalty_map.get(next_peer_cell, 0) + 30
        
        return penalty_map

    def dijkstra_step(self, target_x, target_y):
        """
        Tìm đường đi ngắn nhất đến điểm đích bằng thuật toán Dijkstra,
        kết hợp penalty map đa lớp để ghost né nhau hiệu quả.
        """
        ex, ey = round(self.xcor()), round(self.ycor())
        if not self.valid_cells:
            return

        start_node = min(self.valid_cells, key=lambda c: (c[0]-ex)**2 + (c[1]-ey)**2)
        goal_node = min(self.valid_cells, key=lambda c: (c[0]-target_x)**2 + (c[1]-target_y)**2)

        if start_node == goal_node:
            self._random_fallback_move()
            return

        # Xây dựng bản đồ penalty từ vị trí + hướng của tất cả ghost đồng đội
        penalty_map = self._build_peer_penalty_map()

        frontier = []
        heapq.heappush(frontier, (0, start_node))
        came_from = {start_node: None}
        cost_so_far = {start_node: 0}

        while frontier:
            current_cost, current = heapq.heappop(frontier)
            if current == goal_node:
                break
            cx, cy = current
            for dx, dy in [(CELL_SIZE, 0), (-CELL_SIZE, 0), (0, CELL_SIZE), (0, -CELL_SIZE)]:
                next_node = (cx + dx, cy + dy)
                if next_node in self.valid_cells:
                    penalty = penalty_map.get(next_node, 0)
                    new_cost = cost_so_far[current] + 1 + penalty

                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        heapq.heappush(frontier, (new_cost, next_node))
                        came_from[next_node] = current

        if goal_node in came_from:
            path = []
            curr = goal_node
            while curr != start_node:
                path.append(curr)
                curr = came_from[curr]
            path.reverse()
            
            if path:
                nx, ny = path[0]
                sx, sy = start_node
                if nx > sx: self.setheading(0)
                elif nx < sx: self.setheading(180)
                elif ny > sy: self.setheading(90)
                elif ny < sy: self.setheading(270)
                return

        # Không tìm thấy đường, di chuyển ngẫu nhiên
        self._random_fallback_move()

    def go_after_player(self):
        """Điều hướng Ghost: Chạy trốn khi sợ, Đuổi khi bình thường với cơ chế chống dính."""
        if self.game_mode == "classic":
            current_pos = (round(self.xcor()), round(self.ycor()))
            
            if current_pos not in self.valid_cells:
                return

            px, py = round(self.player.xcor()), round(self.player.ycor())

            # TRẠNG THÁI SỢ HÃI: chạy về góc xa nhất so với Pacman
            if "scare" in str(self._shape):
                min_x = min(c[0] for c in self.valid_cells)
                max_x = max(c[0] for c in self.valid_cells)
                min_y = min(c[1] for c in self.valid_cells)
                max_y = max(c[1] for c in self.valid_cells)
                corners = [(min_x, min_y), (max_x, min_y), (min_x, max_y), (max_x, max_y)]
                flee_target = max(corners, key=lambda c: (c[0]-px)**2 + (c[1]-py)**2)
                self.dijkstra_step(flee_target[0], flee_target[1])
                return

            # TRẠNG THÁI TẤN CÔNG
            # Mỗi ghost dùng offset khác nhau để tránh hội tụ về cùng 1 điểm
            shape_name = str(self._original_shape)
            if "red" in shape_name:
                # Ghost Đỏ (Blinky): Đuổi sát trực tiếp
                self.dijkstra_step(px, py)
            else:
                # Ghost khác: Đón đầu với offset riêng biệt dựa theo index trong peers
                heading = self.player.get_heading()
                
                # Tính index của ghost này trong danh sách peers để dùng offset khác nhau
                try:
                    ghost_index = self.peers.index(self)
                except ValueError:
                    ghost_index = 1
                
                # Offset đón đầu: ghost_index tạo ra sự phân tán (2, 4, 6 ô)
                offset = (ghost_index + 1) * 2 * CELL_SIZE
                tx, ty = px, py
                if heading == 0:   tx += offset
                elif heading == 180: tx -= offset
                elif heading == 90:  ty += offset
                elif heading == 270: ty -= offset

                self.dijkstra_step(tx, ty)
        else:
            # RESPECT MODE: Sử dụng logic Radar khoảng cách
            current_pos = (round(self.xcor()), round(self.ycor()))
            if current_pos in self.valid_cells:
                player_x, player_y = round(self.player.xcor()), round(self.player.ycor())
                enemy_x, enemy_y = round(self.xcor()), round(self.ycor())
                
                if self.distance(self.player) <= ENEMY_RADAR:
                    if player_y == enemy_y and player_x > enemy_x: self.setheading(0)
                    elif player_y == enemy_y and player_x < enemy_x: self.setheading(180)
                    elif player_x == enemy_x and player_y > enemy_y: self.setheading(90)
                    elif player_x == enemy_x and player_y < enemy_y: self.setheading(270)