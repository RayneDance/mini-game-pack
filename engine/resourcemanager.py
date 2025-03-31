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

    def load_image(self, filename, use_alpha=True, target_width=None, target_height=None):
        """
        Loads an image, optionally scaling it. Caches based on filename AND target size.

        Args:
            filename (str): The name of the image file (e.g., 'player.png').
            use_alpha (bool): Load with transparency support.
            target_width (int | None): Desired width, or None for original.
            target_height (int | None): Desired height, or None for original.

        Returns:
            pygame.Surface: The loaded/scaled/cached surface, or a fallback surface.
        """
        # Use size in cache key. None indicates original size.
        cache_key = (filename, target_width, target_height)
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]

        # Build path relative to 'assets/images/'
        full_path = self._build_path("images", filename)

        try:
            print(f"Loading image: {full_path}")
            image = pygame.image.load(full_path)

            if use_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()

            # --- Scaling Logic ---
            final_image = image
            if target_width is not None and target_height is not None:
                 try:
                     print(f"Scaling image '{filename}' to {target_width}x{target_height}")
                     # Use smoothscale for better quality
                     final_image = pygame.transform.smoothscale(image, (target_width, target_height))
                 except Exception as scale_error:
                     print(f"Error scaling image '{filename}': {scale_error}")
                     # Fallback to unscaled or the generic fallback? Let's use unscaled for now.
                     final_image = image # Use original if scaling fails

            # Cache the potentially scaled image
            self._image_cache[cache_key] = final_image
            return final_image

        except pygame.error as e:
            print(f"Error loading image '{full_path}': {e}")
            # Cache and return fallback for this size request
            scaled_fallback = pygame.transform.scale(self.fallback_image, (target_width or 32, target_height or 32))
            self._image_cache[cache_key] = scaled_fallback
            return scaled_fallback
        except FileNotFoundError:
             print(f"Error: Image file not found at '{full_path}'")
             scaled_fallback = pygame.transform.scale(self.fallback_image, (target_width or 32, target_height or 32))
             self._image_cache[cache_key] = scaled_fallback
             return scaled_fallback

    def get_image(self, filename, target_width=None, target_height=None):
        """
        Retrieves a previously loaded image from the cache, optionally scaled.
        If not loaded, attempts to load and scale it.
        """
        # Pass scaling parameters to load_image
        return self.load_image(filename, target_width=target_width, target_height=target_height)


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