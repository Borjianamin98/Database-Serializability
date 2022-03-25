from typing import Tuple

import networkx as nx

from schedule.schedule import Schedule
from utility.network_utility import create_network_from_nx, copy_from_nx


class ViewSerializability:
    """
    Class used to check view serializability of a schedule.

    For checking view serializability of a schedule, polygraph will be used. a polygraph is triple (N, A, C)
    where N is a set of nodes, A is a set of arcs (i.e. ordered pairs of nodes), and C is a set of choices, which
    are ordered triples of nodes such that if (j, k, i) is a choice then (i,j) is an arc. A directed graph (N', A')
    is compatible with the polygraph (N, A, C) iff N is subset of N', A is a subset of A' and if (j, k, i) is in C
    then (j, k) or (k, i) is in A'. A polygraph is acyclic if it has a compatible acyclic directed graph. Testing
    polygraph acyclicity is an NP-complete problem.
    """

    # This attribute of a edge of the graph contains the list of variables that caused this edge
    EDGE_WRITTEN_VARIABLES_ATTRIBUTE = "title"
    ONE_SIDE_CHOICE_COLOR = "green"
    FINISH_NODE_NAME = "finish"
    START_NODE_NAME = "start"

    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.polygraph: nx.DiGraph = None
        self.choices: set[Tuple[str, str, str]] = set()

        # Become true when finding serializable graph called
        self.serializability_checked = False
        self.serializable_graph = None
        self.is_serializable = False

    def calculate_polygraph(self):
        # Specifies the transaction that last wrote the variable
        # Key: variable name, Value: transaction number (in form of string to have 'start' and 'finish' transactions)
        last_writer_state: dict[str, str] = {}

        # Construct nodes and edges of polygraph
        polygraph: nx.DiGraph = nx.DiGraph()
        for transaction_number, operation in self.schedule.get_non_arithmetic_operations_of_schedule():
            transaction_number_string = str(transaction_number)
            polygraph.add_node(transaction_number_string)
            read_written_variable = operation.get_read_written_variable()

            if operation.is_read():
                if read_written_variable not in last_writer_state:
                    last_writer_state[read_written_variable] = ViewSerializability.START_NODE_NAME

                ViewSerializability.__add_edge_with_writer(
                    polygraph,
                    last_writer_state[read_written_variable], transaction_number_string,
                    read_written_variable
                )
            elif operation.is_write():
                last_writer_state[read_written_variable] = transaction_number_string

        # For all variables, we have a node from T(i) to T(finish) if T(i) is last writer
        for variable, last_writer in last_writer_state.items():
            ViewSerializability.__add_edge_with_writer(
                polygraph, last_writer, ViewSerializability.FINISH_NODE_NAME, variable)

        """
        Extract choices based on constructed polygraph.
        When avoiding interference with the arc T(j) -> T(i), the only transactions that need 
        be considered as T(k) (the transaction that cannot be in the middle) are 'writers' of a variable 
        that caused this arc T(j) -> T(i). However we should exclude T(start) and T(finish) and T(i) or T(j).
        Note: if one of T(i) or T(j) are 'start' or 'finish' nodes, then the choice will be converted to an edge.
        """
        one_sided_choices: set[Tuple[str, str]] = set()
        candidate_choices: set[Tuple[str, str, str]] = set()
        for src, dest, data in polygraph.edges(data=True):
            if src == ViewSerializability.START_NODE_NAME and dest == ViewSerializability.FINISH_NODE_NAME:
                continue

            edge_written_variables = data[ViewSerializability.EDGE_WRITTEN_VARIABLES_ATTRIBUTE]
            writer_transactions = set()
            for variable in edge_written_variables:
                writer_transactions.update(self.schedule.variable_to_writer_mapping.get(variable, set()))

            for writer_transaction in writer_transactions:
                writer_transaction_string = str(writer_transaction)
                if (src == writer_transaction_string or
                        dest == writer_transaction_string or
                        writer_transaction_string == ViewSerializability.START_NODE_NAME or
                        writer_transactions == ViewSerializability.FINISH_NODE_NAME):
                    continue

                if src == ViewSerializability.START_NODE_NAME:
                    # Choice become an edge
                    one_sided_choices.add((dest, writer_transaction_string))
                elif dest == ViewSerializability.FINISH_NODE_NAME:
                    # Choice become an edge
                    one_sided_choices.add((writer_transaction_string, src))
                else:
                    candidate_choices.add((dest, writer_transaction_string, src))

        # Add one-sided choices because we ensure about their existence
        for src, dest in one_sided_choices:
            if not polygraph.has_edge(src, dest):
                polygraph.add_edge(src, dest, color=ViewSerializability.ONE_SIDE_CHOICE_COLOR)

        # Remove already existed choices. For choice (i, k, j) if (i, k) or (k, j) exists, then
        # one of the choice modes has occurred and it will no longer be possible for another mode to occur.
        for src, mid, dest in candidate_choices:
            if not polygraph.has_edge(src, mid) and not polygraph.has_edge(mid, dest):
                self.choices.add((src, mid, dest))
        self.polygraph = polygraph

    def export_polygraph(self, output_path: str):
        if not self.polygraph:
            raise ValueError("Calculate polygraph should be called before")

        net = create_network_from_nx(self.polygraph)
        for src, dest in self.__get_choice_edges():
            net.add_edge(src, dest, dashes=True)

        net.write_html(output_path)

    def is_view_serializable(self) -> bool:
        if not self.polygraph:
            raise ValueError("Calculate polygraph should be called before")

        self.serializability_checked = True

        polygraph_is_dag = nx.is_directed_acyclic_graph(self.polygraph)
        if not polygraph_is_dag:
            return False

        if len(self.choices) == 0:
            self.is_serializable = True
            self.serializable_graph = copy_from_nx(self.polygraph)
            return True

        self.is_serializable = self.__find_serializable_graph_recursively(list(self.choices), 0)
        return self.is_serializable

    def export_polygraph_dag_compatible_graph(self, output_path: str):
        if not self.serializability_checked:
            raise ValueError("Check serializability before getting serializable schedule")
        if not self.is_serializable:
            raise ValueError("Schedule is not view serializable")

        net = create_network_from_nx(self.serializable_graph)
        net.write_html(output_path)

    def get_serializable_schedule(self):
        if not self.serializability_checked:
            raise ValueError("Check serializability before getting serializable schedule")
        if not self.is_serializable:
            raise ValueError("Schedule is not view serializable")

        try:
            # Remove 'start' and 'finish' nodes
            return list(nx.topological_sort(self.serializable_graph))[1:-1]
        except nx.exception.NetworkXUnfeasible:
            raise ValueError("serializable graph is not valid (it should be a DAG)")

    def get_transactions_with_blind_write(self):
        transactions_with_blind_write = set()
        for transaction, operations in self.schedule.get_non_arithmetic_operations_of_all_transactions().items():
            # Specifies variable names which are read by transaction
            read_variables: set[str] = set()

            for operation in operations:
                if operation.is_read():
                    read_variables.add(operation.get_read_variable())
                elif operation.is_write():
                    if not operation.get_written_variable() in read_variables:
                        transactions_with_blind_write.add(transaction)
                        break
        return transactions_with_blind_write

    def __find_serializable_graph_recursively(self, choices: list[Tuple[str, str, str]], current_index: int):
        if current_index >= len(choices):
            self.serializable_graph = copy_from_nx(self.polygraph)
            return True

        src, mid, dest = choices[current_index]

        has_serializable_graph = False

        if not has_serializable_graph and not nx.has_path(self.polygraph, mid, src):
            self.polygraph.add_edge(src, mid)
            has_serializable_graph |= self.__find_serializable_graph_recursively(choices, current_index + 1)
            self.polygraph.remove_edge(src, mid)

        if not has_serializable_graph and not nx.has_path(self.polygraph, dest, mid):
            self.polygraph.add_edge(mid, dest)
            has_serializable_graph |= self.__find_serializable_graph_recursively(choices, current_index + 1)
            self.polygraph.remove_edge(mid, dest)

        return has_serializable_graph

    @staticmethod
    def __add_edge_with_writer(graph: nx.DiGraph, src: str, dest: str, writer: str):
        graph.add_edge(src, dest)
        graph[src][dest].setdefault(ViewSerializability.EDGE_WRITTEN_VARIABLES_ATTRIBUTE, set()).add(writer)

    def __get_choice_edges(self):
        choice_edges: set[Tuple[str, str]] = set()
        for src, mid, dest in self.choices:
            choice_edges.add((src, mid))
            choice_edges.add((mid, dest))
        return choice_edges
