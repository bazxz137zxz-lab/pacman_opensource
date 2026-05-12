"""
File docstring.py tổng hợp toàn bộ docstring cho các lớp và hàm trong tất cả file.
"""


# FILE: actors.py

def _res(filename):
    """Trả về đường dẫn tuyệt đối đến file tài nguyên, hỗ trợ cả môi trường thường và PyInstaller."""

class Actor:
    """Class quản lý vị trí, hướng đi, hình ảnh và khả năng hiển thị của một thực thể trong game."""
    
    def __init__(self):
        """Khởi tạo tọa độ, hướng, trạng thái hiển thị và hình dạng mặc định của Actor."""
    def hideturtle(self):
        """Ẩn thực thể khỏi màn hình."""
    def showturtle(self):
        """Hiển thị thực thể trên màn hình."""
    def xcor(self):
        """Lấy tọa độ X hiện tại."""
    def ycor(self):
        """Lấy tọa độ Y hiện tại."""
    def setx(self, x):
        """Thiết lập tọa độ X mới."""
    def sety(self, y):
        """Thiết lập tọa độ Y mới."""

    def goto(self, x, y=None):
        """Di chuyển thực thể đến tọa độ cụ thể (x, y) hoặc thông qua một tuple/list."""
    def setheading(self, h):
        """Thiết lập hướng di chuyển của thực thể (tính bằng độ: 0, 90, 180, 270)."""
    def heading(self):
        """Lấy hướng di chuyển hiện tại (giá trị chính xác)"""
    def get_heading(self):
        """Lấy hướng di chuyển hiện tại đã được làm tròn."""

    def forward(self, distance):
        """Di chuyển thực thể về phía trước theo hướng hiện tại một khoảng cách cho trước."""
    def distance(self, other):
        """Tính toán khoảng cách Euclidean từ thực thể này đến một đối tượng hoặc tọa độ khác."""
    def shape(self, name):
        """Định nghĩa tên hình ảnh sẽ được sử dụng để hiển thị thực thể."""

class Player(Actor):
    """Pacman class, kế thừa từ Actor."""
    def __init__(self, walls):
        """Khởi tạo trạng thái, tốc độ, mạng sống, điểm số, và bản đồ các bức tường cho người chơi."""
    def move(self):
        """Cập nhật tọa độ di chuyển của Pac-Man, xử lý chuyển hướng, kiểm tra va chạm tường và tính năng đi xuyên qua các cạnh màn hình (screen wraparound)."""
    def check_wall_collision(self):
        """Kiểm tra và xử lý giới hạn di chuyển nếu xảy ra va chạm với tường, đồng thời dừng nhân vật (nếu có)."""
    def turn_right(self):
        """Đặt hướng di chuyển tiếp theo sang phải (0 độ)."""
    def turn_left(self):
        """Đặt hướng di chuyển tiếp theo sang trái (180 độ)."""
    def turn_up(self):
        """Đặt hướng di chuyển tiếp theo lên trên (90 độ)."""
    def turn_down(self):
        """Đặt hướng di chuyển tiếp theo xuống dưới (270 độ)."""
    def activate_power_mode(self):
        """Kích hoạt trạng thái tăng sức mạnh (khi ăn Power Pellet), tăng tốc độ di chuyển."""
    def reset_speed(self):
        """Hủy trạng thái tăng sức mạnh, tốc độ di chuyển trở lại bình thường."""
    def change_shape_directon(self):
        """Cập nhật hình ảnh hiển thị của Pac-Man để phù hợp với hướng di chuyển hiện tại."""

class Enemy(Actor):
    """Ghost class, kế thừa từ Actor."""
    def __init__(self, start_x, start_y, walls, valid_cells, player, game_mode):
        """Khởi tạo tọa độ xuất phát, môi trường, mục tiêu là người chơi, và lưu trữ chế độ game hiện tại cho Ghost."""
    def set_peers(self, peers):
        """Hàm nhận danh sách tất cả các ghost từ main.py"""
    def shape(self, name):
        """Cập nhật hình dạng của Ghost và lưu lại hình dáng gốc nếu đây không phải là trạng thái bị hù dọa."""
    def scare(self):
        """Chuyển Ghost sang trạng thái bị hù dọa (thay đổi hình ảnh hiển thị thành chạy trốn)."""
    def unscare(self):
        """Khôi phục Ghost về hình dạng ban đầu sau khi hết trạng thái bị hù dọa."""
    def respawn(self):
        """Đưa Ghost trở lại vị trí xuất phát ban đầu và làm mới trạng thái di chuyển."""
    def move(self):
        """Cập nhật vị trí của Ghost và xử lý việc di chuyển xuyên lề qua các cạnh màn hình."""
    def check_wall_collision(self):
        """Kiểm tra và sửa lỗi vị trí nếu Ghost đi vào tường, thực hiện chuyển động mới."""
    def _random_fallback_move(self):
        """Lựa chọn một hướng di chuyển ngẫu nhiên hợp lệ làm phương án dự phòng khi Ghost bị kẹt hoặc không tìm thấy đường."""
    def start_move(self):
        """Kích hoạt bước di chuyển đầu tiên cho Ghost (sử dụng Dijkstra nếu ở chế độ Classic, nếu không dùng ngẫu nhiên)."""
    def _build_peer_penalty_map(self):
        """
        Xây dựng bản đồ penalty cho các ô lân cận ghost đồng đội như sau:
        - Cell peer đang đứng: penalty = 50 (tránh trực tiếp)
        - Cell kề cạnh peer (vùng đệm 1 bước): penalty = 25
        - Cell là hướng tiếp theo peer đang di chuyển tới: penalty thêm 30
        Trả về dict: {(x, y): penalty_value}
        """
    def go_after_player(self):
        """Điều hướng Ghost: Chạy trốn khi sợ, Đuổi khi bình thường với cơ chế chống dính."""
    def dijkstra_step(self, target_x, target_y):
        """Tìm đường đi ngắn nhất đến điểm đích bằng thuật toán Dijkstra, kết hợp penalty map đa lớp để ghost né nhau hiệu quả."""


# FILE: main.py


def set_timer(func, delay_ms):
    """Thiết lập một bộ đếm thời gian để kích hoạt một hàm mục tiêu sau khoảng thời gian trễ (đơn vị milli giây)."""
    
def check_timers():
    """Kiểm tra và kích hoạt tất cả các hàm hẹn giờ nếu thời gian hiện tại đã vượt qua thời điểm kích hoạt của chúng."""
    
def get_image(name):
    """
    Tải và lưu trữ các hình ảnh từ ổ cứng vào cache, tự động điều chỉnh kích thước theo CELL_SIZE
    Tạo hình ảnh màu đỏ làm mặc định nếu file ảnh bị lỗi hoặc thiếu.
    """
    
def init_screen():
    """Khởi tạo hệ thống Pygame, cài đặt font chữ và thiết lập kích thước cửa sổ game chính."""
    
def bind_controls():
    """Kích hoạt flag cho phép đọc các phím điều khiển nhân vật."""
    
def game_logic(player, pellet_pen, power_pen, player_start_x, player_start_y, enemies):
    """Xử lý các luật logic chính trong lúc đang chơi: ăn hạt thức ăn, ăn hạt sức mạnh, ăn ma, bị ma bắt, và kiểm tra điều kiện kết thúc thắng/thua."""
    
def save_best_score(new_score, mode):
    """Kiểm tra và cập nhật kỷ lục điểm số cao nhất (Best Score) vào file `mazes.py` tùy theo chế độ game (Respect hoặc Classic)."""
    
def mode_selection_screen(screen):
    """Hiển thị màn hình menu bắt đầu, cho phép người chơi chọn chế độ Respect [R] hoặc Classic [C]."""
    
def render_frame(screen, walls, pellet_pen, power_pen, player, enemies, game_state, mode, countdown_val=None):
    """Vẽ toàn bộ khung hình game bao gồm tường, hạt, nhân vật, giao diện điểm số, số mạng và màn hình kết thúc (Win/Lose)."""
    
def run_game(screen, mode):
    """Khởi tạo vòng lặp cho một màn chơi: sinh map, ma và Pac-Man; xử lý sự kiện đếm ngược, vòng lặp game, điều khiển và các thao tác sau khi game kết thúc."""
    
def main():
    """Hàm main"""


# FILE: mazes.py


def calculate_maze_data(maze_level):
    """Phân tích mạng lưới cấp độ dạng chuỗi của ma trận bản đồ để tạo và trả về danh sách tọa độ chi tiết của tường, hạt thức ăn, hạt sức mạnh, vị trí hồi sinh và các ô có thể đi lại."""

# FILE: renderer.py


def to_pygame(x, y):
    """Hàm chuyển đổi từ hệ tọa độ chuẩn (tâm ở giữa màn hình) sang hệ tọa độ Pygame (tâm gốc nằm ở góc trên cùng bên trái)."""

def _res(filename):
    """Trả về đường dẫn tuyệt đối đến file tài nguyên (ảnh)"""

class Pen:
    """Lớp cơ sở đọc cấu trúc bản đồ để khởi tạo môi trường hiển thị cho game."""
    def __init__(self):
        """Khởi tạo các danh sách tọa độ thực thể trong bản đồ thông qua việc gọi hàm calculate_maze_data."""

class Wall(Pen):
    """Lớp chứa dữ liệu cho các bức tường (Wall)."""
    def __init__(self):
        """Tải dữ liệu hình ảnh mặc định của bức tường vào đối tượng."""

class Pellet(Pen):
    """Lớp quản lý dữ liệu hiển thị của hạt điểm (Pellet)."""
    def __init__(self):
        """Khởi tạo bản ghi tem (stamps) cho đối tượng."""
    def draw(self):
        """Đăng ký các vị trí của các hạt điểm vào biến danh sách stamps để chuẩn bị render."""

class PowerPellet(Pen):
    """Lớp quản lý dữ liệu hiển thị của hạt sức mạnh (Power Pellet)."""
    def __init__(self):
        """Khởi tạo bản ghi tem (stamps) cho đối tượng."""
    def draw(self):
        """Đăng ký các vị trí của các hạt sức mạnh vào biến danh sách stamps để chuẩn bị render."""

class UiPen(Pen):
    """Lớp quản lý thiết lập vẽ giao diện người dùng (User Interface)."""
    def __init__(self):
        """Khởi tạo font chữ mặc định của UI."""