import random
import os
from location import CENTER

# Constants about the board representation
DOUBLE_LETTER_SCORE = '-'
TRIPLE_LETTER_SCORE = '='
DOUBLE_WORD_SCORE = '+'
TRIPLE_WORD_SCORE = '#'
NO_PREMIUM = ' '
LAYOUT = ('#  -   #   -  #',
          ' +   =   =   + ',
          '  +   - -   +  ',
          '-  +   -   +  -',
          '    +     +    ',
          ' =   =   =   = ',
          '  -   - -   -  ',
          '#  -   +   -  #',
          '  -   - -   -  ',
          ' =   =   =   = ',
          '    +     +    ',
          '-  +   -   +  -',
          '  +   - -   +  ',
          ' +   =   =   + ',
          '#  -   #   -  #')


# Values of tiles
TILE_VALUES = {}


def set_tile_values():
    for letters, value in {'eaionrtlsu': 1,
                           'dg': 2,
                           'bcmp': 3,
                           'fhvwy': 4,
                           'k': 5,
                           'xj': 8,
                           'qz': 10,
                           'ABCDEFGHIJKLMNOPQRSTUVWXYZ': 0,
                           '_': 0}.items():
        for letter in letters:
            TILE_VALUES[letter] = value
# Why create a function we're only calling once? Because doing the work directly at the top level pollutes the global
# namespace.
set_tile_values()


# The dictionary of legal words
current_dir = os.path.dirname(__file__)  # Current working directory, necessary for this to run when imported into a test
with open(os.path.join(current_dir, 'words.txt')) as file:
    DICTIONARY = set(word.strip() for word in file)


class Board:
    """
    Scrabble board, maintaining bag, players' hands, and other game logic.

    General conventions:

    Each square is either a lower-case letter (a regular tile), an upper-case letter (a played blank), or a symbol.
    Each bag/hand tile is either a lower-case letter (a regular tile) or _ (an unplayed blank).
    Words submitted consist of letters (upper-case for played blanks) and spaces (existing tiles on the board).
    """
    def __init__(self):
        self._squares = [[square for square in row] for row in LAYOUT]
        self._bag = list('aaaaaaaaabbccddddeeeeeeeeeeeeffggghhiiiiiiiiijkllllmmnnnnnnooooooooppqrrrrrrssssttttttuuuuvvwwxyyz__')
        random.shuffle(self._bag)
        self._hands = [[], []]
        self._deal(self._hands[0], 7)
        self._deal(self._hands[1], 7)
        self._scores = [0, 0]
        self._current_player = 0
        self._number_of_passes = 0

    def _deal(self, hand, n):
        """
        Deals n tiles from the bag into hand.
        """
        for i in range(n):
            if not self._bag:  # Bag is empty!
                return
            hand.append(self._bag.pop())

    def __str__(self):
        return '\n'.join(''.join(row) for row in self._squares)

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def can_be_drawn_from_hand(word, hand):
        """
        Returns true if word can be played from the tiles available in hand.
        """
        used = [False] * len(hand)
        for letter in word:
            if letter == ' ':
                continue
            found = False
            for i, tile in enumerate(hand):
                if (not used[i]) and ((letter == tile) or (letter.isupper() and tile == '_')):
                    used[i] = True
                    found = True
                    break
            if not found:
                return False
        return True

    def can_be_placed_on_board(self, word, location, direction):
        """
        Returns true if word can be placed on board, in the sence of not overlapping existing tiles, leaving no gaps,
        having no tiles right before or after it, and not extending beyond the edge of the board.
        """
        before = location - direction
        if before.is_on_board() and self.is_occupied(before):
            return False  # Tile right before word starts
        for letter in word:
            if not location.is_on_board():
                return False  # Off edge of board
            current = self.get_square(location)
            if (letter == ' ') != current.isalpha():
                return False  # Tile played on top of existing tile, or gap in word where there is no tile
            location += direction
        if location.is_on_board() and self.is_occupied(location):
            return False  # Tile right after word ends
        return True

    def get_scores(self):
        """
        Returns the scores of the two players
        """
        return self._scores

    def get_bag_count(self):
        """
        Returns the number of tiles left in the bag.
        """
        return len(self._bag)

    def get_square(self, location):
        return self._squares[location.r][location.c]

    def is_occupied(self, location):
        return self.get_square(location).isalpha()

    def _set_square(self, tile, location):
        self._squares[location.r][location.c] = tile

    def place_word(self, word, location, direction):
        for letter in word:
            if letter != ' ':
                self._set_square(letter, location)
            location += direction

    def would_be_connected(self, word, location, direction):
        """
        Returns True if word, placed at location in direction, would be connected. In other words, word must contain
        an existing tile, be beside an existing tile, or contain the center.
        """
        cross = direction.orthogonal()
        for letter in word:
            if letter == '':
                return True  # Contains a played tile
            if location == CENTER:
                return True  # Contains center
            for neighbor in location + cross, location - cross:
                if neighbor.is_on_board() and self.is_occupied(neighbor):
                    return True  # Letter next to word on one side
            location += direction
        return False

    def is_valid_word(self, word, location, direction):
        """
        Returns true if word, played at location in direction, forms a valid dictionary word of at least two letters.
        """
        if len(word) < 2:
            return False
        letters = ''
        for letter in word:
            if self.is_occupied(location):
                letters += self.get_square(location)
            else:
                letters += letter
            location += direction
        return letters.lower() in DICTIONARY

    def is_valid_cross_word(self, tile, location, direction):
        """
        Returns true if the cross word including location forms a valid dictionary word, or no new cross word is formed.
        """
        if tile == ' ':
            return True  # Word was already on board
        location = self.find_start_of_word(location, direction)
        word = ''
        tile_used = False
        while location.is_on_board():
            if self.is_occupied(location):
                word += self.get_square(location)
            elif tile_used:
                break  # Reached end of cross word
            else:
                word += tile
                tile_used = True
            location += direction
        if len(word) == 1:
            return True  # No cross word here
        return word.lower() in DICTIONARY

    def would_create_only_legal_words(self, word, location, direction):
        """
        Returns true if word, played at location in direction, would create only legal words.
        """
        if not self.is_valid_word(word, location, direction):
            return False
        cross = direction.orthogonal()
        for letter in word:
            if not self.is_valid_cross_word(letter, location, cross):
                return False
            location += direction
        return True

    def find_start_of_word(self, location, direction):
        """
        Returns the location of the first tile in a (cross) word that includes location and moves in direction.
        """
        while True:
            location -= direction
            if not (location.is_on_board() and self.is_occupied(location)):
                return location + direction

    def score_cross_word(self, tile, location, direction):
        """
        Returns the score for the cross word in direction including (but not necessarily starting with) tile played
        at location.
        """
        score = 0
        multiplier = 1
        location = self.find_start_of_word(location, direction)
        if (location + direction).is_on_board() and not self.is_occupied(location + direction):
            return 0  # One letter "cross word"
        tile_used = False
        while location.is_on_board():
            square = self.get_square(location)
            if self.is_occupied(location):
                score += TILE_VALUES[square]
            elif tile_used:
                break  # End of cross word
            else:
                score += TILE_VALUES[tile]
                bonus = self.get_square(location)
                if bonus == DOUBLE_LETTER_SCORE:
                    score += TILE_VALUES[tile]
                elif bonus == TRIPLE_LETTER_SCORE:
                    score += 2 * TILE_VALUES[tile]
                elif bonus == DOUBLE_WORD_SCORE:
                    multiplier *= 2
                elif bonus == TRIPLE_LETTER_SCORE:
                    multiplier *= 3
                tile_used = True
            location += direction
        return score * multiplier

    def score_word(self, word, location, direction):
        """
        Returns the points score for word, played at location in direction.
        """
        score = 0
        multiplier = 1
        for tile in word:
            square = self.get_square(location)
            if tile == ' ':
                score += TILE_VALUES[square]
            else:
                score += TILE_VALUES[tile]
                if square == DOUBLE_LETTER_SCORE:
                    score += TILE_VALUES[tile]
                elif square == TRIPLE_LETTER_SCORE:
                    score += 2 * TILE_VALUES[tile]
                elif square == DOUBLE_WORD_SCORE:
                    multiplier *= 2
                elif square == TRIPLE_WORD_SCORE:
                    multiplier *= 3
            location += direction
        return score * multiplier

    def score(self, word, location, direction):
        """
        Returns the score for playing word at location in direction, including any cross words.
        """
        score = self.score_word(word, location, direction)
        tiles_played = 0
        for tile in word:
            if tile != ' ':
                score += self.score_cross_word(tile, location, direction.orthogonal())
                tiles_played += 1
            location += direction
        if tiles_played == 7:
            score += 50
        return score

    def verify_legality(self, word, location, direction, hand):
        """
        Throws a ValueError if playing word at location in direction from hand would not be legal.
        """
        if len(word) < 2:
            raise ValueError('Word must be at least two letters long.')
        if all(tile == ' ' for tile in word):
            raise ValueError('Word must contain at least one new tile.')
        if not self.can_be_drawn_from_hand(word, hand):
            raise ValueError('Hand does not contains sufficient tiles to play word.')
        if not (self.can_be_placed_on_board(word, location, direction) and
            self.would_be_connected(word, location, direction)):
            raise ValueError('Board placement incorrect (gaps, overlapping tiles, edge of board).')
        if not self.would_create_only_legal_words(word, location, direction):
            raise ValueError('Invalid word created.')

    @staticmethod
    def remove_tiles(word, hand):
        """
        Removes the tiles used in word from and and returns them in a new str.
        """
        result = ''
        for tile in word:
            if 'A' <= tile <= 'Z':
                tile = '_'
            if tile != ' ':
                hand.remove(tile)
                result += tile
        return result

    def game_is_over(self):
        """
        Returns true if the game is over.
        """
        return self._number_of_passes == 2 or not all(self._hands)

    def _score_unplayed_tiles(self):
        """
        Scores any unplayed tiles at the end of the game.
        """
        values = [0, 0]
        for i, hand in enumerate(self._hands):
            for tile in hand:
                if tile not in TILE_VALUES:
                    print(f'{tile} is not in {TILE_VALUES}')
                values[i] += TILE_VALUES[tile]
        for i in range(2):
            self._scores[i] -= values[i]
            if not self._hands[i]:
                self._scores[i] += values[1 - i]

    def exchange(self, hand, tiles_to_exchange):
        """
        Exchanges 0 or more tiles from hand with the bag. Also toggles the current player and resolves the end of the
        game if applicable.
        :param tiles_to_exchange: An array of seven bools indicating which tiles to exchange. Any entries beyond the
        length of hand are ignored.
        """
        removed = [tile for i, tile in enumerate(hand) if tiles_to_exchange[i]]
        dumped = self.remove_tiles(removed, hand)
        self._deal(hand, 7 - len(hand))
        # Return dumped letters to bag
        for tile in dumped:
            self._bag.append(tile)
        random.shuffle(self._bag)
        # If there weren't enough tiles in bag, some dumped tiles may return to hand
        self._deal(hand, 7 - len(hand))
        self._current_player = 1 - self._current_player
        self._number_of_passes += 1
        if self.game_is_over():
            self._score_unplayed_tiles()

    def play(self, word, location, direction, hand):
        """
        Plays word at location in direction from hand. Also refills hand from bag, toggles the current player, and
        resolves the end of the game if applicable.
        """
        self.verify_legality(word, location, direction, hand)
        self._scores[self._current_player] += self.score(word, location, direction)
        self.place_word(word, location, direction)
        self.remove_tiles(word, hand)
        self._deal(hand, 7 - len(hand))
        self._current_player = 1 - self._current_player
        self._number_of_passes = 0
        if self.game_is_over():
            self._score_unplayed_tiles()

    def get_hand(self, player_number):
        return self._hands[player_number]
