class BloomFilter:

    def __init__(self):
        self._bits = 0

    def _hashes(self, key: str) -> list[int]:
        """
        Return a list of hash values (one for each hash algorithm).
        For this implementation, we only return 2 values
        """
        h = abs(hash(key)) % (2**32) # 32-bit int

        # TODO: split into lower 16 bits and higher 16 bits
        lower = 0
        highter = 0
        return [lower, highter]

    def add(self, key: str):
        """
        Add 'key' to the filter
        """

        for h in self._hashes(key):
            pass
            # TODO: implement.
            # should look like:
            # self._bits[h] = True
            # but using a bitvector rather than an array

    def _true_bits(self) -> int:
        """
        Count the number of 1's in the bitvector
        """
        count = 0
        bits = self._bits
        while bits:
            count += bits & 1 # pick out only the rightmost bit
            bits >>= 1
        return count

    def might_contain(self, key: str) -> bool:
        """
        Return whether 'key' is in the filter.
        Might return a false positive, but not a false negative.
        i.e. False indicates 'definitely not in the filter',
        while True indicates 'probably in the filter'.
        """
        for h in self._hashes(key):
            pass
            # TODO: implement.
            # should look like:
            # if not self._bits[h]:
            #     return False # not all the necessary bits were flipped, so definitely not in the filter
        return True

