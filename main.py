import os
import sys

import app
from exceptions.file_exceptions import InvalidInputException

if __name__ == '__main__':
    input_args = sys.argv
    if len(input_args) > 2:  # input arguments include file name too
        raise InvalidInputException(f"Number of input arguments must be less than or equal to 2: {input_args[1:]}")

    # Program executed without giving file path. Use hard-coded file path instead
    if len(input_args) == 1:
        input_file_path = "input-file.txt"
    else:
        input_file_path = input_args[1]

    if not os.path.exists(input_file_path):
        raise InvalidInputException(f"Input file not found: {input_file_path}")

    exit(app.start(input_file_path))
