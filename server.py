# import asyncio
# import json
# import traceback
# import uvicorn
# from contextlib import asynccontextmanager
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.responses import HTMLResponse

# from player import PlayerStatus, PlayerAction
# from game import PokerGame, GamePhase
# from baseplayers import FoldPlayer, RaisePlayer, RandomPlayer, AllInPlayer, MonteCarloPlayer
# from mybot import MyBot
# from udayBot import  MetaPokerBot
# from aggBot import ExploitativePlayer

# class GameState:
#     def __init__(self):
#         self.game = None
#         self.message = "Waiting for players..."

# game_state = GameState()
# connected_clients = set()

# async def broadcast_state():
#     if not connected_clients or not game_state.game:
#         return

#     game = game_state.game
    
#     try:
#         state = {
#             "phase": game.phase.value.upper(),
#             "pot": game.pot,
#             "current_bet": game.current_bet,
#             "community_cards": [str(c) for c in game.community_cards],
#             "active_player_index": game.active_player_index,
#             "message": game_state.message,
#             "players": [
#                 {
#                     "id": i,
#                     "name": p.name,
#                     "stack": p.stack,
#                     "bet": p.bet_amount,
#                     "status": p.status.value.upper(),
#                     "cards": [str(c) for c in p.hole_cards] if p.status != PlayerStatus.OUT else []
#                 } for i, p in enumerate(game.players)
#             ]
#         }
        
#         json_state = json.dumps(state)
        
#         disconnected = set()
#         for client in connected_clients:
#             try:
#                 await client.send_text(json_state)
#             except Exception:
#                 disconnected.add(client)
                
#         for client in disconnected:
#             connected_clients.remove(client)
            
#     except Exception as e:
#         print("\n--- ERROR PACKING JSON STATE ---")
#         traceback.print_exc()

# async def game_loop():
#     print("Server started. WAITING FOR BROWSER TO CONNECT...")
    
#     while not connected_clients:
#         await asyncio.sleep(1)
        
#     print("Browser detected! Starting Poker Game...")
    
#     try:
#         players = [
#             ExploitativePlayer("Agg", 1000),
#             RaisePlayer("Raise", 1000),
#             MyBot("Garv", 1000),
#             RandomPlayer("Rand", 1000),
#             MonteCarloPlayer("Dhruv", 1000),
#             # AllInPlayer("All", 1000),
#             MetaPokerBot("Uday", 1000)
#         ]
        
#         game_state.game = PokerGame(players, big_blind=20)
        
#         for hand in range(20):
#             status = game_state.game.start_new_hand()
#             if not status:
#                 print("Game over: Not enough players.")
#                 break
                
#             game_state.message = f"Starting Hand {hand + 1}"
#             await broadcast_state()
#             await asyncio.sleep(2.0)
            
#             num_tries = 0
#             while game_state.game.phase != GamePhase.SHOWDOWN:
#                 if num_tries == 3:
#                     game_state.game.player_action(PlayerAction.FOLD, 0)
#                     num_tries = 0
#                     continue

#                 player = game_state.game.players[game_state.game.active_player_index]

#                 if game_state.game.num_active_players() == 1 and player.bet_amount == game_state.game.current_bet:
#                     game_state.game.advance_game_phase()
#                     game_state.message = f"Advanced to {game_state.game.phase.value}"
#                     await broadcast_state()
#                     await asyncio.sleep(1.5)
#                     continue

#                 try:
#                     is_successful = game_state.game.get_player_input()
#                 except Exception as e:
#                     print(f"\nERROR - Bot '{player.name}' crashed during its turn:")
#                     traceback.print_exc()
#                     is_successful = False

#                 if not is_successful:
#                     num_tries += 1
#                 else:
#                     num_tries = 0
                
#                 game_state.message = f"{player.name} moved."
#                 await broadcast_state()
#                 await asyncio.sleep(1.5)
            
#             game_state.message = "SHOWDOWN!"
#             await broadcast_state()
#             await asyncio.sleep(5.0)
            
#         game_state.message = "Simulation Complete! Check terminal for scores."
#         await broadcast_state()
        
#     except Exception as e:
#         print("\nFATAL ERROR IN GAME ENGINE:")
#         traceback.print_exc()
#         game_state.message = "ERROR: Server Crashed. Check Terminal."
#         await broadcast_state()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     bg_task = asyncio.create_task(game_loop())
#     yield
#     bg_task.cancel()

# app = FastAPI(lifespan=lifespan)

# @app.get("/")
# async def get_frontend():
#     with open("index.html", "r", encoding="utf-8") as f:
#         return HTMLResponse(f.read())

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     connected_clients.add(websocket)
#     print("\n--- BROWSER CONNECTED! ---")
    
#     if game_state.game:
#         await broadcast_state()
        
#     try:
#         while True:
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         connected_clients.remove(websocket)
#         print("Browser disconnected normally.")
#     except Exception as e:
#         if websocket in connected_clients:
#             connected_clients.remove(websocket)
#         print(f"Browser connection dropped: {e}")

# if __name__ == "__main__":
#     print("Starting Poker Server... Open http://localhost:8000 in your browser.")
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# import asyncio
# import json
# import traceback
# import uvicorn
# from contextlib import asynccontextmanager
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.responses import HTMLResponse

# from player import PlayerStatus, PlayerAction
# from game import PokerGame, GamePhase
# from baseplayers import FoldPlayer, RaisePlayer, RandomPlayer, AllInPlayer, MonteCarloPlayer
# from mybot import MyBot
# from udayBot import  MetaPokerBot
# from aggBot import ExploitativePlayer

# # ADDED: Import your HandEvaluator to get the current hand names
# from hand_evaluator import HandEvaluator

# class GameState:
#     def __init__(self):
#         self.game = None
#         self.message = "Waiting for players..."

# game_state = GameState()
# connected_clients = set()

# async def broadcast_state():
#     if not connected_clients or not game_state.game:
#         return

#     game = game_state.game
    
#     try:
#         # ADDED: Fetch winners for the *current* hand if we are in showdown
#         current_winners = []
#         if game.phase == GamePhase.SHOWDOWN:
#             current_winners = [{"name": name, "amount": amt} for h_num, name, amt in game.hand_winners if h_num == game.hand_number]

#         state = {
#             "phase": game.phase.value.upper(),
#             "pot": game.pot,
#             "current_bet": game.current_bet,
#             "community_cards": [str(c) for c in game.community_cards],
#             "active_player_index": game.active_player_index,
#             "message": game_state.message,
#             "winners": current_winners, # Expose winners to frontend
#             "players": [
#                 {
#                     "id": i,
#                     "name": p.name,
#                     "stack": p.stack,
#                     "bet": p.bet_amount,
#                     "status": p.status.value.upper(),
#                     # ADDED: Evaluate the best hand dynamically using your existing HandEvaluator
#                     "hand_name": HandEvaluator.evaluate_hand(p.hole_cards, game.community_cards).hand_rank.name.replace("_", " ") if p.hole_cards and p.status != PlayerStatus.OUT else "",
#                     "cards": [str(c) for c in p.hole_cards] if p.status != PlayerStatus.OUT else []
#                 } for i, p in enumerate(game.players)
#             ]
#         }
        
#         json_state = json.dumps(state)
        
#         disconnected = set()
#         for client in connected_clients:
#             try:
#                 await client.send_text(json_state)
#             except Exception:
#                 disconnected.add(client)
                
#         for client in disconnected:
#             connected_clients.remove(client)
            
#     except Exception as e:
#         print("\n--- ERROR PACKING JSON STATE ---")
#         traceback.print_exc()

# async def game_loop():
#     print("Server started. WAITING FOR BROWSER TO CONNECT...")
    
#     while not connected_clients:
#         await asyncio.sleep(1)
        
#     print("Browser detected! Starting Poker Game...")
    
#     try:
#         players = [
#             ExploitativePlayer("Agg", 1000),
#             RaisePlayer("Raise", 1000),
#             MyBot("Garv", 1000),
#             RandomPlayer("Rand", 1000),
#             MonteCarloPlayer("Dhruv", 1000),
#             # AllInPlayer("All", 1000),
#             MetaPokerBot("Uday", 1000)
#         ]
        
#         game_state.game = PokerGame(players, big_blind=20)
        
#         for hand in range(20):
#             status = game_state.game.start_new_hand()
#             if not status:
#                 print("Game over: Not enough players.")
#                 break
                
#             game_state.message = f"Starting Hand {hand + 1}"
#             await broadcast_state()
#             await asyncio.sleep(2.0)
            
#             num_tries = 0
#             while game_state.game.phase != GamePhase.SHOWDOWN:
#                 if num_tries == 3:
#                     game_state.game.player_action(PlayerAction.FOLD, 0)
#                     num_tries = 0
#                     continue

#                 player = game_state.game.players[game_state.game.active_player_index]

#                 if game_state.game.num_active_players() == 1 and player.bet_amount == game_state.game.current_bet:
#                     game_state.game.advance_game_phase()
#                     game_state.message = f"Advanced to {game_state.game.phase.value}"
#                     await broadcast_state()
#                     await asyncio.sleep(1.5)
#                     continue

#                 try:
#                     is_successful = game_state.game.get_player_input()
#                 except Exception as e:
#                     print(f"\nERROR - Bot '{player.name}' crashed during its turn:")
#                     traceback.print_exc()
#                     is_successful = False

#                 if not is_successful:
#                     num_tries += 1
#                 else:
#                     num_tries = 0
                
#                 game_state.message = f"{player.name} moved."
#                 await broadcast_state()
#                 await asyncio.sleep(1.5)
            
#             game_state.message = "SHOWDOWN!"
#             await broadcast_state()
#             await asyncio.sleep(5.0)
            
#         game_state.message = "Simulation Complete! Check terminal for scores."
#         await broadcast_state()
        
#     except Exception as e:
#         print("\nFATAL ERROR IN GAME ENGINE:")
#         traceback.print_exc()
#         game_state.message = "ERROR: Server Crashed. Check Terminal."
#         await broadcast_state()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     bg_task = asyncio.create_task(game_loop())
#     yield
#     bg_task.cancel()

# app = FastAPI(lifespan=lifespan)

# @app.get("/")
# async def get_frontend():
#     with open("index.html", "r", encoding="utf-8") as f:
#         return HTMLResponse(f.read())

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     connected_clients.add(websocket)
#     print("\n--- BROWSER CONNECTED! ---")
    
#     if game_state.game:
#         await broadcast_state()
        
#     try:
#         while True:
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         connected_clients.remove(websocket)
#         print("Browser disconnected normally.")
#     except Exception as e:
#         if websocket in connected_clients:
#             connected_clients.remove(websocket)
#         print(f"Browser connection dropped: {e}")

# if __name__ == "__main__":
#     print("Starting Poker Server... Open http://localhost:8000 in your browser.")
#     uvicorn.run(app, host="0.0.0.0", port=8000)

import asyncio
import json
import traceback
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from player import PlayerStatus, PlayerAction
from game import PokerGame, GamePhase
from baseplayers import FoldPlayer, RaisePlayer, RandomPlayer, AllInPlayer, MonteCarloPlayer
from mybot import MyBot
from udayBot import  MetaPokerBot
from aggBot import ExploitativePlayer

# Import HandEvaluator to get the current hand names
from hand_evaluator import HandEvaluator

class GameState:
    def __init__(self):
        self.game = None
        self.message = "Waiting for players..."
        self.show_winners = False # <-- ADDED: Flag to control the popup delay

game_state = GameState()
connected_clients = set()

async def broadcast_state():
    if not connected_clients or not game_state.game:
        return

    game = game_state.game
    
    try:
        current_winners = []
        # ADDED: Only populate winners if the flag is True
        if game.phase == GamePhase.SHOWDOWN and game_state.show_winners:
            current_winners = [{"name": name, "amount": amt} for h_num, name, amt in game.hand_winners if h_num == game.hand_number]

        state = {
            "phase": game.phase.value.upper(),
            "pot": game.pot,
            "current_bet": game.current_bet,
            "community_cards": [str(c) for c in game.community_cards],
            "active_player_index": game.active_player_index,
            "message": game_state.message,
            "winners": current_winners, 
            "players": [
                {
                    "id": i,
                    "name": p.name,
                    "stack": p.stack,
                    "bet": p.bet_amount,
                    "status": p.status.value.upper(),
                    "hand_name": HandEvaluator.evaluate_hand(p.hole_cards, game.community_cards).hand_rank.name.replace("_", " ") if p.hole_cards and p.status != PlayerStatus.OUT else "",
                    "cards": [str(c) for c in p.hole_cards] if p.status != PlayerStatus.OUT else []
                } for i, p in enumerate(game.players)
            ]
        }
        
        json_state = json.dumps(state)
        
        disconnected = set()
        for client in connected_clients:
            try:
                await client.send_text(json_state)
            except Exception:
                disconnected.add(client)
                
        for client in disconnected:
            connected_clients.remove(client)
            
    except Exception as e:
        print("\n--- ERROR PACKING JSON STATE ---")
        traceback.print_exc()

async def game_loop():
    print("Server started. WAITING FOR BROWSER TO CONNECT...")
    
    while not connected_clients:
        await asyncio.sleep(1)
        
    print("Browser detected! Starting Poker Game...")
    
    try:
        players = [
            ExploitativePlayer("Agg", 1000),
            RaisePlayer("Raise", 1000),
            MyBot("Garv", 1000),
            RandomPlayer("Random", 1000),
            MonteCarloPlayer("Dhruv", 1000),
            MetaPokerBot("Uday", 1000)
        ]
        
        game_state.game = PokerGame(players, big_blind=20)
        
        for hand in range(20):
            game_state.show_winners = False # Reset for the new hand
            
            status = game_state.game.start_new_hand()
            if not status:
                print("Game over: Not enough players.")
                break
                
            game_state.message = f"Starting Hand {hand + 1}"
            await broadcast_state()
            await asyncio.sleep(2.0)
            
            num_tries = 0
            while game_state.game.phase != GamePhase.SHOWDOWN:
                if num_tries == 3:
                    game_state.game.player_action(PlayerAction.FOLD, 0)
                    num_tries = 0
                    continue

                player = game_state.game.players[game_state.game.active_player_index]

                if game_state.game.num_active_players() == 1 and player.bet_amount == game_state.game.current_bet:
                    game_state.game.advance_game_phase()
                    game_state.message = f"Advanced to {game_state.game.phase.value}"
                    await broadcast_state()
                    await asyncio.sleep(1.5)
                    continue

                try:
                    is_successful = game_state.game.get_player_input()
                except Exception as e:
                    print(f"\nERROR - Bot '{player.name}' crashed during its turn:")
                    traceback.print_exc()
                    is_successful = False

                if not is_successful:
                    num_tries += 1
                else:
                    num_tries = 0
                
                game_state.message = f"{player.name} moved."
                await broadcast_state()
                await asyncio.sleep(1.5)
            
            # --- THE NEW DELAY LOGIC ---
            
            # 1. Broadcast SHOWDOWN phase first (flips cards, hides popup)
            game_state.show_winners = False 
            game_state.message = "SHOWDOWN!"
            await broadcast_state()
            
            # 2. The Suspense Delay (3 seconds)
            await asyncio.sleep(3.0) 
            
            # 3. Broadcast Winners (triggers popup)
            game_state.show_winners = True 
            await broadcast_state()
            
            # 4. Wait a bit so the user can read the popup before next hand
            await asyncio.sleep(5.0)
            
        game_state.message = "Simulation Complete! Check terminal for scores."
        await broadcast_state()
        
    except Exception as e:
        print("\nFATAL ERROR IN GAME ENGINE:")
        traceback.print_exc()
        game_state.message = "ERROR: Server Crashed. Check Terminal."
        await broadcast_state()

@asynccontextmanager
async def lifespan(app: FastAPI):
    bg_task = asyncio.create_task(game_loop())
    yield
    bg_task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def get_frontend():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    print("\n--- BROWSER CONNECTED! ---")
    
    if game_state.game:
        await broadcast_state()
        
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("Browser disconnected normally.")
    except Exception as e:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        print(f"Browser connection dropped: {e}")

if __name__ == "__main__":
    print("Starting Poker Server... Open http://localhost:8000 in your browser.")
    uvicorn.run(app, host="0.0.0.0", port=8000)