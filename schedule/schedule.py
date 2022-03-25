from typing import Tuple, List, Iterable, KeysView

from schedule.operation import Operation


class Schedule:
    """
    Abstract class represent an parsed schedule from file

    Each schedule consists of some useful data structures:
        - Schedule operations: list of operations done by given schedule file
        - Transaction operations: data structure that specifies the list of operations performed by each transaction
                                  (Each schedule could consists of multiple transaction)
        - Writers mapping: data structure that specifies which transactions updates each variable
    """

    def __init__(self,
                 schedule_operations: List[Tuple[int, Operation]],
                 transaction_operations: dict[int, List[Operation]],
                 variable_to_writer_mapping: dict[str, set[int]]):
        self.schedule_operations = schedule_operations
        self.transaction_operations = transaction_operations
        self.variable_to_writer_mapping = variable_to_writer_mapping

    def get_schedule_transactions(self) -> KeysView[int]:
        return self.transaction_operations.keys()

    def get_non_arithmetic_operations_of_schedule(self) -> List[Tuple[int, Operation]]:
        for transaction_number, operation in self.schedule_operations:
            if not operation.is_arithmetic():
                yield transaction_number, operation

    def get_non_arithmetic_operations_of_all_transactions(self) -> dict[int, List[Operation]]:
        return {t: Schedule.__non_arithmetic_operations(ops) for t, ops in self.transaction_operations.items()}

    @staticmethod
    def __non_arithmetic_operations(operations: List[Operation]) -> Iterable[Operation]:
        return [op for op in operations if not op.is_arithmetic()]

    def __str__(self):
        return (
            f"Schedule[\n"
            f"\tSchedule operations = {self.schedule_operations} \n"
            f"\tTransactions = {self.transaction_operations} \n"
            f"\tWriters mapping = {self.variable_to_writer_mapping} \n"
            f"]"
        )

    def __repr__(self):
        return self.__str__()
