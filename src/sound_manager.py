import pygame
import os

pygame.mixer.init()

# Folder for audio assets
SOUND_DIR = os.path.join("assets", "sounds")

# Loaded short sounds
SOUNDS = {}

# Global states
sfx_volume = 0.6       # Default SFX volume (0–1)
music_volume = 0.05    # Default music volume (0–1)
muted = False          # Global mute flag
current_track = None   # Track currently playing

def set_muted(state: bool):
    # Globally mute/unmute all sounds
    global muted
    muted = state
    if state:
        pygame.mixer.music.set_volume(0)
    else:
        pygame.mixer.music.set_volume(music_volume)

def find_audio_file(base_name):
    # Looks for a valid audio file (.wav, .mp3, .m4a) in SOUND_DIR.
    # Returns the full path or None if missing.
    for ext in [".wav", ".mp3", ".m4a"]:
        path = os.path.join(SOUND_DIR, base_name + ext)
        if os.path.exists(path):
            return path
    print(f"[sound_manager] Missing audio: {base_name}")
    return None


def init_sounds():
    # Initialises the sound system
    pygame.mixer.init()
    print("Sound system initialised.")


# Volume control

def set_sfx_volume_percent(percent):
    # Adjusts the volume for all sound effects (0–100%).
    global sfx_volume
    sfx_volume = max(0, min(1, percent / 100))
    for snd in SOUNDS.values():
        snd.set_volume(sfx_volume)
    print(f"[sound_manager] SFX volume set to {round(sfx_volume, 2)}")


def set_music_volume_percent(percent):
    # Adjusts the background music volume (0–100%).
    global music_volume
    music_volume = max(0, min(1, percent / 100))
    pygame.mixer.music.set_volume(music_volume)
    print(f"[sound_manager] Music volume set to {round(music_volume, 2)}")


def mute_all():
    # Mutes all sounds
    global muted
    muted = True
    pygame.mixer.music.set_volume(0)
    for s in SOUNDS.values():
        s.set_volume(0)
    print("[sound_manager] Audio muted.")


def unmute_all():
    # Unmutes all sounds
    global muted
    muted = False
    pygame.mixer.music.set_volume(music_volume)
    for s in SOUNDS.values():
        s.set_volume(sfx_volume)
    print("[sound_manager] Audio unmuted.")


def is_muted():
    # Returns True if audio is currently muted
    return muted


# Sound effects

def load_sound(name):
    # Loads a short sound effect into memory and stores it in SOUNDS.
    path = find_audio_file(name)
    if not path:
        return None
    sound = pygame.mixer.Sound(path)
    sound.set_volume(0 if muted else sfx_volume)
    SOUNDS[name] = sound
    return sound


def play(name):
    # Plays a short sound effect such as 'hit', 'bust', or menu navigation.
    if muted:
        return
    if name not in SOUNDS:
        snd = load_sound(name)
        if snd is None:
            return
    SOUNDS[name].play()


# Music

def play_music(track, volume=0.05, loop=True):
    # Plays a music track with adjustable volume.
    if muted:
        return
    path = find_audio_file(track)
    if not path:
        print(f"[sound_manager] Could not find music track: {track}")
        return

    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1 if loop else 0)


def stop_music():
    # Stops all background music immediately
    pygame.mixer.music.stop()


def fade_to_music(track, fade_ms=1500, loop=True):
    # Smoothly fades from the current music track to a new one
    global current_track
    if muted:
        return
    pygame.mixer.music.fadeout(fade_ms)
    path = find_audio_file(track)
    if not path:
        return
    pygame.time.delay(fade_ms)
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1 if loop else 0)
    current_track = track
    print(f"[sound_manager] Faded to new track: {track}")


def pause_music():
    # Temporarily pauses background music
    pygame.mixer.music.pause()


def resume_music():
    # Resumes paused background music
    if not muted:
        pygame.mixer.music.unpause()


def set_music_volume(vol):
    # Sets background music volume (direct float 0–1)
    global music_volume
    music_volume = max(0, min(1, vol))
    pygame.mixer.music.set_volume(music_volume)