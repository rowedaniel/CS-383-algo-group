from graph import Graph
import random


class Electorate:
    def __init__(self, districts):
        self.graph = Graph(districts ** 2)
        self._add_edges()
        self.votes = [random.random() > 0.5 for _ in range(self.number_of_voters())]

    def _add_edges(self):
        v = self.number_of_voters()
        d = self.district_size()  # This is also the number of districts
        for r in range(d):
            for c in range(d):
                i = r * d + c
                if c < d - 1:
                    self.graph.add_edge(i, i + 1)  # Edge to right
                if r < d - 1:
                    if r % 2 == 0:  # Even row
                        if c > 0:
                            self.graph.add_edge(i, i + d - 1)  # Edge to lower left
                        self.graph.add_edge(i, i + d)  # Edge to lower right
                    else:  # Odd row
                        self.graph.add_edge(i, i + d)  # Edge to lower left
                        if c < d - 1:
                            self.graph.add_edge(i, i + d + 1)  # Edge to lower right

    def number_of_voters(self):
        return len(self.graph.adj)

    def district_size(self):  # This is also the number of districts
        return int(self.number_of_voters() ** 0.5)

    def graph_with_only_within_district_edges(self, districts):
        g = Graph(self.number_of_voters())
        d = self.district_size()
        for district in districts:
            for i in range(d):
                for j in range(i + 1, d):
                    if district[j] in self.graph.neighbors(district[i]):
                        g.add_edge(district[i], district[j])
        return g

    def _number_of_connected_components(self, g):
        def dfs(i):
            found[i] = True
            for j in g.neighbors(i):
                if not found[j]:
                    dfs(j)
        v = self.number_of_voters()
        found = [False] * v
        result = 0
        for i in range(v):
            if not found[i]:
                dfs(i)
                result += 1
        return result

    def is_valid_map(self, districts):
        v = self.number_of_voters()
        district_size = self.district_size()
        sum = 0
        counted = [False] * v
        for district in districts:
            if len(district) != district_size:
                return False  # District is wrong size
            for voter in district:
                if not (0 <= voter <= v):
                    return False  # Invalid voter
                if counted[voter]:
                    return False  # Voter already assigned to another district
                counted[voter] = True
                sum += 1
        if sum != v:
            return False  # Not enough voters counted
        g = self.graph_with_only_within_district_edges(districts)
        if self._number_of_connected_components(g) != district_size:
            return False  # Wrong number of districts or noncontiguous districts
        return True

    def get_wins(self, districts, party):
        """
        Returns the number of districts won by party.
        """
        result = 0
        district_size = self.district_size()
        for d in districts:
            if sum(self.votes[i] == party for i in d) > district_size / 2:
                result += 1
        return result
