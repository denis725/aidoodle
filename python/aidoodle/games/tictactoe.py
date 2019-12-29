from dataclasses import dataclass
from itertools import product
from typing import Optional, Set, Tuple

import aidoodle.games.ziczaczoe as zzz


Move = zzz.Move
Game = zzz.Game
Player = zzz.Player
apply_move = zzz.apply_move
determine_winner = zzz.determine_winner
init_move = zzz.init_move
init_player = zzz.init_player
get_legal_moves = zzz.get_legal_moves
make_move = zzz.make_move
game_score = zzz.game_score


POSSIBLE_MOVES: Set[Tuple[int, int]] = set(product(range(3), range(3)))

_Row = Tuple[int, int, int, int, int]

TICTACTOEBOARD = (
    (0, 0, 0, 9, 9),  # 9 codes for blocked
    (0, 0, 0, 9, 9),
    (0, 0, 0, 9, 9),
    (9, 9, 9, 9, 9),
    (9, 9, 9, 9, 9))


@dataclass(frozen=True)
class Board(zzz.Board):
    """custom zzz board that's only shows first 3 rows and columns"""
    state: Tuple[_Row, _Row, _Row, _Row, _Row] = TICTACTOEBOARD

    def _rrow(self, i: int) -> str:
        row = self.state[i]
        srow = "|{}|{}|{}|".format(*row[:3])
        srow = srow.replace("0", " ").replace("1", "x").replace("2", "o")
        return srow

    def __repr__(self) -> str:
        return "\n".join((
            "",
            "   0 1 2",
            "0 " + self._rrow(0),
            "1 " + self._rrow(1),
            "2 " + self._rrow(2),
            "",
        ))




MaybeBoard = Optional[Board]


def init_game(board: MaybeBoard = None, player_idx: int = 0) -> Game:
    zzz.Board = Board  # monkey patch tictactoe board
    if board is None:
        board_ = Board(TICTACTOEBOARD)
    else:
        board_ = board

    return Game(
        players=(Player(1), Player(2)),
        board=board_,
        player_idx=player_idx,
    )
