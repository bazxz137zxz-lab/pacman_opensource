"""
Pacman game
Author
"""

import pygame
import random
import os
import sys
import re
import mazes 
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, ENEMY_NUMBER, SCORE_PER_PELLET
from renderer import Wall, Pellet, PowerPellet, UiPen, to_pygame
from actors import Player, Enemy

timers = []
controls_enabled = False
images_cache = {}

def set_timer(func, delay_ms):
    """Thiết lập một bộ đếm thời gian để kích hoạt một hàm mục tiêu sau khoảng thời gian trễ (đơn vị milli giây)."""
    timers.append({"func": func, "trigger": pygame.time.get_ticks() + delay_ms})

def check_timers():
    """Kiểm tra và kích hoạt tất cả các hàm hẹn giờ nếu thời gian hiện tại đã vượt qua thời điểm kích hoạt của chúng."""
    now = pygame.time.get_ticks()
    for t in timers[:]:
        if now >= t["trigger"]:
            t["func"]()
            timers.remove(t)

def get_image(name):
    """
    Tải và lưu trữ các hình ảnh từ ổ cứng vào cache, tự động điều chỉnh kích thước theo CELL_SIZE
    Tạo hình ảnh màu đỏ làm mặc định nếu file ảnh bị lỗi hoặc thiếu.
    """
    if name not in images_cache:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, name)
        try:
            img = pygame.image.load(img_path).convert_alpha()
            images_cache[name] = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        except Exception as e:
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surf.fill((255, 0, 0)) 
            images_cache[name] = surf
    return images_cache[name]

def init_screen():
    """Khởi tạo hệ thống Pygame, cài đặt font chữ và thiết lập kích thước cửa sổ game chính."""
    pygame.init()
    pygame.font.init() 
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("GAME PACMAN :>>")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, "icon.png")
    if os.path.exists(icon_path):
        try:
            icon_surf = pygame.image.load(icon_path).convert_alpha()
            pygame.display.set_icon(icon_surf)
        except Exception:
            pass
    return screen

def bind_controls():
    """Kích hoạt flag cho phép đọc các phím điều khiển nhân vật."""
    global controls_enabled
    controls_enabled = True

def game_logic(player, pellet_pen, power_pen, player_start_x, player_start_y, enemies):
    """Xử lý các luật logic chính trong lúc đang chơi: ăn hạt thức ăn, ăn hạt sức mạnh, ăn ma, bị ma bắt, và kiểm tra điều kiện kết thúc thắng/thua."""
    for (px, py), stamp_id in list(pellet_pen.stamps.items()):
        if player.distance((px, py)) < CELL_SIZE / 2 and (px, py) != (player_start_x, player_start_y):
            del pellet_pen.stamps[(px, py)]
            player.score += SCORE_PER_PELLET 
        elif player.distance((px, py)) < CELL_SIZE / 2 and (px, py) == (player_start_x, player_start_y):
            del pellet_pen.stamps[(px, py)]
            
    for (px, py), stamp_id in list(power_pen.stamps.items()):
        if player.distance((px, py)) < CELL_SIZE / 2:
            del power_pen.stamps[(px, py)]
            player.score += 50
            player.activate_power_mode()
            
            for enemy in enemies:
                enemy.scare()
                
            def end_powerup():
                player.reset_speed()
                for e in enemies:
                    e.unscare()
            set_timer(end_powerup, 5000) 
            
    player.move()
    player.check_wall_collision()
    
    for enemy in enemies:
        enemy.move()
        enemy.check_wall_collision()
        enemy.go_after_player()
        
        if enemy.distance(player) < CELL_SIZE / 2:
            if player.is_powered_up:
                enemy.respawn() 
                player.score += 200 
            else:
                safe_spots = []
                for pellet in pellet_pen.stamps.keys():
                    if all(enemy.distance(pellet) > CELL_SIZE * 5 for e in enemies):
                        safe_spots.append(pellet)
                if safe_spots:
                    player.goto(random.choice(safe_spots))
                player.lives -= 1  
            
    if len(power_pen.stamps) == 0 and len(pellet_pen.stamps) == 0:
        player.state = "stop"
        for enemy in enemies:
            enemy._is_visible = False
            enemy.state = "stop"
        return "win" 
        
    if player.lives <= 0:
        player.state = "stop"
        player._is_visible = False
        for enemy in enemies:
            enemy.state = "stop"
        return "lose" 
        
    return "playing"

def save_best_score(new_score, mode):
    """Kiểm tra và cập nhật kỷ lục điểm số cao nhất (Best Score) vào file mazes.py tùy theo chế độ game (Respect hoặc Classic)."""
    updated = False
    if mode == "respect" and new_score > mazes.R_BEST_SCORE:
        mazes.R_BEST_SCORE = new_score
        updated = True
    elif mode == "classic" and new_score > mazes.C_BEST_SCORE:
        mazes.C_BEST_SCORE = new_score
        updated = True

    if updated:
        try:
            with open("mazes.py", "r", encoding="utf-8") as f:
                content = f.read()
            if mode == "respect":
                content = re.sub(r"R_BEST_SCORE\s*=\s*\d+", f"R_BEST_SCORE = {mazes.R_BEST_SCORE}", content)
            else:
                content = re.sub(r"C_BEST_SCORE\s*=\s*\d+", f"C_BEST_SCORE = {mazes.C_BEST_SCORE}", content)
            with open("mazes.py", "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            pass

def mode_selection_screen(screen):
    """Hiển thị màn hình menu bắt đầu, cho phép người chơi chọn chế độ Respect [press R] hoặc Classic [press C]."""
    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    sub_font = pygame.font.SysFont("Arial", 30)

    title_text = title_font.render("", True, (255, 255, 0))
    opt1_text = sub_font.render("", True, (0, 255, 255))
    opt2_text = sub_font.render("", True, (255, 100, 100))

    base_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(base_dir, "start.png")
    bg_image = None
    if os.path.exists(bg_path):
        try:
            bg_img_raw = pygame.image.load(bg_path).convert()
            bg_image = pygame.transform.scale(bg_img_raw, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception:
            pass

    while True:
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((0, 0, 0))

        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(opt1_text, (SCREEN_WIDTH//2 - opt1_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        screen.blit(opt2_text, (SCREEN_WIDTH//2 - opt2_text.get_width()//2, SCREEN_HEIGHT//2 + 70))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return "respect"
                if event.key == pygame.K_c: return "classic"

def render_frame(screen, walls, pellet_pen, power_pen, player, enemies, game_state, mode, countdown_val=None):
    """Vẽ toàn bộ khung hình game bao gồm tường, hạt, nhân vật, giao diện điểm số, số mạng và màn hình kết thúc (Win/Lose)."""
    screen.fill((0, 0, 0))
    wall_img = get_image("wall.gif")
    for x, y in walls:
        pos = to_pygame(x, y)
        screen.blit(wall_img, (pos[0] - CELL_SIZE//2, pos[1] - CELL_SIZE//2))
        
    for (x, y) in pellet_pen.stamps.keys():
        pos = to_pygame(x, y)
        pygame.draw.circle(screen, (255, 215, 0), pos, int(CELL_SIZE * 0.35 / 2))
        
    for (x, y) in power_pen.stamps.keys():
        pos = to_pygame(x, y)
        pygame.draw.circle(screen, (127, 255, 0), pos, int(CELL_SIZE * 0.8 / 2))
        
    if player._is_visible:
        img = get_image(player._shape if player._shape else "pac.gif")
        pos = to_pygame(player.xcor(), player.ycor())
        screen.blit(img, (pos[0] - CELL_SIZE//2, pos[1] - CELL_SIZE//2))
        
    for enemy in enemies:
        if enemy._is_visible:
            img = get_image(enemy._shape if enemy._shape else "red_enemy.gif")
            pos = to_pygame(enemy.xcor(), enemy.ycor())
            screen.blit(img, (pos[0] - CELL_SIZE//2, pos[1] - CELL_SIZE//2))
            
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, CELL_SIZE * 2))

    ui_font = pygame.font.SysFont("Arial", 22, bold=True)
    score_surf = ui_font.render(f"SCORE: {player.score}", True, (255, 255, 255))
    
    best_score_val = mazes.R_BEST_SCORE if mode == "respect" else mazes.C_BEST_SCORE
    best_txt = f"R-BEST: {best_score_val}" if mode == "respect" else f"C-BEST: {best_score_val}"
    best_surf = ui_font.render(best_txt, True, (255, 215, 0))
    
    lives_surf = ui_font.render(f"LIVES: {player.lives}", True, (255, 255, 255))
    
    screen.blit(score_surf, (20, 10))
    screen.blit(best_surf, (SCREEN_WIDTH//2 - best_surf.get_width()//2, 10)) 
    screen.blit(lives_surf, (SCREEN_WIDTH - 120, 10))

    # Hiển thị thông báo đếm ngược
    if countdown_val is not None and countdown_val > 0:
        count_font = pygame.font.SysFont("Arial", 120, bold=True)
        count_text = count_font.render(str(countdown_val), True, (255, 255, 0))
        screen.blit(count_text, (SCREEN_WIDTH//2 - count_text.get_width()//2, SCREEN_HEIGHT//2 - count_text.get_height()//2))

    if game_state not in ["playing", "countdown"]:
        title_font = pygame.font.SysFont("Arial", 48, bold=True)
        sub_font = pygame.font.SysFont("Arial", 24)

        if game_state == "lose":
            title_text = title_font.render("GAME OVER", True, (255, 0, 0))
        else:
            title_text = title_font.render("YOU WIN!", True, (0, 255, 0))
            
        sub_text = sub_font.render("Press SPACE to return to Menu", True, (255, 255, 255))
        
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//2 - 40))
        screen.blit(sub_text, (SCREEN_WIDTH//2 - sub_text.get_width()//2, SCREEN_HEIGHT//2 + 20))

    pygame.display.flip()

def run_game(screen, mode):
    """Khởi tạo vòng lặp cho một màn chơi: sinh map, ma và Pac-Man; xử lý sự kiện đếm ngược, vòng lặp game, điều khiển và các thao tác sau khi game kết thúc."""
    global timers, controls_enabled
    timers = []
    controls_enabled = False
    
    wall_pen = Wall()
    pellet_pen = Pellet()
    power_pen = PowerPellet()
    
    walls = wall_pen.walls
    ghost_spawns = wall_pen.ghost_spawns 
    valid_cells = wall_pen.valid_cells
    
    pellet_pen.draw()
    pellets = pellet_pen.pellets
    power_pen.draw()
    
    if not pellets: 
        return "quit"

    pellets_sorted = sorted(pellets, key=lambda p: (-p[1], p[0]))
    player_start_x, player_start_y = pellets_sorted[0]
    
    player = Player(walls)
    player.goto(player_start_x, player_start_y)
    
    # 4 ghosts
    enemy_colors = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "red_enemy.gif"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "red_enemy.gif"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "pink_enemy.gif"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "green_enemy.gif"),
    ]
    enemies = []
    for i in range(len(enemy_colors)):
        if ghost_spawns:
            enemy_start_x, enemy_start_y = random.choice(ghost_spawns)
        else:
            enemy_start_x, enemy_start_y = random.choice(pellets)
            
        enemy = Enemy(enemy_start_x, enemy_start_y, walls, valid_cells, player, mode)
        enemy.shape(enemy_colors[i])
        enemies.append(enemy)
        
    for enemy in enemies:
        enemy.set_peers(enemies)
        
    clock = pygame.time.Clock()
    running = True
    
    # Thiết lập trạng thái đếm ngược
    game_state = "countdown"
    countdown_start_ticks = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit" 
            elif event.type == pygame.KEYDOWN:
                if game_state == "playing" and controls_enabled:
                    if event.key == pygame.K_RIGHT: player.turn_right()
                    elif event.key == pygame.K_LEFT: player.turn_left()
                    elif event.key == pygame.K_UP: player.turn_up()
                    elif event.key == pygame.K_DOWN: player.turn_down()
                elif game_state in ["lose", "win"]:
                    if event.key == pygame.K_SPACE:
                        return "menu" 

        if game_state == "countdown":
            seconds_left = 3 - (pygame.time.get_ticks() - countdown_start_ticks) // 1000
            if seconds_left <= 0:
                game_state = "playing"
                
                bind_controls()
                for enemy in enemies:
                    enemy.start_move()
                    
            render_frame(screen, walls, pellet_pen, power_pen, player, enemies, game_state, mode, seconds_left)

        elif game_state == "playing":
            check_timers()
            game_state = game_logic(player, pellet_pen, power_pen, player_start_x, player_start_y, enemies)
            if game_state != "playing":
                save_best_score(player.score, mode)
            render_frame(screen, walls, pellet_pen, power_pen, player, enemies, game_state, mode)
        else:
            render_frame(screen, walls, pellet_pen, power_pen, player, enemies, game_state, mode)
        clock.tick(60)
    return "quit"

def main():
    """Hàm chạy chương trình cốt lõi, quản lý quá trình chuyển đổi giữa màn hình chờ (Menu) và màn chơi thực tế (Run Game)."""
    screen = init_screen()
    
    while True:
        mode = mode_selection_screen(screen)
        if not mode: 
            break 
            
        while True:
            result = run_game(screen, mode)
            if result == "menu":
                break 
            elif result == "quit":
                pygame.quit()
                sys.exit()
                
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()