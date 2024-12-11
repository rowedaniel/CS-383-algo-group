from location import *
from board import *
from move import *
from collections import Counter

ALL_TILES = [True] * 7

#bugs: doesn't handle the case of having two blanks in hand.

class Incrementalist:
    """
    Maybe slightly less dumb AI.
    """

    def __init__(self):
        self._gatekeeper = None

    def set_gatekeeper(self, gatekeeper):
        self._gatekeeper = gatekeeper
    def load_words(self, filename="words.txt"):
        with open(filename, "r") as file:
            return {line.strip().lower() for line in file}

    #Counter method from collections module helps. hopefully i can use it
    #i suspect considering even one wildcard slows considerably. I won't support the bot considering two wildcards
    #for the same reason, except it also just seems strategically wrong to use two wildcards in a turn.
    def get_valid_words(self, hand, words_list, board_tiles):
        lower_only = [letter for letter in hand if not letter.isupper()]
        hand = ''.join(hand)
        board_tiles = ''.join(board_tiles)
        hand_count = Counter(hand.lower())
        board_count = Counter(board_tiles.lower())
        valid_words = []
        for word in words_list:
            word_count = Counter(word)
            #number of occurrences of each letter in word
            combined_count = hand_count + board_count

            #check if word can be formed with letters in hand
            if all(word_count[letter] <= combined_count.get(letter, 0) for letter in word_count):
                #for wildcard purposes, recapitalize any letters in word that werent in lowercase when passed
                recapitalized_word=[]
                for letter in word:
                    if letter.lower() not in lower_only:
                        recapitalized_word.append(letter.upper())
                    else:
                        recapitalized_word.append(letter)
                recapitalized_word = ''.join(recapitalized_word)

                #check that the word contains a letter from the board, but ignore this if its the first move
                if self._gatekeeper.get_square(CENTER) == DOUBLE_WORD_SCORE:
                    valid_words.append(recapitalized_word)
                else:
                    if any(letter in board_count for letter in word):
                        valid_words.append(recapitalized_word)
        return valid_words

    def choose_move(self):
        print(self._gatekeeper.get_last_move())
        hand = self._gatekeeper.get_hand()
        board_info = self.get_board_tiles()
        words = self.load_words("words.txt")
        valid_words=self.get_valid_words(hand, words, board_info[0])
        if "_" in hand:
            for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                replaced_hand = [letter if tile == "_" else tile for tile in hand]
                valid_words.extend(self.get_valid_words(replaced_hand, words, board_info[0]))
        return self.find_best_move(valid_words, board_info[1])

    def find_best_move(self, words, empty_locations):
        best_word = None
        best_score = -1
        best_location = None
        best_direction = None
        #filter out words of nonetype because i was getting some that were for some reason
        words = [x for x in words if x is not None]
        #for each legitimate word:
        for word in words:
            #for each unoccupied location:
            for location in empty_locations:
                #for each direction:
                for direction in HORIZONTAL, VERTICAL:
                    try:
                        self._gatekeeper.verify_legality(word,location,direction)
                        score = self._gatekeeper.score(word,location,direction)
                        #print("valid word found: ", word, " at location ", location, " in direction ", " with score of ", score)
                        if score > best_score:
                            best_score = score
                            best_word = word
                            best_location = location
                            best_direction = direction
                    except:
                        pass
        #could optimize by only checking locations where it's possible to play out that far from the boardspace.
        if best_word is None:
            return ExchangeTiles(ALL_TILES)

        return PlayWord(best_word, best_location, best_direction)

    #not the best name because this also returns the empty positions.
    def get_board_tiles(self):
        board_tiles=[]
        empty_positions=[]
        for row in range(15):
            for col in range(15):
                square = self._gatekeeper.get_square(Location(row, col))
                if square.isalpha():
                    board_tiles.append(square)
                else:
                    empty_positions.append(Location(row, col))


        return board_tiles, empty_positions

