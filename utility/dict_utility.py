from typing import Callable, TypeVar

K = TypeVar("K")
V = TypeVar("V")


def compute_if_absent(dictionary: dict[K, V], key: K, compute_callable: Callable[[K], V]) -> V:
    """
    Retrieve key from dictionary if exists otherwise return computed value from provided callable
    :param dictionary: input dictionary
    :param key: key
    :param compute_callable: callable used to generate default value of key
    :return: corresponding value of key in dictionary
    """
    if key not in dictionary:
        dictionary[key] = compute_callable(key)
    return dictionary[key]
