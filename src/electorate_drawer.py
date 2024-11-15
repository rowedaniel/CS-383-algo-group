import matplotlib.pyplot as plt


def draw(electorate, districts):
    v = electorate.number_of_voters()
    d = electorate.district_size()
    # Find coordinates
    x = [None] * v
    y = [None] * v
    for i in range(v):
        y[i] = (i // d) * (3 ** 0.5) / 2
        if (i // d) % 2 == 0:
            x[i] = i % d
        else:
            x[i] = i % d + 0.5
    # Draw edges
    for voter in range(v):
        for w in electorate.graph_with_only_within_district_edges(districts).adj[voter]:
            if voter < w:
                plt.plot([x[voter], x[w]],
                         [y[voter], y[w]],
                         color='k', zorder=0)
    # Draw voters
    # Yellow is the True party, purple the False party
    plt.scatter(x, y, c=electorate.votes, zorder=0)
    plt.tick_params(left=False, right=False, labelleft=False, labelbottom=False, bottom=False)
    plt.show(block=True)
    exit()


from electorate import Electorate
from striper import Striper

e = Electorate(9)
districts = Striper().gerrymander(e, True)
draw(e, districts)
