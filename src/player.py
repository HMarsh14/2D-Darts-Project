import re
from leaderboard_data import load_leaderboard, save_leaderboard, hash_password

# Validation of gamertag
def validate_gamertag(name, for_registration=True):
    # Validates a new gamertag.
    # Length must be between 3 and 12 characters
    # Only alphanumeric characters allowed
    # Must not already exist (if registering)

    if not (3 <= len(name) <= 12):
        return False, "Gamertag must be 3–12 characters."
    if not re.match(r"^[A-Za-z0-9]+$", name):
        return False, "Only letters and numbers allowed."
    accounts = get_all_gamertags()
    if for_registration and name.lower() in accounts:
        return False, "Gamertag already taken."
    return True, "Valid."

# Get Existing Gamertags
def get_all_gamertags():
    # Returns dictionary of all gamertags and their password hashes

    lb = load_leaderboard()
    return {name.lower(): data.get("password_hash", "") for name, data in lb.items()}

# Saving new gamertag
def save_gamertag(name, password):
    # Saves a new gamertag to the leaderboard file.
    # The password is hashed before storage.
    # Default player stats are set to zero.

    lb = load_leaderboard()
    lb[name] = {
        "password_hash": hash_password(password),
        "legs_won_total": 0,
        "tournaments_won": 0,
        "achievements_unlocked": 0
    }
    save_leaderboard(lb)