import pytest
from electorate import Electorate


@pytest.fixture
def electorate():  # This is run for each test
    yield Electorate(3) # The test is run here


def test_accepts_valid_horizontal_map(electorate):
    assert electorate.is_valid_map([[0, 1, 2], [3, 4, 5], [6, 7, 8]])


def test_accepts_valid_vertical_map(electorate):
    assert electorate.is_valid_map([[0, 3, 6], [1, 4, 7], [2, 5, 8]])


def test_rejects_map_with_too_many_voters(electorate):
    assert not electorate.is_valid_map([[0, 1, 2, 9], [3, 4, 5, 10], [6, 7, 8, 11]])


def test_rejects_map_with_voter_in_more_than_one_district(electorate):
    assert not electorate.is_valid_map([[0, 1, 2], [0, 1, 2], [0, 1, 2]])


def test_rejects_map_that_omits_voter(electorate):
    assert not electorate.is_valid_map([[0, 1], [3, 4], [6, 7]])


def test_rejects_map_with_noncontiguous_district(electorate):
    assert not electorate.is_valid_map([[1, 2, 5], [0, 4, 8], [3, 6, 7]])


def test_rejects_map_with_too_many_districts(electorate):
    assert not electorate.is_valid_map([[i] for i in range(9)])


def test_rejects_map_with_too_few_districts(electorate):
    assert not electorate.is_valid_map([list(range(9))])


def test_rejects_map_with_uneven_districts(electorate):
    assert not electorate.is_valid_map([[0, 1], [2, 3, 4, 5], [6, 7, 8]])
