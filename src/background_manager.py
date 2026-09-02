import os
import pygame

# Gameplay backgrounds
BACKGROUND_OPTIONS = [
    os.path.join("assets", "background_classic.png"),
    os.path.join("assets", "background_brick.png"),
    os.path.join("assets", "background_wood.png"),
]

# Persistent global state
active_background = BACKGROUND_OPTIONS[0]    # Used in gameplay
selected_background = BACKGROUND_OPTIONS[0]  # Previewed in settings
current_ai_difficulty = "intermediate"       # Global AI difficulty

# Manage backgrounds

def get_active_background():
    # Returns a loaded pygame.Surface for the active gameplay background
    try:
        img = pygame.image.load(active_background)
        return pygame.transform.scale(img, (720, 720))
    except Exception as e:
        print(f"[background_manager] Error loading background: {e}")
        fallback = pygame.Surface((720, 720))
        fallback.fill((80, 80, 80))
        return fallback

def get_selected_background_name():
    # Returns the name of the currently selected background
    base = os.path.basename(selected_background).replace("background_", "").replace(".png", "")
    return base.capitalize()

def cycle_background(direction=1):
    # Cycles between background options
    global selected_background
    index = BACKGROUND_OPTIONS.index(selected_background)
    index = (index + direction) % len(BACKGROUND_OPTIONS)
    selected_background = BACKGROUND_OPTIONS[index]

def apply_selected_background():
    # Applies the selected background to gameplay
    global active_background
    active_background = selected_background

# AI management

AI_LEVELS = ["beginner", "intermediate", "advanced"]

def get_ai_difficulty():
    # Returns the current AI difficulty level
    return current_ai_difficulty

def cycle_ai_difficulty(direction=1):
    # Cycles AI difficulty between beginner/intermediate/advanced
    global current_ai_difficulty
    index = AI_LEVELS.index(current_ai_difficulty)
    index = (index + direction) % len(AI_LEVELS)
    current_ai_difficulty = AI_LEVELS[index]