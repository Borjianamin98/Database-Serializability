import re
from typing import Iterator, List


def remove_spaces(input_string: str) -> str:
    """
    Remove spaces from given input string
    :param input_string: input string
    :return: input string while all spaces removed
    """
    return re.sub(r"\s+", "", input_string)


def shorten_long_string(input_string: str, max_characters: int = 20) -> str:
    return (input_string[:max_characters] + "...") if len(input_string) > max_characters else input_string


def list_to_html_string(input_list: list[str], max_elements_to_keep: int = 10) -> str:
    if len(input_list) == 0:
        return "empty"
    numbers_of_element_to_keep = max_elements_to_keep if len(input_list) > max_elements_to_keep else len(input_list)
    return ", ".join((shorten_long_string(e, 5) for e in input_list[:numbers_of_element_to_keep]))
