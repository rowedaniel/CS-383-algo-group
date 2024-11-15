class Graph:

    def __init__(self, v):
        self.adj = [[] for _ in range(v)]

    def add_edge(self, v, w):
        self.adj[v].append(w)
        self.adj[w].append(v)

    def neighbors(self, v):
        return self.adj[v]
