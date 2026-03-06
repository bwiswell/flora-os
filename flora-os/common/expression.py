from enum import Enum


class Expression(Enum):
    FLAT = 0
    OPEN = 1
    RESTING = 2
    SMILE = 3


EXPRESSIONS = {
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
        [False, True, False],
        [False, True, False],
        [True, False, True]
    ],
    Expression.SMILE: [
        [False, False, False],
        [True, True, True],
        [False, True, False]
    ]
}