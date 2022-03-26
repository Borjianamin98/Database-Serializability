import re
from typing import Tuple

from exceptions.file_exceptions import InvalidFileFormatException
from schedule import schedule_parser
from schedule.schedule import Schedule
from utility.file_utility import read_file_line_by_line
from utility.string_utility import is_float


def extract_variable_initial_values(input_file_path: str) -> tuple[int, dict[str, float]]:
    """
    Reads the input file until it sees "#" at the beginning of the line
    and extracts the initial value of the variable
    :param input_file_path: input file path
    :return tuple of number of processed lines and variable initial values
    """

    # Key: variable name, Value: initial value
    variable_initial_values: dict[str, float] = {}

    with open(input_file_path) as file:
        for line_number, line_content in read_file_line_by_line(file):
            if line_content.startswith("#"):
                # Remove all spaces and '#' from line content and split it in two part based on '=' operator
                line_parts = line_content.replace("#", "").split("=")
                if len(line_parts) != 2:
                    raise InvalidFileFormatException(
                        line_number, line_content,
                        "Lines include variable initial values should be in format of '# x = y'"
                    )
                if not re.match("^[a-z]$", line_parts[0]):
                    raise InvalidFileFormatException(
                        line_number, line_content, f"Variable names should be in [a-z] format: {line_parts[0]}")
                if not is_float(line_parts[1]):
                    raise InvalidFileFormatException(
                        line_number, line_content,
                        f"Variable values should be a number: {line_parts[1]}")

                variable_initial_values[line_parts[0]] = float(line_parts[1])
            else:
                break
        return line_number, variable_initial_values


def parse(file_path: str) -> Tuple[dict[str, float], Schedule]:
    """
    Parse give input file and returns extracted information in form of useful data structures.
    The information in the file is in the following format:

    ----------
    Variable initialization
    ...
    Variable initialization
    Schedule command
    ...
    Schedule command
    ----------

    Variable initializations are in the following format: '# x = y'
    Schedule commands  are in the following format: 'x = y op b' or 'R(x)' or 'W(x)'
    for more information, refer to the classes called by Parser.

    :param file_path: input file path
    :return: tuple of <variable initial values, schedule operations, transaction operations, writer mapping> in case of
             successful parsing of given file otherwise throws exception
    """
    num_of_variable_value_lines, variable_initial_values = extract_variable_initial_values(file_path)
    schedule = schedule_parser.read_schedule_file(file_path, num_of_variable_value_lines)
    return variable_initial_values, schedule
