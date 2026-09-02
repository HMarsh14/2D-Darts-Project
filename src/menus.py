# Handles all menu screens
# Provides navigation between game start, leaderboard,
# achievements, and settings.

import pygame
import os
import sys
from player import validate_gamertag, save_gamertag, get_all_gamertags
from leaderboard import display_leaderboard
from leaderboard_data import hash_password
from achievements_menu import display_achievements
from tournament import Tournament
from sound_manager import play_music, fade_to_music, play
from settings_menu import settings_menu
from background_manager import get_ai_difficulty

BLACK = (0, 0, 0)
RED   = (255, 0, 0)
FONT_NAME = "freesansbold.ttf"

BG_PATH = os.path.join("assets", "main_menu.png")

# keep a single global current gamertag
current_gamertag = None

# Utility text drawing
def draw_text(surface, text, size, x, y, selected=False):
    font = pygame.font.Font(FONT_NAME, size)
    color = RED if selected else BLACK
    surf = font.render(text, True, color)
    surface.blit(surf, surf.get_rect(center=(x, y)))

# Main menu
def main_menu(screen):
    global current_gamertag

    play_music("menu_music")
    clock = pygame.time.Clock()
    options = ["Start", "Leaderboard", "Achievements", "Settings", "Exit"]
    selected_index = 0

    # Load background or fallback to grey
    try:
        background = pygame.image.load(BG_PATH)
        background = pygame.transform.scale(background, (720, 720))
    except Exception:
        background = pygame.Surface((720, 720))
        background.fill((50, 50, 50))

    while True:
        screen.blit(background, (0, 0))

        # Draw menu options
        for i, option in enumerate(options):
            draw_text(screen, option, 40, 360, 165 + i * 120, selected=(i == selected_index))

        pygame.display.flip()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Ask main to exit
                return "EXIT"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    play("menu_move")
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    play("menu_select")
                    selected = options[selected_index]
                    if selected == "Exit":
                        fade_to_music("menu_music", fade_ms=1500)
                        return "EXIT"
                    elif selected == "Start":
                        # Gamertag login/registration before starting tournament
                        player_name = gamertag_screen(screen)
                        # Change audio track
                        fade_to_music("game_music", fade_ms=1500)
                        # set global current_gamertag
                        if player_name:
                            current_gamertag = player_name
                        # run tournament
                        result = Tournament(screen, player_name, ai_difficulty=get_ai_difficulty(), num_players=16).run()
                        if result == "EXIT":
                            pygame.quit()
                            sys.exit()
                    elif selected == "Leaderboard":
                        # display_leaderboard is blocking until Backspace, so call directly
                        display_leaderboard(screen)
                    elif selected == "Achievements":
                        # If a player is logged in use that, otherwise force gamertag flow
                        if current_gamertag:
                            display_achievements(screen, current_gamertag)
                        else:
                            player_name = gamertag_screen(screen)
                            if player_name:
                                current_gamertag = player_name
                                display_achievements(screen, current_gamertag)
                    elif selected == "Settings":
                        settings_menu(screen)

        clock.tick(60)

# Gamertag Login / Registration Screen
def gamertag_screen(screen):

    global current_gamertag
    clock = pygame.time.Clock()
    font = pygame.font.Font("freesansbold.ttf", 32)

    input_box = pygame.Rect(210, 360, 300, 50)
    gamertag = ""
    password = ""
    error_msg = ""
    entering_password = False
    login_mode = False

    accounts = get_all_gamertags()

    # Load background or fallback
    bg_path = os.path.join("assets", "blank_background.png")
    try:
        background = pygame.image.load(bg_path)
        background = pygame.transform.scale(background, (720, 720))
    except Exception:
        background = pygame.Surface((720, 720))
        background.fill((30, 30, 30))

    while True:
        screen.blit(background, (0, 0))

        # Display prompt depending on stage
        prompt_text = "Enter your gamertag:" if not entering_password else "Enter your password:"
        prompt = font.render(prompt_text, True, (255, 255, 255))
        screen.blit(prompt, (180, 280))

        # Mask password input
        display_value = "*" * len(password) if entering_password else gamertag
        txt_surface = font.render(display_value, True, (255, 255, 255))
        screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)

        # Show error messages (orange text)
        if error_msg:
            error_surface = font.render(error_msg, True, (255, 165, 0))
            screen.blit(error_surface, (100, 440))

        pygame.display.flip()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if not entering_password:
                        # If gamertag exists -> login mode
                        if gamertag.lower() in accounts:
                            entering_password = True
                            login_mode = True
                            error_msg = ""
                        else:
                            # Else -> validate new gamertag
                            valid, message = validate_gamertag(gamertag)
                            if valid:
                                entering_password = True
                                login_mode = False
                                error_msg = ""
                            else:
                                error_msg = message
                    else:
                        if login_mode:
                            # Authenticate login attempt
                            if accounts.get(gamertag.lower(), "") == hash_password(password):
                                current_gamertag = gamertag
                                return gamertag
                            error_msg = "Incorrect password."
                            password = ""
                        else:
                            # Register new account
                            save_gamertag(gamertag, password)
                            current_gamertag = gamertag
                            return gamertag

                elif event.key == pygame.K_BACKSPACE:
                    if entering_password:
                        password = password[:-1]
                    else:
                        gamertag = gamertag[:-1]
                elif event.unicode and event.unicode.isprintable():
                    if entering_password and len(password) < 12:
                        password += event.unicode
                    elif not entering_password and len(gamertag) < 12:
                        gamertag += event.unicode

        clock.tick(60)