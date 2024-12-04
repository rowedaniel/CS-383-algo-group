class GateKeeper:
    """
    Intermediary between an AI and a Board, allowing the former to get information it needs without allowing full
    access.
    """
    def __init__(self, board, player_number):
        self._board = board
        self._player_number = player_number

    def get_square(self, location):
        """
        Returns the square at location.
        """
        return self._board.get_square(location)

    def verify_legality(self, word, location, direction):
        """
        Throws an IllegalMoveException if it is not legal to play word at location in direction given the AI's
        current hand. Has no effect otherwise. It is the AI's responsibility to call this before calling score
        or returning a move.
        """
        self._board.verify_legality(word, location, direction, self._board.get_hand(self._player_number))

    def score(self, word, location, direction):
        """
        Returns the score for playing word at location in direction. Assumes this is a legal play.
        """
        return self._board.score(word, location, direction)

    def get_hand(self):
        """
        Returns a copy of the AI's hand.
        """
        return self._board.get_hand(self._player_number)[:]

    def get_my_score(self):
        """
        Returns the score of the player associated with this GateKeeper.
        """
        return self._board.get_scores()[self._player_number]

    def get_opponent_score(self):
        """
        Returns the opponent's score.
        """
        return self._board.get_scores()[1 - self._player_number]

    def get_bag_count(self):
        """
        Returns the number of tiles left in the bag.
        """
        return self._board.get_bag_count()

    def get_opponent_hand_size(self):
        """
        Returns the number of tiles left in the opponent's hand.
        """
        return len(self._board.get_hand(1 - self._player_number))

    def __str__(self):
        return str(self._board)
