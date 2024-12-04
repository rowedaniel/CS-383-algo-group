from location import *
from board import *
from move import *

ALL_TILES = [True] * 7


class Incrementalist:
    """
    Dumb AI that picks the highest-scoring one-tile move. Plays a two-tile move on the first turn. Exchanges all of
    its letters if it can't find any other move.
    """

    def __init__(self):
        self._gatekeeper = None

    def set_gatekeeper(self, gatekeeper):
        self._gatekeeper = gatekeeper

    def choose_move(self):
        if self._gatekeeper.get_square(CENTER) == DOUBLE_WORD_SCORE:
            return self._find_two_tile_move()
        return self._find_one_tile_move()

    def _find_two_tile_move(self):
        hand = self._gatekeeper.get_hand()
        best_score = -1
        best_word = None
        for i in range(len(hand)):
            for j in range(len(hand)):
                if i != j:
                    try:
                        # This could be improved slightly by trying all possibilities for the blank
                        word = (hand[i] + hand[j]).replace('_', 'E')
                        self._gatekeeper.verify_legality(word, CENTER, HORIZONTAL)
                        score = self._gatekeeper.score(word, CENTER, HORIZONTAL)
                        if score > best_score:
                            best_score = score
                            best_word = word
                    except:
                        pass  # This move wasn't legal; go on to the next one
        if best_score > -1:
            return PlayWord(best_word, CENTER, HORIZONTAL)
        return ExchangeTiles(ALL_TILES)

    def _find_one_tile_move(self):
        hand = self._gatekeeper.get_hand()
        best_score = -1
        best_move = None
        for tile in hand:
            if tile == '_':
                tile = 'E'  # This could be improved slightly by trying all possibilities for the blank
            for word in tile + ' ', ' ' + tile:
                for row in range(WIDTH):
                    for col in range(WIDTH):
                        location = Location(row, col)
                        for direction in HORIZONTAL, VERTICAL:
                            try:
                                self._gatekeeper.verify_legality(word, location, direction)
                                score = self._gatekeeper.score(word, CENTER, HORIZONTAL)
                                if score > best_score:
                                    best_score = score
                                    best_move = PlayWord(word, location, direction)
                            except:
                                pass  # This move wasn't legal; go on to the next one
        if best_move:
            return best_move
        return ExchangeTiles(ALL_TILES)
