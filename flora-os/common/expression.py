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