import networkx as nx


def pagerank(graph, initial=0.85, personalization=None,
             iterations=100, tol=1.0e-6, nstart=None, weight='weight',
             dangling=None):
    if len(graph) == 0:
        return {}

    if not graph.is_directed():
        directed = graph.to_directed()
    else:
        directed = graph

    right_stochastic = nx.stochastic_graph(directed, weight=weight)
    number_of_nodes = right_stochastic.number_of_nodes()

    if nstart is None:
        x = dict.fromkeys(right_stochastic, 1.0 / number_of_nodes)
    else:
        values_sum = float(sum(nstart.values()))
        x = dict((key, value / values_sum) for key, value in nstart.items())

    if personalization is None:

        p = dict.fromkeys(right_stochastic, 1.0 / number_of_nodes)
    else:
        missing = set(graph) - set(personalization)
        if missing:
            raise Exception("Missing nodes %s" % missing)
        values_sum = float(sum(personalization.values()))
        p = dict((key, value / values_sum) for key, value in personalization.items())

    if dangling is None:

        dangling_weights = p
    else:
        missing = set(graph) - set(dangling)
        if missing:
            raise Exception("Missing nodes %s" % missing)
        values_sum = float(sum(dangling.values()))
        dangling_weights = dict((key, value / values_sum) for key, value in dangling.items())
    dangling_nodes = [n for n in right_stochastic if right_stochastic.out_degree(n, weight=weight) == 0.0]

    for _ in range(iterations):
        xlast = x
        x = dict.fromkeys(xlast.keys(), 0)
        danglesum = initial * sum(xlast[n] for n in dangling_nodes)
        for n in x:

            for nbr in right_stochastic[n]:
                x[nbr] += initial * xlast[n] * right_stochastic[n][nbr][weight]
            x[n] += danglesum * dangling_weights[n] + (1.0 - initial) * p[n]

        err = sum([abs(x[n] - xlast[n]) for n in x])
        if err < number_of_nodes * tol:
            return x
    raise Exception("Eigenvalue solver iteration failed at %d iteration" % iterations)


if __name__ == '__main__':
    G = nx.Graph()
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge(3, 4)
    G.add_edge(4, 5)
    G.add_edge(5, 1)
    print(pagerank(G))
