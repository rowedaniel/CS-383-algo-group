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

    # def get_wins(self, groups, party):
    #     district_size = len(groups[0])  # assuming all groups are the same size
    #     for d in groups:
    #         # Check if all indices in the district are valid
    #         for i in d:
    #             if i >= len(self.votes):
    #                 print(f'self.votes: {self.votes}')
    #                 print(f'self.graph.adj: {self.graph.adj}')
    #                 print(d)
    #                 print(f"Index {i} is out of bounds for self.votes (vote list size: {len(self.votes)})")
    #                 continue  # or handle the error by skipping this district
    #         if sum(self.votes[i] == party for i in d) > district_size / 2:
    #             return True
    #     return False


if __name__ == "__main__":

    e = Electorate(9)
    print(e.get_wins([[0, 9, 18, 19, 28, 27, 36, 37, 38], [1, 10, 11, 12, 21, 22, 31, 32, 41], [2, 3, 4, 13, 14, 23, 24, 33, 42], [5, 6, 15, 16, 7, 8, 17, 26, 25], [20, 29, 30, 39, 48, 47, 46, 45, 54], [34, 43, 52, 51, 60, 61, 70, 69, 68], [40, 49, 50, 59, 58, 67, 66, 75, 76], [35, 44, 53, 62, 71, 80, 79, 78, 77], [55, 64, 63, 72, 73, 74, 65, 56, 57]], True))