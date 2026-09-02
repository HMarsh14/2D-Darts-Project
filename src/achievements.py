# This file defines all possible achievements in the game.

ACHIEVEMENTS = {
    "first_leg": {
        "name": "First Leg", # Unlocked once a player has won their first ever leg
        "description": "Win your first leg",
        "trigger": "leg",
        "condition": lambda player, meta: player.legs_won_total == 1,
    },
    "leg_hunter": {
        "name": "Leg Hunter", # Unlocked once a player has won 50 total legs
        "description": "Win 50 legs (total)",
        "trigger": "leg",
        "condition": lambda player, meta: player.legs_won_total >= 50,
    },
    "set_master": {
        "name": "Set Master", # Unlocked once a player has won their first ever leg
        "description": "Win 25 sets (total)",
        "trigger": "set",
        "condition": lambda player, meta: player.sets >= 25,
    },
    "champion": {
        "name": "Champion", # Unlocked once a player has won a tournament
        "description": "Win a tournament", 
        "trigger": "tournament",
        "condition": lambda player, meta: player.tournaments_won >= 1,
    },
    "ton_scorer": {
        "name": "Ton Scorer", # Unlocked once a player has won scored over 100 with 3 darts
        "description": "Score 100+ points in a single turn",
        "trigger": "turn_end",
        "condition": lambda player, meta: (meta or {}).get("turn_points", 0) >= 100,
    },
    "one_eighty": {
        "name": "180!", # Unlocked once a player has won scored a perfect 180 with 3 darts
        "description": "Hit a perfect 180 in a single turn",
        "trigger": "turn_end",
        "condition": lambda player, meta: (meta or {}).get("turn_points", 0) == 180,
    },
    "checkout_king": {
        "name": "Checkout King", # Unlocked once a player has won a leg finishing on double 20
        "description": "Win a leg by double 20 (D20)",
        "trigger": "leg",
        "condition": lambda player, meta: (meta or {}).get("is_double", False) and (meta or {}).get("finish_points", 0) == 40,
    },
    "nine_darter": {
    "name": "Nine Darter", # Unlocked once a player has scored a perfect leg in only 9 darts (the minimum possible)
    "description": "Complete a leg in just 9 darts",
    "trigger": "leg",
    "condition": lambda player, meta: player.darts_used_in_leg == 9,
    },
}


def check_achievements(player, event, meta=None):
    # Check all achievements that trigger on 'event' for 'player'.
    # If any new ones are unlocked, call player's unlock_achievement and return list of unlocked achievement ids.

    meta = meta or {}
    unlocked = []
    for aid, info in ACHIEVEMENTS.items():
        if info.get("trigger") != event:
            continue # Only check achievements that match this event
        try:
            if info["condition"](player, meta): # Check if achievement condition is met
                if player.unlock_achievement(aid): # Save to leaderboard if newly unlocked
                    unlocked.append(aid) # Add to list of new unlocks
        except Exception as e:
            print(f"[achievements] error checking {aid}: {e}") # I added this to print the error and not crash the game 
    return unlocked