import pygame
import os
import random
import math
from leaderboard_data import load_leaderboard, save_leaderboard
from achievements import check_achievements, ACHIEVEMENTS
from pause_menu import pause_menu
from sound_manager import play
from background_manager import get_active_background, get_ai_difficulty

# Player class
class Player:
    # Represents a single player (human or AI)

    def __init__(self, player_name, player_data=None):
        self.name = player_name

        # Load player data from leaderboard if not provided
        if player_data is None:
            lb = load_leaderboard()
            player_data = lb.get(player_name)
            if player_data is None:
                # Case-insensitive lookup (so "alex" and "Alex" are treated the same)
                for k, v in lb.items():
                    if k.lower() == player_name.lower():
                        player_data = v
                        self.name = k
                        break

        # Assign stored stats, or initialise defaults
        if player_data:
            self.legs_won_total = player_data.get("legs_won_total", 0)
            self.tournaments_won = player_data.get("tournaments_won", 0)
            # load achievements list into a set
            self.achievements = set(player_data.get("achievements", []))
            self.achievements_unlocked = player_data.get("achievements_unlocked", len(self.achievements))
            self.achievements_unlocked = max(self.achievements_unlocked, len(self.achievements))
        else:
            self.legs_won_total = 0
            self.tournaments_won = 0
            self.achievements = set()
            self.achievements_unlocked = 0

        # Match-specific state
        self.score = 501
        self.legs = 0
        self.sets = 0
        self.darts_left = 3
        self.turn_start_score = 501
        self.darts_used_in_leg = 0

    def unlock_achievement(self, aid):
        if self.name.startswith("AI_"):
            return False  # Do not save achievements for AI players

        lb = load_leaderboard() # Load current leaderboard data
        player_data = lb.get(self.name, {})

        # make sure achievements list exists
        unlocked = player_data.get("achievements", [])
        counts = player_data.get("achievement_counts", {}) # Store repeat counts of achievements such as tournaments won

        if aid not in unlocked: # (aid is achievement id)
            unlocked.append(aid) # Add achievement if first time completing

        # increment achievement counter for repeatable unlocks
        counts[aid] = counts.get(aid, 0) + 1

        # Save updated stats back into leaderboard
        player_data["achievements"] = unlocked
        player_data["achievement_counts"] = counts
        player_data["achievements_unlocked"] = len(unlocked)

        lb[self.name] = player_data
        save_leaderboard(lb)
        return True # Always return True so game knows achievement was unlocked
    
    def save_stats(self):
        # Updates the leaderboard file with the player's persistent stats.
        # Ensures the entry exists before updating.

        lb = load_leaderboard()
        player_data = lb.get(self.name, {})

        # Keep previous achievements and counts
        existing_achievements = set(player_data.get("achievements", []))
        existing_counts = player_data.get("achievement_counts", {})

        # Merge the current session's achievements and stats
        merged_achievements = existing_achievements.union(self.achievements)
        player_data.update({
            "legs_won_total": self.legs_won_total,
            "tournaments_won": self.tournaments_won,
            "achievements": list(merged_achievements),
            "achievements_unlocked": len(merged_achievements),
            "achievement_counts": existing_counts,
        })

        lb[self.name] = player_data
        save_leaderboard(lb)

# Gamestate class
class GameState:
    # Holds the current game state (two players and turn tracking).
    
    def __init__(self, player1_name="You", player2_name=None, ai_difficulty=get_ai_difficulty()):
        lb = load_leaderboard()
        p1_data = lb.get(player1_name)
        if player2_name is None:
            player2_name = generate_ai_name()
        p2_data = lb.get(player2_name)

        self.player1 = Player(player1_name, p1_data)
        self.player2 = Player(player2_name, p2_data)
        self.current_player = self.player1
        self.ai_difficulty = ai_difficulty

# AI name generation
def generate_ai_name():
    return random.choice(["Alex", "Taylor", "Jordan", "Jamie", "Sam", "Riley", "Drew", "Morgan", "Casey", "Eric", "Grace", "Billy", "Mike", "Mason", "Luke"])

# Utility functions
def update_player_stats(player):
    # Updates leaderboard entry for a given player with latest stats

    leaderboard = load_leaderboard()
    data = leaderboard.get(player.name, {})

    data.update({
        "legs_won_total": player.legs_won_total,
        "tournaments_won": player.tournaments_won,
        "achievements_unlocked": player.achievements_unlocked,
    })

    leaderboard[player.name] = data
    save_leaderboard(leaderboard)

# AI target selection
def ai_select_target(score, difficulty):
    # Determines AI aiming position and throw power

    # Fixed dartboard sector order (clockwise from top)
    SECTOR_ORDER = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17,
                    3, 19, 7, 16, 8, 11, 14, 9, 12, 5]

    def get_angle(sector_number):
        # Returns radian angle of a given sector number

        index = SECTOR_ORDER.index(sector_number)
        angle_deg = index * 18
        return math.radians(angle_deg - 90)

    def aim_for_ring(sector_number, ring):
        # Returns pixel coordinate for aiming at a sector ring

        ring_radii = {'S': 120, 'T': 90, 'D': 155}
        radius = ring_radii[ring]
        angle_rad = get_angle(sector_number)
        x = int(360 + radius * math.cos(angle_rad))
        y = int(272 + radius * math.sin(angle_rad))
        return (x, y)

    # Difficulty settings
    difficulty_settings = {
        'beginner': {'deviation': 45, 'power_range': (30, 70)},
        'intermediate': {'deviation': 25, 'power_range': (45, 65)},
        'advanced': {'deviation': 8, 'power_range': (50, 58)},
    }
    settings = difficulty_settings.get(difficulty, difficulty_settings['intermediate'])

    def apply_jitter(pos):
        # Adds inaccuracy to simulate realistic dart throws

        dev = settings['deviation']
        return (pos[0] + random.randint(-dev, dev), pos[1] + random.randint(-dev, dev))

    # Checkout map for AI selection
    checkout_map = {
        170:[(20,'T')],167:[(20,'T')],164:[(20,'T')],161:[(20,'T')],
        160:[(20,'T')],158:[(20,'T')],157:[(20,'T')],156:[(20,'T')],
        155:[(20,'T')],154:[(20,'T')],153:[(20,'T')],152:[(20,'T')],
        151:[(20,'T')],150:[(20,'T')],149:[(20,'T')],148:[(20,'T')],
        147:[(20,'T')],146:[(20,'T')],145:[(20,'T')],144:[(20,'T')],
        143:[(20,'T')],142:[(20,'T')],141:[(20,'T')],140:[(20,'T')],
        139:[(20,'T')],138:[(20,'T')],137:[(20,'T')],136:[(20,'T')],
        135:[(20,'T')],134:[(20,'T')],133:[(20,'T')],132:[(20,'T')],
        131:[(20,'T')],130:[(20,'T')],129:[(19,'T')],128:[(18,'T')],
        127:[(20,'T')],126:[(19,'T')],125:[(18,'T')],124:[(20,'T')],
        123:[(19,'T')],122:[(18,'T')],121:[(17,'T')],120:[(20,'T')],
        119:[(19,'T')],118:[(20,'T')],117:[(20,'T')],116:[(20,'T')],
        115:[(20,'T')],114:[(20,'T')],113:[(20,'T')],112:[(20,'T')],
        111:[(20,'T')],110:[(20,'T')],109:[(20,'T')],108:[(20,'T')],
        107:[(19,'T')],106:[(20,'T')],105:[(19,'T')],104:[(18,'T')],
        103:[(17,'T')],102:[(16,'T')],101:[(15,'T')],100:[(20,'T')],
        99:[(19,'T')],98:[(20,'T')],97:[(19,'T')],96:[(20,'T')],
        95:[(19,'T')],94:[(18,'T')],93:[(19,'T')],92:[(20,'T')],
        91:[(17,'T')],90:[(18,'T')],89:[(19,'T')],88:[(16,'T')],
        87:[(17,'T')],86:[(18,'T')],85:[(15,'T')],84:[(20,'T')],
        83:[(17,'T')],82:[(14,'T')],81:[(15,'T')],80:[(20,'T')],
        79:[(13,'T')],78:[(18,'T')],77:[(19,'T')],76:[(20,'T')],
        75:[(17,'T')],74:[(14,'T')],73:[(19,'T')],72:[(16,'T')],
        71:[(13,'T')],70:[(18,'T')],69:[(19,'T')],68:[(20,'T')],
        67:[(17,'T')],66:[(10,'T')],65:[(19,'T')],64:[(16,'T')],
        63:[(13,'T')],62:[(10,'T')],61:[(15,'T')],60:[(20,'S')],
        59:[(19,'S')],58:[(18,'S')],57:[(17,'S')],56:[(16,'S')],
        55:[(15,'S')],54:[(14,'S')],53:[(13,'S')],52:[(12,'S')],
        51:[(11,'S')],50:[('BULL','D')],49:[(9,'S')],48:[(8,'S')],
        47:[(7,'S')],46:[(6,'S')],45:[(5,'S')],44:[(4,'S')],
        43:[(3,'S')],42:[(2,'S')],41:[(1,'S')],40:[(20,'D')],
        39:[(7,'S')],38:[(19,'D')],37:[(5,'S')],36:[(18,'D')],
        35:[(3,'S')],34:[(17,'D')],33:[(1,'S')],32:[(16,'D')],
        31:[(7,'S')],30:[(15,'D')],29:[(5,'S')],28:[(14,'D')],
        27:[(3,'S')],26:[(13,'D')],25:[(1,'S')],24:[(12,'D')],
        23:[(3,'S')],22:[(11,'D')],21:[(1,'S')],20:[(10,'D')],
        19:[(3,'S')],18:[(9,'D')],17:[(1,'S')],16:[(8,'D')],
        15:[(3,'S')],14:[(7,'D')],13:[(1,'S')],12:[(6,'D')],
        11:[(3,'S')],10:[(5,'D')],9:[(1,'S')],8:[(4,'D')],
        7:[(1,'S')],6:[(3,'D')],5:[(1,'S')],4:[(2,'D')],
        3:[(1,'S')],2:[(1,'D')],
    }

    # Checkout logic
    if score in checkout_map:
        seg, ring = checkout_map[score][0]
        if seg == 'BULL':
            return apply_jitter((360, 272)), random.randint(*settings['power_range'])
        pos = aim_for_ring(seg, ring)
        return apply_jitter(pos), random.randint(*settings['power_range'])

    # General scoring logic
    if score > 100:
        return apply_jitter(aim_for_ring(20, 'T')), random.randint(*settings['power_range'])
    if score == 50:
        return apply_jitter((360, 272)), random.randint(*settings['power_range'])
    return apply_jitter(aim_for_ring(20, 'T')), random.randint(*settings['power_range'])

# Dart throw simulation
def simulate_dart_throw(position, power):
    # Simulates the result of a dart throw

    x, y = position

    # Power affects accuracy
    if power < 20:   deviation_range = 35
    elif power < 40: deviation_range = 25
    elif power < 47: deviation_range = 15
    elif power > 80: deviation_range = 35
    elif power > 60: deviation_range = 25
    elif power > 53: deviation_range = 15
    else:            deviation_range = 5

    # Apply deviation
    x += random.randint(-deviation_range, deviation_range)
    y += random.randint(-deviation_range, deviation_range)

    # Calculate angle and distance from dartboard centre
    cx, cy = 360, 272
    dx, dy = x - cx, cy - y
    distance = math.hypot(dx, dy)
    angle = (math.degrees(math.atan2(-dy, dx)) + 360 + 90) % 360

    # Find sector
    sectors = [20,1,18,4,13,6,10,15,2,17,3,19,7,16,8,11,14,9,12,5]
    sector_index = int((angle + 9) // 18) % 20
    base_score = sectors[sector_index]

    # Assign score based on ring hit
    if distance < 15:
        return 50, True, (x, y) # Bullseye
    elif distance < 30:
        return 25, False, (x, y) # Outer bull
    elif 75 <= distance <= 105:
        return base_score * 3, False, (x, y)
    elif 140 <= distance <= 165:
        return base_score * 2, True, (x, y)
    elif distance < 165:
        return base_score, False, (x, y)
    else:
        return 0, False, (x, y)

# Helper functions
def wait_with_event_pump(ms):
    # Delays for ms milliseconds while processing events (prevents freezing)

    start = pygame.time.get_ticks()
    clock = pygame.time.Clock()
    while pygame.time.get_ticks() - start < ms:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit()
        clock.tick(60)

def safe_font(path, size):
    # Loads a font safely, falling back to system default if missing

    try:
        return pygame.font.Font(path, size)
    except Exception:
        return pygame.font.SysFont(None, size)

def safe_image(path, size=None):
    # Loads an image safely, returning a placeholder if missing

    try:
        img = pygame.image.load(path)
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        s = pygame.Surface(size if size else (50,50))
        s.fill((120,120,120))
        return s

# Main match loop
def aim_and_throw_dart(screen, player1_name, player2_name=None, ai_difficulty = get_ai_difficulty()):
    # Runs a darts match between player1 and player2 (human vs AI).
    # Handles scoring, leg/set/match progression, bust rules,
    # and animations for both AI and human throws.

    # Drawing helpers
    def draw_scoreboard(font):
        # Draws player names, scores, legs and sets on the scoreboard area.
 
        p1, p2 = state.player1, state.player2

        # Player 1 row (name in black for contrast, numeric values in white)
        screen.blit(font.render(f"{p1.name}", True, (0,0,0)), (430, 648))
        screen.blit(font.render(f"{p1.score}", True, (255,255,255)), (680, 648))
        screen.blit(font.render(f"{p1.legs}",  True, (255,255,255)), (646, 648))
        screen.blit(font.render(f"{p1.sets}",  True, (255,255,255)), (616, 648))

        # Player 2 row
        screen.blit(font.render(f"{p2.name}", True, (0,0,0)), (430, 690))
        screen.blit(font.render(f"{p2.score}", True, (255,255,255)), (680, 690))
        screen.blit(font.render(f"{p2.legs}",  True, (255,255,255)), (646, 690))
        screen.blit(font.render(f"{p2.sets}",  True, (255,255,255)), (616, 690))

    def draw_power_bar(pwr):
        # Draws the multi-colour power bar using blocks to show
        # zones (red / orange / yellow / green). The white line indicates current power
        # Power range is 0-100, mapped to pixels by multiplying by 3

        bar_x, bar_y = 30, 690
        bar_width, bar_height = 300, 20

        # Colour bands (visual feedback to the player for risk/reward)
        pygame.draw.rect(screen, (255,0,0),   (bar_x,     bar_y, 60, bar_height))
        pygame.draw.rect(screen, (255,120,0), (bar_x+60,  bar_y, 60, bar_height))
        pygame.draw.rect(screen, (255,200,0), (bar_x+120, bar_y, 21, bar_height))
        pygame.draw.rect(screen, (0,255,0),   (bar_x+141, bar_y, 18, bar_height))
        pygame.draw.rect(screen, (255,200,0), (bar_x+159, bar_y, 21, bar_height))
        pygame.draw.rect(screen, (255,120,0), (bar_x+180, bar_y, 60, bar_height))
        pygame.draw.rect(screen, (255,0,0),   (bar_x+240, bar_y, 60, bar_height))

        # Current power indicator (white vertical line)
        pygame.draw.line(screen, (255,255,255), (bar_x + pwr * 3, bar_y), (bar_x + pwr * 3, bar_y + bar_height), 2)

        # Outline of the whole bar
        pygame.draw.rect(screen, (255,255,255), (bar_x, bar_y, bar_width, bar_height), 2)

    def render_frame(show_ready_dart=True, ready_pos=None):
        # Centralised frame renderer.
        # - Draws board, scoreboard, power bar, crosshair and all previously thrown darts.
        # - Keeps visual state rendering consistent across animations and events.

        # Background & scoreboard
        screen.blit(dartboard, (0, 0))
        screen.blit(scoreboard_img, (420, 620))

        # Scores and player info
        draw_scoreboard(score_font)

        # Power bar displayed at the bottom-left
        draw_power_bar(power)

        # Crosshair
        pygame.draw.line(screen, (200,200,200), (crosshair.centerx-5, crosshair.centery-5), (crosshair.centerx+5, crosshair.centery+5), 2)
        pygame.draw.line(screen, (200,200,200), (crosshair.centerx-5, crosshair.centery+5), (crosshair.centerx+5, crosshair.centery-5), 2)

        # Previously-thrown darts (persist on the board until cleared)
        for pos in dart_poses:
            screen.blit(dart_image, (pos[0]-31, pos[1]-6))

        # Show the ready dart (pulled back while charging)
        if show_ready_dart and ready_pos is not None:
            screen.blit(dart_image, (ready_pos[0]-31, ready_pos[1]-6))

    def show_flash_and_text(message, text_color=(0,0,0), flash_color=(255,255,255), flash_time=1200):
        # overlay flash + message. Used for leg/set win messages and visual feedback
        # Renders the current frame first, then draws a overlay and message
        # wait_with_event_pump is used to avoid freezing

        # Render current frame (dartboard, scores, etc.)
        render_frame(show_ready_dart=False)

        # Make overlay
        overlay = pygame.Surface((720, 720))
        overlay.fill(flash_color)
        overlay.set_alpha(160)
        screen.blit(overlay, (0, 0))

        # Draw message centered on screen
        popup_font = safe_font(None, 48)
        popup_surf = popup_font.render(message, True, text_color)
        popup_rect = popup_surf.get_rect(center=(360, 360))
        screen.blit(popup_surf, popup_rect)

        pygame.display.flip()
        wait_with_event_pump(flash_time)

    def show_bust_flash():
        # Wrapper for showing a BUST screen

        play("bust")
        show_flash_and_text("BUST!")

    def reset_power_state():
        # Resets power-related state after a throw or when changing turns.
        # Declared with nonlocal so nested functions can modify outer-scope variables.

        nonlocal power, power_dir, charging, dart_ready, animating
        power = 0
        power_dir = 1
        charging = False
        dart_ready = True
        animating = False

    def animate_dart_throw(start_pos, end_pos):
        # frame-by-frame animation for a dart moving from start_pos to end_pos.
        # Uses render_frame to keep the background consistent between steps.

        steps = 18
        for i in range(steps):
            t = i / (steps - 1)
            # Straight-line animation
            x = int(start_pos[0] * (1 - t) + end_pos[0] * t)
            y = int(start_pos[1] * (1 - t) + end_pos[1] * t)

            # While animating, show the base/ready dart position (not charged)
            ready_pos = (dart_base_x, dart_base_y)
            render_frame(show_ready_dart=False, ready_pos=ready_pos)

            # Draw the moving dart on top
            screen.blit(dart_image, (x - 31, y - 6))
            pygame.display.flip()

            # Process events to avoid not responding and cap animation FPS
            pygame.event.pump()
            anim_clock.tick(75)

    # Setup before entering loop
    opponent_name = player2_name or generate_ai_name()
    state = GameState(player1_name, opponent_name, ai_difficulty)

    # Store turn start scores used for bust rollback
    state.player1.turn_start_score = state.player1.score
    state.player2.turn_start_score = state.player2.score

    # Load images (safe_image falls back to placeholders if assets are missing)
    ai_difficulty = get_ai_difficulty()
    dartboard = get_active_background()
    print("Loading background from:", dartboard)
    screen.blit(dartboard, (0, 0))
    scoreboard_img = safe_image(os.path.join("assets", "scoreboard.png"), (300,100))
    dart_image = safe_image(os.path.join("assets", "dart.png"), (60,60))

    # Crosshair initial position (centred near bull)
    crosshair = pygame.Rect(350, 262, 20, 20)

    # Origin point where darts "launch" from (player hand)
    dart_base_x, dart_base_y = 360, 550

    # Clocks for main loop and animations
    main_clock = pygame.time.Clock()
    anim_clock = pygame.time.Clock()

    # Font used for scoreboard text
    score_font = safe_font(None, 26)

    # Power / input state variables
    power = 0
    power_dir = 1
    charging = False
    dart_ready = True
    max_power = 100
    space_released = True
    animating = False

    # Persistent list of thrown dart positions to display on the board
    dart_poses = []

    # Main match loop
    while True:
        # Collect events once and iterate
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return "EXIT" # signalling to exit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    result = pause_menu(screen)
                    if result == "MENU":
                        return "MENU"  # quit to main menu

        # AI turn
        if state.current_player == state.player2:
            # Save starting score for bust rollback
            state.player2.turn_start_score = state.player2.score

            # AI gets up to 3 darts (may finish early)
            for _ in range(3):
                # Wait a short, randomised time while pumping events (makes AI feel realistic)
                wait_with_event_pump(random.randint(900,1500))

                # Decide where to aim and how hard to throw
                ai_target, ai_power = ai_select_target(state.player2.score, state.ai_difficulty)

                # Simulate the accuracy to get the actual result
                score, is_double, dart_pos = simulate_dart_throw(ai_target, ai_power)

                # animate from base to result
                start_pos = (dart_base_x, dart_base_y)
                animate_dart_throw(start_pos, dart_pos)
                play("hit")

                # Brief pause after the animation to make readable
                wait_with_event_pump(250)

                # Record landed dart visually and update score
                dart_poses.append(dart_pos)
                state.player2.darts_used_in_leg += 1
                state.player2.score -= score

                # check throw-based achievements (ton, 180)
                new_unlocked = check_achievements(p, "throw", {"points": score})
                for new_achievement in new_unlocked:
                    show_flash_and_text(f"Achievement Unlocked: {ACHIEVEMENTS[new_achievement]['name']}", text_color=(255,215,0))

                # bust rules: <0 or exactly 1 are invalid finishes -> end turn
                if state.player2.score < 0 or state.player2.score == 1:
                    show_bust_flash()
                    state.player2.score = state.player2.turn_start_score
                    dart_poses.clear() # remove thrown darts from board
                    state.current_player = state.player1
                    break

                # If exact zero: must be double to count as leg win
                if state.player2.score == 0:
                    if is_double:
                        # Valid leg finish
                        state.player2.legs += 1
                        state.player2.legs_won_total += 1

                        unlocked = check_achievements(p, "leg", meta={"is_double": is_double, "finish_points": score})
                        if unlocked:
                            for aid in unlocked:
                                print(f"Achievement unlocked: {aid}")

                        # leg-based achievements (first leg, leg hunter, checkout king)
                        new_unlocked = check_achievements(p, "leg", {"finish_points": score, "is_double": is_double})
                        for new_achievement in new_unlocked:
                            show_flash_and_text(f"Achievement Unlocked: {ACHIEVEMENTS[new_achievement]['name']}", text_color=(255,215,0))

                        state.player2.save_stats() # persist cumulative legs

                        # If leg-win leads to set-win
                        if state.player2.legs >= 3:
                            play("set_win")
                            state.player2.sets += 1

                            new_unlocked = check_achievements(p, "set", {})
                            for new_achievment in new_unlocked:
                                show_flash_and_text(f"Achievement Unlocked: {ACHIEVEMENTS[new_achievment]['name']}", text_color=(255,215,0))

                            state.player2.legs = 0
                            state.player1.legs = 0
                            show_flash_and_text(f"{state.player2.name} wins the set!")

                            # If set-win completes match
                            if state.player2.sets == 3:
                                play("win_match")
                                update_player_stats(state.player1)
                                update_player_stats(state.player2)
                                show_flash_and_text(f"{state.player2.name} wins the match!")
                                return state.player2.name
                        else:
                            # Leg won but match not over
                            play("leg_win")
                            show_flash_and_text(f"{state.player2.name} wins the leg!")

                        # Reset scores for next leg and give next turn to player1
                        state.player2.darts_used_in_leg = 0
                        state.player1.score = 501
                        state.player2.score = 501
                        dart_poses.clear()
                        state.current_player = state.player1
                        break
                    else:
                        # If finishing on non-double, count as bust (rule enforcement)
                        show_bust_flash()
                        state.player2.score = state.player2.turn_start_score
                        dart_poses.clear()
                        state.current_player = state.player1
                        break
            
            turn_points = state.current_player.turn_start_score - state.current_player.score
            unlocked = check_achievements(state.current_player, "turn_end", meta={"turn_points": turn_points})
            if unlocked:
                for aid in unlocked:
                    print(f"Achievement unlocked: {aid}")

            # After AI's up-to-3-darts loop: ensure control passes back to player
            if state.current_player == state.player2:
                # If AI still marked as current (didn't bust or win), switch to human
                state.current_player = state.player1
                state.player1.darts_left = 3
                dart_poses.clear()

            # Reset power visuals/state in case the player was mid-charge
            reset_power_state()

        # Human player turn
        # Movement of the crosshair using continuous key press detection
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  and crosshair.left > 0:     crosshair.move_ip(-2, 0)
        if keys[pygame.K_RIGHT] and crosshair.right < 720:  crosshair.move_ip( 2, 0)
        if keys[pygame.K_UP]    and crosshair.top > 0:      crosshair.move_ip(0, -2)
        if keys[pygame.K_DOWN]  and crosshair.bottom < 720: crosshair.move_ip(0,  2)

        # Handle key events from the batch collected earlier
        for event in events:
            # Begin charging power while spacebar is held
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and dart_ready and not charging and space_released and not animating:
                    charging = True
                    space_released = False

            # On release of spacebar perform the throw if properly charged
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                space_released = True
                if charging and dart_ready and not animating:
                    # Lock state for the duration of the throw
                    throw_power = power
                    charging = False
                    dart_ready = False
                    animating = True

                    # Save starting score at the beginning of the player's turn for bust rollback
                    if state.player1.darts_left == 3:
                        state.player1.turn_start_score = state.player1.score

                    # Calculate visual pullback of the dart depending on power
                    pullback = int((throw_power / max_power) * 30)
                    start_pos = (dart_base_x, dart_base_y + pullback)

                    # Determine actual throw outcome (score, double flag, landing position)
                    score, is_double, dart_pos = simulate_dart_throw(crosshair.center, throw_power)

                    # Animate dart travel and clear events afterwards to avoid accidental input
                    animate_dart_throw(start_pos, dart_pos)
                    play("hit")
                    pygame.event.clear()
                    animating = False

                    # Record and apply score
                    dart_poses.append(dart_pos)
                    p = state.current_player
                    p.score -= score
                    state.player1.darts_used_in_leg += 1

                    # check throw-based achievements (ton, 180)
                    new_unlocked = check_achievements(p, "throw", {"points": score})
                    for new_achievement in new_unlocked:
                        show_flash_and_text(f"Achievement Unlocked: {ACHIEVEMENTS[new_achievement]['name']}", text_color=(255,215,0))

                    # Bust handling
                    if p.score < 0 or p.score == 1:
                        # Invalid finish - turn is forfeit and score rolled back
                        show_bust_flash()
                        p.score = p.turn_start_score
                        p.darts_left = 3
                        # Switch to opponent (AI)
                        state.current_player = state.player2
                        state.player2.turn_start_score = state.player2.score
                        dart_poses.clear()
                        reset_power_state()

                    # Exact 0 score
                    elif p.score == 0:
                        if is_double:
                            # Valid finish -> award leg and possibly set/match
                            p.legs += 1
                            p.legs_won_total += 1

                            # leg-based achievements (first leg, leg hunter, checkout king)
                            new_unlocked = check_achievements(p, "leg", {"finish_points": score, "is_double": is_double})
                            for new_achievement in new_unlocked:
                                show_flash_and_text(f"Achievement Unlocked: {ACHIEVEMENTS[new_achievement]['name']}", text_color=(255,215,0))

                            p.save_stats()

                            # Set handling
                            if p.legs >= 3:
                                play("set_win")
                                p.sets += 1

                                new_unlocked = check_achievements(p, "set", {})
                                for new_achievment in new_unlocked:
                                    show_flash_and_text(f"Achievement Unlocked: {ACHIEVEMENTS[new_achievment]['name']}", text_color=(255,215,0))

                                p.legs = 0
                                (state.player1 if p is state.player2 else state.player2).legs = 0
                                show_flash_and_text(f"{p.name} wins the set!")

                                # Match win condition
                                if p.sets == 3:#
                                    play("win_match")
                                    update_player_stats(state.player1)
                                    update_player_stats(state.player2)
                                    show_flash_and_text(f"{p.name} wins the match!")
                                    return p.name
                            else:
                                # Leg won but match continues
                                play("leg_win")
                                show_flash_and_text(f"{p.name} wins the leg!")

                            # Reset for next leg
                            state.player1.darts_used_in_leg = 0
                            state.player1.score = 501
                            state.player2.score = 501
                            state.player1.darts_left = 3
                            state.player2.darts_left = 3
                            state.current_player = state.player1
                            dart_poses.clear()
                            reset_power_state()

                        # Must finish on a double - otherwise treated as a bust
                        else:
                            show_bust_flash()
                            p.darts_left = 3
                            state.current_player = state.player2
                            state.player2.turn_start_score = state.player2.score
                            dart_poses.clear()
                            reset_power_state()
                    
                    # Non-finishing result
                    else:
                        # Decrement remaining darts for this player's turn
                        p.darts_left -= 1

                        # If out of darts, switch to opponent
                        if p.darts_left == 0:
                            turn_points = state.current_player.turn_start_score - state.current_player.score
                            unlocked = check_achievements(state.current_player, "turn_end", meta={"turn_points": turn_points})
                            if unlocked:
                                for aid in unlocked:
                                    print(f"Achievement unlocked: {aid}")
                            p.darts_left = 3
                            state.current_player = state.player2
                            state.player2.turn_start_score = state.player2.score
                            dart_poses.clear()
                        
                        # Prepare visual/power state for next dart (either same player or opponent)
                        reset_power_state()

        # power charge oscillation
        if charging:
            if power_dir == 1:
                power += 2
                if power >= max_power:
                    power_dir = -1
            else:
                power -= 2
                if power <= 0:
                    power_dir = 1

        # Pullback visual for the ready dart (makes power visible as movement)
        pullback = int((power / max_power) * 30) if charging else 0
        ready_dart_pos = (dart_base_x, dart_base_y + pullback)

        # Final render for this tick
        render_frame(show_ready_dart=True, ready_pos=ready_dart_pos)
        pygame.display.flip()
        main_clock.tick(60)