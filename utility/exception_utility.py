import sys


def print_exception_chain(exception: BaseException):
    """
    Remove exception message from given exception to root cause
    :param exception: target exception instance
    """
    errors = [exception.__str__()]
    while exception.__cause__:
        exception = exception.__cause__
        errors.append(exception.__str__())
    errors.reverse()

    sys.stderr.flush()
    sys.stderr.write("\n".join(errors))
