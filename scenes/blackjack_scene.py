# --- File: scenes/blackjack_scene.py ---

import pygame
import random
import time

# Engine/Scene imports
from engine.scene import Scene
from engine.ui.text_entity import TextEntity
from engine.components.transform import Transform
from engine.components.render import Render
from engine.components.drawables import DrawDepth # Corrected import name
from engine.gameobj import Entity # Import base Entity for cards

# --- Blackjack Constants ---
# Appearance
BACKGROUND_COLOR = (0, 80, 20) # Casino Green
# CARD_FONT_SIZE = 40 # No longer needed for card display
INFO_FONT_SIZE = 30
MESSAGE_FONT_SIZE = 36
TEXT_COLOR = (255, 255, 255) # White
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (255, 255, 0) # Yellow highlight
DEALER_Y = 100
PLAYER_Y = 350
START_X_OFFSET = 300 # Initial X offset for first card
CARD_SPACING = 80   # Horizontal space between card centers (adjust based on image size)
BUTTON_Y = 500
HIT_BUTTON_X = 200
STAND_BUTTON_X = 400

# Card Assets
CARD_DECK_PATH = "Deck1" # Subdirectory within assets/images/
CARD_BACK_FILENAME = "BackRed1.png" # <<< UPDATE if your card back name is different

# Gameplay
DECK_SUITS = ["H", "D", "C", "S"] # Hearts, Diamonds, Clubs, Spades
DECK_RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"] # T=10
BLACKJACK_VALUE = 21
DEALER_STAND_MIN = 17

# --- Define Target Card Size ---
TARGET_CARD_WIDTH = 71   # Example: Standard poker size width
TARGET_CARD_HEIGHT = 96 # Example: Standard poker size height

# Game States
STATE_DEALING = "DEALING"
STATE_PLAYER_TURN = "PLAYER_TURN"
STATE_DEALER_TURN = "DEALER_TURN"
STATE_ROUND_OVER = "ROUND_OVER"

# Card Suit Mapping for Filenames
SUIT_TO_NAME = {"H": "Hearts", "D": "Diamonds", "C": "Clubs", "S": "Spades"}


class BlackjackScene(Scene):
    def load(self):
        print("BlackjackScene Loading...")
        self.engine.render_system.set_background_color(BACKGROUND_COLOR)
        self.engine.screen.set_screen_size(800, 600)
        self.engine.events.tick.subscribe(self._update)
        # Game State Variables
        self.deck = []
        self.player_hand = [] # Logical hand (rank, suit)
        self.dealer_hand = [] # Logical hand (rank, suit)
        self.player_card_entities = [] # List of graphical entities
        self.dealer_card_entities = [] # List of graphical entities

        self.player_score = 0
        self.dealer_score = 0
        self.game_state = STATE_DEALING
        self.message = ""
        self.dealer_card_hidden = True
        self.card_size = (TARGET_CARD_WIDTH, TARGET_CARD_HEIGHT)# Store card image size once loaded

        self.dealer_last_action = 0

        # --- Preload Card Back ---
        self.card_back_texture = self.engine.resource_manager.get_image(
            f"{CARD_DECK_PATH}/{CARD_BACK_FILENAME}"
        )
        if self.card_back_texture:
             # Assume all cards are the same size as the back initially
             self.card_size = self.card_back_texture.get_size()
             print(f"Detected Card Size: {self.card_size}")
        else:
             print(f"ERROR: Could not load card back image: {CARD_BACK_FILENAME}")
             # Set a default size or handle error appropriately
             self.card_size = (71, 96) # Example fallback size

        # --- UI Text Entities (No card text needed) ---
        info_x = START_X_OFFSET - 150 # Adjust based on card positions
        self.dealer_hand_text = self._create_ui_text("Dealer:", INFO_FONT_SIZE, x=info_x, y=DEALER_Y)
        self.dealer_score_text = self._create_ui_text("Score: ?", INFO_FONT_SIZE, x=info_x, y=DEALER_Y + 30)
        self.deck_count = self._create_ui_text("Deck Count: ?", INFO_FONT_SIZE, x=info_x, y=DEALER_Y - 60)

        self.player_hand_text = self._create_ui_text("Player:", INFO_FONT_SIZE, x=info_x, y=PLAYER_Y)
        self.player_score_text = self._create_ui_text("Score: 0", INFO_FONT_SIZE, x=info_x, y=PLAYER_Y + 30)


        self.message_text = self._create_ui_text("", MESSAGE_FONT_SIZE, x=self.engine.screen.width // 2, y=250)
        # Centering will happen in _update_display

        # Buttons
        self.hit_button = self._create_ui_text("[H]it", INFO_FONT_SIZE, x=HIT_BUTTON_X, y=BUTTON_Y, color=BUTTON_COLOR)
        self.stand_button = self._create_ui_text("[S]tand", INFO_FONT_SIZE, x=STAND_BUTTON_X, y=BUTTON_Y, color=BUTTON_COLOR)

        # Subscribe Events
        self.subscribe(self.engine.events.key_down, self.handle_input)
        self.subscribe(self.engine.events.mouse_button_down, self.handle_mouse_click)

        # Start the first round
        self._start_new_round()

    def unload(self):
        # Make sure card entities are cleared if scene is unloaded mid-game
        self._clear_card_entities(self.player_card_entities)
        self._clear_card_entities(self.dealer_card_entities)
        self._clear_card_entities(self.player_hand)
        self._clear_card_entities(self.dealer_hand)
        super().unload()
        print("BlackjackScene Unloaded.")

    def _update(self, dt):
        if self.game_state == STATE_DEALER_TURN:
            self.dealer_last_action += dt
            if self.dealer_last_action > 750:
                self._dealer_play()
                self.dealer_last_action = 0
        self._update_display()


    # --- Card Filename Helper ---
    def _get_card_filename(self, card):
        """Converts (rank, suit) tuple to image filename."""
        if not card: return None
        rank, suit = card
        try:
            suit_name = SUIT_TO_NAME[suit]
            # Rank seems to be direct: 2..9, T, J, Q, K, A
            filename = f"{CARD_DECK_PATH}/{suit_name}{rank}.png"
            return filename
        except KeyError:
            print(f"Error: Invalid suit '{suit}' in card {card}")
            return None

    # --- Entity Management Helpers ---
    def _create_card_entity(self, card_data, x, y, is_hidden=False):
        """Creates a graphical card entity, loading a SCALED texture."""
        texture = None
        filename_for_load = None

        if is_hidden:
            # Use preloaded scaled back texture
            texture = self.card_back_texture
            filename_for_load = f"{CARD_DECK_PATH}/{CARD_BACK_FILENAME}" # For cache key consistency
        else:
            filename_for_load = self._get_card_filename(card_data)
            if filename_for_load:
                # Load image using resource manager, specifying target size
                texture = self.engine.resource_manager.get_image(
                    filename_for_load,
                    target_width=TARGET_CARD_WIDTH,
                    target_height=TARGET_CARD_HEIGHT
                )

        if not texture or texture == self.engine.resource_manager.fallback_image:
             print(f"Error/Fallback: Could not get texture for card {'BACK' if is_hidden else card_data} (filename: {filename_for_load})")
             # Create a fallback visual scaled to the target size
             texture = pygame.Surface(self.card_size)
             texture.fill((255, 0, 255))
             pygame.draw.rect(texture, (0,0,0), texture.get_rect(), 2)

        # Create Entity using scene helper
        entity = self.create_entity(
            Entity,
            transform=Transform(x, y),
            render=Render(texture=texture, draw_depth=DrawDepth.OBJECT), # Pass texture directly
            events=self.engine.events
        )
        return entity

    def _clear_card_entities(self, entity_list):
        """Destroys all entities in a list and clears the list."""
        for entity in entity_list:
            self.destroy_entity(entity)
        entity_list.clear()

    def _sync_card_entities(self, hand_data, entity_list, start_x, y, hide_one=False):
        """Creates, updates, or destroys SCALED card entities."""
        num_cards_needed = len(hand_data)

        for i in range(num_cards_needed):
            card = hand_data[i]
            is_hidden = (hide_one and i == 1)
            # Use new CARD_SPACING
            card_x = start_x + i * CARD_SPACING

            if i < len(entity_list):  # Update existing
                entity = entity_list[i]
                entity.components[Transform].x = card_x
                entity.components[Transform].y = y
                # Update texture only if hidden state changes (or if needed)
                # Get target texture
                target_texture = None
                if is_hidden:
                    target_texture = self.card_back_texture
                else:
                    filename = self._get_card_filename(card)
                    if filename:
                        target_texture = self.engine.resource_manager.get_image(
                            filename,
                            target_width=TARGET_CARD_WIDTH,
                            target_height=TARGET_CARD_HEIGHT
                        )
                # Update only if texture differs (and target texture loaded ok)
                if target_texture and entity.components[Render].texture != target_texture:
                    entity.components[Render].set_texture(target_texture)
            else:  # Create new
                new_entity = self._create_card_entity(card, card_x, y, is_hidden)
                entity_list.append(new_entity)

        # Remove excess
        while len(entity_list) > num_cards_needed:
            entity_to_remove = entity_list.pop()
            self.destroy_entity(entity_to_remove)


    # --- UI Helper (Remains the same) ---
    def _create_ui_text(self, text, size, x, y, color=TEXT_COLOR, depth=DrawDepth.UI):
         # ... (no changes) ...
         entity = self.create_entity(TextEntity,
            text=text, font_name=None, font_size=size, color=color,
            engine=self.engine, x=x, y=y, depth=depth
         )
         return entity

    # --- Game Logic (Core logic remains mostly the same) ---
    def _create_deck(self):
        self.deck = [(rank, suit) for rank in DECK_RANKS for suit in DECK_SUITS]

    def _shuffle_deck(self):
        random.shuffle(self.deck)

    def _deal_card(self, hand):
        # Deals to logical hand only, graphical update happens in _update_display
        if not self.deck:
            print("Deck empty! Reshuffling...")
            self._create_deck()
            self._shuffle_deck()
        card = self.deck.pop()
        hand.append(card)
        return card

    def _calculate_hand_value(self, hand, count_hidden=False):
        value = 0
        ace_count = 0
        for i, (rank, suit) in enumerate(hand):
            if count_hidden is False and self.dealer_card_hidden and hand == self.dealer_hand and i == 1:
                continue # Skip hidden dealer card

            if rank.isdigit():
                value += int(rank)
            elif rank in ["T", "J", "Q", "K"]:
                value += 10
            elif rank == "A":
                ace_count += 1
                value += 11 # Assume 11 initially

        while value > BLACKJACK_VALUE and ace_count > 0:
            value -= 10
            ace_count -= 1
        return value


    def _start_new_round(self):
        print("Starting new round...")
        # Clear logical hands
        self.player_hand.clear()
        self.dealer_hand.clear()
        # Clear graphical entities
        self._clear_card_entities(self.player_card_entities)
        self._clear_card_entities(self.dealer_card_entities)
        self.hit_button.set_visible(True)
        self.stand_button.set_visible(True)

        self._create_deck()
        self._shuffle_deck()
        self.dealer_card_hidden = True
        self.message = ""

        # Deal initial cards to logical hands
        self._deal_card(self.player_hand)
        self._deal_card(self.dealer_hand)
        self._deal_card(self.player_hand)
        self._deal_card(self.dealer_hand)

        self.player_score = self._calculate_hand_value(self.player_hand)
        self.dealer_score = self._calculate_hand_value(self.dealer_hand, count_hidden=False)

        # Check for initial Blackjack
        if self.player_score == BLACKJACK_VALUE:
            # ... (Blackjack check logic remains the same) ...
            self.dealer_card_hidden = False
            self.dealer_score = self._calculate_hand_value(self.dealer_hand)
            if self.dealer_score == BLACKJACK_VALUE:
                 self._end_round("Push! Both have Blackjack!")
            else:
                 self._end_round("Blackjack! Player wins!")
        else:
            self.game_state = STATE_PLAYER_TURN
            self.message = "Player turn: [H]it or [S]tand?"

        # Update display AFTER dealing logical hands
        self._update_display()


    def _player_hit(self):
        if self.game_state != STATE_PLAYER_TURN: return
        print("Player hits.")
        self._deal_card(self.player_hand) # Deal to logical hand
        self.player_score = self._calculate_hand_value(self.player_hand)
        self._update_display() # Update graphics and scores

        if self.player_score > BLACKJACK_VALUE:
            self._end_round("Player busts!")
        elif self.player_score == BLACKJACK_VALUE:
            self._player_stand()


    def _player_stand(self):
        if self.game_state != STATE_PLAYER_TURN: return
        print("Player stands.")
        self.game_state = STATE_DEALER_TURN
        self.dealer_card_hidden = False # Reveal card (logical state)
        self.dealer_score = self._calculate_hand_value(self.dealer_hand)
        self.message = "Dealer's turn..."
        self._update_display() # Update display to show revealed card


    def _dealer_play(self):
        if self.dealer_score < DEALER_STAND_MIN:
            print("Dealer hits.")
            self._deal_card(self.dealer_hand) # Deal to logical hand
            self.dealer_score = self._calculate_hand_value(self.dealer_hand)
            if self.dealer_score > BLACKJACK_VALUE:
                self._end_round("Dealer busts! Player wins!")
                return
        else:
            print("Dealer stands.")
            self._end_round(self._determine_winner())


    def _determine_winner(self):
         # ... (no changes needed) ...
         if self.player_score > self.dealer_score:
            return "Player wins!"
         elif self.dealer_score > self.player_score:
            return "Dealer wins!"
         else:
            return "Push!"

    def _end_round(self, result_message):
        print(f"Round Over: {result_message}")
        self.game_state = STATE_ROUND_OVER
        self.hit_button.set_visible(False)
        self.stand_button.set_visible(False)
        self.message = f"{result_message} (Press Enter/Space/Click to deal again)"
        self.dealer_card_hidden = False
        self._update_display()


    # --- Display Update ---
    def _update_display(self):
        """Updates scores, messages, and syncs card entities."""
        # Sync graphical cards using updated constants
        self._sync_card_entities(self.player_hand, self.player_card_entities, START_X_OFFSET, PLAYER_Y)
        self._sync_card_entities(self.dealer_hand, self.dealer_card_entities, START_X_OFFSET, DEALER_Y,
                                 hide_one=self.dealer_card_hidden)

        # Update Scores Text
        self.player_score_text.text = f"Score: {self.player_score}"
        if self.dealer_card_hidden:
            visible_dealer_score = self._calculate_hand_value([self.dealer_hand[0]]) if self.dealer_hand else 0
            self.dealer_score_text.text = f"Score: {visible_dealer_score} + ?"
        else:
            full_dealer_score = self._calculate_hand_value(self.dealer_hand)
            self.dealer_score_text.text = f"Score: {full_dealer_score}"

        self.deck_count.text = f"Deck Count: {len(self.deck)}"

        # Update Message & Center it
        self.message_text.text = self.message
        if Render in self.message_text.components and self.message_text.components[Render].texture:
            text_width = self.message_text.components[Render].texture.get_width()
            self.message_text.components[Transform].x = (self.engine.screen.width - text_width) // 2

        # Update Button Appearance
        is_player_turn = (self.game_state == STATE_PLAYER_TURN)
        self.hit_button.color = BUTTON_HOVER_COLOR if is_player_turn else BUTTON_COLOR
        self.stand_button.color = BUTTON_HOVER_COLOR if is_player_turn else BUTTON_COLOR


    # --- Input Handling (Remains largely the same, but add click-to-restart) ---
    def handle_input(self, key):
        # ... (Escape, H, S handling remains same) ...
        if key == pygame.K_ESCAPE:
            self.scene_manager.set_active_scene("main_menu")
            return

        if self.game_state == STATE_PLAYER_TURN:
            if key == pygame.K_h:
                self._player_hit()
            elif key == pygame.K_s:
                self._player_stand()
        elif self.game_state == STATE_ROUND_OVER:
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self._start_new_round()

    def handle_mouse_click(self, pos, button):
        if button != 1: return # Left click only

        if self.game_state == STATE_PLAYER_TURN:
             # ... (Hit/Stand button click logic remains same) ...
              # Check Hit Button
            if self.hit_button.components[Render].texture:
                 hit_rect = self.hit_button.components[Render].texture.get_rect(
                     topleft=(self.hit_button.components[Transform].x, self.hit_button.components[Transform].y))
                 if hit_rect.collidepoint(pos):
                     self._player_hit()
                     return

            # Check Stand Button
            if self.stand_button.components[Render].texture:
                 stand_rect = self.stand_button.components[Render].texture.get_rect(
                     topleft=(self.stand_button.components[Transform].x, self.stand_button.components[Transform].y))
                 if stand_rect.collidepoint(pos):
                     self._player_stand()
                     return

        elif self.game_state == STATE_ROUND_OVER:
            # If round is over, any click starts a new round
            print("Click detected to start new round.")
            self._start_new_round()