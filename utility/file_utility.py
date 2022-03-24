from typing import TextIO

from utility import string_utility


def read_file_line_by_line(file: TextIO, num_of_lines_to_skip: int = 0):
    line_number = 0
    for line in file:
        line_number += 1
        if line_number < num_of_lines_to_skip:
            continue

        line_content = string_utility.remove_spaces(line.strip())
        # Skip empty lines or comment lines
        if not line_content or line_content.startswith("//"):
            continue

        yield line_number, line_content
