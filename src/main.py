import pygame
from menus import main_menu
import sys
from sound_manager import init_sounds

def main():
    # Initialise pygame
    pygame.init()
    init_sounds()

    # Create the game window (720x720)
    screen = pygame.display.set_mode((720, 720))
    pygame.display.set_caption("Precision Darts")

    # Call the main menu loop
    while True:
        result = main_menu(screen)
        if result == "EXIT":
            pygame.quit()
            break

# Run the program only if this file is executed directly
if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pygame.quit()
        sys.exit()