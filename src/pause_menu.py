# pause_menu.py
import pygame
import os
from instructions import display_instructions
from sound_manager import play

FONT = "freesansbold.ttf"

def pause_menu(screen):
    clock = pygame.time.Clock()

    # Load background image
    bg_path = os.path.join("assets", "pause_menu.png")
    try:
        background = pygame.image.load(bg_path)
        background = pygame.transform.scale(background, (720, 720))
    except Exception:
        background = pygame.Surface((720, 720))
        background.fill((30, 30, 30))

    options = ["Resume", "Instructions", "Quit to Main Menu"]
    selected_index = 0

    while True:
        screen.blit(background, (0, 0))

        # Draw menu options
        font = pygame.font.Font(FONT, 40)
        for i, option in enumerate(options):
            color = (255, 0, 0) if i == selected_index else (0, 0, 0)
            surf = font.render(option, True, color)
            screen.blit(surf, surf.get_rect(center=(360, 230 + i * 130)))

        pygame.display.flip()

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "quit"
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
                    if selected == "Resume":
                        return None
                    elif selected == "Instructions":
                        display_instructions(screen)
                    elif selected == "Quit to Main Menu":
                        return "MENU"

        clock.tick(60)