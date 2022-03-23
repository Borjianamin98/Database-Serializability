class InvalidFileFormatException(Exception):
    """
    Raised for errors in the input file format including non-compliance with
    the conditions described in the task, broken file or etc.

    Attributes:
        line number: input line number, which caused the error
        line content: input line content, which caused the error
        message: description of error
    """

    def __init__(self, line_number: int, line_content: str, message: str = ""):
        self.line_number = line_number
        self.line_content = line_content
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        if self.message:
            return (
                "Invalid line format: "
                f"line = {self.line_number} line content = '{self.line_content}' message = {self.message}"
            )
        else:
            return (
                "Invalid line format: "
                f"line = {self.line_number} line content = '{self.line_content}'"
            )


class InvalidInputException(Exception):
    """
    Raised when retrieve invalid arguments during executing programs

    Attributes:
        message: description of error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
