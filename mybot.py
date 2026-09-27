# # # # # from player import Player, PlayerAction

# # # # # class MyBot(Player):
# # # # #     def action(self, game_state, action_history):
# # # # #         # Unpack the game state
# # # # #         card1, card2 = game_state[0], game_state[1]
# # # # #         community = game_state[2:7]       # 5 community cards (0 = not dealt)
# # # # #         pot        = game_state[7]
# # # # #         current_bet = game_state[8]
# # # # #         blind      = game_state[9]
# # # # #         my_stack   = game_state[11 + game_state[10]]  # game_state[10] = active player index

# # # # #         call_amount = current_bet - self.bet_amount

# # # # #         # Simple strategy: raise with high cards, call medium, fold low
# # # # #         high_cards = {11, 12, 13, 14, 24, 25, 26, 27}  # Jacks-Aces (spades + hearts)
        
# # # # #         if card1 in high_cards or card2 in high_cards:
# # # # #             raise_to = current_bet + blind * 3
# # # # #             if self.stack > raise_to:
# # # # #                 return PlayerAction.RAISE, raise_to
# # # # #             return PlayerAction.ALL_IN, self.stack

# # # # #         elif call_amount == 0:
# # # # #             return PlayerAction.CHECK, 0

# # # # #         elif call_amount <= pot * 0.3:  # call if pot odds are decent
# # # # #             return PlayerAction.CALL, call_amount

# # # # #         else:
# # # # #             return PlayerAction.FOLD, 0

# # # # # import random
# # # # # import time
# # # # # from typing import Tuple, List
# # # # # from player import Player, PlayerAction
# # # # # from card import Card, Rank, Suit
# # # # # from hand import decode_card
# # # # # from hand_evaluator import HandEvaluator

# # # # # class MyBot(Player):
# # # # #     def __init__(self, name: str, stack: int, simulations: int = 1000):
# # # # #         super().__init__(name, stack)
# # # # #         self.simulations = simulations
# # # # #         self.evaluator = HandEvaluator()

# # # # #     def action(self, game_state: list[int], action_history: list) -> Tuple[PlayerAction, int]:
# # # # #         # 1. Parse game_state list based on game.get_game_state() definition
# # # # #         community_indices = game_state[2:7]
# # # # #         community_cards = [decode_card(idx) for idx in community_indices if idx != 0]
        
# # # # #         pot = game_state[7]
# # # # #         current_bet = game_state[8]
# # # # #         big_blind = game_state[9]
        
# # # # #         # Calculate how much we need to put in to stay in the hand
# # # # #         call_amount = current_bet - self.bet_amount

# # # # #         # 2. Run Simulations
# # # # #         win_prob = self._simulate_win_probability(self.hole_cards, community_cards)

# # # # #         # 3. Calculate Pot Odds
# # # # #         # Pot odds = amount to call / (total pot after calling)
# # # # #         pot_odds = 0.0
# # # # #         if call_amount > 0:
# # # # #             pot_odds = call_amount / (pot + call_amount)

# # # # #         # 4. Execute Strategy
# # # # #         return self._make_decision(win_prob, pot_odds, call_amount, big_blind)

# # # # #     def _simulate_win_probability(self, hole_cards: List[Card], community_cards: List[Card]) -> float:
# # # # #         # Pre-flop uses a weighted estimate to save time/compute
# # # # #         if len(community_cards) == 0:
# # # # #             return self._preflop_win_estimate(hole_cards)
        
# # # # #         wins = 0
# # # # #         ties = 0
        
# # # # #         # Identify cards already out of the deck
# # # # #         known_cards = set()
# # # # #         for c in hole_cards + community_cards:
# # # # #             known_cards.add((c.rank, c.suit))
        
# # # # #         deck = [Card(r, s) for r in Rank for s in Suit if (r, s) not in known_cards]
# # # # #         cards_to_reveal = 5 - len(community_cards)

# # # # #         for _ in range(self.simulations):
# # # # #             random.shuffle(deck)
            
# # # # #             # Simulate remaining community cards
# # # # #             sim_community = community_cards + deck[:cards_to_reveal]
# # # # #             # Simulate opponent cards (next 2 in deck)
# # # # #             opp_cards = deck[cards_to_reveal:cards_to_reveal + 2]
            
# # # # #             # Use the provided HandEvaluator
# # # # #             my_result = self.evaluator.evaluate_hand(hole_cards, sim_community)
# # # # #             opp_result = self.evaluator.evaluate_hand(opp_cards, sim_community)
            
# # # # #             # Compare results
# # # # #             if my_result.hand_rank.value > opp_result.hand_rank.value:
# # # # #                 wins += 1
# # # # #             elif my_result.hand_rank.value < opp_result.hand_rank.value:
# # # # #                 continue
# # # # #             else:
# # # # #                 # Same rank, compare tie-breaker values
# # # # #                 if my_result.hand_value > opp_result.hand_value:
# # # # #                     wins += 1
# # # # #                 elif my_result.hand_value == opp_result.hand_value:
# # # # #                     ties += 1
                    
# # # # #         return (wins + ties * 0.5) / self.simulations

# # # # #     def _preflop_win_estimate(self, hole_cards: List[Card]) -> float:
# # # # #         """Ported logic from your original snippet for Pre-flop speed."""
# # # # #         card1, card2 = hole_cards
# # # # #         r1, r2 = card1.rank.value, card2.rank.value
# # # # #         high, low = max(r1, r2), min(r1, r2)
# # # # #         is_pair = r1 == r2
# # # # #         is_suited = card1.suit == card2.suit

# # # # #         if is_pair:
# # # # #             if high >= 13: return 0.85 # K-K or A-A
# # # # #             if high >= 10: return 0.75
# # # # #             return 0.55 + (high - 2) * 0.02
        
# # # # #         if high == 14: # Ace high
# # # # #             if low >= 12: return 0.67 if is_suited else 0.65
# # # # #             return 0.55 if is_suited else 0.52
            
# # # # #         return 0.50

# # # # #     def _make_decision(self, win_prob: float, pot_odds: float, call_amount: int, bb: int) -> Tuple[PlayerAction, int]:
# # # # #         if call_amount == 0:
# # # # #             if win_prob >= 0.65:
# # # # #                 bet_size = max(bb, self.stack // 2)
# # # # #                 return PlayerAction.BET, bet_size
# # # # #             return PlayerAction.CHECK, 0

# # # # #         if win_prob > pot_odds + 0.05:
# # # # #             if win_prob >= 0.80:
# # # # #                 return PlayerAction.RAISE, call_amount + bb
# # # # #             return PlayerAction.CALL, call_amount
        
# # # # #         return PlayerAction.FOLD, 0


# # # # import random
# # # # import time
# # # # from typing import Dict, List, Tuple
# # # # from player import Player, PlayerAction
# # # # from card import Card, Rank, Suit

# # # # class MyBot(Player):
# # # #     """Expectiminimax AI adapted for the Poker Engine."""
    
# # # #     def __init__(self, name: str, stack: int, max_depth: int = 3, determinizations: int = 10):
# # # #         super().__init__(name, stack)
# # # #         self.max_depth = max_depth
# # # #         self.determinizations = determinizations
# # # #         self.nodes_explored = 0

# # # #     def _decode_card(self, index: int) -> Card:
# # # #         """Helper to decode engine integer cards back to Card objects."""
# # # #         if index == 0:
# # # #             return None
# # # #         index = (index - 1) % 52 
# # # #         suit_val = index // 13
# # # #         rank_val = (index % 13) + 2
# # # #         return Card(Rank(rank_val), Suit(suit_val))

# # # #     def action(self, game_state: list[int], action_history: list) -> Tuple[PlayerAction, int]:
# # # #         start_time = time.time()
# # # #         self.nodes_explored = 0
# # # #         timeout_seconds = 10.0
        
# # # #         # 1. Parse engine's state list
# # # #         community_indices = game_state[2:7]
# # # #         community_cards = [self._decode_card(idx) for idx in community_indices if idx != 0]
        
# # # #         pot = game_state[7]
# # # #         current_bet = game_state[8]
# # # #         big_blind = game_state[9]
        
# # # #         call_amount = current_bet - self.bet_amount
# # # #         min_raise = current_bet + big_blind
        
# # # #         # Construct a mock state dictionary exactly as the original algorithm expects
# # # #         mock_game_state = {
# # # #             'player': {
# # # #                 'hole_cards': self.hole_cards,
# # # #                 'chips': self.stack
# # # #             },
# # # #             'pot': pot,
# # # #             'call_amount': call_amount,
# # # #             'min_raise': min_raise,
# # # #             'community_cards': community_cards
# # # #         }

# # # #         # --- CORE LOGIC START (Preserved exactly as requested) ---
# # # #         possible_worlds = self._generate_determinizations(
# # # #             self.hole_cards,
# # # #             community_cards,
# # # #             self.determinizations
# # # #         )
        
# # # #         actions = ['fold', 'call', 'raise']
# # # #         action_values = {}
        
# # # #         for action in actions:
# # # #             if action == 'fold':
# # # #                 action_values[action] = -call_amount if call_amount > 0 else 0
# # # #                 continue
            
# # # #             total_value = 0
# # # #             worlds_evaluated = 0
            
# # # #             for i, opponent_cards in enumerate(possible_worlds):
# # # #                 # Strict timeout check
# # # #                 if time.time() - start_time > timeout_seconds * 0.85:
# # # #                     break
                
# # # #                 det_state = self._create_determinized_state(mock_game_state, opponent_cards)
                
# # # #                 value = self._expectiminimax(
# # # #                     det_state,
# # # #                     depth=0,
# # # #                     is_maximizing=True,
# # # #                     alpha=float('-inf'),
# # # #                     beta=float('inf'),
# # # #                     action=action,
# # # #                     timeout=timeout_seconds,
# # # #                     start_time=start_time
# # # #                 )
                
# # # #                 total_value += value
# # # #                 worlds_evaluated += 1
        
# # # #             if worlds_evaluated > 0:
# # # #                 action_values[action] = total_value / worlds_evaluated
# # # #             else:
# # # #                 action_values[action] = 0

# # # #         best_action = max(action_values.items(), key=lambda x: x[1])[0]
# # # #         # --- CORE LOGIC END ---

# # # #         # 2. Translate string action back to engine's PlayerAction
# # # #         if best_action == 'raise':
# # # #             # Ensure we have enough chips to raise, otherwise just call
# # # #             if self.stack > call_amount:
# # # #                 return PlayerAction.RAISE, min_raise
# # # #             else:
# # # #                 return PlayerAction.CALL, call_amount
# # # #         elif best_action == 'call':
# # # #             if call_amount == 0:
# # # #                 return PlayerAction.CHECK, 0
# # # #             return PlayerAction.CALL, call_amount
# # # #         else: # fold
# # # #             if call_amount == 0:
# # # #                 return PlayerAction.CHECK, 0  # Smarter to check for free than fold
# # # #             return PlayerAction.FOLD, 0

# # # #     def _generate_determinizations(self, my_cards: List[Card],
# # # #                                    community_cards: List[Card],
# # # #                                    count: int) -> List[List[Card]]:
# # # #         # Using a tuple set for safer hash comparisons
# # # #         known_cards = set()
# # # #         for c in my_cards + community_cards:
# # # #             known_cards.add((c.rank, c.suit))
        
# # # #         unknown_cards = [
# # # #             Card(rank, suit)
# # # #             for rank in Rank
# # # #             for suit in Suit
# # # #             if (rank, suit) not in known_cards
# # # #         ]
        
# # # #         possible_hands = []
# # # #         for _ in range(count):
# # # #             random.shuffle(unknown_cards)
# # # #             possible_hands.append(unknown_cards[:2].copy())
        
# # # #         return possible_hands

# # # #     def _create_determinized_state(self, game_state: Dict,
# # # #                                    opponent_cards: List[Card]) -> Dict:
# # # #         det_state = game_state.copy()
# # # #         det_state['opponent_cards'] = opponent_cards
# # # #         return det_state

# # # #     def _expectiminimax(self, state: Dict, depth: int,
# # # #                         is_maximizing: bool, alpha: float, beta: float,
# # # #                         action: str, timeout: float, start_time: float) -> float:
# # # #         self.nodes_explored += 1
        
# # # #         if time.time() - start_time > timeout * 0.9:
# # # #             return self._evaluate_state(state, action)
        
# # # #         if depth >= self.max_depth:
# # # #             return self._evaluate_state(state, action)
        
# # # #         if is_maximizing:
# # # #             max_value = float('-inf')
            
# # # #             for next_action in ['call', 'raise']:
# # # #                 value = self._expectiminimax(
# # # #                     state, depth + 1, False,
# # # #                     alpha, beta, next_action,
# # # #                     timeout, start_time
# # # #                 )
# # # #                 max_value = max(max_value, value)
# # # #                 alpha = max(alpha, value)
                
# # # #                 if beta <= alpha:
# # # #                     break
            
# # # #             return max_value
# # # #         else:
# # # #             min_value = float('inf')
            
# # # #             for next_action in ['fold', 'call', 'raise']:
# # # #                 value = self._expectiminimax(
# # # #                     state, depth + 1, True,
# # # #                     alpha, beta, next_action,
# # # #                     timeout, start_time
# # # #                 )
# # # #                 min_value = min(min_value, value)
# # # #                 beta = min(beta, value)
                
# # # #                 if beta <= alpha:
# # # #                     break
            
# # # #             return min_value

# # # #     def _evaluate_state(self, state: Dict, action: str) -> float:
# # # #         pot = state['pot']
# # # #         call_amount = state['call_amount']
        
# # # #         if action == 'fold':
# # # #             return -call_amount
# # # #         elif action == 'call':
# # # #             return pot * 0.5 - call_amount
# # # #         elif action == 'raise':
# # # #             return pot * 0.6 - call_amount * 1.5
        
# # # #         return 0.0

# # # # import random
# # # # import time
# # # # from typing import Dict, List, Tuple
# # # # from player import Player, PlayerAction
# # # # from card import Card, Rank, Suit
# # # # from hand_evaluator import HandEvaluator

# # # # class MyBot(Player):
# # # #     """Expectiminimax AI adapted for the Poker Engine with Aggro-Counter mechanics."""
    
# # # #     def __init__(self, name: str, stack: int, max_depth: int = 3, determinizations: int = 10):
# # # #         super().__init__(name, stack)
# # # #         self.max_depth = max_depth
# # # #         self.determinizations = determinizations
# # # #         self.nodes_explored = 0
# # # #         self.evaluator = HandEvaluator()

# # # #     def _decode_card(self, index: int) -> Card:
# # # #         """Helper to decode engine integer cards back to Card objects."""
# # # #         if index == 0:
# # # #             return None
# # # #         index = (index - 1) % 52 
# # # #         suit_val = index // 13
# # # #         rank_val = (index % 13) + 2
# # # #         return Card(Rank(rank_val), Suit(suit_val))

# # # #     def action(self, game_state: list[int], action_history: list) -> Tuple[PlayerAction, int]:
# # # #         start_time = time.time()
# # # #         self.nodes_explored = 0
# # # #         timeout_seconds = 10.0
        
# # # #         # 1. Parse engine's state list
# # # #         community_indices = game_state[2:7]
# # # #         community_cards = [self._decode_card(idx) for idx in community_indices if idx != 0]
        
# # # #         pot = game_state[7]
# # # #         current_bet = game_state[8]
# # # #         big_blind = game_state[9]
        
# # # #         call_amount = current_bet - self.bet_amount
# # # #         min_raise = current_bet + big_blind
        
# # # #         # Construct state dict for the algorithm
# # # #         mock_game_state = {
# # # #             'player': {
# # # #                 'hole_cards': self.hole_cards,
# # # #                 'chips': self.stack
# # # #             },
# # # #             'pot': pot,
# # # #             'call_amount': call_amount,
# # # #             'min_raise': min_raise,
# # # #             'community_cards': community_cards
# # # #         }

# # # #         # --- CORE EXPECTIMINIMAX LOGIC ---
# # # #         possible_worlds = self._generate_determinizations(
# # # #             self.hole_cards,
# # # #             community_cards,
# # # #             self.determinizations
# # # #         )
        
# # # #         actions = ['fold', 'call', 'raise']
# # # #         action_values = {}
        
# # # #         for action in actions:
# # # #             if action == 'fold':
# # # #                 action_values[action] = -call_amount if call_amount > 0 else 0
# # # #                 continue
            
# # # #             total_value = 0
# # # #             worlds_evaluated = 0
            
# # # #             for i, opponent_cards in enumerate(possible_worlds):
# # # #                 if time.time() - start_time > timeout_seconds * 0.85:
# # # #                     break
                
# # # #                 det_state = self._create_determinized_state(mock_game_state, opponent_cards)
                
# # # #                 value = self._expectiminimax(
# # # #                     det_state,
# # # #                     depth=0,
# # # #                     is_maximizing=True,
# # # #                     alpha=float('-inf'),
# # # #                     beta=float('inf'),
# # # #                     action=action,
# # # #                     timeout=timeout_seconds,
# # # #                     start_time=start_time
# # # #                 )
                
# # # #                 total_value += value
# # # #                 worlds_evaluated += 1
        
# # # #             if worlds_evaluated > 0:
# # # #                 action_values[action] = total_value / worlds_evaluated
# # # #             else:
# # # #                 action_values[action] = 0

# # # #         best_action = max(action_values.items(), key=lambda x: x[1])[0]

# # # #         # 2. Translate to Engine Action
# # # #         if best_action == 'raise':
# # # #             if self.stack > call_amount:
# # # #                 return PlayerAction.RAISE, min_raise
# # # #             return PlayerAction.CALL, call_amount
            
# # # #         elif best_action == 'call':
# # # #             if call_amount == 0:
# # # #                 return PlayerAction.CHECK, 0
# # # #             return PlayerAction.CALL, call_amount
            
# # # #         else:
# # # #             if call_amount == 0:
# # # #                 return PlayerAction.CHECK, 0  
# # # #             return PlayerAction.FOLD, 0

# # # #     def _generate_determinizations(self, my_cards: List[Card], community_cards: List[Card], count: int) -> List[List[Card]]:
# # # #         known_cards = {(c.rank, c.suit) for c in my_cards + community_cards}
# # # #         unknown_cards = [Card(rank, suit) for rank in Rank for suit in Suit if (rank, suit) not in known_cards]
        
# # # #         possible_hands = []
# # # #         for _ in range(count):
# # # #             random.shuffle(unknown_cards)
# # # #             possible_hands.append(unknown_cards[:2].copy())
        
# # # #         return possible_hands

# # # #     def _create_determinized_state(self, game_state: Dict, opponent_cards: List[Card]) -> Dict:
# # # #         det_state = game_state.copy()
# # # #         det_state['opponent_cards'] = opponent_cards
# # # #         return det_state

# # # #     def _expectiminimax(self, state: Dict, depth: int, is_maximizing: bool, alpha: float, beta: float, action: str, timeout: float, start_time: float) -> float:
# # # #         self.nodes_explored += 1
        
# # # #         if time.time() - start_time > timeout * 0.9 or depth >= self.max_depth:
# # # #             return self._evaluate_state(state, action)
        
# # # #         if is_maximizing:
# # # #             max_value = float('-inf')
# # # #             for next_action in ['call', 'raise']:
# # # #                 value = self._expectiminimax(state, depth + 1, False, alpha, beta, next_action, timeout, start_time)
# # # #                 max_value = max(max_value, value)
# # # #                 alpha = max(alpha, value)
# # # #                 if beta <= alpha: break
# # # #             return max_value
# # # #         else:
# # # #             min_value = float('inf')
# # # #             for next_action in ['fold', 'call', 'raise']:
# # # #                 value = self._expectiminimax(state, depth + 1, True, alpha, beta, next_action, timeout, start_time)
# # # #                 min_value = min(min_value, value)
# # # #                 beta = min(beta, value)
# # # #                 if beta <= alpha: break
# # # #             return min_value

# # # #     def _evaluate_state(self, state: Dict, action: str) -> float:
# # # #         """
# # # #         Card-Aware Evaluation Function with Counter-Aggression Logic.
# # # #         """
# # # #         pot = state['pot']
# # # #         call_amount = state['call_amount']
# # # #         my_cards = state['player']['hole_cards']
# # # #         opp_cards = state['opponent_cards']
# # # #         community = state['community_cards']
        
# # # #         # 1. Compare our real hand vs the simulated opponent hand
# # # #         win_prob = self._quick_compare(my_cards, opp_cards, community)
        
# # # #         # 2. Identify if we are facing high aggression (All-Ins or massive raises)
# # # #         # If the amount we have to call is a huge chunk of the pot, someone is being highly aggressive.
# # # #         is_aggressive_bet = call_amount > (pot * 0.4)

# # # #         if action == 'fold':
# # # #             return -call_amount if call_amount > 0 else 0
            
# # # #         elif action == 'call':
# # # #             # Base Expected Value (EV) formula
# # # #             expected_return = (pot * win_prob) - (call_amount * (1 - win_prob))
            
# # # #             # Counter-Aggression Trap Mechanics
# # # #             if is_aggressive_bet:
# # # #                 if win_prob > 0.65:
# # # #                     # TRAP: If they overbet and we have a strong hand, reward calling heavily.
# # # #                     expected_return += pot * 0.6 
# # # #                 else:
# # # #                     # DODGE: If they overbet and we have a mediocre/weak hand, heavily penalize calling.
# # # #                     expected_return -= call_amount * 1.5 
                    
# # # #             return expected_return
            
# # # #         elif action == 'raise':
# # # #             # Base raise EV formula
# # # #             expected_return = (pot * 1.2 * win_prob) - (call_amount * 1.5 * (1 - win_prob))
            
# # # #             if is_aggressive_bet:
# # # #                 if win_prob >= 0.80:
# # # #                     # COUNTER-SHOVE: If we have a monster hand, raising an aggressive player is highly profitable.
# # # #                     return expected_return + pot 
# # # #                 else:
# # # #                     # NO BLUFFING: Do not try to bluff-raise someone who is already going all-in/raising aggressively.
# # # #                     return -call_amount * 3 
                    
# # # #             return expected_return
            
# # # #         return 0.0

# # # #     def _quick_compare(self, my_cards: List[Card], opp_cards: List[Card], community: List[Card]) -> float:
# # # #         """Fast hand evaluation to determine win probability against the determinized opponent."""
# # # #         if not community:
# # # #             # Pre-flop heuristic comparison
# # # #             my_weight = self._preflop_weight(my_cards)
# # # #             opp_weight = self._preflop_weight(opp_cards)
# # # #             return my_weight / (my_weight + opp_weight + 0.001)

# # # #         # Post-flop actual comparison
# # # #         my_res = self.evaluator.evaluate_hand(my_cards, community)
# # # #         opp_res = self.evaluator.evaluate_hand(opp_cards, community)

# # # #         # 1.0 = Win, 0.5 = Tie, 0.0 = Loss
# # # #         if my_res.hand_rank.value > opp_res.hand_rank.value: return 1.0
# # # #         if my_res.hand_rank.value < opp_res.hand_rank.value: return 0.0

# # # #         if my_res.hand_value > opp_res.hand_value: return 1.0
# # # #         if my_res.hand_value < opp_res.hand_value: return 0.0
        
# # # #         return 0.5

# # # #     def _preflop_weight(self, cards: List[Card]) -> float:
# # # #         """Assigns a raw weight to pre-flop starting hands."""
# # # #         r1, r2 = cards[0].rank.value, cards[1].rank.value
# # # #         high, low = max(r1, r2), min(r1, r2)
# # # #         weight = float(high * 2 + low)
        
# # # #         if r1 == r2: 
# # # #             weight *= 1.5 # Pair bonus
# # # #         if cards[0].suit == cards[1].suit: 
# # # #             weight *= 1.1 # Suited bonus
            
# # # #         return weight

# # # import random
# # # import time
# # # from typing import Dict, List, Tuple
# # # from player import Player, PlayerAction
# # # from card import Card, Rank, Suit
# # # from hand_evaluator import HandEvaluator

# # # class MyBot(Player):
# # #     """Smart Defensive AI: Sizes bets by hand strength and evades aggro traps."""
    
# # #     def __init__(self, name: str, stack: int, simulations: int = 500):
# # #         super().__init__(name, stack)
# # #         self.simulations = simulations
# # #         self.evaluator = HandEvaluator()

# # #     def _decode_card(self, index: int) -> Card:
# # #         """Helper to decode engine integer cards back to Card objects."""
# # #         if index == 0: return None
# # #         index = (index - 1) % 52 
# # #         suit_val = index // 13
# # #         rank_val = (index % 13) + 2
# # #         return Card(Rank(rank_val), Suit(suit_val))

# # #     def action(self, game_state: list[int], action_history: list) -> Tuple[PlayerAction, int]:
# # #         # Parse state
# # #         community_indices = game_state[2:7]
# # #         community_cards = [self._decode_card(idx) for idx in community_indices if idx != 0]
        
# # #         pot = game_state[7]
# # #         current_bet = game_state[8]
# # #         big_blind = game_state[9]
        
# # #         call_amount = current_bet - self.bet_amount

# # #         # 1. Hand Evaluation (Win Probability)
# # #         win_prob = self._calculate_win_prob(self.hole_cards, community_cards)

# # #         # 2. Defensive Trap-Avoidance Mechanics
# # #         pot_odds = call_amount / (pot + call_amount) if call_amount > 0 else 0
        
# # #         # Detect aggressive/random players making massive bets (> 50% of the pot)
# # #         is_huge_bet = call_amount > (pot * 0.5)

# # #         # 3. Action Logic: NO ONE HAS BET YET
# # #         if call_amount == 0:
# # #             if win_prob >= 0.85:
# # #                 # Monster hand: Bet large (Pot size bet)
# # #                 bet_amt = min(self.stack, max(big_blind, pot))
# # #                 return PlayerAction.BET, bet_amt
                
# # #             elif win_prob >= 0.65:
# # #                 # Good hand: Bet medium (Half pot)
# # #                 bet_amt = min(self.stack, max(big_blind, pot // 2))
# # #                 return PlayerAction.BET, bet_amt
                
# # #             else:
# # #                 # Weak/Marginal hand: Check to see the next cards for free
# # #                 return PlayerAction.CHECK, 0

# # #         # 4. Action Logic: FACING A BET OR RAISE
# # #         else:
# # #             # Pre-flop strictness: Fold trash immediately to avoid bleeding chips to RaisePlayer
# # #             if not community_cards and win_prob < 0.55:
# # #                 return PlayerAction.FOLD, 0

# # #             if win_prob >= 0.85:
# # #                 # TRAP SPRUNG: We have a monster hand, re-raise the aggressive player.
# # #                 raise_amt = min(self.stack, current_bet + max(pot, big_blind * 3))
# # #                 return PlayerAction.RAISE, raise_amt
                
# # #             elif win_prob >= 0.65:
# # #                 # Good hand, but proceed with caution
# # #                 if is_huge_bet and win_prob < 0.75:
# # #                     # DODGE: A random/raise player went crazy, and our hand isn't quite good enough.
# # #                     return PlayerAction.FOLD, 0
# # #                 return PlayerAction.CALL, call_amount
                
# # #             elif win_prob >= pot_odds + 0.15: 
# # #                 # Mathematical call (requires a 15% safety buffer over normal pot odds)
# # #                 if is_huge_bet:
# # #                     return PlayerAction.FOLD, 0
# # #                 return PlayerAction.CALL, call_amount
                
# # #             else:
# # #                 # Bad hand -> Easy fold
# # #                 return PlayerAction.FOLD, 0

# # #     def _calculate_win_prob(self, my_cards: List[Card], community_cards: List[Card]) -> float:
# # #         """Runs simulations post-flop, or uses a strict heuristic pre-flop."""
# # #         if not community_cards:
# # #             return self._preflop_win_estimate(my_cards)
            
# # #         wins, ties = 0, 0
# # #         known_cards = {(c.rank, c.suit) for c in my_cards + community_cards}
# # #         deck = [Card(r, s) for r in Rank for s in Suit if (r, s) not in known_cards]
        
# # #         cards_needed = 5 - len(community_cards)
        
# # #         for _ in range(self.simulations):
# # #             random.shuffle(deck)
# # #             sim_community = community_cards + deck[:cards_needed]
# # #             opp_cards = deck[cards_needed:cards_needed + 2]
            
# # #             my_res = self.evaluator.evaluate_hand(my_cards, sim_community)
# # #             opp_res = self.evaluator.evaluate_hand(opp_cards, sim_community)
            
# # #             if my_res.hand_rank.value > opp_res.hand_rank.value: wins += 1
# # #             elif my_res.hand_rank.value < opp_res.hand_rank.value: continue
# # #             elif my_res.hand_value > opp_res.hand_value: wins += 1
# # #             elif my_res.hand_value == opp_res.hand_value: ties += 1
            
# # #         return (wins + ties * 0.5) / self.simulations

# # #     def _preflop_win_estimate(self, hole_cards: List[Card]) -> float:
# # #         """Strict pre-flop evaluator that easily identifies bad hands."""
# # #         r1, r2 = hole_cards[0].rank.value, hole_cards[1].rank.value
# # #         high, low = max(r1, r2), min(r1, r2)
# # #         is_pair = r1 == r2
# # #         is_suited = hole_cards[0].suit == hole_cards[1].suit

# # #         if is_pair:
# # #             if high >= 13: return 0.85 # AA, KK
# # #             if high >= 10: return 0.75 # TT, JJ, QQ
# # #             if high >= 7: return 0.65  # Medium pairs
# # #             return 0.55                # Low pairs
        
# # #         if high >= 13 and low >= 10: 
# # #             return 0.65 if is_suited else 0.60 # High broadways (AK, KQ)
            
# # #         if high == 14: 
# # #             return 0.60 if is_suited else 0.55 # Ace with weak kicker
            
# # #         if is_suited and high >= 10:
# # #             return 0.55 # Suited face cards
            
# # #         # Trash hands (e.g., 2-7 offsuit) drop down to 0.40, causing instant folds against raises
# # #         return 0.40

# # import random
# # import time
# # from typing import Dict, List, Tuple
# # from player import Player, PlayerAction
# # from card import Card, Rank, Suit
# # from hand_evaluator import HandEvaluator

# # class MyBot(Player):
# #     """Smart Defensive AI: Uses tiered hand rankings to size bets and confidently avoid traps."""
    
# #     def __init__(self, name: str, stack: int, simulations: int = 500):
# #         super().__init__(name, stack)
# #         self.simulations = simulations
# #         self.evaluator = HandEvaluator()

# #     def _decode_card(self, index: int) -> Card:
# #         """Helper to decode engine integer cards back to Card objects."""
# #         if index == 0: return None
# #         index = (index - 1) % 52 
# #         suit_val = index // 13
# #         rank_val = (index % 13) + 2
# #         return Card(Rank(rank_val), Suit(suit_val))

# #     def action(self, game_state: list[int], action_history: list) -> Tuple[PlayerAction, int]:
# #         # Parse state
# #         community_indices = game_state[2:7]
# #         community_cards = [self._decode_card(idx) for idx in community_indices if idx != 0]
        
# #         pot = game_state[7]
# #         current_bet = game_state[8]
# #         big_blind = game_state[9]
        
# #         call_amount = current_bet - self.bet_amount

# #         # 1. Hand Evaluation (Win Probability)
# #         win_prob = self._calculate_win_prob(self.hole_cards, community_cards)

# #         # 2. Defensive Trap-Avoidance Mechanics
# #         # Real pot odds calculation
# #         pot_odds = call_amount / (pot + call_amount) if call_amount > 0 else 0
        
# #         # A huge bet is defined as 1.5x the pot OR 5x the big blind
# #         is_huge_bet = call_amount > max(pot * 1.5, big_blind * 5)

# #         # 3. Action Logic: NO ONE HAS BET YET
# #         if call_amount == 0:
# #             if win_prob >= 0.70:
# #                 # Good hand: Bet half pot
# #                 bet_amt = min(self.stack, max(big_blind, pot // 2))
# #                 return PlayerAction.BET, bet_amt
# #             else:
# #                 # Weak/Marginal hand: Check to see the next cards for free
# #                 return PlayerAction.CHECK, 0

# #         # 4. Action Logic: FACING A BET OR RAISE
# #         else:
# #             if win_prob >= 0.75:
# #                 # TRAP SPRUNG: We have a very strong hand, re-raise the aggressive player.
# #                 raise_amt = min(self.stack, current_bet + max(pot, big_blind * 2))
# #                 return PlayerAction.RAISE, raise_amt
                
# #             elif win_prob >= pot_odds: 
# #                 # Mathematical call (True pot odds vs Equity)
# #                 if is_huge_bet and win_prob < 0.65:
# #                     # DODGE: If the bet is massive AND our hand isn't in a premium tier
# #                     return PlayerAction.FOLD, 0
# #                 return PlayerAction.CALL, call_amount
                
# #             else:
# #                 # Hand doesn't justify the pot odds -> Easy fold
# #                 return PlayerAction.FOLD, 0

# #     def _calculate_win_prob(self, my_cards: List[Card], community_cards: List[Card]) -> float:
# #         """Runs Monte Carlo simulations post-flop, or uses a strict tier heuristic pre-flop."""
# #         if not community_cards:
# #             return self._preflop_win_estimate(my_cards)
            
# #         wins, ties = 0, 0
# #         known_cards = {(c.rank, c.suit) for c in my_cards + community_cards}
# #         deck = [Card(r, s) for r in Rank for s in Suit if (r, s) not in known_cards]
        
# #         cards_needed = 5 - len(community_cards)
        
# #         for _ in range(self.simulations):
# #             random.shuffle(deck)
# #             sim_community = community_cards + deck[:cards_needed]
# #             opp_cards = deck[cards_needed:cards_needed + 2]
            
# #             my_res = self.evaluator.evaluate_hand(my_cards, sim_community)
# #             opp_res = self.evaluator.evaluate_hand(opp_cards, sim_community)
            
# #             if my_res.hand_rank.value > opp_res.hand_rank.value: wins += 1
# #             elif my_res.hand_rank.value < opp_res.hand_rank.value: continue
# #             elif my_res.hand_value > opp_res.hand_value: wins += 1
# #             elif my_res.hand_value == opp_res.hand_value: ties += 1
            
# #         return (wins + ties * 0.5) / self.simulations

# #     def _preflop_win_estimate(self, hole_cards: List[Card]) -> float:
# #         """Categorizes starting hands into real-world equity tiers."""
# #         r1, r2 = hole_cards[0].rank.value, hole_cards[1].rank.value
# #         high, low = max(r1, r2), min(r1, r2)
# #         is_pair = r1 == r2
# #         is_suited = hole_cards[0].suit == hole_cards[1].suit

# #         # Pairs
# #         if is_pair:
# #             if high >= 13: return 0.85 # AA, KK
# #             if high >= 10: return 0.75 # QQ, JJ, TT
# #             if high >= 7: return 0.65  # 99, 88, 77
# #             return 0.55                # 66-22

# #         # Ace High Hands
# #         if high == 14:
# #             if low >= 12: return 0.80 if is_suited else 0.75 # AK, AQ
# #             if low >= 10: return 0.70 if is_suited else 0.65 # AJ, AT
# #             if low >= 8: return 0.60 if is_suited else 0.55  # A9, A8
# #             return 0.55 if is_suited else 0.45               # A7-A2

# #         # High Broadways (KQ, KJ, QJ)
# #         if high >= 10 and low >= 10:
# #             return 0.65 if is_suited else 0.55

# #         # Suited Connectors (e.g., 89s, 67s)
# #         if is_suited:
# #             if high - low <= 2: return 0.55 
# #             return 0.50

# #         # Offsuit High Connectors (e.g., T9o, JTo)
# #         if high - low <= 2 and high >= 9:
# #             return 0.50
            
# #         # Absolute Trash (e.g., 7-2 offsuit, J-4 offsuit)
# #         return 0.35

import random
import time
from typing import Dict, List, Tuple
from player import Player, PlayerAction
from card import Card, Rank, Suit
from hand_evaluator import HandEvaluator, HandRank

class MyBot(Player):
    """Smart Aggro-Defensive AI: Raises made hands, strictly defends against All-Ins."""
    
    def __init__(self, name: str, stack: int, simulations: int = 500):
        super().__init__(name, stack)
        self.simulations = simulations
        self.evaluator = HandEvaluator()

    def _decode_card(self, index: int) -> Card:
        if index == 0: return None
        index = (index - 1) % 52 
        suit_val = index // 13
        rank_val = (index % 13) + 2
        return Card(Rank(rank_val), Suit(suit_val))

    def action(self, game_state: list[int], action_history: list) -> Tuple[PlayerAction, int]:
        # Parse state
        community_indices = game_state[2:7]
        community_cards = [self._decode_card(idx) for idx in community_indices if idx != 0]
        
        pot = game_state[7]
        current_bet = game_state[8]
        big_blind = game_state[9]
        
        call_amount = current_bet - self.bet_amount

        # 1. Win Probability (Simulations & Tiers)
        win_prob = self._calculate_win_prob(self.hole_cards, community_cards)

        # 2. Identify Current Made Hand (Post-Flop)
        current_hand_val = 0
        if community_cards:
            current_hand_val = self.evaluator.evaluate_hand(self.hole_cards, community_cards).hand_rank.value

        # 3. Threat Assessment: Detect All-Ins and Massive Overbets
        # If the bet is more than 1.5x the pot OR threatens more than 60% of our stack
        is_shove = call_amount > (pot * 1.5) or call_amount >= (self.stack * 0.6)
        pot_odds = call_amount / (pot + call_amount) if call_amount > 0 else 0

        # --- ACTION LOGIC: NO BET TO CALL (We act first or it checked to us) ---
        if call_amount == 0:
            if current_hand_val >= HandRank.THREE_OF_A_KIND.value:
                # MONSTER HAND (3-of-a-kind, Straight, Flush, etc.): Bet Pot Size
                bet_amt = min(self.stack, max(big_blind, pot))
                return PlayerAction.BET, bet_amt
                
            elif win_prob >= 0.70:
                # Good Draw / High Pair: Bet Half Pot
                bet_amt = min(self.stack, max(big_blind, pot // 2))
                return PlayerAction.BET, bet_amt
                
            else:
                return PlayerAction.CHECK, 0

        # --- ACTION LOGIC: FACING A BET / RAISE / ALL-IN ---
        else:
            # DEFENSE 1: Pre-Flop All-In Lockdown
            if not community_cards and is_shove:
                # Only call a pre-flop shove with absolute premium tiers (AA, KK, QQ, AK)
                if win_prob >= 0.75:
                    return PlayerAction.CALL, call_amount
                return PlayerAction.FOLD, 0

            # OFFENSE: Raise on strong made hands or massive equity
            if current_hand_val >= HandRank.THREE_OF_A_KIND.value or win_prob >= 0.80:
                raise_amt = min(self.stack, current_bet + max(pot, big_blind * 3))
                # Ensure we have enough to legally raise, otherwise just shove/call
                if self.stack > call_amount + big_blind:
                    return PlayerAction.RAISE, raise_amt
                return PlayerAction.CALL, call_amount

            # DEFENSE 2: Mathematical Call with Safety Buffers
            if win_prob >= pot_odds + 0.05: 
                if is_shove and win_prob < 0.70:
                    # DODGE: They shoved post-flop, and we only have a marginal hand/draw.
                    return PlayerAction.FOLD, 0
                return PlayerAction.CALL, call_amount
                
            else:
                # Bad odds or weak hand -> Fold
                return PlayerAction.FOLD, 0

    def _calculate_win_prob(self, my_cards: List[Card], community_cards: List[Card]) -> float:
        """Runs Monte Carlo simulations post-flop, or uses a strict tier heuristic pre-flop."""
        if not community_cards:
            return self._preflop_win_estimate(my_cards)
            
        wins, ties = 0, 0
        known_cards = {(c.rank, c.suit) for c in my_cards + community_cards}
        deck = [Card(r, s) for r in Rank for s in Suit if (r, s) not in known_cards]
        
        cards_needed = 5 - len(community_cards)
        
        for _ in range(self.simulations):
            random.shuffle(deck)
            sim_community = community_cards + deck[:cards_needed]
            opp_cards = deck[cards_needed:cards_needed + 2]
            
            my_res = self.evaluator.evaluate_hand(my_cards, sim_community)
            opp_res = self.evaluator.evaluate_hand(opp_cards, sim_community)
            
            if my_res.hand_rank.value > opp_res.hand_rank.value: wins += 1
            elif my_res.hand_rank.value < opp_res.hand_rank.value: continue
            elif my_res.hand_value > opp_res.hand_value: wins += 1
            elif my_res.hand_value == opp_res.hand_value: ties += 1
            
        return (wins + ties * 0.5) / self.simulations

    def _preflop_win_estimate(self, hole_cards: List[Card]) -> float:
        """Categorizes starting hands into real-world equity tiers."""
        r1, r2 = hole_cards[0].rank.value, hole_cards[1].rank.value
        high, low = max(r1, r2), min(r1, r2)
        is_pair = r1 == r2
        is_suited = hole_cards[0].suit == hole_cards[1].suit

        if is_pair:
            if high >= 13: return 0.85 # AA, KK
            if high >= 10: return 0.75 # QQ, JJ, TT
            if high >= 7: return 0.65  # 99, 88, 77
            return 0.55                # 66-22

        if high == 14:
            if low >= 12: return 0.80 if is_suited else 0.75 # AK, AQ
            if low >= 10: return 0.70 if is_suited else 0.65 # AJ, AT
            if low >= 8: return 0.60 if is_suited else 0.55  # A9, A8
            return 0.55 if is_suited else 0.45               # A7-A2

        if high >= 10 and low >= 10:
            return 0.65 if is_suited else 0.55 # KQ, KJ, QJ

        if is_suited:
            if high - low <= 2: return 0.55 # Connectors
            return 0.50

        if high - low <= 2 and high >= 9:
            return 0.50 # Offsuit high connectors
            
        return 0.35 # Trash

