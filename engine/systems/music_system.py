import pygame
import os
import random
import sys # For resource_path

# --- Helper Function (ensure this is available) ---
# Place this here or in a shared utils file and import it
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # _MEIPASS not found, running in normal Python environment
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# --- ---

class MusicSystem:
    DEFAULT_VOLUME = 0.5
    VOLUME_STEP = 0.1
    SUPPORTED_EXTENSIONS = ('.ogg', '.mp3', '.wav', '.mid') # Add more if needed

    def __init__(self, engine, music_folder="assets/sounds/music", auto_play=True):
        self.engine = engine
        self.music_folder_relative = music_folder
        self.playlist = []
        self.current_track_index = -1
        self.volume = self.DEFAULT_VOLUME
        self.is_playing = False

        # --- Initialize Mixer ---
        try:
            if not pygame.mixer.get_init():
                 print("MusicSystem: Initializing pygame.mixer...")
                 pygame.mixer.init()
            else:
                 print("MusicSystem: pygame.mixer already initialized.")
            # Make sure music mixer specifically is working
            pygame.mixer.music.set_volume(self.volume)
            print(f"MusicSystem: Mixer initialized. Initial volume set to {self.volume}")
        except pygame.error as e:
            print(f"MusicSystem: ERROR - Failed to initialize pygame.mixer: {e}. Music disabled.")
            return # Cannot continue without mixer

        # --- Load Music ---
        self._load_playlist()

        # --- Subscribe to Events ---
        self.engine.events.key_down.subscribe(self.handle_input)
        self.engine.events.tick.subscribe(self.update) # Check for track end

        # --- Auto Play ---
        if auto_play and self.playlist:
            self.play()

    def _load_playlist(self):
        """Finds music files in the specified folder."""
        self.playlist = []
        try:
            # Use resource_path to find the absolute path to the music folder
            music_dir_abs = resource_path(self.music_folder_relative)
            print(f"MusicSystem: Scanning for music in: {music_dir_abs}")

            if not os.path.isdir(music_dir_abs):
                print(f"MusicSystem: WARNING - Music directory not found: {music_dir_abs}")
                return

            for filename in os.listdir(music_dir_abs):
                if filename.lower().endswith(self.SUPPORTED_EXTENSIONS):
                    full_path = os.path.join(music_dir_abs, filename)
                    self.playlist.append(full_path)

            if self.playlist:
                random.shuffle(self.playlist) # Shuffle the order
                print(f"MusicSystem: Found {len(self.playlist)} music tracks. Playlist shuffled.")
                # print(f"Playlist: {self.playlist}") # Optional: Debug print
            else:
                print("MusicSystem: No music tracks found in the specified folder.")

        except Exception as e:
            print(f"MusicSystem: ERROR loading playlist: {e}")

    def _play_track(self, index):
        """Loads and plays a specific track index."""
        if not self.playlist or not (0 <= index < len(self.playlist)):
            print("MusicSystem: Invalid track index or empty playlist.")
            self.is_playing = False
            return

        filepath = self.playlist[index]
        print(f"MusicSystem: Playing track {index + 1}/{len(self.playlist)}: {os.path.basename(filepath)}")

        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(self.volume) # Ensure volume is set
            pygame.mixer.music.play()
            self.current_track_index = index
            self.is_playing = True
        except pygame.error as e:
            print(f"MusicSystem: ERROR playing track '{filepath}': {e}")
            self.is_playing = False
            # Optionally try next track?
            # self._play_next_track(force=True) # Be careful of infinite loops if all fail

    def _play_next_track(self, force=False):
        """Plays the next track in the playlist, wrapping around."""
        if not self.playlist:
             self.is_playing = False
             return

        # Only proceed if forced or if music isn't busy (meaning it finished or stopped)
        if force or not pygame.mixer.music.get_busy():
            next_index = (self.current_track_index + 1) % len(self.playlist)
            self._play_track(next_index)
        else:
            # This case shouldn't happen if called from update correctly, but safety check
             self.is_playing = True # It must still be playing

    def play(self, index=0):
        """Starts playing music from the specified index (default 0)."""
        print("MusicSystem: Play requested.")
        self._play_track(index)

    def stop(self):
        """Stops music playback."""
        print("MusicSystem: Stop requested.")
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload() # Unload to release file handle
        except pygame.error as e:
             print(f"MusicSystem: Error stopping music: {e}")
        self.is_playing = False
        self.current_track_index = -1 # Reset index

    def set_volume(self, vol):
        """Sets the music volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, vol)) # Clamp value
        try:
            pygame.mixer.music.set_volume(self.volume)
            print(f"MusicSystem: Volume set to {self.volume:.1f}")
        except pygame.error as e:
             print(f"MusicSystem: Error setting volume: {e}")

    def adjust_volume(self, delta):
        """Adjusts volume by a delta, clamping between 0.0 and 1.0."""
        new_volume = self.volume + delta
        self.set_volume(new_volume) # set_volume handles clamping and setting

    def update(self, dt):
        """Checks if the current track has finished and plays the next one."""
        if self.is_playing and not pygame.mixer.music.get_busy():
             print("MusicSystem: Track finished, playing next.")
             self._play_next_track(force=True) # Force playing next as current one ended

    def handle_input(self, key):
        """Handles volume control keys."""
        if key == pygame.K_KP_PLUS:
            print("MusicSystem: Volume Up key pressed.")
            self.adjust_volume(self.VOLUME_STEP)
        elif key == pygame.K_KP_MINUS:
            print("MusicSystem: Volume Down key pressed.")
            self.adjust_volume(-self.VOLUME_STEP)
        elif key == pygame.K_KP_DIVIDE:
            print("Playing next track.")
            self._play_next_track(force=True)