from enum import IntEnum


class SwathGeneratorType(IntEnum):
    N_SWATH = 0
    SWATH_LENGTH = 1
    ANGLE = 2


class RouteGeneratorType(IntEnum):
    ADVANCED = 0
    BOUSTROPHEDON = 1
    SNAKE = 2
    SPIRAL = 3
