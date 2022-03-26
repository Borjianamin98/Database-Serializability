from typing import List


class InvalidScheduleCommandException(Exception):
    """
    Raised for errors in the input file format regarding invalid schedule command.

    Attributes:
        message: description of error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TransactionOperationExecutionException(Exception):
    """
    Raised when operations are not executable. (For example read variable from database which does not
    exist in database)

    Attributes:
        message: description of error
    """

    def __init__(self, message: str, metadata: List[str]):
        self.message = message
        self.metadata = metadata
        super().__init__(self.message)

    def get_metadata(self) -> List[str]:
        return self.metadata

    def get_message(self) -> str:
        return self.message


class OperandVariableNotFoundException(Exception):
    """
    Raised when operation has a variable that is not available during execution.

    Attributes:
        variable: name of variable
    """

    def __init__(self, variable: str):
        self.variable = variable
        self.message = f"Variable not found: {variable}"
        super().__init__(self.message)

    def get_variable(self):
        return self.variable
