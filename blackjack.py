# Mini-project #6 - Blackjack
# =========================================================
# Additional functionality includes: value hints, counter for deals,
#  'Restart' button, 'Show rules/Hide rules' switch, Same Deck mode,
#  warning messages if the invalid button is pressed
#  or a deck is re-filled in Same Deck mode to prevent shortage of cards.

# /Basic functionality as it is described in Mini-project assignment takes about 180 lines without comments :-/

import simplegui
import random

# load card sprite - 949x392 - source: jfitz.com
CARD_SIZE = (73, 98)
CARD_CENTER = (36.5, 49)
card_images = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/cards.jfitz.png")

CARD_BACK_SIZE = (71, 96)
CARD_BACK_CENTER = (35.5, 48)
card_back = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/card_back.png")

in_play = False             # checks if the Player's hand is in play
outcome = ""                # upper message / notifiction
message = ""                # lower message / addressing to Player
score = 0                   # counter for wins (+1) and loses (-1)
hint_off = True             # control variable for 'Show Hint' button
outcome_color = "#00008B"   # basic color of outcome message (changed if warning message is blinking)
blinks = 0                  # counter for timer
deals = 0                   # number of deals / zeroed by Restart button
shuffle_off = False         # control variable for Same Deck mode
show_rules = False          # control variable for Show Rules mode

rules = ["1. Press 'Deal' to re-fill and re-shuffle the deck",
         "     before playing. Do not press it at the middle",
         "     of a hand; otherwise, you lose the hand.",
         "2. Press 'Same deck' to play without filling a deck.",
         "     If the deck is almost empty, it is re-filled automatically",
         "     and appropriate notificaton is displayed.",
         "3. Score +1 if you win and -1 if you lose.",
         "4. See number of deals in a counter before SCORE.",
         "5. Press 'Restart' to set score and number of deals to zero.",
         "     You can press it at any moment without losing a hand.",
         "6. Optionally, switch on/off value hints for a hand.",
         "7. The rest goes according to /simplified/ Blackjack rules:",
         "     to win, have 21 or less but more than Dealer has",
         "     unless he busted."]

# define globals for cards
SUITS = ('C', 'S', 'H', 'D')
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K')
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':10, 'Q':10, 'K':10}

# define card class
class Card:
    def __init__(self, suit, rank):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print "Invalid card: ", suit, rank

    def __str__(self):
        return self.suit + self.rank

    def get_suit(self):
        return self.suit

    def get_rank(self):
        return self.rank

    def draw(self, canvas, pos):
        """Draws a 'face' of card based on its rank and suit = x & y coordinates in tiled image"""
        card_loc = (CARD_CENTER[0] + CARD_SIZE[0] * RANKS.index(self.rank),
                    CARD_CENTER[1] + CARD_SIZE[1] * SUITS.index(self.suit))
        canvas.draw_image(card_images, card_loc, CARD_SIZE, [pos[0] + CARD_CENTER[0], pos[1] + CARD_CENTER[1]], CARD_SIZE)

    def draw_back(self, canvas, pos):
        """Draws card back"""
        canvas.draw_image(card_back, CARD_BACK_CENTER, CARD_BACK_SIZE, [pos[0] + CARD_CENTER[0], pos[1] + CARD_CENTER[1]], CARD_SIZE)

# define hand class
class Hand:
    def __init__(self):
        self.hand = []

    def __str__(self):
        return str([str(item) for item in self.hand])

    def add_card(self, card):
        self.hand.append(card)

    # count aces as 1, if the hand has an ace, then add 10 to hand value if it doesn't bust
    def get_value(self):
        self.value = 0
        for item in self.hand:
            self.value += VALUES[item.get_rank()]
        for item in self.hand:
            if item.get_rank() == "A":
                if self.value + 10 <= 21:
                    self.value += 10
        return self.value

    def busted(self):
        return self.value > 21

    def draw(self, canvas, p, index=[]):
        """Draws a hand. If some cards need to be drawn as 'hole',
i.e., replaced by card_back image, their indexes in hand list should be specified
and passed as 'index' argument (initialized as an empty list).
For example, in Blackjack, index takes either [0], or [].
    This option might be useful in other card games templates
when one needs to 'hide' not only the first card in a hand, but more cards."""

        for item in self.hand:
            item.draw(canvas, [p[0] + (CARD_SIZE[0] + 10) * self.hand.index(item), p[1]])
        for i in index:
            self.hand[i].draw_back(canvas, [p[0] + (CARD_SIZE[0] + 10) * i, p[1]])

# define deck class
class Deck:
    def __init__(self):
        self.deck = [Card(s, r) for s in SUITS for r in RANKS]

    # add cards back to deck and shuffle
    def shuffle(self):
        self.deck = [Card(s, r) for s in SUITS for r in RANKS]
        random.shuffle(self.deck)

    def deal_card(self):
        """Deal a card; if no cards are left in deck, it is re-filled"""
        if self.get_len() < 1:
            self.shuffle()
        return self.deck.pop(0)

    def __str__(self):
        return str([str(item) for item in self.deck])

    def get_len(self):
        """Useful method to control the number of cards left in a deck"""
        return len(self.deck)

# define event handlers for buttons
def deal():
    """re-fills and re-shuffles a deck unless Same Deck mode is switched on.
makes initial deal of 2x2 cards, with 'a hole' card for Dealer"""
    global outcome, message, in_play, dealt, player_hand, dealer_hand, score, deck, deals, shuffle_off
    player_hand = Hand()
    dealer_hand = Hand()
    if in_play:
        score -=1
    if not shuffle_off:
        deck.shuffle()
    else:
        shuffle_off = False
    for i in range(2):
        player_hand.add_card(deck.deal_card())
        dealer_hand.add_card(deck.deal_card())
    in_play = True
    message = "Hit or stand?"
    outcome = "?..."
    deals += 1

def same_deck():
    """Prevents re-filling and re-shuffling of a deck, then deals.
If the number or cards in deck is less than needed for a round
(in this case, 7 is suggested as an optimal max number),
it is re-filled and a notification message is displayed"""
    global shuffle_off, outcome_reserve, warning
    shuffle_off = True
    if deck.get_len() < 7:
        warning = "New deck released!"
        timer.start()
        outcome_reserve = "?..."
    deal()

def hit():
    """If 'Hit' button is pressed when Player's hand is in play,
counts the value of Player's hand and indicate if he/she is busted"""
    global in_play, dealt, player_hand, deck, outcome, message, score, outcome_reserve, warning
    if not in_play:
        warning = "Invalid option!"
        timer.start()
        outcome_reserve = outcome
    else:
        player_hand.add_card(deck.deal_card())
        player_hand.get_value()
        if player_hand.busted():
            score -= 1
            outcome = "You've busted and lost!"
            message = "Want new deal?"
            in_play = False
        else:
            message = "Hit or stand?"

def stand():
    """Values Dealer's hand and prints the result of a round"""
    global dealer_hand, player_hand, deck, message, outcome, outcome_reserve, in_play, dealt, score, warning
    if in_play:
        while dealer_hand.get_value() < 17:
            dealer_hand.add_card(deck.deal_card())
        if dealer_hand.busted():
            score += 1
            outcome = "Dealer busted, you won!"
        elif in_play and dealer_hand.get_value() > player_hand.get_value():
            score -= 1
            outcome = "Dealer won!"
        elif in_play and dealer_hand.get_value() == player_hand.get_value():
            score -= 1
            outcome = "Ties! Dealer won!"
        else:
            score += 1
            outcome = "You won!"
        in_play = False
    else:
        warning = "Invalid option!"
        timer.start()
        outcome_reserve = outcome
    message = "Want new deal?"

def value_hint():
    """Changes global variables to draw hint values.
Changes the button label, so that it could be used as on/off switch"""
    global hint_off
    if hint_off:
        hint_button.set_text("Hide value hint")
        hint_off = False
    else:
        hint_button.set_text("Show value hint")
        hint_off = True

def rules_hint():
    """Changes global variables to draw 'Help' page.
Changes the button label, so that it could be used as on/off switch"""
    global show_rules
    if show_rules:
        rules_button.set_text("Show rules")
        frame.set_canvas_background("Green")
        show_rules = False
    else:
        rules_button.set_text("Return to the game")
        show_rules = True

def restart():
    """Set score and number of deals to zero, even if pressed at the middle of the hand"""
    global score, deals, in_play
    score = 0
    if in_play:
        score = 1
    deals = 0
    deal()

def timer():
    """Adds blinking effect to the warning messages"""
    global outcome_color, outcome, outcome_reserve, blinks, warning
    outcome = warning
    if outcome_color == "#00008B":
        outcome_color = "Red"
    elif outcome_color == "Red":
        outcome_color = "White"
    else:
        outcome_color = "Red"
    blinks += 1
    if blinks == 20:
        outcome_color = "#00008B"
        timer.stop()
        blinks = 0
        outcome = outcome_reserve

# draw handler
def draw(canvas):
    """Draws 'a table with cards' of 'Help page', based on a control variable.
Indicates what cards should be drawn as 'hole'.
Displays/hides value hints on the button click"""
    global player_hand, dealer_hand, index, switch_hint, show_rules
    if not show_rules:
        if in_play:
            index = [0]
        else:
            index = []
        dealer_hand.draw(canvas, [130, 200], index)
        player_hand.draw(canvas, [130, 350])
        canvas.draw_text("Black", [70, 75], 40, "Black")
        canvas.draw_text("jack", [185, 75], 40, "Yellow")
        canvas.draw_text("SCORE: " + str(score), [410, 70], 20, "White")
        canvas.draw_text(str(deals) + ")", [370, 70], 20, "Yellow")
        canvas.draw_text("Dealer:", [27, 255], 20, "White")
        canvas.draw_text("Player:", [27, 405], 20, "White")
        canvas.draw_text(outcome, [130, 155], 30, outcome_color)
        canvas.draw_text(message, [130, 505], 30, "#00008B")
        if not hint_off:
            canvas.draw_text("value = " + str(player_hand.get_value()), [23, 435], 15, "Yellow")
            if not in_play:
                canvas.draw_text("value = " + str(dealer_hand.get_value()), [23, 285], 15, "Yellow")
    else:
        frame.set_canvas_background("Teal")
        for rule in rules:
            canvas.draw_text("QUICK HELP:", [240, 65], 17, "Yellow")
            canvas.draw_text(rule, [60, 115 + rules.index(rule) * 30], 17, "White")

# initialization frame
frame = simplegui.create_frame("Blackjack", 630, 600)
frame.set_canvas_background("Green")

# buttons and canvas callback
frame.add_button("Deal", deal, 200)
frame.add_button("Same deck", same_deck, 200)
frame.add_button("Hit",  hit, 200)
frame.add_button("Stand", stand, 200)
hint_button = frame.add_button("Show value hint", value_hint, 200)
frame.add_button("Restart", restart, 200)
rules_button = frame.add_button("Show rules", rules_hint, 200)
frame.set_draw_handler(draw)
timer = simplegui.create_timer(70, timer)

# deal an initial hand
deck = Deck()
deal()

# get things rolling
frame.start()
