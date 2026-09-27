from enum import Enum
from typing import List
from card import Card, Deck
from player import Player, PlayerAction, PlayerStatus
from hand_evaluator import HandEvaluator
from math import ceil


class GamePhase(Enum):
    SETUP = "setup"
    PRE_FLOP = "pre-flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"


class PokerGame:
    def __init__(self, players: List[Player], big_blind: int, hand_number: int = 0):
        self.players = players
        self.big_blind = big_blind
        self.deck = None
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0  # how much has been raised (includes big blind)
        self.phase = GamePhase.SETUP
        self.button_position = 0
        self.active_player_index = 0
        self.has_played = [False] * len(self.players)
        self.action_history = []
        self.hand_number = hand_number
        self.hand_winners = []

    def start_new_hand(self):
        print("\n====== NEW HAND ======")
        # Reset game state
        self.hand_number += 1
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.phase = GamePhase.SETUP

        # Reset player_hand statuses
        num_active = 0
        for i, player in enumerate(self.players):
            player.reset_for_new_hand()
            self.has_played[i] = False if player.status == PlayerStatus.ACTIVE else True
            num_active += 1 - int(self.has_played[i])

        if num_active <= 1:
            return False

        # Move button to next player_hand
        self.button_position = (self.button_position + 1) % len(self.players)

        # Deal cards
        self._deal_hole_cards()

        # Post blinds
        self._post_blinds()

        # Begin pre-flop betting
        self.phase = GamePhase.PRE_FLOP
        self.active_player_index = (self.button_position + 2) % len(self.players)
        self._adjust_active_player_index()

        # Show game state
        self.display_game_state()
        return True

    def _deal_hole_cards(self):
        for player in self.players:
            if player.status != PlayerStatus.OUT:
                player.hole_cards = self.deck.deal(2)

    def _post_blinds(self):
        # Big blind only, no small blind
        bb_position = (self.button_position + 1) % len(self.players)
        bb_player = self.players[bb_position]

        while bb_player.status != PlayerStatus.ACTIVE:
            bb_position = (bb_position + 1) % len(self.players) # go to the next player position
            bb_player = self.players[bb_position]

        if bb_player.stack > 0:
            action, amount = bb_player.take_action(PlayerAction.BET, self.big_blind)
            self.pot += amount
            self.current_bet = self.big_blind
            print(f"{bb_player.name} posts big blind: {amount}")

    def _adjust_active_player_index(self):
        # Find next active player_hand
        original_index = self.active_player_index
        while not self.players[self.active_player_index].can_make_action():
            self.active_player_index = (self.active_player_index + 1) % len(self.players)
            if self.active_player_index == original_index:
                # We've gone all the way around, no active players
                return False
        return True

    # def player_action(self, action: PlayerAction, amount: int = 0) -> bool:
    #     player = self.players[self.active_player_index]
    #     amount = min(amount, player.stack)

    #     if amount < 0:
    #         print("Amount cannot be negative.")
    #         return False

    #     amount = ceil(amount)

    #     # Validate action
    #     if action == PlayerAction.CHECK and self.current_bet > player.bet_amount:
    #         print(f"Cannot check when there's a bet. Current bet: {self.current_bet}")
    #         return False

    #     if action == PlayerAction.CALL:
    #         amount = self.current_bet - player.bet_amount

    #     if action in [PlayerAction.BET, PlayerAction.RAISE]:
    #         # For a bet, the minimum is the big blind
    #         min_amount = self.big_blind

    #         # For a raise, the minimum is the current bet plus the minimum raise amount
    #         if self.current_bet > 0:
    #             min_amount = self.current_bet
    #         else:
    #             action = PlayerAction.BET

    #         if amount <= min_amount:
    #             print(f"Minimum {action.value} is {min_amount}")
    #             return False

    #         # Update current bet
    #         self.current_bet = amount

    #     if action == PlayerAction.ALL_IN:
    #         if amount <= 0:
    #             return False
    #         if amount > self.current_bet:
    #             self.current_bet = player.bet_amount

    #     actual_action, actual_amount = player.take_action(action, amount)
    #     self.pot += actual_amount
    #     self.action_history.append((self.phase.value, player.name, actual_action.value, actual_amount))

    #     # Execute action
    #     print(f"{player.name} {actual_action.value}s", end="")
    #     if action in [PlayerAction.BET, PlayerAction.RAISE, PlayerAction.CALL]:
    #         print(f"to {actual_amount}")
    #     else:
    #         print()

    #     print(f"{player.name} puts {actual_amount} into the pot.")

    #     # Move to next player_hand
    #     self.has_played[self.active_player_index] = True
    #     self.active_player_index = (self.active_player_index + 1) % len(self.players)

    #     # Check if betting round is complete
    #     if self.is_betting_round_complete():
    #         self.advance_game_phase()
    #     else:
    #         self._adjust_active_player_index()

    #     # Show updated game state
    #     self.display_game_state()
    #     return True

    def player_action(self, action: PlayerAction, amount: int = 0) -> bool:
        player = self.players[self.active_player_index]

        if amount < 0:
            print("Amount cannot be negative.")
            return False

        amount = ceil(amount)

        # --- Validations & Targeting ---
        if action == PlayerAction.CHECK:
            if self.current_bet > player.bet_amount:
                print(f"Cannot check. Current bet to call is: {self.current_bet}")
                return False
                
        elif action == PlayerAction.CALL:
            if self.current_bet == player.bet_amount:
                action = PlayerAction.CHECK # Auto-correct to check if no bet is owed
            else:
                amount = self.current_bet  # Target total bet for a call is the table's current bet

        elif action in [PlayerAction.BET, PlayerAction.RAISE]:
            min_target = self.big_blind if self.current_bet == 0 else self.current_bet + self.big_blind
            if amount < min_target:
                print(f"Minimum bet/raise target is {min_target}")
                return False

        # --- Execute the action ---
        actual_action, actual_amount = player.take_action(action, amount)
        self.pot += actual_amount
        self.action_history.append((self.phase.value, player.name, actual_action.value, actual_amount))

        # --- The ALL-IN / Current Bet Fix ---
        # The true current bet of the table is simply the MAXIMUM bet_amount any player currently has.
        if player.bet_amount > self.current_bet:
            self.current_bet = player.bet_amount

        # Log action cleanly
        print(f"{player.name} {actual_action.value}s", end="")
        if actual_action in [PlayerAction.BET, PlayerAction.RAISE, PlayerAction.CALL]:
            print(f" to {player.bet_amount} (added {actual_amount} to pot)")
        elif actual_action == PlayerAction.ALL_IN:
            print(f" (added {actual_amount} to pot, total commitment: {player.bet_amount})")
        else:
            print()

        # Move to next active player
        self.has_played[self.active_player_index] = True
        self.active_player_index = (self.active_player_index + 1) % len(self.players)

        # Check round end
        if self.is_betting_round_complete():
            self.advance_game_phase()
        else:
            self._adjust_active_player_index()

        self.display_game_state()
        return True

    def is_betting_round_complete(self) -> bool:
        for player in self.players:
            if player.status in [PlayerStatus.FOLDED, PlayerStatus.ALL_IN, PlayerStatus.OUT]:
                continue
            if player.bet_amount != self.current_bet:
                return False
        return all(self.has_played)

    def advance_game_phase(self):
        # Reset bet amounts for the next betting round
        active_bets = [p.bet_amount for p in self.players if p.status not in [PlayerStatus.OUT, PlayerStatus.FOLDED]]
        if active_bets:
            highest_bet = max(active_bets)
            players_with_highest = [p for p in self.players if p.bet_amount == highest_bet]
            
            # If only ONE person has the highest bet, the excess is uncalled
            if len(players_with_highest) == 1:
                other_bets = [p.bet_amount for p in self.players if p.status not in [PlayerStatus.OUT, PlayerStatus.FOLDED] and p.bet_amount < highest_bet]
                second_highest = max(other_bets) if other_bets else 0
                
                refund = highest_bet - second_highest
                if refund > 0:
                    p = players_with_highest[0]
                    p.stack += refund
                    p.bet_amount -= refund
                    self.pot -= refund
                    self.current_bet = second_highest
                    print(f"\n[!] {p.name}'s uncalled bet of {refund} was returned.")

        if self.num_active_players() + self.num_all_in_players() == 1:  # all players folded except one
            self.direct_showdown()  # go directly to showdown and declare winner
            return

        no_one_active = all([p.status in [PlayerStatus.ALL_IN, PlayerStatus.FOLDED, PlayerStatus.OUT] for p in self.players])
        if no_one_active:  # all players other than folded players are all-in
            self.all_in_showdown()  # one or more than one person is all-in and others are folded/out
            return

        for player in self.players:
            player.bet_amount = 0
        self.current_bet = 0

        # Move to the next phase
        if self.phase == GamePhase.PRE_FLOP:
            self.phase = GamePhase.FLOP
            self.community_cards.extend(self.deck.deal(3))
        elif self.phase == GamePhase.FLOP:
            self.phase = GamePhase.TURN
            self.community_cards.extend(self.deck.deal(1))
        elif self.phase == GamePhase.TURN:
            self.phase = GamePhase.RIVER
            self.community_cards.extend(self.deck.deal(1))
        elif self.phase == GamePhase.RIVER:
            self.phase = GamePhase.SHOWDOWN
            self._showdown()
            return

        # Start betting with player_hand after button
        self.active_player_index = (self.button_position + 1) % len(self.players)
        self._adjust_active_player_index()
        self._reset_has_played()

    def direct_showdown(self):  # direct to showdown
        self.phase = GamePhase.SHOWDOWN
        self._showdown()
        return

    def all_in_showdown(
            self):  # if more than one players are all-in first deal sufficient community cards then go to showdown
        num_remaining = 5 - len(self.community_cards)
        if num_remaining > 0:
            self.community_cards.extend(self.deck.deal(num_remaining))

        self.phase = GamePhase.SHOWDOWN
        self._showdown()
        return

    # def _showdown(self):
    #     # Evaluate hands for all players who haven't folded
    #     active_players = [p for p in self.players if p.status not in [PlayerStatus.FOLDED, PlayerStatus.OUT]]

    #     if len(active_players) == 1:
    #         # Only one player_hand left, they win automatically
    #         winner = active_players[0]
    #         winner.stack += self.pot
    #         print(f"\n{winner.name} wins {self.pot} chips")
    #         return

    #     # Evaluate hands
    #     results = []
    #     print("\n=== SHOWDOWN ===")
    #     for player in active_players:
    #         result = HandEvaluator.evaluate_hand(player.hole_cards, self.community_cards)
    #         results.append((player, result))

    #         print(f"{player.name}: {[str(c) for c in player.hole_cards]} - {result.hand_rank.name}")

    #     # Find the winner(s)
    #     results.sort(key=lambda x: (x[1].hand_rank.value, x[1].hand_value), reverse=True)
    #     best_result = results[0][1]

    #     winners = []
    #     for player, result in results:
    #         if (result.hand_rank == best_result.hand_rank and
    #                 result.hand_value == best_result.hand_value):
    #             winners.append(player)

    #     # Distribute the pot
    #     split_amount = self.pot // len(winners)
    #     remainder = self.pot % len(winners)

    #     for player in winners:
    #         winnings = split_amount
    #         if remainder > 0:
    #             winnings += 1
    #             remainder -= 1

    #         player.stack += winnings
    #         print(f"{player.name} wins {winnings} chips with {best_result.hand_rank.name}")
    #         self.hand_winners.append((self.hand_number, player.name, winnings))
    # def _showdown(self):
    #     """
    #     Evaluates hands for all players who haven't folded and distributes the pot.
    #     """
    #     # 1. Identify players still in the hand (not folded, not out of the game)
    #     active_players = [p for p in self.players if p.status not in [PlayerStatus.FOLDED, PlayerStatus.OUT]]

    #     # Safety Check: If for some reason no one is left, exit to avoid IndexError
    #     if not active_players:
    #         print("\nNo active players left to contest the pot.")
    #         return

    #     # 2. Handle the "Last Man Standing" case (Everyone else folded)
    #     if len(active_players) == 1:
    #         winner = active_players[0]
    #         winner.stack += self.pot
    #         print(f"\n{winner.name} wins {self.pot} chips")
    #         # Record the win in hand_winners history
    #         self.hand_winners.append((self.hand_number, winner.name, self.pot))
    #         return

    #     # 3. Multi-player Showdown (Requires Hand Evaluation)
    #     results = []
    #     print("\n=== SHOWDOWN ===")
        
    #     for player in active_players:
    #         # Evaluate the best 5-card hand from hole cards + community cards
    #         result = HandEvaluator.evaluate_hand(player.hole_cards, self.community_cards)
    #         results.append((player, result))

    #         # Log what each player is holding
    #         card_str = [str(c) for c in player.hole_cards]
    #         print(f"{player.name}: {card_str} - {result.hand_rank.name}")

    #     # 4. Sort results to find the best hand
    #     # Sort by Hand Rank value (e.g., Flush > Pair), then by tie-breaker hand_value tuple
    #     results.sort(key=lambda x: (x[1].hand_rank.value, x[1].hand_value), reverse=True)
        
    #     # The best result is now at index 0
    #     best_result = results[0][1]

    #     # 5. Identify all winners (to handle split pots)
    #     winners = []
    #     for player, result in results:
    #         if (result.hand_rank == best_result.hand_rank and
    #                 result.hand_value == best_result.hand_value):
    #             winners.append(player)

    #     # 6. Distribute the pot (including remainder handling)
    #     split_amount = self.pot // len(winners)
    #     remainder = self.pot % len(winners)

    #     for player in winners:
    #         winnings = split_amount
    #         # Distribute odd chips 1-by-1 to winners
    #         if remainder > 0:
    #             winnings += 1
    #             remainder -= 1

    #         player.stack += winnings
    #         print(f"{player.name} wins {winnings} chips with {best_result.hand_rank.name}")
            
    #         # Record each winner in history
    #         self.hand_winners.append((self.hand_number, player.name, winnings))

    def _showdown(self):
        active_players = [p for p in self.players if p.status not in [PlayerStatus.FOLDED, PlayerStatus.OUT]]

        # Safety Check: Prevent crash if list is empty
        if not active_players:
            print("\nNo active players left to contest the pot.")
            return

        # Last Man Standing
        if len(active_players) == 1:
            winner = active_players[0]
            winner.stack += self.pot
            print(f"\n{winner.name} wins {self.pot} chips")
            self.hand_winners.append((self.hand_number, winner.name, self.pot))
            return

        results = []
        print("\n=== SHOWDOWN ===")
        for player in active_players:
            result = HandEvaluator.evaluate_hand(player.hole_cards, self.community_cards)
            results.append((player, result))
            print(f"{player.name}: {[str(c) for c in player.hole_cards]} - {result.hand_rank.name}")

        results.sort(key=lambda x: (x[1].hand_rank.value, x[1].hand_value), reverse=True)
        best_result = results[0][1]

        winners = []
        for player, result in results:
            if (result.hand_rank == best_result.hand_rank and result.hand_value == best_result.hand_value):
                winners.append(player)

        split_amount = self.pot // len(winners)
        remainder = self.pot % len(winners)

        for player in winners:
            winnings = split_amount
            if remainder > 0:
                winnings += 1
                remainder -= 1

            player.stack += winnings
            print(f"{player.name} wins {winnings} chips with {best_result.hand_rank.name}")
            self.hand_winners.append((self.hand_number, player.name, winnings))

    def display_game_state(self):
        print(f"\nPhase: {self.phase.value}")
        print(f"Pot: {self.pot}")

        if self.community_cards:
            print(f"Community cards: {[str(c) for c in self.community_cards]}")

        print("\nPlayers:")
        for i, player in enumerate(self.players):
            position = ""
            if i == self.button_position:
                position = "(BTN)"

            active = "→ " if i == self.active_player_index and player.can_make_action() else "  "

            print(f"{active}{player.name} {position}: ${player.stack} {player.status.value}")

    def _reset_has_played(self):
        self.has_played = [False if player.status == PlayerStatus.ACTIVE else True for player in self.players]

    def num_active_players(self) -> int:
        return len([p for p in self.players if p.status == PlayerStatus.ACTIVE])

    def num_all_in_players(self) -> int:  # players who are all in
        return len([p for p in self.players if p.status == PlayerStatus.ALL_IN])

    def get_player_input(self) -> bool:
        player = self.players[self.active_player_index]
        game_state = self.get_game_state()
        action, amount = player.action(game_state, self.action_history)
        return self.player_action(action, amount)

    def get_game_state(self) -> list[int]:
        """
        Returns the current game state in the following structure:
        <1. Hole Cards' Index>
        card1
        card2
        <2. Community Cards' Index. 0 means not yet dealt>
        card1
        card2
        card3
        card4
        card5
        <3. Pot>
        pot
        <4. Current Raise Amount>
        current_raise
        <5. Blind>
        blind
        <6. Active Player Index>
        active_player_index
        <7. Number of players>
        num_players
        <8. Each player's stack>
        stack1
        stack2
        stack3
        stack4
        <9. Hand number>
        hand_number
        """
        player = self.players[self.active_player_index]
        player_cards = [card.get_index() for card in player.hole_cards] + (2 - len(player.hole_cards)) * [0]
        community_cards = [card.get_index() for card in self.community_cards] + (5 - len(self.community_cards)) * [0]
        return [
            *player_cards,
            *community_cards,
            self.pot,
            self.current_bet,
            self.big_blind,
            self.active_player_index,
            len(self.players),
            *(p.stack for p in self.players),
            self.hand_number,
        ]


if __name__ == "__main__":
    example_players = [
        Player("Bot", 1000),
        Player("Alice", 1000),
        Player("Bob", 1000),
        Player("Charlie", 1000),
        Player("Dave", 1000),
    ]
    game = PokerGame(example_players, big_blind=20)
    game.start_new_hand()
    game.advance_game_phase()
    print(game.get_game_state())
