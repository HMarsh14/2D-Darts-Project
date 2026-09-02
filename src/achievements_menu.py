import pygame
import os
from achievements import ACHIEVEMENTS
from leaderboard_data import load_leaderboard
from sound_manager import play

FONT = "freesansbold.ttf"

def display_achievements(screen, gamertag):
    clock = pygame.time.Clock()

    # Load player data from leaderboard
    lb = load_leaderboard()
    pdata = lb.get(gamertag, {})

    unlocked = pdata.get("achievements", []) # Which achievements have been unlocked
    counts = pdata.get("achievement_counts", {}) # Track how many times an achievement has been earned
    achievement_ids = list(ACHIEVEMENTS.keys())
    current_index = 0

    # Load trophy images for locked/unlocked
    gold_path = os.path.join("assets", "gold_trophy.png")
    grey_path = os.path.join("assets", "grey_trophy.png")
    try:
        trophy_gold = pygame.image.load(gold_path)
        trophy_gold = pygame.transform.scale(trophy_gold, (720, 720))
        trophy_grey = pygame.image.load(grey_path)
        trophy_grey = pygame.transform.scale(trophy_grey, (720, 720))
    except Exception:
        # Fallback if images can't load
        trophy_gold = pygame.Surface((720, 720)); trophy_gold.fill((255,215,0))
        trophy_grey = pygame.Surface((720, 720)); trophy_grey.fill((120,120,120))

    while True:

        # Title
        title_font = pygame.font.Font(FONT, 60)
        title = title_font.render("Achievements", True, (255,255,255))
        screen.blit(title, title.get_rect(center=(360, 80)))

        # Current achievement info
        aid = achievement_ids[current_index]
        info = ACHIEVEMENTS[aid]

        # Draw trophy
        unlocked_status = aid in unlocked
        trophy = trophy_gold if unlocked_status else trophy_grey
        screen.blit(trophy, (0, 0))

        # Name + description of achievements
        name_font = pygame.font.Font(FONT, 36)
        desc_font = pygame.font.Font(FONT, 24)

        name_text = name_font.render(info["name"], True, (255,255,255))
        desc_text = desc_font.render(info["description"], True, (255,255,255))

        screen.blit(name_text, name_text.get_rect(center=(360, 550)))
        screen.blit(desc_text, desc_text.get_rect(center=(360, 600)))

        # Draw the counter number on the trophy if more than 1
        count = counts.get(aid, 0)
        if count > 1:
            counter_font = pygame.font.Font(FONT, 48)
            counter_surf = counter_font.render(str(count), True, (0,0,0))
            counter_rect = counter_surf.get_rect(center=(360, 300))  # center of trophy
            screen.blit(counter_surf, counter_rect)

        # Navigation Instructions
        hint_font = pygame.font.Font(FONT, 20)
        hint = hint_font.render("Arrow Keys to scroll, Backspace to return", True, (255,255,255))
        screen.blit(hint, hint.get_rect(center=(360, 680)))

        pygame.display.flip()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_index = (current_index - 1) % len(achievement_ids)
                elif event.key == pygame.K_RIGHT:
                    current_index = (current_index + 1) % len(achievement_ids)
                elif event.key == pygame.K_BACKSPACE:
                    play("menu_select")
                    return  # back to menu

        clock.tick(60)