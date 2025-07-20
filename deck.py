import random

class Deck():
    def __init__(self, cards):
        # if len(cards) < 45 or len(cards) > 60:
        #     raise ValueError("Deck must contain between 45 and 60 cards.")
        self.cards = cards

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, count=1):
        if count < 1 and count > 7:
            raise ValueError("Count must be at least 1 and less than 7")
        
        if count > len(self.cards):
            raise ValueError("Not enough cards in the deck to draw.")
        
        drawn_cards = self.cards[:count]
        self.cards = self.cards[count:]
        
        return drawn_cards

    def __len__(self):
        return len(self.cards)

    def __str__(self):
        return f"Deck of {len(self.cards)} cards"