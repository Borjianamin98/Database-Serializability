from exceptions.file_exceptions import InvalidFileFormatException
from parse.parser import parse
from serializability.conflict_serializability import ConflictSerializability
from utility import exception_utility
from view import view_generator
from view.view_generator import PRECEDING_GRAPH_FILE_PATH


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
    conflict_serializability.export_preceding_graph(PRECEDING_GRAPH_FILE_PATH, cycle_path)

    view_generator.generate_view(
        schedule_operations=schedule.schedule_operations,
        total_schedule_transactions=schedule.schedule_transactions_count(),
        is_conflict_serializable=is_conflict_serializable
    )
    # view_generator.open_index_html()
