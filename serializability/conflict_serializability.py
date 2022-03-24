from typing import List, Tuple

import networkx as nx
from pyvis.network import Network

from schedule.operation import Operation
from schedule.schedule import Schedule


class ConflictSerializability:
    """
    Class used to check conflict serializability of schedule.
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

    def export_preceding_graph(self, output_path: str, marked_path: List[Tuple[int, int]] = None):
        if not self.preceding_graph:
            raise ValueError("Calculate preceding graph should be called before")

        net = Network(height="90%", width="100%", directed=True, notebook=True)
        for node in self.preceding_graph.nodes:
            net.add_node(node, shape="circle")
        for source, target in self.preceding_graph.edges:
            net.add_edge(source, target)
        if marked_path:
            for source, destination in marked_path:
                net.add_edge(source, destination, color="red")

        # Note: Active below line if you want to check modifying physic attributes
        # net.show_buttons()
        net.set_options("""
        var options = {
          "edges": {
            "color": {
              "inherit": true
            },
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 0.5
              }
            },
            "smooth": {
              "type": "curvedCW",
              "forceDirection": "none"
            }
          },
          "physics": {
            "minVelocity": 0.75
          }
        }
        """)
        net.write_html(output_path)

    def is_conflict_serializable(self) -> Tuple[bool, List[Tuple[int, int]]]:
        """
        Returns tuple consist of whether schedule is serializable or not, in addition to cycle path in graph
        if precedence graph is not conflict serializable (contains cycle)
        :return: tuple of <is conflict serializable, precedence cycle path>
        """
        if not self.preceding_graph:
            raise ValueError("Calculate preceding graph should be called before")

        try:
            cycle_path = nx.find_cycle(self.preceding_graph)
            return False, [(int(src), int(dest)) for src, dest in cycle_path]
        except nx.exception.NetworkXNoCycle:
            return True, []

    def get_serializable_schedule(self):
        """
        Returns serializable schedule if preceding graph is DAG (conflict serializable)
        :return: ordered list of nodes which define serializable schedule
        """
        if not self.preceding_graph:
            raise ValueError("Calculate preceding graph should be called before")

        try:
            return list(nx.topological_sort(self.preceding_graph))
        except nx.exception.NetworkXUnfeasible:
            raise ValueError("Preceding graph is not conflict serializable")

    @staticmethod
    def __any_read_write_on(operations: List[Operation], variable_name: str):
        return any((op.is_read_write_on(variable_name) for op in operations))
