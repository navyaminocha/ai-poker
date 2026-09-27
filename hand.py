# from card import Rank, Suit, Card

# def decode_card(index):
#     if index == 0: # Handle 'no card' placeholder
#         return None
#     # Ensure index is 0-51
#     index = (index - 1) % 52 
#     suit_val = index // 13
#     rank_val = (index % 13) + 2
#     return Card(Rank(rank_val), Suit(suit_val))

from card import Rank, Suit, Card

def decode_card(index):
    if index == 0: 
        return None
        
    # Subtract 1 to align with 0-based indexing before division
    # Modulo 52 ensures we never go out of bounds
    adjusted_index = (index - 1) % 52 
    
    suit_val = adjusted_index // 13
    rank_val = (adjusted_index % 13) + 2
    
    return Card(Rank(rank_val), Suit(suit_val))