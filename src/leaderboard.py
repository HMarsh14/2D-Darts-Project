# Responsible for displaying the leaderboard screen.
# Supports multiple categories (legs won, tournaments won,
# achievements unlocked) and sorts players accordingly.

import pygame
import sys
import os
from leaderboard_data import load_leaderboard
from sound_manager import play

# Global font & colours used for consistency
FONT_NAME = "freesansbold.ttf"
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)

# Categories available in the leaderboard screen
CATEGORIES = ["legs", "tournaments", "achievements"]

# Text Rendering Helpers
def draw_text(surface, text, size, x, y, color=BLACK):
    # Draws plain text at (x,y) with given font size
    font = pygame.font.Font(FONT_NAME, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

def highlight_text(surface, text, size, x, y, selected=False):
    # Draws text, highlighted in red if currently selected
    font = pygame.font.Font(FONT_NAME, size)
    color = RED if selected else BLACK
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)

# Main Leaderboard Display Function
def display_leaderboard(screen):
    # Shows the leaderboard screen.
    # Allows the player to switch categories with arrow keys.
    # Displays top 5 players sorted by selected stat.
    # Backspace returns to main menu.

    # Attempt to load background image, else fallback is a plain surface
    bg_path = os.path.join("assets", "leaderboard.png")
    try:
        background = pygame.image.load(bg_path)
        background = pygame.transform.scale(background, (720, 720))
    except Exception:
        background = pygame.Surface((720, 720))
        background.fill((235, 235, 235))

    current_category_index = 0
    clock = pygame.time.Clock()

    players_data = load_leaderboard()

    # Transform JSON data into objects for easier sorting
    players = [
        type("P", (), {"name": name, **stats})
        for name, stats in players_data.items()
    ]

    running = True
    while running:
        screen.blit(background, (0, 0))

        # Draw category selection row (legs / tournaments / achievements)
        current_category = CATEGORIES[current_category_index]
        x_positions = [120, 360, 600]
        for i, category in enumerate(CATEGORIES):
            highlight_text(screen, category.capitalize(), 26, x_positions[i], 142, selected=(i == current_category_index))

        # Sort players by chosen category
        if current_category == "legs":
            sorted_players = sorted(players, key=lambda p: getattr(p, "legs_won_total", 0), reverse=True)
        elif current_category == "tournaments":
            sorted_players = sorted(players, key=lambda p: getattr(p, "tournaments_won", 0), reverse=True)
        else:
            sorted_players = sorted(players, key=lambda p: getattr(p, "achievements_unlocked", 0), reverse=True)

        # Draw top 5 players
        x_rank = 150
        x_name = 360
        x_value = 570
        y = 230
        for rank, p in enumerate(sorted_players[:5], start=1):
            if current_category == "legs":
                stat = f"{getattr(p, 'legs_won_total', 0)}"
            elif current_category == "tournaments":
                stat = f"{getattr(p, 'tournaments_won', 0)}"
            else:
                stat = f"{getattr(p, 'achievements_unlocked', 0)}"

            # Draw each column separately
            draw_text(screen, f"{rank}.", 30, x_rank, y)
            draw_text(screen, p.name, 30, x_name, y)
            draw_text(screen, stat, 30, x_value, y)
            y += 98 # vertical spacing

        # Navigation instructions
        draw_text(screen, "Arrow Keys Change Category | Backspace to Return", 20, 360, 680, BLACK)
        pygame.display.flip()

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_category_index = (current_category_index - 1) % len(CATEGORIES)
                elif event.key == pygame.K_RIGHT:
                    current_category_index = (current_category_index + 1) % len(CATEGORIES)
                elif event.key == pygame.K_BACKSPACE:
                    play("menu_select")
                    running = False

        clock.tick(60)