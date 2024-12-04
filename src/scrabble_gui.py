import string
from tkinter import *

from gatekeeper import GateKeeper
from incrementalist import Incrementalist
from location import *
from board import *
from enum import Enum


def rgb_to_hex(r, g, b):
    """
    From https://stackoverflow.com/a/65983607
    """
    return f'#{r:X}{g:X}{b:X}'


TABLE_COLOR = rgb_to_hex(24, 64, 35)
TILE_COLOR = rgb_to_hex(251, 224, 174)
SHADED_TILE_COLOR = rgb_to_hex(125, 112, 87)

# Colors extracted from https://www.vecteezy.com/vector-art/90549-scrabble-board-free-vector
COLORS = {NO_PREMIUM:rgb_to_hex(226, 206, 177),
          DOUBLE_LETTER_SCORE:rgb_to_hex(185, 202, 206),
          TRIPLE_LETTER_SCORE:rgb_to_hex(67, 162, 198),
          DOUBLE_WORD_SCORE:rgb_to_hex(205, 176, 180),
          TRIPLE_WORD_SCORE:rgb_to_hex(200, 130, 142)}


def color_tiles():
    for letter in string.ascii_lowercase + string.ascii_uppercase + '_':
        COLORS[letter] = TILE_COLOR


color_tiles()

SQUARE_WIDTH = 30

class Mode(Enum):
    BOARD = 0,  # Waiting for user to play a word on the board
    HAND = 1,  # Waiting for user to select tiles (if any) to exchange
    ILLEGAL_MOVE = 2,  # Waiting for user to acknowledge an illegal move
    AI_PLAYING = 3,  # Waiting for AI to play
    GAME_OVER = 4  # Game over

class Scrabble:
    def __init__(self):
        self.board = Board()
        self.mode = Mode.AI_PLAYING
        self.ai = Incrementalist()
        self.ai.set_gatekeeper(GateKeeper(self.board, 0))
        self.created = [[False for _ in range(WIDTH)] for _ in range(WIDTH)]
        self.cursor_position = CENTER
        self.cursor_direction = VERTICAL
        self.word_being_constructed = ''
        self.hand_cursor = 0
        self.tiles_to_discard = [False] * 7
        self.root = Tk()
        self.root.title('Scrabble')
        self.root['bg'] = TABLE_COLOR
        self.canvas = Canvas(self.root, width=450, height=450, bg=TABLE_COLOR, highlightthickness=0)
        self.canvas.pack(side=LEFT, padx=10, pady=10)
        self.squares = self._create_squares()
        self.cursor = None
        self.right_frame = Frame(bg=TABLE_COLOR)
        self.right_frame.pack(side=LEFT, padx=10, pady=10, fill=Y, expand=1)
        self.opponent_rack, self.opponent_tiles, _, _ = self._create_hand(True)
        self.opponent_label = self._create_label('Opponent: 0', 0)
        self._create_label('', 0)
        self.user_rack, self.user_tiles, self.user_letters, self.user_letter_points = self._create_hand(False)
        self.user_label = self._create_label('You: 0', 0)
        self._create_label('', 0)
        self.entry_label = self._create_label('[]', 0)
        self.instructions = self._create_message('These are the instructions.\nFollow them.', 1)
        self._play_ai_move()
        self.root.bind_all('<KeyPress>', lambda e: self._handle_key_press(e.char))
        # You'd think you could do these in a loop, but the putting a loop variable inside a lambda causes problems
        self.root.bind('<Left>', lambda e: self._handle_key_press('<Left>'))
        self.root.bind('<Right>', lambda e: self._handle_key_press('<Right>'))
        self.root.bind('<Up>', lambda e: self._handle_key_press('<Up>'))
        self.root.bind('<Down>', lambda e: self._handle_key_press('<Down>'))
        self.root.bind('<BackSpace>', lambda e: self._handle_key_press('<BackSpace>'))
        self.root.bind('<Return>', lambda e: self._handle_key_press('<Return>'))
        self.root.bind('<Control_L>', lambda e: self._handle_key_press('<Control>'))
        self.root.bind('<Control_R>', lambda e: self._handle_key_press('<Control>'))
        self.root.mainloop()

    def _create_squares(self):
        grid = [[None for _ in range(WIDTH)] for _ in range(WIDTH)]
        for r in range(WIDTH):
            for c in range(WIDTH):
                grid[r][c] = self.canvas.create_rectangle(c * SQUARE_WIDTH,
                                                          r * SQUARE_WIDTH,
                                                          c * SQUARE_WIDTH + (SQUARE_WIDTH - 1),
                                                          r * SQUARE_WIDTH + (SQUARE_WIDTH - 1),
                                                          fill=COLORS[self.board.get_square(Location(r, c))],
                                                          outline='white')
        return grid

    def _create_hand(self, face_down):
        rack = Canvas(self.right_frame, width=SQUARE_WIDTH * 7, height=SQUARE_WIDTH, bg=TABLE_COLOR, highlightthickness=0)
        rack.pack(side=TOP)
        tiles = [None for _ in range(7)]
        letters = [None for _ in range(7)]
        letter_points = [None for _ in range(7)]
        for c in range(7):
            tiles[c], letters[c], letter_points[c] = self._create_tile('x', face_down, rack, c * SQUARE_WIDTH, 0)
        return rack, tiles, letters, letter_points

    def _create_tile(self, letter, face_down, canvas, x, y):
        tile = canvas.create_rectangle(x, y, x + (SQUARE_WIDTH - 1), y + SQUARE_WIDTH - 1,
                                         fill=COLORS[letter], outline='black')
        letter_points = TILE_VALUES[letter]
        if not face_down:
            if letter.isupper():
                letter = canvas.create_text(x + (SQUARE_WIDTH // 2), y + SQUARE_WIDTH * 4 // 9, text=letter,
                                            fill='red', font=('Arial', 12))
                letter_points = None
            else:
                letter = canvas.create_text(x + (SQUARE_WIDTH // 2), y + SQUARE_WIDTH * 4 // 9, text=letter.upper(),
                                            fill='black', font=('Arial', 12))
                letter_points = canvas.create_text(x + SQUARE_WIDTH * 4 // 5, y + SQUARE_WIDTH * 4 // 5,
                                                   text=letter_points, fill='black', font=('Arial', 7))
        return tile, letter, letter_points

    def _create_label(self, text, expand):
        label = Label(self.right_frame, text=text, background=TABLE_COLOR, foreground='white')
        label.pack(side=TOP, fill=Y, expand=expand)
        return label

    def _create_message(self, text, expand):
        message = Message(self.right_frame, text=text, background=TABLE_COLOR, foreground='white', width=SQUARE_WIDTH * 7)
        message.pack(side=TOP, fill=Y, expand=expand)
        return message

    def _update_cursor(self):
        if self.cursor:
            self.canvas.delete(self.cursor)
        if self.mode == Mode.BOARD:
            # Center of shape
            x = self.cursor_position.c * SQUARE_WIDTH + (SQUARE_WIDTH // 2)
            y = self.cursor_position.r * SQUARE_WIDTH + (SQUARE_WIDTH // 2)
            e = SQUARE_WIDTH // 5
            if self.cursor_direction == HORIZONTAL:
                points = [(x - 2 * e, y - e), (x + 2 * e, y), (x - 2 * e, y + e)]
            else:
                points = [(x - e, y - 2 * e), (x + e, y - 2 * e), (x, y + 2 * e)]
            self.cursor = self.canvas.create_polygon(points, outline='black', fill='white')

    def _handle_key_press(self, key):
        if self.mode == Mode.BOARD:
            # Toggle board cursor direction
            if key == '/':
                self.cursor_direction = self.cursor_direction.orthogonal()
                self._update_cursor()
            # Move board cursor
            next_ = None
            if key == '<Left>':
                next_ = self.cursor_position - HORIZONTAL
            elif key == '<Right>':
                next_ = self.cursor_position + HORIZONTAL
            elif key == '<Up>':
                next_ = self.cursor_position - VERTICAL
            elif key == '<Down>':
                next_ = self.cursor_position + VERTICAL
            if next_ and next_.is_on_board():
                self.cursor_position = next_
            # Type in word to be played
            elif key.isalpha() or key == ' ':
                self.word_being_constructed += key
            elif key == '<BackSpace>' and self.word_being_constructed:
                self.word_being_constructed = self.word_being_constructed[:-1]
            # Play word
            elif key == '<Return>':
                try:
                    self.board.play(self.word_being_constructed,
                                    self.cursor_position,
                                    self.cursor_direction,
                                    self.board.get_hand(1))
                    if self.board.game_is_over():
                        self.mode = Mode.GAME_OVER
                    else:
                        self._play_ai_move()
                except ValueError as e:
                    self.instructions.configure(text='Illegal move:\n\n' +
                                                str(e) + '\n\n'
                                                'Hit enter to continue')
                    self.mode = Mode.ILLEGAL_MOVE
            # Switch to hand mode
            elif key == '<Control>':
                self.mode = Mode.HAND
                self.hand_cursor = 0
                self.tiles_to_discard = [False] * 7
        elif self.mode == Mode.HAND:
            if key == '<Control>':
                self._enter_board_mode()
            elif key == '<Left>':
                self.hand_cursor = max(0, self.hand_cursor - 1)
            elif key == '<Right>':
                self.hand_cursor = min(len(self.board.get_hand(1)) - 1, self.hand_cursor + 1)
            elif key == ' ':
                self.tiles_to_discard[self.hand_cursor] = not self.tiles_to_discard[self.hand_cursor]
            elif key == '<Return>':
                self.board.exchange(self.board.get_hand(1), self.tiles_to_discard)
                if self.board.game_is_over():
                    self.mode = Mode.GAME_OVER
                else:
                    self._play_ai_move()
        elif self.mode == Mode.ILLEGAL_MOVE:
            if key == '<Return>':
                self._enter_board_mode()
        self._update()

    def _update(self):
        # Board tiles
        for r in range(WIDTH):
            for c in range(WIDTH):
                tile = self.board.get_square(Location(r, c))
                if tile.isalpha() and not self.created[r][c]:
                    self._create_tile(tile, False, self.canvas, c * SQUARE_WIDTH, r * SQUARE_WIDTH)
                    self.created[r][c] = True
        # Cursor
        self._update_cursor()
        # Opponent's tiles
        hand = self.board.get_hand(0)
        for i, t in enumerate(self.opponent_tiles):
            if i >= len(hand):
                self.opponent_rack.delete(t)
        # User's tiles
        hand = self.board.get_hand(1)
        for i, t in enumerate(self.user_tiles):
            if i >= len(hand):
                self.user_rack.delete(t)
                self.user_rack.delete(self.user_letters[i])
                self.user_rack.delete(self.user_letter_points[i])
            else:
                self._update_tile(hand, i)
        # Scores
        self.opponent_label.configure(text=f'Opponent: {self.board.get_scores()[0]}')
        self.user_label.configure(text=f'You: {self.board.get_scores()[1]}')
        # Instructions
        if self.mode == Mode.BOARD:
            self.entry_label.configure(text=f'[{self.word_being_constructed}]')
            self.instructions.configure(text='Type a word and hit enter to play.\n\n'
                                        'Use spaces for tiles already on board, '
                                        'an upper-case letter to play a blank.\n\n'
                                        'Use arrow keys to move cursor, '
                                        '/ to toggle direction.\n\n'
                                        'Use ctrl to exchange letters or pass.')
        elif self.mode == Mode.HAND:
            self.instructions.configure(text='Use arrow keys to move in hand.\n\n'
                                        'Space to mark/unmark tile.\n\n'
                                        'Enter to exchange marked tiles.\n\n'
                                        'Use ctrl to return to board.')
        elif self.mode == Mode.ILLEGAL_MOVE:
            pass  # Instructions were updated when the illegal move was played
        elif self.mode == Mode.GAME_OVER:
            self.instructions.configure(text='Game over.')
        elif self.mode == Mode.AI_PLAYING:
            self.instructions.configure(text='Opponent thinking...')

    def _update_tile(self, hand, i):
        letter_text = self.user_letters[i]
        points_text = self.user_letter_points[i]
        letter = hand[i]
        points = TILE_VALUES[letter]
        if letter == '_':
            letter = ''
            points = ''
        self.user_rack.itemconfig(points_text, text=points)
        self.user_rack.itemconfig(letter_text, text=letter.upper())
        if self.mode == Mode.HAND:
            if i == self.hand_cursor:
                self.user_rack.itemconfig(self.user_tiles[i], outline='white')
            else:
                self.user_rack.itemconfig(self.user_tiles[i], outline='black')
            if self.tiles_to_discard[i]:
                self.user_rack.itemconfig(self.user_tiles[i], fill=SHADED_TILE_COLOR)
            else:
                self.user_rack.itemconfig(self.user_tiles[i], fill=TILE_COLOR)
        else:
            self.user_rack.itemconfig(self.user_tiles[i], fill=TILE_COLOR)

    def _play_ai_move(self):
        self.mode = Mode.AI_PLAYING
        self._update()
        move = self.ai.choose_move()
        place = move.play(self.board, 0)
        if place:
            self.cursor_position, self.cursor_direction = place
        if self.board.game_is_over():
            self.mode = Mode.GAME_OVER
        else:
            self._enter_board_mode()
        self._update()

    def _enter_board_mode(self):
        self.mode = Mode.BOARD
        self.word_being_constructed = ''


Scrabble()
quit()
