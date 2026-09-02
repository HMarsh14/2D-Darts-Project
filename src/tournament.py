# Implements the Tournament class
# Seeds human player and AI opponents
# Displays matchups and results
# Updates player stats on leaderboard

import random
import pygame
import sys
import os
from leaderboard_data import ensure_player_exists, load_leaderboard
from game import aim_and_throw_dart, Player, generate_ai_name
from achievements import check_achievements, ACHIEVEMENTS
from sound_manager import fade_to_music
from background_manager import get_ai_difficulty

FONT = "freesansbold.ttf"

# Utility Functions
def wait_with_event_pump(ms):
    # Delays for ms milliseconds while still processing pygame events (prevents freeze)

    start = pygame.time.get_ticks()
    clock = pygame.time.Clock()
    while pygame.time.get_ticks() - start < ms:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)

def show_message(screen, text, size=36, color=(255,255,255), ms=1500):
    # Displays a temporary message in the middle of the screen

    font = pygame.font.Font(FONT, size)
    screen.fill((0,0,0))
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(360, 360))
    screen.blit(surf, rect)
    pygame.display.flip()
    wait_with_event_pump(ms)

def show_round_pairings(screen, pairs):
    # Displays the pairings for a tournament round

    # Maps the round to its background
    bg_files = {
        16: "round_of_16.png",
        8:  "quarter_finals.png",
        4:  "semi_finals.png",
        2:  "final.png",
    }

    # Custom layout values for each round
    layout_settings = {
        16: {"start_y": 177, "spacing_y": 63},
        8: {"start_y": 265, "spacing_y": 63},
        4: {"start_y": 325, "spacing_y": 63},
        2: {"start_y": 360, "spacing_y": 0},
    }

    num_players = len(pairs) * 2
    bg_filename = bg_files.get(num_players, "blank_background.png")
    layout = layout_settings.get(num_players, layout_settings[16])  # fallback to round of 16 layout

    # Load and scale background
    try:
        bg = pygame.image.load(os.path.join("assets", bg_filename))
        bg = pygame.transform.scale(bg, (720, 720))
    except Exception:
        bg = pygame.Surface((720, 720))
        bg.fill((200, 0, 0))

    # Fonts
    name_font = pygame.font.Font(FONT, 28)

    # Draw background
    screen.blit(bg, (0, 0))

    # Positions for names
    left_x = 150
    right_x = 580
    start_y = layout["start_y"]
    spacing_y = layout["spacing_y"]

    for i, (p1, p2) in enumerate(pairs):
        y = start_y + i * spacing_y

        left_name = name_font.render(p1.name, True, (0, 0, 0))
        right_name = name_font.render(p2.name, True, (0, 0, 0))
        screen.blit(left_name, left_name.get_rect(center=(left_x, y)))
        screen.blit(right_name, right_name.get_rect(center=(right_x, y)))

    pygame.display.flip()
    wait_with_event_pump(4000)

# Tournament Class
class Tournament:
    # Represents a knockout-style tournament with 16 players (adjustable however).
    # Seeds a human player alongside AI players, then runs matches until a winner is found.

    def __init__(self, screen, human_name, ai_difficulty=get_ai_difficulty(), num_players=16):
        if num_players not in (2,4,8,16,32,64):
            raise ValueError("num_players must be power of two (2,4,8,16,...)")
        self.screen = screen
        self.human_name = human_name
        self.ai_difficulty = ai_difficulty
        self.num_players = num_players
        self.players = self._seed_players()

    def _reset_for_next_round(self, player):
        # Resets player's in-match stats for the next round

        player.score = 501
        player.darts_left = 3
        player.legs = 0
        player.sets = 0

    def _seed_players(self):
        # Human player is added first
        # AI opponents generated with unique names
        # All opponents ensured in leaderboard

        roster = [Player(self.human_name, self._get_player_data(self.human_name))]
        used = {self.human_name.lower()}  # names in this tournament

        while len(roster) < self.num_players:
            ai_name = "AI_" + generate_ai_name()

            # keep regenerating name until it's unique in the tournament
            while ai_name.lower() in used:
                ai_name = "AI_" + generate_ai_name()

            # ensure it's in leaderboard
            ensure_player_exists(ai_name)
            roster.append(Player(ai_name, self._get_player_data(ai_name)))
            used.add(ai_name.lower())

        random.shuffle(roster)
        return roster

    def _get_player_data(self, name):
        # Fetches leaderboard entry for a given player name

        return load_leaderboard().get(name)

    def run(self, simulate=False):
        # Executes the tournament until a champion is found

        round_num = 1
        current = self.players[:]

        while len(current) > 1:
            winners = []
            pairs = [(current[i], current[i+1]) for i in range(0, len(current), 2)]
            show_round_pairings(self.screen, pairs)

            for p1, p2 in pairs:
                if simulate:
                # Always pick a random winner for testing
                    winner_name = random.choice([p1.name, p2.name])
                # Human-involved match
                elif p1.name == self.human_name or p2.name == self.human_name:
                    if p1.name == self.human_name:
                        winner_name = aim_and_throw_dart(self.screen, p1.name, p2.name, self.ai_difficulty)
                    else:
                        winner_name = aim_and_throw_dart(self.screen, p2.name, p1.name, self.ai_difficulty)
                else:
                    # AI vs AI -> random winner
                    winner_name = random.choice([p1.name, p2.name])

                # Convert winner_name -> actual Player object
                if winner_name in ("MENU", "EXIT"):
                    fade_to_music("menu_music", fade_ms=1500)
                    return winner_name
                if winner_name == p1.name:
                    winner = p1
                else:
                    winner = p2

                self._reset_for_next_round(winner)
                winners.append(winner)

            current = winners
            round_num += 1

        # Champion found
        champion = current[0]
        ensure_player_exists(champion.name)  # make sure entry exists
        champion.tournaments_won += 1
        champion.save_stats()

        new_unlocked = check_achievements(champion, "tournament", {})
        for new_achievement in new_unlocked:
            show_message(self.screen, f"Achievement Unlocked: {ACHIEVEMENTS[new_achievement]['name']}!", size=28, color=(255,215,0), ms=1500)
        
        # Display winner
        bg_path = os.path.join("assets", "blank_background.png")
        try:
            bg_img = pygame.image.load(bg_path)
            bg_img = pygame.transform.scale(bg_img, (720, 720))
        except:
            bg_img = None

        # Show winner screen
        font_big = pygame.font.Font(FONT, 56)
        font_small = pygame.font.Font(FONT, 32)

        self.screen.fill((0, 0, 0))
        if bg_img:
            self.screen.blit(bg_img, (0, 0))

        text = font_big.render(f"Tournament Winner!", True, (255, 215, 0))
        rect = text.get_rect(center=(360, 260))
        self.screen.blit(text, rect)

        champ_text = font_small.render(f"{champion.name}", True, (255, 255, 255))
        champ_rect = champ_text.get_rect(center=(360, 360))
        self.screen.blit(champ_text, champ_rect)

        pygame.display.flip()
        wait_with_event_pump(4000)  # pause for 4 seconds