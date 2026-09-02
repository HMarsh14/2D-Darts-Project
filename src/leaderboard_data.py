# Handles all interactions with the leaderboard.json file.
# Responsible for saving player stats, creating new players,
# password hashing, and authentication.

import json
import os
import hashlib

LEADERBOARD_FILE = "leaderboard.json"

# Password Handling
def hash_password(password):
    # Hash the password for security
    return hashlib.sha256(password.encode()).hexdigest()

# File I/O Functions
def load_leaderboard():
    # Loads leaderboard data from JSON
    # Returns empty dictionary if file not found
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_leaderboard(data):
    # Saves leaderboard dictionary back to JSON
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# Player creation and authentication
def create_player(gamertag, password):
    # Creates a new player account if gamertag not already taken
    lb = load_leaderboard()
    if gamertag in lb:
        return None # Prevents overwriting existing account
    lb[gamertag] = {
    "password_hash": hash_password(password),
    "legs_won_total": 0,
    "tournaments_won": 0,
    "achievements_unlocked": 0,
    "achievements": []
}
    save_leaderboard(lb)
    return lb[gamertag]

def authenticate_player(gamertag, password):
    # Verifies gamertag + password combination
    lb = load_leaderboard()
    entry = lb.get(gamertag)
    if not entry:
        return None
    return entry if entry.get("password_hash") == hash_password(password) else None

def ensure_player_exists(gamertag):
    # Ensures that a player entry exists in the leaderboard
    # Used for AI players that don’t require passwords
    lb = load_leaderboard()
    if gamertag not in lb:
        lb[gamertag] = {
            "password_hash": "",
            "legs_won_total": 0,
            "tournaments_won": 0,
            "achievements_unlocked": 0,
            "achievements": []
        }
        save_leaderboard(lb)
    return lb[gamertag]

# Update Stats
def update_tournaments_won(player_name):
    # Increments the tournament win count for the given player
    data = load_leaderboard()
    if player_name not in data:
        # Create entry if it doesn’t exist
        data[player_name] = {
            "password_hash": "",
            "legs_won_total": 0,
            "tournaments_won": 0,
            "achievements_unlocked": 0
        }
    data[player_name]["tournaments_won"] = data[player_name].get("tournaments_won", 0) + 1
    save_leaderboard(data)