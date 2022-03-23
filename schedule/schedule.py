from typing import Tuple, List

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
                 variable_to_writer_mapping: dict[str, List[int]]):
        self.schedule_operations = schedule_operations
        self.transaction_operations = transaction_operations
        self.variable_to_writer_mapping = variable_to_writer_mapping

    def run_schedule(self, in_memory_database: dict[str, int]):
        in_memory_state: dict[str, int] = {}
        for _, operation in self.schedule_operations:
            print("state:", in_memory_state)
            print("database:", in_memory_database)
            print(operation)
            if operation.is_read():
                in_memory_state[operation.get_read_variable()] = in_memory_database[operation.get_read_variable()]
            elif operation.is_write():
                in_memory_database[operation.get_written_variable()] = in_memory_state[operation.get_written_variable()]
            else:
                in_memory_state[operation.result_variable()] = operation.do_arithmetic(in_memory_state)

    def get_schedule_non_arithmetic_operations(self) -> List[Tuple[int, Operation]]:
        for transaction_number, operation in self.schedule_operations:
            if not operation.is_arithmetic():
                yield transaction_number, operation

    def get_non_arithmetic_operations_count(self) -> dict[int, int]:
        return {t: Schedule.__non_arithmetic_operations_count(ops) for t, ops in self.transaction_operations}

    @staticmethod
    def __non_arithmetic_operations_count(operations: List[Operation]) -> int:
        return sum(1 for op in operations if not op.is_arithmetic())

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
