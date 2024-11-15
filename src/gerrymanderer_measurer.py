from electorate import Electorate


def measure(d, n, gerrymanderer):
    """
    Returns the average measurement over n d * d electorates
    :param d: Number of districts (and also number of voters per district)
    :param n: Number of simulations to run
    :param gerrymanderer: An object with a gerrymander method
    :return: A number between 0.0 (losing every district) and 1.0 (winning every district).
    """
    sum = 0
    for i in range(n):
        e = Electorate(d)
        for party in [False, True]:
            districts = gerrymanderer.gerrymander(e, party)
            if not e.is_valid_map(districts):
                raise ValueError('Invalid districts')
            sum += e.get_wins(districts, party)
    return sum / (d * 2 * n)


from striper import Striper

print(measure(9, 100, Striper()))
