import networkx as nx


class pagerank:

    def __init__(
        self,
        graph,
        initial=0.85,
        personalization=None,
        iterations=100,
        tol=1.0e-6,
        nstart=None,
        weight='weight',
        dangling=None,
    ):
        self.graph = graph
        self.initial = initial
        self.personalization = personalization
        self.iterations = iterations
        self.tol = tol
        self.nstart = nstart
        self.weight = weight
        self.dangling = dangling
        self.directed_graph = None
        self.x = None
        self.p = None
        self.dangling_nodes = None
        self.dangling_weights = None

    def validate_length_of_graph(self):
        if len(self.graph) == 0:
            return {}

    def get_directed_graph(self):
        if not self.graph.is_directed():
            self.directed_graph = self.graph.to_directed()
        else:
            self.directed_graph = self.graph

    def x_parameter_when_null(self, right_stochastic, number_of_nodes):
        self.x = dict.fromkeys(right_stochastic, 1.0 / number_of_nodes)

    def x_parameter_when_not_null(self, right_stochastic, number_of_nodes):
        values_sum = float(sum(self.nstart.values()))
        self.x = dict((key, value / values_sum) for key, value in self.nstart.items())

    def x_according_to_nstart(self, right_stochastic, number_of_nodes):
        {
            None: self.x_parameter_when_null
        }.get(self.nstart, self.x_parameter_when_not_null)(right_stochastic, number_of_nodes)

    def p_according_to_personalization(self, right_stochastic, number_of_nodes):
        if self.personalization is None:
            self.p = dict.fromkeys(right_stochastic, 1.0 / number_of_nodes)
        else:
            missing = set(self.graph) - set(self.personalization)
            if missing:
                raise Exception(f"Missing nodes {missing}")
            values_sum = float(sum(self.personalization.values()))
            self.p = dict((key, value / values_sum) for key, value in self.personalization.items())

    def get_dangling_nodes(self, right_stochastic):
        if self.dangling is None:
            self.dangling_weights = self.p
        else:
            missing = set(self.graph) - set(self.dangling)
            if missing:
                raise Exception(f"Missing nodes {missing}")
            values_sum = float(sum(self.dangling.values()))
            self.dangling_weights = dict(
                (key, value / values_sum) for key, value in self.dangling.items()
            )
        self.dangling_nodes = [n for n in right_stochastic if right_stochastic.out_degree(n, weight=self.weight) == 0.0]

    def count_pagerank(self, right_stochastic, number_of_nodes):
        for _ in range(self.iterations):
            xlast = self.x
            x = dict.fromkeys(xlast.keys(), 0)
            danglesum = self.initial * sum(xlast[n] for n in self.dangling_nodes)
            for n in x:
                for nbr in right_stochastic[n]:
                    x[nbr] += self.initial * xlast[n] * right_stochastic[n][nbr][self.weight]
                x[n] += danglesum * self.dangling_weights[n] + (1.0 - self.initial) * self.p[n]

            err = sum([abs(x[n] - xlast[n]) for n in x])
            if err < number_of_nodes * self.tol:
                return x
        raise Exception(f"Eigenvalue solver iteration failed at {self.iterations} iteration")

    def result(self):
        self.validate_length_of_graph()
        self.get_directed_graph()
        right_stochastic = nx.stochastic_graph(
            self.directed_graph,
            weight=self.weight
        )
        number_of_nodes = right_stochastic.number_of_nodes()
        self.x_according_to_nstart(right_stochastic, number_of_nodes)
        self.p_according_to_personalization(right_stochastic, number_of_nodes)
        self.get_dangling_nodes(right_stochastic)
        return self.count_pagerank(right_stochastic, number_of_nodes)


def pagerank_func(
    graph,
    initial=0.85,
    personalization=None,
    iterations=100,
    tol=1.0e-6,
    nstart=None,
    weight='weight',
    dangling=None
):
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
            raise Exception(f"Missing nodes {missing}")
        values_sum = float(sum(personalization.values()))
        p = dict((key, value / values_sum) for key, value in personalization.items())

    if dangling is None:
        dangling_weights = p
    else:
        missing = set(graph) - set(dangling)
        if missing:
            raise Exception(f"Missing nodes {missing}")
        values_sum = float(sum(dangling.values()))
        dangling_weights = dict(
            (key, value / values_sum) for key, value in dangling.items()
        )
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
    raise Exception(f"Eigenvalue solver iteration failed at {iterations} iteration")


if __name__ == '__main__':
    G = nx.Graph()
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge(3, 4)
    G.add_edge(4, 5)
    G.add_edge(5, 1)

    print("klasa: ", pagerank(G).result())
    print("funkcja: ", pagerank_func(G))
