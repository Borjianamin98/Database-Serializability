import re


def remove_spaces(input_string: str):
    """
    Remove spaces from given input string
    :param input_string: input string
    :return: input string while all spaces removed
    """
    return re.sub(r"\s+", "", input_string)
