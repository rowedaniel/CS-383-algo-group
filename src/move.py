class ExchangeTiles:
    """
    Move exchanging 0 or more tiles.
    """
    def __init__(self, tiles_to_exchange):
        """
        :param tiles_to_exchange: An array of seven bools indicating which tiles in the hand to exchange. Any entries
        beyond the length of the hand are ignored.
        """
        self.tiles_to_exchange = tiles_to_exchange

    def play(self, board, player_number):
        board.exchange(board.get_hand(player_number), self.tiles_to_exchange)


class PlayWord:
    """
    Move playing one or more tiles on the board.
    """
    def __init__(self, word, location, direction):
        self._word = word
        self._location = location
        self._direction = direction

    def play(self, board, player_number):
        board.play(self._word, self._location, self._direction, board.get_hand(player_number))
        # These are returned for the benefit of the GUI
        return self._location, self._direction
