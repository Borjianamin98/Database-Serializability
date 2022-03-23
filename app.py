from exceptions.file_exceptions import InvalidFileFormatException
from parse.parser import parse
from utility import exception_utility


def start(file_path: str):
    try:
        variable_initial_values, schedule = parse(file_path)
    except InvalidFileFormatException as e:
        exception_utility.print_exception_chain(e)
        return 1

    print(variable_initial_values)
    print(schedule)
    schedule.run_schedule(variable_initial_values)
