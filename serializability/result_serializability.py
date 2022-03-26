from typing import Tuple, List

from exceptions.schedule_exceptions import TransactionOperationExecutionException, OperandVariableNotFoundException
from schedule.operation import Operation
from schedule.schedule import Schedule
from utility.string_utility import list_to_html_string

ExecutionMetadata = List[str]
InMemoryState = dict[str, int]  # Key: variable name, Value: variable value


class ResultSerializability:
    """
    Class used to check result serializability of a schedule.

    For checking result serializability of a schedule, we should consider all permutations of transactions and their
    final result in database. If any of them have same effect on database as given schedule, then given schedule is
    serializable based on result equivalence criteria.
    """

    def __init__(self, schedule: Schedule):
        self.schedule = schedule

        self.schedule_executed = False
        self.schedule_final_database_state: InMemoryState = {}
        self.schedule_execution_metadata: ExecutionMetadata = []
        self.schedule_execution_error = ""

        self.serializability_checked = False
        self.serializable_permutation = None
        self.is_serializable = False

    def run_schedule(self, variable_initial_values: dict[str, int]) -> bool:
        self.schedule_executed = True
        try:
            database_state, execution_metadata = ResultSerializability.__run_transaction_operations(
                variable_initial_values, self.schedule.schedule_operations)
            self.schedule_final_database_state = database_state
            self.schedule_execution_metadata = execution_metadata
            return True
        except TransactionOperationExecutionException as e:
            # Store partial metadata with error.
            self.schedule_execution_metadata = e.get_metadata()
            self.schedule_execution_error = e.get_message()
            return False

    def is_result_serializable(self) -> bool:
        self.serializability_checked = True

        self.is_serializable = False

        return self.is_serializable

    def get_serializable_schedule(self):
        if not self.serializability_checked:
            raise ValueError("Check serializability before getting serializable schedule")
        if not self.is_serializable:
            raise ValueError("Schedule is not result serializable")

        pass

    @staticmethod
    def __run_transaction_operations(
            initial_database_state: InMemoryState,
            transaction_operations: List[Tuple[int, Operation]]) -> Tuple[InMemoryState, ExecutionMetadata]:
        """
        Retrieve list of operations in form of transaction (tuple of <transaction number, operation>) and
        execute them serially.
        :param initial_database_state: initial value of variables in database before starting execution.
        :param transaction_operations: operations with transaction metadata
        :return: tuple of <final database state, execution metadata> of execution. During execution, some metadata
                 generated for each operation (for example final result of operation). Also at the end of execution,
                 state of database will be changed and final state will be reported by this method. Throw exception in
                 case of invalid list of operations.
        """
        in_memory_database = initial_database_state.copy()

        # In memory state of variables for each executed transaction over time.
        # Key: transaction number, Value: In-memory state of transaction including mapping of variable name to value
        in_memory_state: dict[int, InMemoryState] = {}

        # Metadata information
        execution_metadata: ExecutionMetadata = []

        for index, (transaction_number, operation) in enumerate(transaction_operations):
            operation_number = index + 1
            transaction_in_memory_state = in_memory_state.setdefault(transaction_number, dict())

            if operation.is_read():
                read_variable = operation.get_read_variable()
                if read_variable not in in_memory_database:
                    raise TransactionOperationExecutionException(
                        f"Read operation is not possible because " +
                        f"the read variable does not exist in the database during execution:\n" +
                        f"operation number = {operation_number} variable = {read_variable}", execution_metadata)
                read_value = in_memory_database[read_variable]
                transaction_in_memory_state[read_variable] = read_value
                execution_metadata.append(f"{read_variable} = {read_value}")
            elif operation.is_write():
                written_variable = operation.get_written_variable()
                if written_variable not in transaction_in_memory_state:
                    raise TransactionOperationExecutionException(
                        f"Write operation is not possible because " +
                        f"the written variable does not exist in the memory of transaction during execution:\n" +
                        f"Operation number = {operation_number}\n" +
                        f"Transaction number = {transaction_number}\n" +
                        f"Not available written variable = {written_variable}\n" +
                        f"Available variables = {list_to_html_string(list(transaction_in_memory_state.keys()))}\n",
                        execution_metadata)
                written_value = transaction_in_memory_state[written_variable]
                in_memory_database[written_variable] = written_value
                execution_metadata.append(f"{written_variable} = {written_value}")
            else:
                try:
                    result_value = operation.do_arithmetic(transaction_in_memory_state)
                except OperandVariableNotFoundException as e:
                    raise TransactionOperationExecutionException(
                        f"Arithmetic operation is not possible because " +
                        f"one of operands does not exist in the memory of transaction during execution:\n" +
                        f"Operation number = {operation_number}\n" +
                        f"Transaction number = {transaction_number}\n" +
                        f"Not available operand = {e.get_variable()}\n" +
                        f"Available operands = {list_to_html_string(list(transaction_in_memory_state.keys()))}\n",
                        execution_metadata)
                result_variable = operation.get_result_variable()
                execution_metadata.append(
                    f"{result_variable} = "
                    f"{operation.get_with_actual_value(transaction_in_memory_state)} = "
                    f"{result_value}")
                transaction_in_memory_state[result_variable] = result_value

        return in_memory_database, execution_metadata
