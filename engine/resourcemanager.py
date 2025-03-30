# Create a new file: engine/resource_manager.py

import pygame
import os # Needed for path joining

class ResourceManager:
    def __init__(self, base_path="assets"):
        """
        Initializes the ResourceManager.

        Args:
            base_path (str): The root directory where resource subfolders (like 'images', 'sounds') are located.
        """
        self.base_path = base_path
        self._image_cache = {}
        self._sound_cache = {}
        self._font_cache = {}
        # Add more caches as needed (e.g., for data files)

        # --- Load a default fallback image (optional but good practice) ---
        self.fallback_image = self._create_fallback_surface()

        # Ensure pygame.mixer is initialized if using sounds
        if not pygame.mixer.get_init():
             pygame.mixer.init()
        # Ensure pygame.font is initialized if using fonts
        if not pygame.font.get_init():
             pygame.font.init()


    def _create_fallback_surface(self, size=(32, 32), color=(255, 0, 255)):
        """Creates a simple magenta surface to return when an image fails to load."""
        surface = pygame.Surface(size)
        surface.fill(color)
        # Optionally draw something simple like an 'X'
        pygame.draw.line(surface, (0,0,0), (0,0), size, 1)
        pygame.draw.line(surface, (0,0,0), (0, size[1]-1), (size[0]-1, 0), 1)
        return surface

    def _build_path(self, resource_type_folder, filename):
        """Constructs the full path to a resource."""
        return os.path.join(self.base_path, resource_type_folder, filename)

    def load_image(self, filename, use_alpha=True):
        """
        Loads an image from the 'images' subfolder. Caches it if successful.

        Args:
            filename (str): The name of the image file (e.g., 'player.png').
            use_alpha (bool): Whether to load with transparency support (.convert_alpha()).

        Returns:
            pygame.Surface: The loaded (or cached) image surface, or a fallback surface on error.
        """
        if filename in self._image_cache:
            return self._image_cache[filename]

        full_path = self._build_path("images", filename)

        try:
            print(f"Loading image: {full_path}") # Debug print
            image = pygame.image.load(full_path)

            if use_alpha:
                image = image.convert_alpha() # Use transparency
            else:
                image = image.convert() # Opaque images

            self._image_cache[filename] = image
            return image

        except pygame.error as e:
            print(f"Error loading image '{full_path}': {e}")
            # Store and return the fallback image for this filename
            self._image_cache[filename] = self.fallback_image
            return self.fallback_image
        except FileNotFoundError:
             print(f"Error: Image file not found at '{full_path}'")
             self._image_cache[filename] = self.fallback_image
             return self.fallback_image

    def get_image(self, filename):
        """
        Retrieves a previously loaded image from the cache.
        If not loaded, attempts to load it.

        Args:
            filename (str): The name of the image file.

        Returns:
            pygame.Surface: The image surface or fallback surface.
        """
        # This essentially becomes an alias for load_image as load_image checks cache first
        return self.load_image(filename)

    def load_sound(self, filename):
        """
        Loads a sound from the 'sounds' subfolder. Caches it if successful.

        Args:
            filename (str): The name of the sound file (e.g., 'shoot.wav').

        Returns:
            pygame.mixer.Sound | None: The loaded sound object, or None on error.
        """
        if filename in self._sound_cache:
            return self._sound_cache[filename]

        full_path = self._build_path("sounds", filename)

        try:
            print(f"Loading sound: {full_path}") # Debug print
            sound = pygame.mixer.Sound(full_path)
            self._sound_cache[filename] = sound
            return sound

        except pygame.error as e:
            print(f"Error loading sound '{full_path}': {e}")
            return None
        except FileNotFoundError:
             print(f"Error: Sound file not found at '{full_path}'")
             return None

    def get_sound(self, filename):
        """
        Retrieves a previously loaded sound from the cache.
        If not loaded, attempts to load it.

        Args:
            filename (str): The name of the sound file.

        Returns:
            pygame.mixer.Sound | None: The sound object or None.
        """
        return self.load_sound(filename)

    def load_font(self, filename, size):
        """
        Loads a font. If filename is None, loads the default system font.
        Caches it based on filename AND size.

        Args:
            filename (str | None): The name of the font file (e.g., 'arial.ttf') or None for default.
            size (int): The point size to load the font at.

        Returns:
            pygame.font.Font | None: The loaded font object, or None on error.
        """
        # Cache key includes size and uses None itself if filename is None
        cache_key = (filename, size)
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]

        # --- Handle None filename for default font ---
        if filename is None:
            try:
                print(f"Loading default system font at size {size}") # Debug print
                font = pygame.font.Font(None, size) # Pass None to pygame.font.Font
                self._font_cache[cache_key] = font
                return font
            except Exception as e:
                print(f"Error loading default system font (size {size}): {e}")
                # Cache None to avoid retrying constantly? Maybe not.
                return None # Return None on error
        # --- End handling None filename ---

        # --- Original logic for specific font files ---
        full_path = self._build_path("fonts", filename)
        try:
            print(f"Loading font file: {full_path} at size {size}") # Debug print
            font = pygame.font.Font(full_path, size)
            self._font_cache[cache_key] = font
            return font
        except pygame.error as e:
            print(f"Error loading font '{full_path}': {e}")
            # Fallback logic remains the same (try default, return None)
            try:
                 print(f"Warning: Falling back to default system font.")
                 fallback_font = pygame.font.Font(None, size)
                 self._font_cache[cache_key] = fallback_font # Cache the fallback
                 return fallback_font
            except Exception as fallback_e:
                 print(f"Error loading default system font as fallback: {fallback_e}")
                 return None
        except FileNotFoundError:
            print(f"Error: Font file not found at '{full_path}'")
            # Fallback logic remains the same
            try:
                 print(f"Warning: Falling back to default system font.")
                 fallback_font = pygame.font.Font(None, size)
                 self._font_cache[cache_key] = fallback_font # Cache the fallback
                 return fallback_font
            except Exception as fallback_e:
                 print(f"Error loading default system font as fallback: {fallback_e}")
                 return None

    def get_font(self, filename, size):
        """
        Retrieves a previously loaded font of a specific size from the cache.
        If not loaded, attempts to load it. Handles filename=None for default font.
        """
        # No change needed here, load_font now handles None correctly
        return self.load_font(filename, size)

    def clear_cache(self):
        """Removes all resources from the cache."""
        self._image_cache.clear()
        self._sound_cache.clear()
        self._font_cache.clear()
        print("Resource cache cleared.")