import re


def remove_spaces(input_string: str) -> str:
    """
    Remove spaces from given input string
    :param input_string: input string
    :return: input string while all spaces removed
    """
    return re.sub(r"\s+", "", input_string)


def shorten_long_string(input_string: str) -> str:
    return (input_string[:20] + "...") if len(input_string) > 20 else input_string
