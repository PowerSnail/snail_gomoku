import numpy as np
import enum
from typing import Tuple
from dataclasses import dataclass
from scipy import signal


_conv2d = signal.convolve2d
_board_dtype = np.int8

BLACK = 0
WHITE = 1


@dataclass
class GameState:
    data: np.ndarray
    turn: int
    ended: bool


class ResultType(enum.Enum):
    Success = 0
    AlreadyOccupied = 1
    Violate33Ban = 2
    Violate44Ban = 3
    ViolateOverline = 4
    AlreadyFinished = 5


@dataclass
class Result:
    type: ResultType
    state: GameState


@dataclass
class GameConfig:
    size: int
    ban_black_33: bool = True
    ban_black_44: bool = True
    ban_black_overline: bool = True


def new_game(conf: GameConfig) -> GameState:
    return GameState(
        np.zeros([2, conf.size, conf.size], dtype=_board_dtype), BLACK, False
    )


def put(conf: GameConfig, state: GameState, x: int, y: int) -> Result:
    if state.ended:
        return Result(ResultType.AlreadyFinished, state)

    i = x * conf.size + y
    if np.any(state.data[:, y, x]):
        return Result(ResultType.AlreadyOccupied, state)

    data = np.copy(state.data)
    data[state.turn, y, x] = 1

    if conf.ban_black_33 and _has_33(data[state.turn]):
        return Result(ResultType.Violate33Ban, state)
    if conf.ban_black_44 and _has_44(data[state.turn]):
        return Result(ResultType.Violate44Ban, state)
    if conf.ban_black_overline and _has_overline(data[state.turn]):
        return Result(ResultType.ViolateOverline, state)

    if _has_five(data[state.turn]):
        return Result(ResultType.Success, GameState(data, state.turn, True))

    else:
        return Result(ResultType.Success, GameState(data, 1 - state.turn, False))


def _has_33(board: np.ndarray):
    # TODO: implement 33 detector
    return False


def _has_44(board: np.ndarray):
    # TODO: implement 44 detector
    return False


def _has_overline(board: np.ndarray):
    # TODO: implement overline detector
    return False


HFILTER = np.ones((1, 5), dtype=_board_dtype)
VFILTER = np.ones((5, 1), dtype=_board_dtype)
DIAG1 = np.eye(5, dtype=_board_dtype)
DIAG2 = np.rot90(DIAG1)


def _has_five(board):
    for f in (HFILTER, VFILTER, DIAG1, DIAG2):
        if np.any(_conv2d(board, f) == 5):
            return True
    return False
