import pygame
import sys
import math
from card import Suit
from player import PlayerStatus

class GameVisualizer:
    def __init__(self, width=1200, height=800):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("AI Poker 2025 - Bot Visualizer")
        
        # Enhanced Colors
        self.FLOOR_COLOR = (30, 30, 35)
        self.TABLE_BORDER = (90, 50, 20)   # Wooden brown
        self.TABLE_FELT = (34, 120, 50)    # Casino green
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (220, 20, 20)
        self.GOLD = (255, 215, 0)
        self.GRAY = (150, 150, 150)
        self.DARK_GRAY = (80, 80, 80)
        self.ACTIVE_BG = (50, 50, 80)      # Highlight background for active player
        
        # Fonts
        self.rank_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 16, bold=True)
        self.title_font = pygame.font.SysFont('Arial', 22, bold=True)

    def draw_suit_shape(self, suit, cx, cy, size=12):
        """Draws the actual suit shapes using Pygame polygons/circles to guarantee they render properly."""
        if suit == Suit.HEARTS:
            # Hearts: Two circles on top, triangle on bottom
            pygame.draw.circle(self.screen, self.RED, (cx - size//2.5, cy - size//4), size//2)
            pygame.draw.circle(self.screen, self.RED, (cx + size//2.5, cy - size//4), size//2)
            pygame.draw.polygon(self.screen, self.RED, [(cx - size*.9, cy - size//6), (cx + size*.9, cy - size//6), (cx, cy + size)])
        
        elif suit == Suit.DIAMONDS:
            # Diamonds: Simple rhombus
            pygame.draw.polygon(self.screen, self.RED, [(cx, cy - size), (cx + size*.85, cy), (cx, cy + size), (cx - size*.85, cy)])
        
        elif suit == Suit.CLUBS:
            # Clubs: Three circles and a rectangular stem
            pygame.draw.circle(self.screen, self.BLACK, (cx, cy - size//2), size//2)
            pygame.draw.circle(self.screen, self.BLACK, (cx - size//2, cy + size//4), size//2)
            pygame.draw.circle(self.screen, self.BLACK, (cx + size//2, cy + size//4), size//2)
            pygame.draw.rect(self.screen, self.BLACK, (cx - size//4, cy + size//4, size//2, size*.75))
        
        elif suit == Suit.SPADES:
            # Spades: Inverted heart essentially, plus a stem
            pygame.draw.circle(self.screen, self.BLACK, (cx - size//2, cy + size//4), size//2)
            pygame.draw.circle(self.screen, self.BLACK, (cx + size//2, cy + size//4), size//2)
            pygame.draw.polygon(self.screen, self.BLACK, [(cx - size*.9, cy + size//3), (cx + size*.9, cy + size//3), (cx, cy - size)])
            pygame.draw.rect(self.screen, self.BLACK, (cx - size//4, cy + size//4, size//2, size*.75))

    def draw_card(self, card, x, y, face_up=True):
        card_w, card_h = 60, 85
        
        if not face_up:
            # Fancy card back
            pygame.draw.rect(self.screen, self.WHITE, (x, y, card_w, card_h), border_radius=6)
            pygame.draw.rect(self.screen, (20, 50, 100), (x+4, y+4, card_w-8, card_h-8), border_radius=4)
            # Simple pattern on the back
            pygame.draw.line(self.screen, (40, 80, 140), (x+4, y+4), (x+card_w-4, y+card_h-4), 2)
            pygame.draw.line(self.screen, (40, 80, 140), (x+card_w-4, y+4), (x+4, y+card_h-4), 2)
            return

        # Card body
        pygame.draw.rect(self.screen, self.WHITE, (x, y, card_w, card_h), border_radius=6)
        pygame.draw.rect(self.screen, self.GRAY, (x, y, card_w, card_h), 1, border_radius=6)
        
        # Get Rank string (handling the 10, J, Q, K, A)
        rank_str = "10" if card.rank.value == 10 else "JQKA"[card.rank.value - 11] if card.rank.value > 10 else str(card.rank.value)
        color = self.RED if card.suit in [Suit.HEARTS, Suit.DIAMONDS] else self.BLACK
        
        # Draw Rank
        rank_surface = self.rank_font.render(rank_str, True, color)
        self.screen.blit(rank_surface, (x + 6, y + 4))
        
        # Draw small suit under rank
        self.draw_suit_shape(card.suit, x + 12 + (6 if rank_str=="10" else 0), y + 36, size=6)
        
        # Draw large suit in center
        self.draw_suit_shape(card.suit, x + card_w//2, y + card_h//2 + 10, size=15)

    def draw_state(self, game):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill(self.FLOOR_COLOR)
        
        # --- Draw Table ---
        # Outer wooden rail
        table_rect_outer = (100, 150, self.width - 200, self.height - 300)
        pygame.draw.ellipse(self.screen, self.TABLE_BORDER, table_rect_outer)
        # Inner green felt
        table_rect_inner = (130, 180, self.width - 260, self.height - 360)
        pygame.draw.ellipse(self.screen, self.TABLE_FELT, table_rect_inner)
        
        # --- Draw Table Info (Pot, Phase, Bet) ---
        info_bg = pygame.Surface((400, 40), pygame.SRCALPHA)
        info_bg.fill((0, 0, 0, 150))
        self.screen.blit(info_bg, (self.width//2 - 200, self.height//2 - 90))
        
        pot_text = self.title_font.render(f"Phase: {game.phase.value.upper()} | Pot: ${game.pot}", True, self.GOLD)
        self.screen.blit(pot_text, (self.width//2 - pot_text.get_width()//2, self.height//2 - 82))
        
        # --- Draw Community Cards ---
        comm_x = self.width//2 - (5 * 70)//2
        for i in range(5):
            cx, cy = comm_x + i * 70, self.height//2 - 20
            if i < len(game.community_cards):
                self.draw_card(game.community_cards[i], cx, cy)
            else:
                pygame.draw.rect(self.screen, (25, 90, 40), (cx, cy, 60, 85), 2, border_radius=6)
                
        # --- Draw Players ---
        num_players = len(game.players)
        for i, player in enumerate(game.players):
            # Calculate position along the table edge
            angle = i * (2 * math.pi / num_players) - math.pi/2
            radius_x, radius_y = self.width//2 - 140, self.height//2 - 150
            
            # Anchor point for the player's "station"
            px = self.width//2 + int(math.cos(angle) * radius_x)
            py = self.height//2 + int(math.sin(angle) * radius_y)
            
            box_width, box_height = 140, 130
            bx, by = px - box_width//2, py - box_height//2
            
            # Highlight active player with a solid background box and a gold border
            is_active = (i == game.active_player_index and player.can_make_action() and game.phase.value != "showdown")
            if is_active:
                pygame.draw.rect(self.screen, self.ACTIVE_BG, (bx, by, box_width, box_height), border_radius=10)
                pygame.draw.rect(self.screen, self.GOLD, (bx, by, box_width, box_height), 3, border_radius=10)
                # "TURN" badge
                turn_text = self.small_font.render("CURRENT TURN", True, self.BLACK)
                pygame.draw.rect(self.screen, self.GOLD, (bx + box_width//2 - 60, by - 12, 120, 20), border_radius=5)
                self.screen.blit(turn_text, (bx + box_width//2 - turn_text.get_width()//2, by - 10))

            # Draw Player Info
            status_color = self.GRAY if player.status == PlayerStatus.FOLDED else self.WHITE
            
            name_text = self.small_font.render(f"{player.name}", True, status_color)
            stack_text = self.small_font.render(f"${player.stack}", True, self.GOLD)
            action_text = self.small_font.render(f"[{player.status.value}] Bet: ${player.bet_amount}", True, status_color)
            
            self.screen.blit(name_text, (bx + 10, by + 10))
            self.screen.blit(stack_text, (bx + box_width - stack_text.get_width() - 10, by + 10))
            
            # Draw Hole Cards inside the box
            if player.status != PlayerStatus.OUT:
                for j, card in enumerate(player.hole_cards):
                    self.draw_card(card, bx + 10 + j * 65, by + 35, face_up=(player.status != PlayerStatus.FOLDED))

            self.screen.blit(action_text, (bx + box_width//2 - action_text.get_width()//2, by + box_height - 25))

        pygame.display.flip()