import re
from typing import Tuple, List

from exceptions.file_exceptions import InvalidFileFormatException
from exceptions.schedule_exceptions import InvalidScheduleCommandException
from schedule.operation import Operation
from schedule.schedule import Schedule
from utility.dict_utility import compute_if_absent
from utility.file_utility import read_file_line_by_line
from utility.string_utility import is_int


def extract_transaction_operation(schedule_command_operation: str) -> Operation:
    """
    Each schedule command consist of an operation in one of below format:
      - Arithmetic operation (including +, *, -, /): exactly one operation in form of 'x = y operation z'
      - Read operation: Read value of variable from database in form of 'R(x)'
      - Write operation: Update value of variable in database in form of 'W(x)'
    A schedule operation is valid if formatted based on the above information.

    :param schedule_command_operation: operation of a schedule transaction
    :return: operation if given operation is valid otherwise throw exception
    """
    # Handle read/write operation (like 'R(x)' or 'W(x)')
    matches = re.match(r"^([RW])\(([a-z])\)$", schedule_command_operation)
    if matches:
        operator, operand1_var = matches.groups()
        return Operation(operator, operand1_var)

    # Handle arithmetic operation
    # Regex to match string of form 'x = y op z' (y or z can be numbers)
    matches = re.match(r"^([a-z]+)=([a-z]+|-?\d*\.?\d+)([+*\-/])([a-z]+|-?\d*\.?\d+)$", schedule_command_operation)
    if matches:
        result_var, operand1_var, operator, operand2_var = matches.groups()
        return Operation(operator, operand1_var, operand2_var, result_var)

    raise InvalidScheduleCommandException(
        "Schedule transaction operation is not valid. "
        "It should be only arithmetic or read/write operation in predefined form."
    )


def extract_schedule_command(schedule_command: str) -> tuple[int, int, Operation]:
    """
    Each schedule command should be in form of:
    <line number, transaction number, operation>
    A command is valid if its various parts are according to the predefined format.

    :param schedule_command: given schedule command
    :return tuple of <line number, transaction number, operation> otherwise throw exception in case of invalid command
    """
    if len(schedule_command) < 3:
        raise InvalidScheduleCommandException("Schedule command should be in form of <...> (at least 3 character)")
    if not (schedule_command.startswith("<") and schedule_command.endswith(">")):
        raise InvalidScheduleCommandException("Schedule command should start and end in form of <...>")

    schedule_command = schedule_command[1:-1]  # Remove <> from schedule command
    command_parts = schedule_command.split(",")
    if len(command_parts) != 3:
        raise InvalidScheduleCommandException(
            f"Schedule command must consist of 3 different parts separated by commas: "
            f"extracted parts = {command_parts}")
    if not is_int(command_parts[0]):
        raise InvalidScheduleCommandException(f"Schedule command line number should be a number: {command_parts[0]}")
    if not is_int(command_parts[1]):
        raise InvalidScheduleCommandException(
            f"Schedule command transaction number should be a number: {command_parts[1]}")
    command_line_number = int(command_parts[0])
    transaction_number = int(command_parts[1])
    transaction_operation = extract_transaction_operation(command_parts[2])
    return command_line_number, transaction_number, transaction_operation


def read_schedule_file(input_file_path: str, num_of_header_lines: int) -> Schedule:
    """
    Reads the schedule from file
    Initially, a number of lines that are specified based on the input are ignored. (header lines)
    Each of the following lines are in the following format which describe schedule commands:
    <line number, transaction number, operation>
    Description of different parts:
        line number: Current line number in given schedule
        transaction number: Current number of transaction (Each schedule could consists of multiple transaction)
        operation: operation of transaction
            
    The content of lines will be parsed and extracted in the form of schedule.

    :param input_file_path: input file path
    :param num_of_header_lines: number of lines to skip (header lines)
    :return final schedule model after parsing file. Also throw exception in case of invalid schedule file.
    """

    # Key: variable name, Value: list of writers (schedule numbers)
    variable_to_writer_mapping: dict[str, set[int]] = {}

    # Key: transaction number, Value: list of operations
    transaction_operations: dict[int, List[Operation]] = {}

    # List of current schedule operations (Left: transaction number, Right: operation)
    schedule_operations: List[Tuple[int, Operation]] = []

    with open(input_file_path) as file:
        for line_number, line_content in read_file_line_by_line(file, num_of_header_lines):
            # Extract transaction information from schedule command
            try:
                _, transaction_number, transaction_operation = extract_schedule_command(line_content)
            except InvalidScheduleCommandException as e:
                raise InvalidFileFormatException(line_number, line_content) from e

            # Update data structures
            compute_if_absent(transaction_operations, transaction_number, lambda k: []).append(transaction_operation)
            if transaction_operation.is_write():
                compute_if_absent(variable_to_writer_mapping, transaction_operation.get_written_variable(),
                                  lambda k: set()).add(transaction_number)
            schedule_operations.append((transaction_number, transaction_operation))

    return Schedule(schedule_operations, transaction_operations, variable_to_writer_mapping)
