from exceptions.file_exceptions import InvalidFileFormatException
from parse.parser import parse
from serializability.conflict_serializability import ConflictSerializability
from serializability.result_serializability import ResultSerializability
from serializability.view_serializability import ViewSerializability
from utility import exception_utility
from view import view_generator
from view.view_generator import PRECEDING_GRAPH_FILE_PATH, POLYGRAPH_FILE_PATH, POLYGRAPH_COMPATIBLE_DAG_FILE_PATH


def start(file_path: str):
    try:
        variable_initial_values, schedule = parse(file_path)
    except InvalidFileFormatException as e:
        exception_utility.print_exception_chain(e)
        return 1

    conflict_serializability = ConflictSerializability(schedule)
    conflict_serializability.calculate_preceding_graph()
    is_conflict_serializable, cycle_path = conflict_serializability.is_conflict_serializable()
    conflict_serializable_schedule = None
    if is_conflict_serializable:
        conflict_serializable_schedule = conflict_serializability.get_serializable_schedule()
    conflict_serializability.export_preceding_graph(PRECEDING_GRAPH_FILE_PATH, cycle_path)

    view_serializability = ViewSerializability(schedule)
    view_serializability.calculate_polygraph()
    if not is_conflict_serializable and len(view_serializability.get_transactions_with_blind_write()) == 0:
        is_view_serializable = False
    else:
        is_view_serializable = view_serializability.is_view_serializable()
    view_serializable_schedule = None
    if is_view_serializable:
        view_serializable_schedule = view_serializability.get_serializable_schedule()
        view_serializability.export_polygraph_dag_compatible_graph(POLYGRAPH_COMPATIBLE_DAG_FILE_PATH)
    view_serializability.export_polygraph(POLYGRAPH_FILE_PATH)

    result_serializability = ResultSerializability(schedule)
    schedule_execution_successful = result_serializability.run_schedule(variable_initial_values)
    is_result_serializable = result_serializability.is_result_serializable(variable_initial_values)
    result_serializable_schedule_operations = None
    result_serializable_execution_metadata = None
    if is_result_serializable:
        result_serializable_schedule_operations, result_serializable_execution_metadata = \
            result_serializability.get_serializable_schedule()

    view_generator.generate_view(
        schedule_operations=schedule.schedule_operations,
        schedule_transactions_count=len(schedule.get_schedule_transactions()),

        is_conflict_serializable=is_conflict_serializable,
        conflict_serializable_schedule=conflict_serializable_schedule,

        is_view_serializable=is_view_serializable,
        view_serializable_schedule=view_serializable_schedule,

        schedule_execution_successful=schedule_execution_successful,
        schedule_execution_error=result_serializability.schedule_execution_error,
        schedule_execution_metadata=result_serializability.schedule_execution_metadata,
        schedule_execution_final_database_state=result_serializability.schedule_execution_final_database_state,

        is_result_serializable=is_result_serializable,
        result_serializable_schedule_operations=result_serializable_schedule_operations,
        result_serializable_execution_metadata=result_serializable_execution_metadata,
    )
    # view_generator.open_index_html()
