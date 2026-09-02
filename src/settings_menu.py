import pygame
import os
import sys
from sound_manager import (
    set_music_volume,
    play_music,
    stop_music,
    set_muted,
    muted,           # Import the global mute flag
    music_volume,    # Import global music volume
    sfx_volume,      # Import global sfx volume
)
from background_manager import (
    cycle_background,
    apply_selected_background,
    get_selected_background_name,
    get_ai_difficulty,
    cycle_ai_difficulty
)

FONT = "freesansbold.ttf"

# Track live adjustments during the settings session
music_volume = music_volume
sfx_volume = sfx_volume
muted = muted

def settings_menu(screen):
    global music_volume, sfx_volume, muted

    clock = pygame.time.Clock()
    selected_option = 0
    options = ["Background", "AI Difficulty", "Music Volume", "SFX Volume", "Mute / Unmute", "Back"]

    # Load settings background
    bg_path = os.path.join("assets", "settings.png")
    try:
        background = pygame.image.load(bg_path)
        background = pygame.transform.scale(background, (720, 720))
    except Exception:
        background = pygame.Surface((720, 720))
        background.fill((200, 0, 0))

    while True:
        screen.blit(background, (0, 0))
        option_font = pygame.font.Font(FONT, 34)

        # Text labels
        bg_text = f"Background: {get_selected_background_name()}"
        ai_text = f"AI Difficulty: {get_ai_difficulty().capitalize()}"
        music_text = f"Music Volume: {int(music_volume * 100)}%"
        sfx_text = f"SFX Volume: {int(sfx_volume * 100)}%"
        mute_text = "Muted" if muted else "Unmuted"

        labels = [bg_text, ai_text, music_text, sfx_text, mute_text, "Back"]

        for i, label in enumerate(labels):
            color = (255, 0, 0) if i == selected_option else (0, 0, 0)
            surf = option_font.render(label, True, color)
            screen.blit(surf, surf.get_rect(center=(360, 170 + i * 95)))

        pygame.display.flip()

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)

                elif event.key == pygame.K_LEFT:
                    if options[selected_option] == "Background":
                        cycle_background(-1)
                    elif options[selected_option] == "AI Difficulty":
                        cycle_ai_difficulty(-1)
                    elif options[selected_option] == "Music Volume":
                        music_volume = max(0.0, music_volume - 0.01)
                        set_music_volume(music_volume)
                    elif options[selected_option] == "SFX Volume":
                        sfx_volume = max(0.0, sfx_volume - 0.05)

                elif event.key == pygame.K_RIGHT:
                    if options[selected_option] == "Background":
                        cycle_background(1)
                    elif options[selected_option] == "AI Difficulty":
                        cycle_ai_difficulty(1)
                    elif options[selected_option] == "Music Volume":
                        music_volume = min(1.0, music_volume + 0.01)
                        set_music_volume(music_volume)
                    elif options[selected_option] == "SFX Volume":
                        sfx_volume = min(1.0, sfx_volume + 0.05)

                elif event.key == pygame.K_RETURN:
                    if options[selected_option] == "Mute / Unmute":
                        muted = not muted
                        set_muted(muted)  # Sync global mute flag

                        if muted:
                            stop_music()
                        else:
                            # Resume the menu music only if not muted
                            play_music("menu_music")
                    elif options[selected_option] == "Background":
                        apply_selected_background()
                    elif options[selected_option] == "Back":
                        return
                elif event.key == pygame.K_BACKSPACE:
                    return

        clock.tick(60)