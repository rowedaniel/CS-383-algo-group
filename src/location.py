class Location:
    def __init__(self, r, c):
        self.r = r
        self.c = c

    def __add__(self, other):
        return Location(self.r + other.r, self.c + other.c)

    def __sub__(self, other):
        return Location(self.r - other.r, self.c - other.c)

    def is_on_board(self):
        return 0 <= self.r < WIDTH and 0 <= self.c < WIDTH

    def __eq__(self, other):
        return self.r == other.r and self.c == other.c

    def __str__(self):
        return f'<{self.r}, {self.c}>'

    def __repr__(self):
        return self.__str__()

    def orthogonal(self):
        """
        Returns the direction orthogonal to this one. HORIZONTAL and VERTICAL are orthogonal.
        """
        if self == HORIZONTAL:
            return VERTICAL
        return HORIZONTAL


# Width of the board
WIDTH = 15

# Adding this to a location moves one space right
HORIZONTAL = Location(0, 1)


# Adding this to a location moves one space left
VERTICAL = Location(1, 0)


# Center of the board
CENTER = Location(7, 7)
