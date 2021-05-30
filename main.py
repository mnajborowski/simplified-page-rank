import networkx as nx


class PageRank:

    def __init__(
        self,
        graph,
        alpha=0.85,
        personalization=None,
        iterations=100,
        tol=1.0e-6,
        nstart=None,
        weight='weight',
        dangling=None,
    ):
        self.graph = graph
        self.initial = alpha
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

    def __validate_length_of_graph(self):
        if len(self.graph) == 0:
            return {}

    def __get_directed_graph(self):
        if not self.graph.is_directed():
            self.directed_graph = self.graph.to_directed()
        else:
            self.directed_graph = self.graph

    def __x_parameter_when_null(self, right_stochastic, number_of_nodes):
        self.x = dict.fromkeys(right_stochastic, 1.0 / number_of_nodes)

    def __x_parameter_when_not_null(self, right_stochastic, number_of_nodes):
        values_sum = float(sum(self.nstart.values()))
        self.x = dict((key, value / values_sum) for key, value in self.nstart.items())

    def __x_according_to_nstart(self, right_stochastic, number_of_nodes):
        {
            None: self.__x_parameter_when_null
        }.get(self.nstart, self.__x_parameter_when_not_null)(right_stochastic, number_of_nodes)

    def __p_parameter_when_null(self, right_stochastic, number_of_nodes):
        self.p = dict.fromkeys(right_stochastic, 1.0 / number_of_nodes)

    def __p_parameter_when_not_null(self, right_stochastic, number_of_nodes):
        missing = set(self.graph) - set(self.personalization)
        if missing:
            raise Exception(f"Missing nodes {missing}")
        values_sum = float(sum(self.personalization.values()))
        self.p = dict((key, value / values_sum) for key, value in self.personalization.items())

    def __p_according_to_personalization(self, right_stochastic, number_of_nodes):
        {
            None: self.__p_parameter_when_null
        }.get(self.personalization, self.__p_parameter_when_not_null)(right_stochastic, number_of_nodes)

    def __get_dangling_nodes(self, right_stochastic):
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

    def __count_pagerank(self, right_stochastic, number_of_nodes):
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
        self.__validate_length_of_graph()
        self.__get_directed_graph()
        right_stochastic = nx.stochastic_graph(
            self.directed_graph,
            weight=self.weight
        )
        number_of_nodes = right_stochastic.number_of_nodes()
        self.__x_according_to_nstart(right_stochastic, number_of_nodes)
        self.__p_according_to_personalization(right_stochastic, number_of_nodes)
        self.__get_dangling_nodes(right_stochastic)
        return self.__count_pagerank(right_stochastic, number_of_nodes)


if __name__ == '__main__':
    G = nx.Graph()
    G.add_edge(1, 2)
    G.add_edge(2, 3)
    G.add_edge(3, 4)
    G.add_edge(4, 5)
    G.add_edge(5, 1)

    print("Result:", PageRank(G).result())
