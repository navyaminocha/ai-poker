from enum import Enum
from typing import List, Tuple
from dataclasses import dataclass
from card import Card
from math import ceil


class PlayerAction(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all-in"


class PlayerStatus(Enum):
    ACTIVE = "active"
    FOLDED = "folded"
    ALL_IN = "all-in"
    OUT = "out"


@dataclass
class Player:
    name: str
    stack: int
    uuid: int = 0
    status: PlayerStatus = PlayerStatus.ACTIVE
    hole_cards: List[Card] = None
    bet_amount: int = 0

    def __post_init__(self):
        if self.hole_cards is None:
            self.hole_cards = []

    def reset_for_new_hand(self):
        self.hole_cards = []
        self.status = PlayerStatus.ACTIVE if self.stack > 0 else PlayerStatus.OUT
        self.bet_amount = 0

    def can_make_action(self) -> bool:
        return self.status in [PlayerStatus.ACTIVE]

    # def take_action(self, action: PlayerAction, amount: int = 0) -> Tuple[PlayerAction, int]:
    #     if amount < 0:
    #         raise ValueError("Amount cannot be negative.")

    #     amount = ceil(amount)
    #     if action == PlayerAction.FOLD:
    #         self.status = PlayerStatus.FOLDED
    #         return action, 0

    #     if action == PlayerAction.CALL:
    #         max_bet = min(amount, self.stack)
    #         self.stack -= max_bet
    #         self.bet_amount += max_bet
    #         if self.stack == 0:
    #             self.status = PlayerStatus.ALL_IN
    #             return PlayerAction.ALL_IN, max_bet
    #         return PlayerAction.CALL, max_bet

    #     if action in [PlayerAction.BET, PlayerAction.RAISE]:
    #         # Calculate maximum possible bet
    #         max_bet = min(amount, self.stack)
    #         delta = max_bet - self.bet_amount

    #         if action == PlayerAction.RAISE:
    #             max_bet = min(amount - self.bet_amount, self.stack)

    #         # Update stack and bet amount
    #         if max_bet == self.stack:  # all-in case, when player is all-in the chips he puts in is the stack itself
    #             self.stack -= max_bet
    #             self.bet_amount += max_bet
    #         else:  # when player is not all-in he has to reach maximum bet
    #             self.stack -= delta  # (max_bet - self.bet_amount)
    #             self.bet_amount += delta

    #         # Check if player_hand is all-in
    #         if self.stack == 0:
    #             self.status = PlayerStatus.ALL_IN
    #             return PlayerAction.ALL_IN, max_bet

    #         return action, delta  # if the case in not all-in case then return delta not max_bet

    #     if action == PlayerAction.ALL_IN:
    #         actual = self.stack
    #         self.bet_amount += self.stack
    #         self.stack = 0
    #         self.status = PlayerStatus.ALL_IN
    #         return PlayerAction.ALL_IN, actual

    #     return action, 0
    def take_action(self, action: PlayerAction, amount: int = 0) -> Tuple[PlayerAction, int]:
        if amount < 0:
            raise ValueError("Amount cannot be negative.")

        from math import ceil
        amount = ceil(amount)
        
        if action == PlayerAction.FOLD:
            self.status = PlayerStatus.FOLDED
            return action, 0

        # For CALL, BET, RAISE, 'amount' is the TARGET TOTAL BET the player wants to reach this round.
        if action in [PlayerAction.CALL, PlayerAction.BET, PlayerAction.RAISE, PlayerAction.ALL_IN]:
            if action == PlayerAction.ALL_IN:
                # For ALL_IN, ignore 'amount' and take their entire remaining stack.
                delta = self.stack
            else:
                # Calculate how much MORE chips they need to put into the pot.
                delta = amount - self.bet_amount
                
            # A player can never add more than their current stack
            actual_delta = min(delta, self.stack)
            
            # Update player state
            self.stack -= actual_delta
            self.bet_amount += actual_delta
            
            # If the action consumed their whole stack, it's forcibly an ALL_IN
            if self.stack == 0:
                self.status = PlayerStatus.ALL_IN
                return PlayerAction.ALL_IN, actual_delta
                
            return action, actual_delta

        return action, 0

    def action(self, game_state: list[int], action_history: list) -> Tuple[PlayerAction, int]:
        """
        Parameters:
            game_state: a numerical representation of the game state
            action_history: a list of actions taken in sequence

        Returns:
            A PlayerAction and amount tuple
        """
        return PlayerAction.FOLD, 0
