from player import Player, PlayerAction
from game import PokerGame, GamePhase
from card import Card
import random
from hand_evaluator import HandEvaluator
from card import Card, Rank, Suit, Deck

import random
from player import Player, PlayerAction
from card import Card, Rank, Suit
from hand_evaluator import HandEvaluator

class MonteCarloPlayer(Player):
    def __init__(self, name, stack, simulations=400):
        super().__init__(name, stack)
        self.simulations = simulations
        self.initial_stack = stack

    def action(self, game_state: list[int], action_history: list):
        # --- Parse game state ---
        my_cards_idx   = game_state[0:2]
        comm_cards_idx = [i for i in game_state[2:7] if i != 0]
        pot            = game_state[7]
        current_bet    = game_state[8]
        big_blind      = game_state[9]
        num_players    = game_state[10]

        my_bet_so_far = self.bet_amount
        call_amount   = current_bet - my_bet_so_far

        my_cards   = [self._index_to_card(i) for i in my_cards_idx]
        comm_cards = [self._index_to_card(i) for i in comm_cards_idx]

        # --- Win rate via simulation ---
        sim_count = self._get_simulation_count(comm_cards, pot, big_blind)
        win_rate  = self.calculate_win_rate(my_cards, comm_cards, num_players - 1, sim_count)

        # --- Modifiers ---
        stack_ratio           = self.stack / max(self.initial_stack, 1)
        tightness_modifier    = 0.06 if stack_ratio < 0.5 else 0.0
        aggression_multiplier = 1.75 if stack_ratio > 1.5 else 1.25

        opponent_aggression   = self._estimate_opponent_aggression(action_history)
        aggression_adjustment = opponent_aggression * 0.02

        spr = self.stack / max(pot, 1)

        # --- Decision logic ---

        # ALL-IN
        allin_threshold = max(0.45, 0.70 - (0.1 / max(spr, 1))) + (tightness_modifier / 2)
        if win_rate > allin_threshold:
            return PlayerAction.ALL_IN, self.stack

        # RAISE
        raise_threshold = 0.28 + tightness_modifier + aggression_adjustment
        if win_rate > raise_threshold:
            raise_size = int(current_bet + (pot * 0.85 * aggression_multiplier))
            min_raise  = current_bet + big_blind
            return PlayerAction.RAISE, max(raise_size, min_raise)

        # CALL
        if call_amount > 0:
            pot_odds    = call_amount / (pot + call_amount)
            call_buffer = 0.0 + tightness_modifier
            if win_rate > (pot_odds + call_buffer):
                return PlayerAction.CALL, call_amount
            return PlayerAction.FOLD, 0

        # CHECK or BET
        if call_amount == 0:
            bet_threshold = 0.30 + tightness_modifier
            if win_rate > bet_threshold:
                bet_size = max(int(pot * 0.85), big_blind * 3)
                return PlayerAction.BET, bet_size
            return PlayerAction.CHECK, 0

        return PlayerAction.FOLD, 0

    def calculate_win_rate(self, my_cards, comm_cards, num_opponents, sim_count=None):
        if sim_count is None:
            sim_count = self.simulations

        wins = 0
        visible_indices = {c.get_index() for c in (my_cards + comm_cards)}
        full_deck       = [self._index_to_card(i) for i in range(52)]
        remaining_deck  = [c for c in full_deck if c.get_index() not in visible_indices]

        needed_comm  = 5 - len(comm_cards)
        cards_needed = needed_comm + (num_opponents * 2)

        valid_sims = 0

        for _ in range(sim_count):
            if len(remaining_deck) < cards_needed:
                continue

            random.shuffle(remaining_deck)

            sim_comm = comm_cards + remaining_deck[:needed_comm]
            my_res   = HandEvaluator.evaluate_hand(my_cards, sim_comm)

            best_outcome = "win"

            for i in range(num_opponents):
                start_idx = needed_comm + (i * 2)
                opp_cards = remaining_deck[start_idx: start_idx + 2]
                opp_res   = HandEvaluator.evaluate_hand(opp_cards, sim_comm)

                if (opp_res.hand_rank.value > my_res.hand_rank.value or
                        (opp_res.hand_rank == my_res.hand_rank and
                         opp_res.hand_value > my_res.hand_value)):
                    best_outcome = "loss"
                    break
                elif (opp_res.hand_rank == my_res.hand_rank and
                      opp_res.hand_value == my_res.hand_value):
                    best_outcome = "tie"

            if best_outcome == "win":
                wins += 1
            elif best_outcome == "tie":
                wins += 0.5

            valid_sims += 1

        return wins / valid_sims if valid_sims > 0 else 0.0

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _get_simulation_count(self, comm_cards, pot, big_blind):
        street_sims = {0: 700, 3: 550, 4: 450, 5: 350}
        base = street_sims.get(len(comm_cards), self.simulations)
        if pot > big_blind * 20:
            base = int(base * 1.5)
        return base

    def _estimate_opponent_aggression(self, action_history):
        if not action_history:
            return 0.0
        raises = sum(
            1 for a in action_history
            if isinstance(a, dict) and a.get("action") in ("RAISE", "ALL_IN")
        )
        return raises / len(action_history)

    def _index_to_card(self, index: int) -> Card:
        suit_val = index // 13
        rank_val = (index % 13) + 1
        return Card(Rank(rank_val + 1), Suit(suit_val))

class FoldPlayer(Player):

    def action(self, game_state: list[int], action_history: list):
        return PlayerAction.FOLD, 0
    
class AllInPlayer(Player):
    def action(self, game_state: list[int], action_history: list):
        return PlayerAction.ALL_IN, self.stack
    

    
class RandomPlayer(Player):
    def action(self, game_state: list[int], action_history: list):
        # 1. Extract necessary info from game_state
        current_bet = game_state[8]
        big_blind = game_state[9]
        
        # Calculate how much is needed to stay in (Call amount)
        call_amount = current_bet - self.bet_amount
        
        prob = random.random()

        # CASE A: No one has bet yet (It's a "Check" or "Bet" situation)
        if call_amount == 0:
            if prob < 0.3:  # 30% chance to Bet
                # Bet a random amount between 1 BB and 1/4 of the stack
                max_bet = max(big_blind, self.stack // 4)
                bet_amount = random.randint(big_blind, max(big_blind, max_bet))
                return PlayerAction.BET, bet_amount
            else:  # 70% chance to Check
                return PlayerAction.CHECK, 0

        # CASE B: Someone has bet (Must Fold, Call, Raise, or All-In)
        else:
            if prob < 0.2:  # 20% chance to Fold
                return PlayerAction.FOLD, 0
            
            elif prob < 0.7:  # 50% chance to Call
                # Engine handles the stack vs call_amount logic in take_action
                return PlayerAction.CALL, call_amount
            
            elif prob < 0.9:  # 20% chance to Raise
                # Raise must be at least the current_bet + small increment
                raise_to = current_bet + big_blind
                if self.stack > (raise_to - self.bet_amount):
                    return PlayerAction.RAISE, raise_to
                else:
                    return PlayerAction.ALL_IN, self.stack
            
            else:  # 10% chance to go All-In
                return PlayerAction.ALL_IN, self.stack
        



class RaisePlayer(Player):

    def action(self, game_state: list[int], action_history: list):
        current_raise = game_state[8]
        if self.stack > (current_raise + 40):
            return PlayerAction.RAISE, current_raise + 40
        return PlayerAction.ALL_IN, self.stack



class InputPlayer(Player):
    def action(self, game_state: list[int], action_history: list):
        call_amount = game_state[8] - self.bet_amount

        # Display available actions
        print("Available actions:")
        if call_amount == 0:
            print("1. Check")
            print("2. Bet")
        else:
            print("1. Fold")
            print("2. Call", call_amount)
            print("3. Raise")

        action_input = input("Enter choice: ")

        try:
            if call_amount == 0:
                if action_input == "1":
                    return PlayerAction.CHECK, 0
                elif action_input == "2":
                    amount = int(input("Enter bet amount: "))
                    return PlayerAction.BET, amount
            else:
                if action_input == "1":
                    return PlayerAction.FOLD, 0
                elif action_input == "2":
                    return PlayerAction.CALL, call_amount
                elif action_input == "3":
                    amount = int(input(f"Enter total raise amount: "))
                    return PlayerAction.RAISE, amount
                else:
                    return PlayerAction.FOLD, 0
        except ValueError:
            print("Invalid input")
            return PlayerAction.FOLD, 0
