import random
import time
from typing import Dict, List, Tuple
from player import Player, PlayerAction
from card import Card, Rank, Suit
from hand_evaluator import HandEvaluator, HandRank

RANKS = "23456789TJQKA"
SUITS = "cdhs"

def card_value(card):
    return RANKS.index(card[0])

def evaluate_hand_strength(hole_cards, community_cards):
    """
    VERY simplified hand strength:
    Returns value between 0 and 1
    """
    all_cards = hole_cards + community_cards
    
    values = [card_value(c) for c in all_cards]
    
    # High card strength
    max_val = max(values)
    
    # Pair check
    pair = len(set(values)) < len(values)
    
    strength = max_val / 12  # normalize (A highest = 12)
    
    if pair:
        strength += 0.3
    
    return min(strength, 1.0)


# ----- Decision Logic -----

def decide_action(game_state):
    """
    game_state example:
    {
        "hole_cards": ["Ah", "Kd"],
        "community_cards": ["2c", "7d", "Jh"],
        "pot": 100,
        "current_bet": 10,
        "min_raise": 20
    }
    """
    
    hole_cards = game_state["hole_cards"]
    community_cards = game_state["community_cards"]
    current_bet = game_state["current_bet"]
    min_raise = game_state["min_raise"]
    
    strength = evaluate_hand_strength(hole_cards, community_cards)
    
    # Add randomness (bluff factor)
    bluff = random.random()
    
    # ---- Decision Rules ----
    
    if strength > 0.8:
        # Very strong hand → aggressive
        return {
            "action": "raise",
            "amount": min_raise * 2
        }
    
    elif strength > 0.5:
        if bluff > 0.7:
            return {
                "action": "raise",
                "amount": min_raise
            }
        else:
            return {
                "action": "call"
            }
    
    else:
        if bluff > 0.85:
            return {
                "action": "call"
            }
        else:
            return {
                "action": "fold"
            }


# ----- Example Run -----

if __name__ == "__main__":
    game_state = {
        "hole_cards": ["Ah", "Kd"],
        "community_cards": ["2c", "7d", "Jh"],
        "pot": 100,
        "current_bet": 10,
        "min_raise": 20
    }
    
    decision = decide_action(game_state)
    print(decision)