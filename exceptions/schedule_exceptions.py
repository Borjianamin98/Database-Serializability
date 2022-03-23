class InvalidScheduleCommandException(Exception):
    """
    Raised for errors in the input file format regarding invalid schedule command.

    Attributes:
        message: description of error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
