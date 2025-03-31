# --- File: scenes/snake_scene.py ---

import pygame
import random
from collections import deque # Efficient for adding/removing from both ends

from engine.gameobj import Entity
# Engine/Scene imports
from engine.scene import Scene
from engine.ui.text_entity import TextEntity
from engine.components.transform import Transform
from engine.components.render import Render
from engine.components.drawables import DrawDepth # Optional: If needed for layering

# --- Snake Game Constants ---
MOVE_INTERVAL = 200 # Seconds between snake moves (controls speed)

# Colors
BACKGROUND_COLOR = (10, 10, 25)
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
TEXT_COLOR = (230, 230, 230)
GAME_OVER_COLOR = (255, 50, 50)
BORDER_COLOR = (255, 255, 0) # Yellow
BORDER_THICKNESS = 3

# Directions (based on grid coordinates, not pixels)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


class SnakeScene(Scene):
    # Accept grid parameters in constructor
    def __init__(self, engine, scene_manager, grid_width, grid_height, tile_size):
        super().__init__(engine, scene_manager)
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.tile_size = tile_size
        # Calculate screen dimensions based on passed grid info (for centering, etc.)
        self.screen_width = self.grid_width * self.tile_size
        self.screen_height = self.grid_height * self.tile_size


    def load(self):
        print("SnakeScene Loading...")
        self.engine.render_system.set_background_color(BACKGROUND_COLOR)
        self.engine.screen.set_screen_size(self.grid_width * self.tile_size, self.grid_height * self.tile_size)

        # Game State - use self.grid_width/height directly
        print(f"Grid Dimensions: {self.grid_width}x{self.grid_height}")

        self.snake_segments = deque()
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.food_entity = None
        self.score = 0
        self.move_timer = 0.0
        self.is_game_over = False
        self.game_over_entities = []

        # Create UI
        self.score_text = self.create_entity(TextEntity,
            text=f"Score: {self.score}", font_name=None, font_size=24,
            color=TEXT_COLOR, engine=self.engine, x=10, y=10, depth=DrawDepth.UI
        )

        # Initialize Game Elements
        self._create_initial_snake()
        self._spawn_food()

        # Subscribe to Events
        self.subscribe(self.engine.events.key_down, self.handle_input)
        self.subscribe(self.engine.events.tick, self.update)

    # --- Add draw_overlay method ---
    def draw_overlay(self, surface):
        """Draws elements directly onto the screen after entities are rendered."""
        # Draw the border rectangle
        border_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        pygame.draw.rect(surface, BORDER_COLOR, border_rect, BORDER_THICKNESS)

    def unload(self):
        super().unload()
        print("SnakeScene Unloaded.")

    def update(self, dt):
        """Main game loop logic for Snake, called every tick."""
        if self.is_game_over:
            return  # Do nothing if game is over

        self.move_timer += dt
        if self.move_timer >= MOVE_INTERVAL:
            self.move_timer -= MOVE_INTERVAL  # Subtract interval for accuracy
            self._move_snake()

    def handle_input(self, key):
        """Handles player input for changing snake direction or restarting."""
        new_direction = self.direction

        if key == pygame.K_UP or key == pygame.K_w:
            new_direction = UP
        elif key == pygame.K_DOWN or key == pygame.K_s:
            new_direction = DOWN
        elif key == pygame.K_LEFT or key == pygame.K_a:
            new_direction = LEFT
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            new_direction = RIGHT
        elif key == pygame.K_ESCAPE:
            # Always allow returning to menu
            self.scene_manager.set_active_scene("main_menu")
            return  # Exit early
        elif self.is_game_over and (key == pygame.K_RETURN or key == pygame.K_SPACE):
            self._restart_game()
            return  # Exit early after restart

        # --- Direction Change Logic ---
        # Prevent reversing direction immediately
        current_dx, current_dy = self.direction
        new_dx, new_dy = new_direction
        if (current_dx + new_dx != 0) or (current_dy + new_dy != 0):
            # Only update next_direction if it's not the direct opposite
            self.next_direction = new_direction

    def _create_initial_snake(self):
        """Creates the starting snake segments."""
        start_x = self.grid_width // 4 # Use instance variable
        start_y = self.grid_height // 2 # Use instance variable
        initial_length = 3
        self.snake_segments.clear()

        for i in range(initial_length):
            grid_pos = (start_x - i, start_y)
            pixel_x = grid_pos[0] * self.tile_size # Use instance variable
            pixel_y = grid_pos[1] * self.tile_size # Use instance variable
            transform = Transform(pixel_x, pixel_y)
            render = Render()
            render.set_draw_depth(DrawDepth.OBJECT)
            segment_surface = pygame.Surface((self.tile_size, self.tile_size)) # Use instance variable
            segment_surface.fill(SNAKE_COLOR)
            pygame.draw.rect(segment_surface, (0, 150, 0), segment_surface.get_rect(), 1)
            render.set_texture(segment_surface)
            segment_entity = self.engine.new_entity(transform=transform, render=render)
            self.add_entity(segment_entity)
            self.snake_segments.append(segment_entity)

        self.direction = RIGHT
        self.next_direction = RIGHT


    def _move_snake(self):
        """Handles moving the snake one step, collision checks, and eating."""
        if not self.snake_segments: return

        self.direction = self.next_direction

        head_entity = self.snake_segments[0]
        head_transform = head_entity.components[Transform]
        # Use self.tile_size for calculations
        current_grid_x = head_transform.x // self.tile_size
        current_grid_y = head_transform.y // self.tile_size
        new_grid_x = current_grid_x + self.direction[0]
        new_grid_y = current_grid_y + self.direction[1]
        new_grid_pos = (new_grid_x, new_grid_y)

        # Wall Collision - Use self.grid_width/height
        if not (0 <= new_grid_x < self.grid_width and 0 <= new_grid_y < self.grid_height):
            self._game_over()
            return
        # Self Collision
        for i in range(1, len(self.snake_segments)):
            segment = self.snake_segments[i]
            seg_transform = segment.components[Transform]
            # Use self.tile_size
            seg_grid_x = seg_transform.x // self.tile_size
            seg_grid_y = seg_transform.y // self.tile_size
            if new_grid_pos == (seg_grid_x, seg_grid_y):
                self._game_over()
                return

        # Add new head
        pixel_x = new_grid_pos[0] * self.tile_size # Use instance variable
        pixel_y = new_grid_pos[1] * self.tile_size # Use instance variable
        transform = Transform(pixel_x, pixel_y)
        render = Render()
        render.set_draw_depth(DrawDepth.OBJECT)
        segment_surface = pygame.Surface((self.tile_size, self.tile_size)) # Use instance variable
        segment_surface.fill(SNAKE_COLOR)
        pygame.draw.rect(segment_surface, (0, 150, 0), segment_surface.get_rect(), 1)
        render.set_texture(segment_surface)
        new_head_entity = self.engine.new_entity(transform=transform, render=render) # Need events
        self.add_entity(new_head_entity)
        self.snake_segments.appendleft(new_head_entity)

        # Check Food Collision
        ate_food = False
        if self.food_entity:
            food_transform = self.food_entity.components[Transform]
             # Use self.tile_size
            food_grid_x = food_transform.x // self.tile_size
            food_grid_y = food_transform.y // self.tile_size
            if new_grid_pos == (food_grid_x, food_grid_y):
                ate_food = True
                self.score += 1

                match self.score:
                    case 30:
                        self.engine.events.steam_achievements.emit(achievement_api_name="S")
                    case 75:
                        self.engine.events.steam_achievements.emit(achievement_api_name="X")
                    case 150:
                        self.engine.events.steam_achievements.emit(achievement_api_name="F")

                self.score_text.text = f"Score: {self.score}"
                self.destroy_entity(self.food_entity)
                self.food_entity = None
                self._spawn_food()

        # Remove Tail
        if not ate_food:
            tail_entity = self.snake_segments.pop()
            self.destroy_entity(tail_entity)


    def _spawn_food(self):
        """Finds a valid spot and creates a food entity."""
        # Use self.grid_width/height
        possible_positions = set((x, y) for x in range(self.grid_width) for y in range(self.grid_height))
        snake_positions = set()
        for segment in self.snake_segments:
            transform = segment.components[Transform]
            # Use self.tile_size
            grid_x = transform.x // self.tile_size
            grid_y = transform.y // self.tile_size
            snake_positions.add((grid_x, grid_y))

        available_positions = list(possible_positions - snake_positions)

        if not available_positions:
            print("Warning: No space left to spawn food!")
            self._game_over()
            return

        grid_pos = random.choice(available_positions)
        # Use self.tile_size
        pixel_x = grid_pos[0] * self.tile_size
        pixel_y = grid_pos[1] * self.tile_size

        transform = Transform(pixel_x, pixel_y)
        render = Render()
        render.set_draw_depth(DrawDepth.OBJECT)
         # Use self.tile_size
        food_surface = pygame.Surface((self.tile_size, self.tile_size))
        food_surface.fill(FOOD_COLOR)
        # Use self.tile_size
        pygame.draw.circle(food_surface, (150, 0, 0), (self.tile_size // 2, self.tile_size // 2), self.tile_size // 2 - 2)
        render.set_texture(food_surface)

        self.food_entity = self.create_entity(
            Entity,
            transform=transform,
            render=render,
            events=self.engine.events # Need events for base Entity
        )


    def _game_over(self):
        """Handles the game over state."""
        if self.is_game_over: return

        print(f"Game Over! Final Score: {self.score}")
        self.is_game_over = True

        # Use self.screen_width/height for centering text
        screen_width = self.screen_width
        screen_height = self.screen_height

        go_text = self.create_entity(TextEntity,
            text="Game Over!", font_name=None, font_size=72, color=GAME_OVER_COLOR,
            engine=self.engine, x=screen_width // 2, y=screen_height // 2 - 60, depth=DrawDepth.UI
        )
        if Render in go_text.components and go_text.components[Render].texture:
             text_width = go_text.components[Render].texture.get_width()
             go_text.components[Transform].x -= text_width // 2
        self.game_over_entities.append(go_text)

        restart_text = self.create_entity(TextEntity,
            text="Press Enter/Space to Restart or ESC for Menu",
            font_name=None, font_size=30, color=TEXT_COLOR,
            engine=self.engine, x=screen_width // 2, y=screen_height // 2 + 20, depth=DrawDepth.UI
        )
        if Render in restart_text.components and restart_text.components[Render].texture:
            text_width = restart_text.components[Render].texture.get_width()
            restart_text.components[Transform].x -= text_width // 2
        self.game_over_entities.append(restart_text)



    def _restart_game(self):
        """Resets the game state to start over."""
        print("Restarting Snake game...")

        # Clear existing game elements
        # Destroy snake segments (iterate copy of deque)
        for segment in list(self.snake_segments):
             self.destroy_entity(segment)
        self.snake_segments.clear()

        # Destroy food
        if self.food_entity:
             self.destroy_entity(self.food_entity)
             self.food_entity = None

        # Destroy game over text
        for entity in self.game_over_entities:
             self.destroy_entity(entity)
        self.game_over_entities.clear()

        # Reset state variables
        self.score = 0
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.move_timer = 0.0
        self.is_game_over = False

        # Update score display
        self.score_text.text = f"Score: {self.score}"

        # Re-initialize snake and food
        self._create_initial_snake()
        self._spawn_food()