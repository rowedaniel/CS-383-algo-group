from fingerprint_match import match
from random import randint

def random_dense_array(n):
    return [[randint(0, (1 << 32) - 1) for _ in range(n)] for _ in range(n)]

def random_sparse_array(n):
    result = [[0] * n for _ in range(n)]
    result[randint(0, n - 1)][randint(0, n - 1)] = randint(0, (1 << 32) - 1)
    return result

def overwrite(pattern, text, i, j):
    m = len(pattern)
    for a in range(m):
        for b in range(m):
            text[a + i][b + j] = pattern[a][b]

def finds_match(m, n, dense):
    """
    Creates a random m x m pattern and a random n x n text in which the pattern appears.
    Returns True if match can find the match.
    :param dense: If True, the pattern and text each have only one nonzero element.
    """
    if dense:
        pattern = random_dense_array(m)
        text = random_dense_array(n)
    else:
        pattern = random_sparse_array(m)
        text = [[0] * n for _ in range(n)]
    i = randint(0, n - m)
    j = randint(0, n - m)
    overwrite(pattern, text, i, j)
    assert match(pattern, text) == (i, j)

def test_finds_small_matches_in_dense_arrays():
    for _ in range(10):
        finds_match(2, 3, True)

def test_finds_large_matches_in_dense_arrays():
    for _ in range(10):
        finds_match(50, 200, True)

def test_finds_small_matches_in_sparse_arrays():
    for _ in range(10):
        finds_match(3, 10, False)

def test_finds_large_matches_in_sparse_arrays():
    for _ in range(10):
        finds_match(50, 200, False)

def test_finds_nonmatches():
    for _ in range(10):
        assert match(random_dense_array(3), random_sparse_array(10)) is None
