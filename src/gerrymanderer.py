from electorate import Electorate

class Gerrymanderer:

    def __init__(self):
        # used for dynamic programming-style caching of which district a voter is in
        self.voter_district = {}
        self.districts = []
        self.num_voters = []

    def gerrymander(self, electorate: Electorate, party: bool):
        self.districts = self._stripe(electorate, party)
        
        # update voter district table
        for i,district in enumerate(self.districts):
            for voter in district:
                self.voter_district[voter] = i

        for i in range(10):
            self._improve_districts(electorate, party)
        return self.districts

    def _improve_districts(self,
                           electorate: Electorate,
                           party: bool,
                           ) -> None:
        self.num_voters = [
                sum(electorate.votes[voter]==party for voter in district)
                for district in self.districts
                ]

        for i,_ in enumerate(self.districts):
            if self.num_voters[i] <= electorate.district_size() // 2:
                # losing district, attempt to improve
                self._attempt_improve_district(i, electorate, party)



    def _attempt_improve_district(self,
                      district: int,
                      electorate: Electorate,
                      party: bool) -> None:
        for voter in self.districts[district]:
            if electorate.votes[voter] != party:
                self._attempt_swap(district, voter, electorate, party)

    def _attempt_swap(self,
                      district: int,
                      voter: int,
                      electorate: Electorate,
                      party: bool) -> None:
        for neighbor in electorate.graph.adj[voter]:
            if electorate.votes[neighbor] != party:
                # voting against, wouldn't help to swap
                continue

            neigh_district = self.voter_district[neighbor]
            if neigh_district == district or \
               self.num_voters[neigh_district] <= electorate.district_size() // 2 + 1:
                # either the neighbor's in the same district,
                # or removing neighbor from their district will cause that district to lose
                continue

            # print(self.num_voters[neigh_district], electorate.district_size() // 2 + 1)
            self._swap(voter, neighbor, electorate, party)
            if electorate.is_valid_map(self.districts):
                print("just swapped district", district, "with", neigh_district)
                print("num_voters is", self.num_voters)
                break
            else:
                # swapping breaks contiguity
                self._swap(voter, neighbor, electorate, party)

    def _swap(self, voter: int, neighbor: int, electorate: Electorate, party: bool) -> None:
        # print("\nswapping", voter, neighbor)
        # print(electorate.district_size() // 2 + 1)
        # print("voter districts:",self.voter_district[voter], self.voter_district[neighbor])
        # print("districts:", self.districts)
        # print("num_voters:", self.num_voters)

        d1 = self.voter_district[voter]
        d2 = self.voter_district[neighbor]
        self.voter_district[voter], self.voter_district[neighbor] = d2, d1
        self.districts[d1][self.districts[d1].index(voter)] = neighbor
        self.districts[d2][self.districts[d2].index(neighbor)] = voter
        self.num_voters[d1] += 1 if electorate.votes[neighbor] == party else -1
        self.num_voters[d2] += 1 if electorate.votes[voter] == party else -1

        # print("voter districts:",self.voter_district[voter], self.voter_district[neighbor])
        # print("districts:", self.districts)
        # print("num_voters:", self.num_voters)
        # print()
                

    def _stripe(self, electorate: Electorate, party: bool) -> list[list[int]]:
        d = electorate.district_size()
        if party:
            return [list(range(d * i, d * ( i + 1))) for i in range(d)]
        else:
            return [list(range(i, d * d, d)) for i in range(d)]
