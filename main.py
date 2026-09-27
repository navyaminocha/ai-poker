# # import os
# # import sys
# # import time
# # from player import PlayerStatus, PlayerAction
# # from game import PokerGame, GamePhase
# # from baseplayers import InputPlayer, RaisePlayer, FoldPlayer
# # from mybot import MyBot


# # def run_game(num_hands):

# #     players = [
# #         MyBot("Bot", 1000),
# #         InputPlayer("Alice", 1000),
# #         InputPlayer("Bob", 1000),
# #         InputPlayer("Charlie", 1000),
# #         InputPlayer("David", 1000)
# #     ]
    
# #     # Create game
# #     game = PokerGame(players, big_blind=20)

# #     # Run several hands
# #     for _ in range(num_hands):
# #         print(f"\nHand number {game.hand_number + 1}")
# #         game_status = game.start_new_hand()
# #         if not game_status:
# #             print(f"Not enough players left in the game... game over.")
# #             break
        
# #         # Main game loop
# #         num_tries = 0
# #         while game.phase != GamePhase.SHOWDOWN:
# #             if num_tries == 3:
# #                 game.player_action(PlayerAction.FOLD, 0)
# #                 num_tries = 0
# #                 continue

# #             player = game.players[game.active_player_index]

# #             if game.num_active_players() == 1 and player.bet_amount == game.current_bet:
# #                 game.advance_game_phase()
# #                 game.display_game_state()
# #                 continue

# #             print(f"\n{player.name}'s turn")
# #             print(f"Your cards: {[str(c) for c in player.hole_cards]}")

# #             try:
# #                 is_successful = game.get_player_input()
# #             except Exception as e:
# #                 print(f"Player {player.name}'s turn failed: {e}")
# #                 is_successful = False

# #             if not is_successful:
# #                 print("Invalid command received.")
# #                 num_tries += 1
# #             else:
# #                 num_tries = 0
# #             time.sleep(.5)

# #         print("\nHand complete. Starting new hand...")
# #         # time.sleep(5)

# #     print("Winners are:")
# #     for g, winner, winning in game.hand_winners:
# #         print(f"Game {g}: {winner} ({winning})")
# #     print("\nFinal stack sizes are:")
# #     for player in game.players:
# #         print(f"{player.name}: ${player.stack}")


# # if __name__ == "__main__":
# #     # start_time = time.time()
# #     # with open("logs.txt", "w", encoding="utf-8") as f:
# #     #     sys.stdout = f
# #     #     run_game(40)
# #     #
# #     # sys.stdout = sys.__stdout__
# #     # end_time = time.time()
# #     # print("Game over. Total time taken:", end_time - start_time)
# #     run_game(10)

# import os
# import sys
# import time
# from player import PlayerStatus, PlayerAction
# from game import PokerGame, GamePhase
# from baseplayers import InputPlayer, RaisePlayer, FoldPlayer
# from mybot import MyBot
# from visualizer import GameVisualizer  # <-- Import the visualizer

# def run_game(num_hands):
#     # Setup visualizer
#     visualizer = GameVisualizer()

#     # Changed InputPlayers to Bot classes so the visualizer can run automatically
#     players = [
#         MyBot("Bot 1", 1000),
#         MyBot("Bot 2", 1000),
#         RaisePlayer("Aggressive Bob", 1000),
#         FoldPlayer("Timid Charlie", 1000),
#         MyBot("Bot 3", 1000)
#     ]
    
#     game = PokerGame(players, big_blind=20)

#     for _ in range(num_hands):
#         print(f"\nHand number {game.hand_number + 1}")
#         game_status = game.start_new_hand()
#         if not game_status:
#             print(f"Not enough players left in the game... game over.")
#             break
        
#         # Draw initial pre-flop state
#         visualizer.draw_state(game)
#         time.sleep(1)
        
#         num_tries = 0
#         while game.phase != GamePhase.SHOWDOWN:
#             if num_tries == 3:
#                 game.player_action(PlayerAction.FOLD, 0)
#                 num_tries = 0
#                 continue

#             player = game.players[game.active_player_index]

#             if game.num_active_players() == 1 and player.bet_amount == game.current_bet:
#                 game.advance_game_phase()
#                 game.display_game_state()
#                 visualizer.draw_state(game) # Update UI on phase change
#                 time.sleep(0.5)
#                 continue

#             print(f"\n{player.name}'s turn")
            
#             try:
#                 is_successful = game.get_player_input()
#             except Exception as e:
#                 print(f"Player {player.name}'s turn failed: {e}")
#                 is_successful = False

#             if not is_successful:
#                 num_tries += 1
#             else:
#                 num_tries = 0
            
#             # Update visualizer after every valid turn
#             visualizer.draw_state(game)
#             time.sleep(0.8) # Adjust this to speed up or slow down the game

#         # Final draw for the Showdown
#         visualizer.draw_state(game)
#         print("\nHand complete. Starting new hand in 4 seconds...")
#         time.sleep(4) # Pause so you can see the final hands and pot distribution

#     print("\nWinners are:")
#     for g, winner, winning in game.hand_winners:
#         print(f"Game {g}: {winner} ({winning})")
    
#     print("\nFinal stack sizes are:")
#     for player in game.players:
#         print(f"{player.name}: ${player.stack}")
        
#     # Keep window open until user closes it manually at the end
#     print("\nSimulation complete. Close the Pygame window to exit.")
#     import pygame
#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()

# if __name__ == "__main__":
#     run_game(10)

import os
import sys
import time
from player import PlayerStatus, PlayerAction
from game import PokerGame, GamePhase
from baseplayers import InputPlayer, RaisePlayer, FoldPlayer
from mybot import MyBot
from visualizer import GameVisualizer 

def run_game(num_hands):
    visualizer = GameVisualizer()

    players = [
        MyBot("Bot 1", 1000),
        MyBot("Bot 2", 1000),
        RaisePlayer("Aggro Bob", 1000),
        FoldPlayer("Timid Charlie", 1000),
        MyBot("Bot 3", 1000)
    ]
    
    game = PokerGame(players, big_blind=20)

    for _ in range(num_hands):
        print(f"\nHand number {game.hand_number + 1}")
        game_status = game.start_new_hand()
        if not game_status:
            print(f"Not enough players left in the game... game over.")
            break
        
        # Draw initial state and wait
        visualizer.draw_state(game)
        time.sleep(2.0) # SLOWED DOWN: Wait 2 seconds at the start of a hand
        
        num_tries = 0
        while game.phase != GamePhase.SHOWDOWN:
            if num_tries == 3:
                game.player_action(PlayerAction.FOLD, 0)
                num_tries = 0
                continue

            player = game.players[game.active_player_index]

            if game.num_active_players() == 1 and player.bet_amount == game.current_bet:
                game.advance_game_phase()
                game.display_game_state()
                visualizer.draw_state(game)
                time.sleep(1.5) # SLOWED DOWN: Pause when advancing phases (flop, turn, river)
                continue

            print(f"\n{player.name}'s turn")
            
            try:
                is_successful = game.get_player_input()
            except Exception as e:
                print(f"Player {player.name}'s turn failed: {e}")
                is_successful = False

            if not is_successful:
                num_tries += 1
            else:
                num_tries = 0
            
            visualizer.draw_state(game)
            time.sleep(1.5) # SLOWED DOWN: Wait 1.5 seconds after EVERY bot move

        # Draw the final showdown state
        visualizer.draw_state(game)
        print("\nHand complete. Starting new hand in 6 seconds...")
        time.sleep(6.0) # SLOWED DOWN: Keep the final hand visible for 6 seconds so you can see who won!

    print("\nWinners are:")
    for g, winner, winning in game.hand_winners:
        print(f"Game {g}: {winner} ({winning})")
    
    print("\nFinal stack sizes are:")
    for player in game.players:
        print(f"{player.name}: ${player.stack}")
        
    print("\nSimulation complete. Close the Pygame window to exit.")
    import pygame
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    run_game(10)
