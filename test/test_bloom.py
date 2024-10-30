import pytest
from bloom import BloomFilter

with open('resources/bad.txt', 'r') as file:
    BAD = [line.rstrip() for line in file]

with open('resources/good.txt', 'r') as file:
    GOOD = [line.rstrip() for line in file]


@pytest.fixture
def filter_():  # This is run for each test
    yield BloomFilter() # The test is run here


def test_key_is_not_initially_present(filter_):
    assert not filter_.might_contain('badplace.com')


def test_adds_key(filter_):
    filter_.add('badplace.com')
    assert filter_.might_contain('badplace.com')


def test_add_sets_two_bits(filter_):
    assert filter_._true_bits() == 0
    filter_.add('badplace.com')
    assert filter_._true_bits() == 2
    filter_.add('awfulplace.com')
    # NOTE: This test will very rarely fail by coincidence
    assert filter_._true_bits() == 4


def test_add_does_not_add_another_item(filter_):
    filter_.add('badplace.com')
    assert not filter_.might_contain('goodplace.com')


def test_adds_all_entries(filter_):
    for domain in BAD:
        filter_.add(domain)
    for domain in BAD:
        assert filter_.might_contain(domain)


def test_false_positive_rate_is_low(filter_):
    for domain in BAD:
        filter_.add(domain)
    # Using the built-in filter function to find the elements of GOOD for which might_contain is True
    # NOTE: This test will very rarely fail by coincidence
    assert len(list(filter(filter_.might_contain, GOOD))) < 0.01 * len(GOOD)
