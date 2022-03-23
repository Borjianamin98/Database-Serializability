from typing import List

import networkx as nx

from schedule.schedule import Schedule


class ConflictSerializability:
    """
    Class used to check conflict serializability of schedule. Also provide some useful functions to draw preceding
    graph, etc.
    """

    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.preceding_graph = None

    def calculate_preceding_graph(self):
        # Specifies that the number of operations of the transaction has been processed.
        # Key: transaction number, Value: tuple of <number of processed, total number> operations of transaction
        transaction_states: dict[int, List[int, int]] = {t: (0, length) for t, length in
                                                         self.schedule.get_non_arithmetic_operations_count() if
                                                         length != 0}

        preceding_graph: nx.DiGraph = nx.DiGraph()
        for transaction_number, operation in self.schedule.get_schedule_non_arithmetic_operations():
            transaction_states[transaction_number][0] += 1
            if operation.is_write():
                for t, (state, total) in transaction_states.items():
                    if t == transaction_number:
                        continue
                    if state == 0:
                        preceding_graph.add_edge(transaction_number, t)
                    elif state == total:
                        preceding_graph.add_edge(t, transaction_number)
                    else:
                        preceding_graph.add_edge(transaction_number, t)
                        preceding_graph.add_edge(t, transaction_number)
        self.preceding_graph = preceding_graph
