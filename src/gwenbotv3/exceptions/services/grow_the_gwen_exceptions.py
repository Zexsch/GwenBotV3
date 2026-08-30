"""Exceptions for the grow the gwen autobattler"""


# pylint: disable=missing-class-docstring
class GrowTheGwenError(Exception):
    pass


class PlayerInsertionError(GrowTheGwenError):
    pass


class PlayerNotFoundError(GrowTheGwenError):
    pass
