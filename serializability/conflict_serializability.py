from typing import List, Tuple

import networkx as nx
from pyvis.network import Network

from schedule.operation import Operation
from schedule.schedule import Schedule


class ConflictSerializability:
    """
    Class used to check conflict serializability of schedule. Also provide some useful functions to draw preceding
    graph, etc.
    """

    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.preceding_graph: nx.DiGraph = None

    def calculate_preceding_graph(self):
        # Specifies that the number of operations of the transaction has been processed.
        # Key: transaction number, Value: tuple of <number of processed, total number> operations of transaction
        # Note: Use List instead of tuple to have mutations but for automatic type inference, use tuple for type hint
        # noinspection PyTypeChecker
        transaction_states: dict[int, Tuple[int, int, List[Operation]]] = {
            t: [0, len(operations), operations] for t, operations in
            self.schedule.get_non_arithmetic_operations().items() if
            len(operations) != 0
        }

        preceding_graph: nx.DiGraph = nx.DiGraph()
        for cur_t, operation in self.schedule.get_schedule_non_arithmetic_operations():
            transaction_states[cur_t][0] += 1
            preceding_graph.add_node(cur_t)

            if operation.is_write():
                for target_t, (state, total, transaction_operations) in transaction_states.items():
                    if target_t == cur_t:
                        continue

                    # Check existence of precedence between T(cur_t) and T(target_t) (T(cur_t) before T(target_t))
                    if (not preceding_graph.has_edge(cur_t, target_t) and
                            state < total and
                            ConflictSerializability.__any_read_write_on(transaction_operations[state:],
                                                                        operation.get_written_variable())):
                        preceding_graph.add_edge(cur_t, target_t)

                    # Check existence of precedence between T(cur_t) and T(target_t) (T(cur_t) after T(target_t))
                    if (not preceding_graph.has_edge(target_t, cur_t) and
                            state > 0 and
                            ConflictSerializability.__any_read_write_on(transaction_operations[:state],
                                                                        operation.get_written_variable())):
                        preceding_graph.add_edge(target_t, cur_t)

        self.preceding_graph = preceding_graph

    def draw_preceding_graph(self):
        if not self.preceding_graph:
            raise ValueError("Calculate preceding graph should be called before calling draw")

        net = Network(height="100%", width="100%", directed=True)
        for node in self.preceding_graph.nodes:
            net.add_node(node, shape="circle")
        for source, target in self.preceding_graph.edges:
            net.add_edge(source, target)
        net.show_buttons(filter_=['physics'])
        net.show(f"preceding-graph.html")

    @staticmethod
    def __any_read_write_on(operations: List[Operation], variable_name: str):
        return any((op.is_read_write_on(variable_name) for op in operations))
