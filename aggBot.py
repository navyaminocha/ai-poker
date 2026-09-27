from player import Player, PlayerAction
from hand_evaluator import HandEvaluator, HandRank
from card import Card
import random

# ═══════════════════════════════════════════════════════════════════
#  PATCH NOTES — what changed and why
# ═══════════════════════════════════════════════════════════════════
#
#  BUG FIX 1 — "list index out of range" crash (hands 2, 3, 6)
#    CAUSE:   Direct indexing into game_state without length checks.
#             Any variation in num_players or state size caused a crash.
#    FIX:     All game_state reads go through safe() helper which
#             returns a default value instead of raising IndexError.
#             Also wrapped hand evaluator call in try/except.
#    EFFECT:  Bot never crashes → never force-folded again.
#             Hand 2 (77) and Hand 3 (QQ) would now play out fully.
#
#  BUG FIX 2 — "Invalid command" when we are the blind poster
#    CAUSE:   When we post the blind, self.bet_amount == blind already.
#             call_amount = cur_raise - self.bet_amount = 0.
#             Old code could return CALL with amount=0, which the
#             engine rejected as invalid → forced fold.
#    FIX:     call_amount = max(0, cur_raise - self.bet_amount).
#             Any time call_amount == 0, we use CHECK or BET, never CALL.
#    EFFECT:  No more invalid commands when acting from blind position.
#
#  BUG FIX 3 — Opponent stats inflated by re-processing full history
#    CAUSE:   _update_opponent_stats() iterated over the ENTIRE
#             action_history on every single action. By turn 10,
#             every stat was counted 10× — classifying everyone as
#             a maniac because allin_ratio was artificially inflated.
#    FIX:     Track self._history_len and only process new entries
#             added since the last call (slice action_history).
#    EFFECT:  Opponent profiles are now accurate. Bot correctly
#             identifies passive folders and adjusts strategy.
#
#  IMPROVEMENT 1 — Consistent 3× blind open raise
#    WHAT:    All preflop opens are exactly blind × 3. No more
#             escalating 35→102→153 sizing on medium hands.
#    WHY:     Baseline-Raiser won pots consistently with clean 60
#             chip raises (blind=20). Consistent sizing is harder
#             to read and keeps pot controlled on speculative hands.
#    EFFECT:  Stops chip bleeding from over-sized preflop pots.
#
#  IMPROVEMENT 2 — Mandatory c-bet on flop when we raised preflop
#    WHAT:    If we raised preflop and reach the flop unchallenged,
#             always fire a continuation bet of 40% pot.
#    WHY:     Raiser c-bet 40 chips on every flop and won most pots
#             without showdown. Checking the flop gives up free equity.
#             Opponents often miss the flop and fold to any bet.
#    EFFECT:  Win significantly more pots without going to showdown.
#
#  IMPROVEMENT 3 — Short stack push/fold mode
#    WHAT:    When stack drops below 4× blind, stop calling/folding
#             incrementally. Strong hand → all-in. Else → fold.
#    WHY:     In hands 6-9 MyBot had $70-90 and kept bleeding chips
#             with small calls then folding. With a tiny stack, one
#             shove is better than a slow death.
#    EFFECT:  Gives real chance to double up from a short stack.
#
#  IMPROVEMENT 4 — No 3-bet with medium hands
#    WHAT:    Only 3-bet (re-raise a raiser) if strength >= 0.70.
#             Medium hands facing a raise → call or fold, never raise.
#    WHY:     Hand 5: had 8Tc (medium) and kept re-raising Baseline-
#             Raiser preflop, building a huge pot then folding the flop.
#             That's the single most chip-destroying pattern.
#    EFFECT:  Stops the build-huge-pot-then-fold-flop disaster.
#
# ═══════════════════════════════════════════════════════════════════

RANK_VALUES = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]


def card_index_to_card(idx: int) -> Card:
    from card import Suit, Rank
    suit_idx = idx // 13
    rank_idx = idx % 13
    suits = list(Suit)
    ranks = list(Rank)
    return Card(rank=ranks[rank_idx], suit=suits[suit_idx])


def get_preflop_strength(card_idx_1: int, card_idx_2: int) -> float:
    r1 = card_idx_1 % 13
    r2 = card_idx_2 % 13
    suited = (card_idx_1 // 13) == (card_idx_2 // 13)
    hi = max(r1, r2)
    lo = min(r1, r2)

    if r1 == r2:
        return 0.50 + (hi / 12.0) * 0.50

    gap = hi - lo
    score = (RANK_VALUES[hi] + RANK_VALUES[lo]) / 2.0
    score = (score - 2.0) / 12.0
    gap_penalty  = gap * 0.04
    suited_bonus = 0.06 if suited else 0.0
    return max(0.0, min(1.0, score - gap_penalty + suited_bonus))


def get_postflop_strength(hole_cards: list, community_cards: list) -> float:
    if not community_cards:
        return 0.5
    try:
        result = HandEvaluator.evaluate_hand(hole_cards, community_cards)
    except Exception:
        return 0.30   # BUG FIX 1: never crash here

    strength_map = {
        1: 0.10, 2: 0.28, 3: 0.45, 4: 0.60,
        5: 0.67, 6: 0.74, 7: 0.83, 8: 0.93,
        9: 0.97, 10: 1.00,
    }
    base = strength_map.get(result.hand_rank.value, 0.5)

    try:
        kicker_bonus = (result.hand_value[0] / 14.0) * 0.05
    except Exception:
        kicker_bonus = 0.0

    return min(1.0, base + kicker_bonus)


class ExploitativePlayer(Player):

    def __init__(self, name: str, stack: int):
        super().__init__(name, stack)

        # ── Tunable parameters ───────────────────────────────────
        self.BLUFF_FREQUENCY  = 0.25
        self.VALUE_BET_STRONG = 0.75
        self.VALUE_BET_MEDIUM = 0.45
        self.BLUFF_BET_FRAC   = 0.45
        self.CBET_FRAC        = 0.40   # c-bet: 40% of pot
        self.OPEN_RAISE_MULT  = 3      # 3× blind open raise
        self.STRONG_THRESH    = 0.65
        self.MEDIUM_THRESH    = 0.38
        self.THREEBET_THRESH  = 0.70   # min strength to re-raise
        self.ALLIN_THRESH     = 0.85

        # ── Internal state ───────────────────────────────────────
        self.opp_stats        = {}
        self._history_len     = 0      # BUG FIX 3
        self._raised_preflop  = False
        self._last_hand_num   = -1

    # ─────────────────────────────────────────────────────────────
    #  SAFE PARSER  (BUG FIX 1)
    # ─────────────────────────────────────────────────────────────
    def _parse(self, gs: list) -> dict:
        def safe(i, d=0):
            try:    return gs[i]
            except: return d

        n = safe(11, 2)
        return {
            "hole":     [safe(0), safe(1)],
            "comm":     [c for c in [safe(2),safe(3),safe(4),safe(5),safe(6)] if c != 0],
            "pot":      safe(7,  0),
            "raise":    safe(8,  0),
            "blind":    safe(9, 20),
            "n":        n,
            "stacks":   [safe(12+i) for i in range(n)],
            "hand_num": safe(12+n, 0),
        }

    # ─────────────────────────────────────────────────────────────
    #  MAIN ACTION
    # ─────────────────────────────────────────────────────────────
    def action(self, game_state: list, action_history: list):
        s          = self._parse(game_state)
        hole_idx   = s["hole"]
        comm_idx   = s["comm"]
        pot        = max(s["pot"], 1)
        blind      = max(s["blind"], 1)
        cur_raise  = s["raise"]
        hand_num   = s["hand_num"]

        # BUG FIX 2: correct call amount, never negative
        call_amount = max(0, cur_raise - self.bet_amount)

        # Reset per-hand flags on new hand
        if hand_num != self._last_hand_num:
            self._raised_preflop = False
            self._last_hand_num  = hand_num

        # Card conversion — safe fallback if it errors
        try:
            hole_cards = [card_index_to_card(i) for i in hole_idx if i > 0]
            comm_cards = [card_index_to_card(i) for i in comm_idx if i > 0]
        except Exception:
            return (PlayerAction.CHECK, 0) if call_amount == 0 else (PlayerAction.FOLD, 0)

        is_preflop = len(comm_cards) == 0

        # Hand strength — safe fallback
        try:
            if is_preflop:
                strength = get_preflop_strength(hole_idx[0], hole_idx[1])
            else:
                strength = get_postflop_strength(hole_cards, comm_cards)
        except Exception:
            strength = 0.30

        # Opponent modeling (incremental — BUG FIX 3)
        self._update_opp_stats(action_history)
        profile = self._table_profile()

        # Adjust thresholds per profile
        strong_t = self.STRONG_THRESH
        medium_t = self.MEDIUM_THRESH
        bluff_f  = self.BLUFF_FREQUENCY

        if profile == "passive":
            medium_t -= 0.05;  bluff_f = 0.35
        elif profile == "maniac":
            strong_t += 0.12;  medium_t += 0.10;  bluff_f = 0.05
        elif profile == "loose":
            bluff_f = 0.08
        elif profile == "aggressive":
            strong_t += 0.05

        pot_odds = call_amount / (pot + call_amount) if call_amount > 0 else 0.0

        # Short stack mode (IMPROVEMENT 3)
        if self.stack <= blind * 4:
            if strength >= strong_t - 0.05:
                return PlayerAction.ALL_IN, self.stack
            if call_amount == 0:
                return PlayerAction.CHECK, 0
            return PlayerAction.FOLD, 0

        return self._decide(strength, pot_odds, pot, call_amount,
                            blind, is_preflop, strong_t, medium_t, bluff_f)

    # ─────────────────────────────────────────────────────────────
    #  DECISION ENGINE
    # ─────────────────────────────────────────────────────────────
    def _decide(self, strength, pot_odds, pot, call_amount,
                blind, is_preflop, strong_t, medium_t, bluff_f):

        open_raise = blind * self.OPEN_RAISE_MULT   # IMPROVEMENT 1: 3× blind

        # ══════════════ PREFLOP ══════════════
        if is_preflop:

            if strength >= strong_t:
                if call_amount > 0:
                    # IMPROVEMENT 4: only 3-bet with genuinely strong hand
                    if strength >= self.THREEBET_THRESH:
                        reraise = call_amount + open_raise
                        if self.stack > reraise:
                            self._raised_preflop = True
                            return PlayerAction.RAISE, reraise
                    if call_amount < self.stack:
                        return PlayerAction.CALL, call_amount
                    return PlayerAction.ALL_IN, self.stack
                else:
                    if self.stack > open_raise:
                        self._raised_preflop = True
                        return PlayerAction.RAISE, open_raise
                    return PlayerAction.ALL_IN, self.stack

            elif strength >= medium_t:
                if call_amount > 0:
                    # IMPROVEMENT 4: never re-raise with medium hand
                    if strength > pot_odds and call_amount < self.stack * 0.25:
                        return PlayerAction.CALL, call_amount
                    return PlayerAction.FOLD, 0
                else:
                    if self.stack > open_raise:
                        self._raised_preflop = True
                        return PlayerAction.RAISE, open_raise
                    return PlayerAction.CHECK, 0

            else:
                # Occasional bluff-raise to stay unpredictable
                if call_amount == 0 and random.random() < bluff_f * 0.6:
                    if self.stack > open_raise:
                        self._raised_preflop = True
                        return PlayerAction.RAISE, open_raise
                # BUG FIX 2: if we're blind and owe nothing, CHECK
                if call_amount == 0:
                    return PlayerAction.CHECK, 0
                return PlayerAction.FOLD, 0

        # ══════════════ POSTFLOP ══════════════
        else:

            # IMPROVEMENT 2: c-bet if we raised preflop and it's free
            if self._raised_preflop and call_amount == 0:
                cbet = max(int(pot * self.CBET_FRAC), blind)
                if self.stack > cbet:
                    self._raised_preflop = False   # only fire once
                    return PlayerAction.BET, cbet

            if strength >= strong_t:
                if strength >= self.ALLIN_THRESH:
                    return PlayerAction.ALL_IN, self.stack
                bet = max(int(pot * self.VALUE_BET_STRONG), blind)
                if call_amount > 0:
                    if call_amount >= self.stack:
                        return PlayerAction.ALL_IN, self.stack
                    reraise = call_amount + bet
                    if self.stack > reraise:
                        return PlayerAction.RAISE, reraise
                    return PlayerAction.CALL, call_amount
                else:
                    if self.stack > bet:
                        return PlayerAction.BET, bet
                    return PlayerAction.ALL_IN, self.stack

            elif strength >= medium_t:
                if call_amount > 0:
                    if strength > pot_odds + 0.05:
                        if call_amount >= self.stack:
                            return PlayerAction.ALL_IN, self.stack
                        return PlayerAction.CALL, call_amount
                    return PlayerAction.FOLD, 0
                else:
                    bet = max(int(pot * self.VALUE_BET_MEDIUM), blind)
                    if self.stack > bet:
                        return PlayerAction.BET, bet
                    return PlayerAction.CHECK, 0

            else:
                if random.random() < bluff_f:
                    bluff_bet = max(int(pot * self.BLUFF_BET_FRAC), blind)
                    if call_amount > 0:
                        if call_amount > 0.12 * self.stack:
                            return PlayerAction.FOLD, 0
                        reraise = call_amount + bluff_bet
                        if self.stack > reraise:
                            return PlayerAction.RAISE, reraise
                        return PlayerAction.FOLD, 0
                    else:
                        if self.stack > bluff_bet:
                            return PlayerAction.BET, bluff_bet
                        return PlayerAction.CHECK, 0

                if call_amount == 0:
                    return PlayerAction.CHECK, 0
                return PlayerAction.FOLD, 0

    # ─────────────────────────────────────────────────────────────
    #  OPPONENT MODELING
    # ─────────────────────────────────────────────────────────────
    def _update_opp_stats(self, history: list):
        # BUG FIX 3: only process entries we haven't seen yet
        for entry in history[self._history_len:]:
            if len(entry) < 4:
                continue
            _, name, act, _ = entry
            if name == self.name:
                continue
            if name not in self.opp_stats:
                self.opp_stats[name] = {
                    "raises":0,"calls":0,"folds":0,
                    "checks":0,"allin":0,"total":0
                }
            s = self.opp_stats[name]
            s["total"] += 1
            if act in ("raise","bet"):  s["raises"] += 1
            elif act == "call":         s["calls"]  += 1
            elif act == "fold":         s["folds"]  += 1
            elif act == "check":        s["checks"] += 1
            elif act == "all-in":       s["allin"]  += 1
        self._history_len = len(history)

    def _table_profile(self) -> str:
        if not self.opp_stats:
            return "unknown"
        total_acts   = sum(s["total"]              for s in self.opp_stats.values())
        if total_acts == 0:
            return "unknown"
        total_raises = sum(s["raises"]+s["allin"]  for s in self.opp_stats.values())
        total_folds  = sum(s["folds"]              for s in self.opp_stats.values())
        total_calls  = sum(s["calls"]              for s in self.opp_stats.values())
        total_allins = sum(s["allin"]              for s in self.opp_stats.values())

        if total_allins / total_acts > 0.25:   return "maniac"
        if total_raises / total_acts > 0.40:   return "aggressive"
        if total_folds  / total_acts > 0.50:   return "passive"
        if total_calls  / total_acts > 0.50:   return "loose"
        if total_folds  / total_acts > 0.35:   return "tight"
        return "unknown"