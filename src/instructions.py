# Displays an instructions/help screen with a background image.

import pygame
import os
from sound_manager import play

def display_instructions(screen):
    clock = pygame.time.Clock()

    # Load background
    bg_path = os.path.join("assets", "how_to_play.png")
    try:
        background = pygame.image.load(bg_path)
        background = pygame.transform.scale(background, (720, 720))
    except Exception:
        background = pygame.Surface((720, 720))
        background.fill((30, 30, 30))

    while True:
        screen.blit(background, (0, 0))
        pygame.display.flip()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_BACKSPACE, pygame.K_ESCAPE):
                    play("menu_select")
                    return  # back to pause menu

        clock.tick(60)