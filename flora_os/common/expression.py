from enum import Enum


class Expression(Enum):
    CORNERS = 0
    FLAT = 1
    OPEN = 2
    RESTING = 3
    SMILE = 4


EXPRESSIONS = {
    Expression.CORNERS: [
        [True, False, True],
        [False, False, False],
        [True, False, True]
    ],
    Expression.FLAT: [
        [False, False, False],
        [True, True, True],
        [False, False, False]
    ],
    Expression.OPEN: [
        [False, True, False],
        [True, False, True],
        [False, True, False]
    ],
    Expression.RESTING: [
        [True, False, True],
        [True, True, True],
        [False, True, False]
    ],
    Expression.SMILE: [
        [True, True, True],
        [True, False, True],
        [True, False, True]
    ]
}