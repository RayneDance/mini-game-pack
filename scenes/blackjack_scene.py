# --- File: scenes/blackjack_scene.py ---

import pygame
import random
import time # For small delays maybe

# Engine/Scene imports
from engine.scene import Scene
from engine.ui.text_entity import TextEntity
from engine.components.transform import Transform
from engine.components.render import Render
from engine.components.drawables import DrawDepth

# --- Blackjack Constants ---
# Appearance
BACKGROUND_COLOR = (0, 80, 20) # Casino Green
CARD_FONT_SIZE = 40
INFO_FONT_SIZE = 30
MESSAGE_FONT_SIZE = 36
TEXT_COLOR = (255, 255, 255) # White
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (255, 255, 0) # Yellow highlight
DEALER_CARD_X = 150
PLAYER_CARD_X = 150
DEALER_Y = 100
PLAYER_Y = 350
CARD_SPACING = 40
BUTTON_Y = 500
HIT_BUTTON_X = 200
STAND_BUTTON_X = 400

# Gameplay
DECK_SUITS = ["H", "D", "C", "S"] # Hearts, Diamonds, Clubs, Spades
DECK_RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"] # T=10
BLACKJACK_VALUE = 21
DEALER_STAND_MIN = 17

# Game States
STATE_DEALING = "DEALING"
STATE_PLAYER_TURN = "PLAYER_TURN"
STATE_DEALER_TURN = "DEALER_TURN"
STATE_ROUND_OVER = "ROUND_OVER"


class BlackjackScene(Scene):
    def load(self):
        print("BlackjackScene Loading...")
        self.engine.render_system.set_background_color(BACKGROUND_COLOR)

        # Game State Variables
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.player_score = 0
        self.dealer_score = 0 # Score based on visible cards initially
        self.game_state = STATE_DEALING # Initial state
        self.message = ""
        self.dealer_card_hidden = True

        # UI Entities (Create placeholders, text set in _update_display)
        self.dealer_hand_text = self._create_ui_text("Dealer:", INFO_FONT_SIZE, x=DEALER_CARD_X - 80, y=DEALER_Y)
        self.dealer_score_text = self._create_ui_text("Score: ?", INFO_FONT_SIZE, x=DEALER_CARD_X - 80, y=DEALER_Y + 30)
        self.dealer_cards_text = self._create_ui_text("", CARD_FONT_SIZE, x=DEALER_CARD_X, y=DEALER_Y)

        self.player_hand_text = self._create_ui_text("Player:", INFO_FONT_SIZE, x=PLAYER_CARD_X - 80, y=PLAYER_Y)
        self.player_score_text = self._create_ui_text("Score: 0", INFO_FONT_SIZE, x=PLAYER_CARD_X - 80, y=PLAYER_Y + 30)
        self.player_cards_text = self._create_ui_text("", CARD_FONT_SIZE, x=PLAYER_CARD_X, y=PLAYER_Y)

        self.message_text = self._create_ui_text("", MESSAGE_FONT_SIZE, x=self.engine.screen.width // 2, y=250)
        self.message_text.components[Transform].x -= 100 # Approx center, update later

        # Buttons (Text entities acting as buttons)
        self.hit_button = self._create_ui_text("[H]it", INFO_FONT_SIZE, x=HIT_BUTTON_X, y=BUTTON_Y, color=BUTTON_COLOR)
        self.stand_button = self._create_ui_text("[S]tand", INFO_FONT_SIZE, x=STAND_BUTTON_X, y=BUTTON_Y, color=BUTTON_COLOR)

        # Subscribe Events
        self.subscribe(self.engine.events.key_down, self.handle_input)
        self.subscribe(self.engine.events.mouse_button_down, self.handle_mouse_click)
        # Optional: Add mouse motion for hover later
        # self.subscribe(self.engine.events.mouse_motion, self.handle_mouse_motion)

        # Start the first round
        self._start_new_round()

    def unload(self):
        super().unload()
        print("BlackjackScene Unloaded.")

    # --- UI Helper ---
    def _create_ui_text(self, text, size, x, y, color=TEXT_COLOR, depth=DrawDepth.UI):
        """Helper to create and track TextEntity."""
        entity = self.create_entity(TextEntity,
            text=text, font_name=None, font_size=size, color=color,
            engine=self.engine, x=x, y=y, depth=depth
        )
        return entity

    # --- Game Logic ---
    def _create_deck(self):
        self.deck = [(rank, suit) for rank in DECK_RANKS for suit in DECK_SUITS]

    def _shuffle_deck(self):
        random.shuffle(self.deck)

    def _deal_card(self, hand):
        if not self.deck:
            print("Deck empty! Reshuffling...")
            self._create_deck()
            self._shuffle_deck()
            # Optional: Add a small message?
        card = self.deck.pop()
        hand.append(card)
        return card

    def _calculate_hand_value(self, hand, count_hidden=False):
        value = 0
        ace_count = 0
        for i, (rank, suit) in enumerate(hand):
            if not count_hidden and self.dealer_card_hidden and hand == self.dealer_hand and i == 1:
                continue # Skip hidden dealer card

            if rank.isdigit():
                value += int(rank)
            elif rank in ["T", "J", "Q", "K"]:
                value += 10
            elif rank == "A":
                ace_count += 1
                value += 11 # Assume 11 initially

        # Adjust for Aces if value is over 21
        while value > BLACKJACK_VALUE and ace_count > 0:
            value -= 10
            ace_count -= 1
        return value

    def _format_card(self, card):
        rank, suit = card
        # Optional: Use unicode symbols for suits later
        # suit_symbols = {"H": "♥", "D": "♦", "C": "♣", "S": "♠"}
        return f"{rank}{suit}" # e.g., "KH", "AS", "7D"

    def _format_hand(self, hand, hide_one=False):
        if not hand: return ""
        if hide_one and len(hand) > 1:
            # Show first card, hide second
            return f"{self._format_card(hand[0])} [?]"
        else:
            return " ".join(self._format_card(card) for card in hand)

    def _start_new_round(self):
        print("Starting new round...")
        self.player_hand.clear()
        self.dealer_hand.clear()
        self._create_deck()
        self._shuffle_deck()
        self.dealer_card_hidden = True
        self.message = ""

        # Deal initial hands
        self._deal_card(self.player_hand)
        self._deal_card(self.dealer_hand)
        self._deal_card(self.player_hand)
        self._deal_card(self.dealer_hand) # Dealer's hidden card

        self.player_score = self._calculate_hand_value(self.player_hand)
        # Dealer's visible score
        self.dealer_score = self._calculate_hand_value(self.dealer_hand, count_hidden=False)

        # Check for initial player Blackjack
        if self.player_score == BLACKJACK_VALUE:
            self.dealer_card_hidden = False # Reveal dealer card immediately
            self.dealer_score = self._calculate_hand_value(self.dealer_hand)
            if self.dealer_score == BLACKJACK_VALUE:
                self._end_round("Push! Both have Blackjack!")
            else:
                self._end_round("Blackjack! Player wins!")
        else:
            self.game_state = STATE_PLAYER_TURN
            self.message = "Player turn: [H]it or [S]tand?"

        self._update_display()


    def _player_hit(self):
        if self.game_state != STATE_PLAYER_TURN: return
        print("Player hits.")
        self._deal_card(self.player_hand)
        self.player_score = self._calculate_hand_value(self.player_hand)
        self._update_display()

        if self.player_score > BLACKJACK_VALUE:
            self._end_round("Player busts!")
        elif self.player_score == BLACKJACK_VALUE:
            # Player got 21, automatically stand
            self._player_stand()


    def _player_stand(self):
        if self.game_state != STATE_PLAYER_TURN: return
        print("Player stands.")
        self.game_state = STATE_DEALER_TURN
        self.dealer_card_hidden = False # Reveal card
        self.dealer_score = self._calculate_hand_value(self.dealer_hand) # Update score with revealed card
        self.message = "Dealer's turn..."
        self._update_display()
        # Give a slight delay before dealer plays for visual feedback
        # Option 1: Simple time.sleep (blocks rendering) - Not ideal
        # Option 2: Use a timer in self.update() to trigger _dealer_play - Better
        # For now, let's call directly for simplicity, add timer later if needed
        self._dealer_play()


    def _dealer_play(self):
        # This logic assumes it's called *after* revealing card and updating score
        while self.dealer_score < DEALER_STAND_MIN:
            print("Dealer hits.")
            # Add delay here if using timer approach
            self._deal_card(self.dealer_hand)
            self.dealer_score = self._calculate_hand_value(self.dealer_hand)
            self._update_display() # Update display after each dealer hit

            if self.dealer_score > BLACKJACK_VALUE:
                self._end_round("Dealer busts! Player wins!")
                return # Exit loop and function

        # Dealer stands
        print("Dealer stands.")
        self._end_round(self._determine_winner())


    def _determine_winner(self):
        # Assumes neither busted here (busts handled earlier)
        if self.player_score > self.dealer_score:
            return "Player wins!"
        elif self.dealer_score > self.player_score:
            return "Dealer wins!"
        else:
            return "Push!" # Scores are equal

    def _end_round(self, result_message):
        print(f"Round Over: {result_message}")
        self.game_state = STATE_ROUND_OVER
        self.message = f"{result_message} (Press Enter/Space to deal again)"
        self.dealer_card_hidden = False # Ensure card is revealed
        self._update_display()

    # --- Display Update ---
    def _update_display(self):
        """Updates all Text Entities based on the current game state."""
        # Update Hands
        self.player_cards_text.text = self._format_hand(self.player_hand)
        self.dealer_cards_text.text = self._format_hand(self.dealer_hand, hide_one=self.dealer_card_hidden)

        # Update Scores
        self.player_score_text.text = f"Score: {self.player_score}"
        if self.dealer_card_hidden:
            # Show score of visible card only
            visible_dealer_score = self._calculate_hand_value([self.dealer_hand[0]]) if self.dealer_hand else 0
            self.dealer_score_text.text = f"Score: {visible_dealer_score} + ?"
        else:
            self.dealer_score_text.text = f"Score: {self._calculate_hand_value(self.dealer_hand)}" # Show full score

        # Update Message & Center it
        self.message_text.text = self.message
        if Render in self.message_text.components and self.message_text.components[Render].texture:
            text_width = self.message_text.components[Render].texture.get_width()
            self.message_text.components[Transform].x = (self.engine.screen.width - text_width) // 2

        # Update Button Visibility/Appearance (Optional: change color based on state)
        is_player_turn = (self.game_state == STATE_PLAYER_TURN)
        # For now, just leave buttons visible, rely on state checks in handlers
        self.hit_button.color = BUTTON_HOVER_COLOR if is_player_turn else BUTTON_COLOR
        self.stand_button.color = BUTTON_HOVER_COLOR if is_player_turn else BUTTON_COLOR


    # --- Input Handling ---
    def handle_input(self, key):
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
            # Check Hit Button
            if self.hit_button.components[Render].texture: # Check if texture exists
                 hit_rect = self.hit_button.components[Render].texture.get_rect(
                     topleft=(self.hit_button.components[Transform].x, self.hit_button.components[Transform].y))
                 if hit_rect.collidepoint(pos):
                     self._player_hit()
                     return # Click handled

            # Check Stand Button
            if self.stand_button.components[Render].texture: # Check if texture exists
                 stand_rect = self.stand_button.components[Render].texture.get_rect(
                     topleft=(self.stand_button.components[Transform].x, self.stand_button.components[Transform].y))
                 if stand_rect.collidepoint(pos):
                     self._player_stand()
                     return # Click handled

        elif self.game_state == STATE_ROUND_OVER:
            # Allow clicking anywhere (or specific area) to restart?
            # For now, only keyboard restart is implemented. Add click restart later if desired.
            pass

    # Optional: handle_mouse_motion for hover effects on buttons
    # def handle_mouse_motion(self, pos): ...