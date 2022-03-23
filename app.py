from exceptions.file_exceptions import InvalidFileFormatException
from parse.parser import parse
from serializability.conflict_serializability import ConflictSerializability
from utility import exception_utility


def start(file_path: str):
    try:
        variable_initial_values, schedule = parse(file_path)
    except InvalidFileFormatException as e:
        exception_utility.print_exception_chain(e)
        return 1

    print(schedule)
    conflict_serializability = ConflictSerializability(schedule)
    conflict_serializability.calculate_preceding_graph()
    is_conflict_serializable, cycle_path = conflict_serializability.is_conflict_serializable()
    conflict_serializability.draw_preceding_graph(cycle_path)
