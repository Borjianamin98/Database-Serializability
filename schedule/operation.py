class Operation:
    """
    Abstract class represent an operation of transaction

    Each operation either is arithmetic operation or read/write operation.
    Operand specify type of operation:
      - +, *, -, / (Arithmetic)
      - R (Read)
      - W (Write)
    """

    def __init__(self, operator: str, operand1: str, operand2: str = "", result: str = ""):
        self.operator = operator
        self.operand1 = operand1
        self.operand2 = operand2
        self.result = result

    def is_arithmetic(self) -> bool:
        return self.operator != "R" and self.operator != "W"

    def is_read(self) -> bool:
        return self.operator == "R"

    def is_write(self) -> bool:
        return self.operator == "W"

    def get_read_variable(self) -> str:
        assert self.is_read()
        return self.operand1

    def get_written_variable(self) -> str:
        assert self.is_write()
        return self.operand1

    def get_read_written_variable(self) -> str:
        assert self.is_write() or self.is_read()
        return self.operand1

    def do_arithmetic(self, variables: dict[str, int]) -> int:
        assert self.is_arithmetic()
        return eval(
            f"{self.__get_operand_value(variables, self.operand1)} "
            f"{self.operator} "
            f"{self.__get_operand_value(variables, self.operand2)}"
        )

    def result_variable(self):
        assert self.is_arithmetic()
        return self.result

    def is_read_write_on(self, variable: str):
        return self.operand1 == variable

    @staticmethod
    def __get_operand_value(variables: dict[str, int], operand: str) -> int:
        if str.isnumeric(operand):
            return int(operand)
        else:
            return variables[operand]

    def get_html_view(self):
        if self.is_arithmetic():
            return f"{self.result} = {self.operand1} {self.operator} {self.operand2}"
        else:
            return f"{self.operator}({self.operand1})"

    def __str__(self):
        if self.is_arithmetic():
            return f"Operation['{self.result}' = '{self.operand1}' '{self.operator}' '{self.operand2}']"
        else:
            return f"Operation[{self.operator}({self.operand1})]"

    def __repr__(self):
        return self.__str__()
