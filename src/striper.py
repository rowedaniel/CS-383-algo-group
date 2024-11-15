class Striper:


    def gerrymander(self, electorate, party):
        d = electorate.district_size()
        if party:
            return [list(range(d * i, d * ( i + 1))) for i in range(d)]
        else:
            return [list(range(i, d * d, d)) for i in range(d)]

