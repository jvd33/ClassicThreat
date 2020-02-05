from typing import Sized, Iterable, Iterator, Tuple


def flatten(arr: Iterable) -> Iterable:
    """
    Takes an array of arrays and flattens it into a single array
    :param arr: The "list of lists" to flatten
    :return:
    """
    return [el for sublist in arr for el in sublist]