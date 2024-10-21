class BloomFilter:

    def __init__(self):
        self._bits = 0

    def _hashes(self, key: str) -> list[int]:
        """
        Return a list of hash values (one for each hash algorithm).
        For this implementation, we only return 2 values
        """
        h = abs(hash(key)) % (2**32) # 32-bit int

        
        lower = h % (2**16)
        higher = (h >> 16) % (2**16)
        return [lower, higher]

    def add(self, key: str):
        """
        Add 'key' to the filter
        """

        for h in self._hashes(key):
            self._bits = self._bits | (1<<h)

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
            if not(self._bits & (1<<h)):
                return False
        return True
