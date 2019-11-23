from dataclasses import dataclass
from itertools import product
import random
from typing import Any, List, Tuple, Optional, Generator, Set, Union


POSSIBLE_PLAYERS: Set[int] = {1, 2}
POSSIBLE_MOVES: Set[Tuple[int, int]] = set(product(range(3), range(3)))


class Player(int):
    def __init__(self, i: int):
        if i not in POSSIBLE_PLAYERS:
            raise ValueError
        super().__init__()

    def __repr__(self) -> str:
        return f"Player({self})"


class Move:
    def __init__(self, i: int, j: int):
        if (i, j) not in POSSIBLE_MOVES:
            raise ValueError
        self.i = i
        self.j = j

    def __repr__(self) -> str:
        return f"Move({self.i}, {self.j})"

    def __iter__(self) -> Generator[int, None, None]:
        yield self.i
        yield self.j

    def __eq__(self, other: Any) -> bool:
        try:
            i: int
            j: int
            i, j = other
            return (i == self.i) and (j == self.j)
        except TypeError:
            return False

    def __hash__(self) -> int:
        return hash((self.i, self.j))


_Row = Tuple[int, int, int]
_Board = Tuple[_Row, _Row, _Row]
MaybeBoard = Optional[_Board]
MaybePlayer = Optional[Player]


class Board:
    def __init__(self, state: MaybeBoard = None):
        if state is None:
            state = (
                (0, 0, 0),
                (0, 0, 0),
                (0, 0, 0))
        self.state = state

    def _rrow(self, i: int) -> str:
        row = self.state[i]
        return "|{}|{}|{}|".format(*row)

    def __repr__(self) -> str:
        return "\n".join((
            "",
            self._rrow(0),
            self._rrow(1),
            self._rrow(2),
        ))

    def __iter__(self) -> Generator[_Row, None, None]:
        yield from self.state

    def __eq__(self, other: Any) -> bool:
        try:
            res: bool = self.state == other.state
            return res
        except (TypeError, AttributeError):
            return False


@dataclass
class Game:
    player: Player
    winner: MaybePlayer
    board: Board


def _sum_board_rows(board: Board) -> Tuple[int, int]:
    sum_1: int = max(sum(p == 1 for p in row) for row in board)
    sum_2: int = max(sum(p == 2 for p in row) for row in board)
    return sum_1, sum_2


def _sum_board_cols(board: Board) -> Tuple[int, int]:
    board = _transpose_board(board)
    sum_1: int = max(sum(p == 1 for p in row) for row in board)
    sum_2: int = max(sum(p == 2 for p in row) for row in board)
    return sum_1, sum_2


def _sum_board_diag(board: Board) -> Tuple[int, int]:
    r0, r1, r2 = iter(board)
    sum_1: int = max(
        (r0[0] == 1) + (r1[1] == 1) + (r2[2] == 1),
        (r0[2] == 1) + (r1[1] == 1) + (r2[0] == 1),
    )
    sum_2: int = max(
        (r0[0] == 2) + (r1[1] == 2) + (r2[2] == 2),
        (r0[2] == 2) + (r1[1] == 2) + (r2[0] == 2),
    )
    return sum_1, sum_2


def _transpose_board(board: Board) -> Board:
    row0, row1, row2 = tuple(zip(*board.state))
    return Board((row0, row1, row2))


def determine_winner(board: Board) -> MaybePlayer:
    # test row winner
    sum_row_1, sum_row_2 = _sum_board_rows(board)
    if sum_row_1 == 3:
        return Player(1)
    if sum_row_2 == 3:
        return Player(2)

    # test col winner
    sum_col_1, sum_col_2 = _sum_board_cols(board)
    if sum_col_1 == 3:
        return Player(1)
    if sum_col_2 == 3:
        return Player(2)

    # test diag winner
    sum_diag_1, sum_diag_2 = _sum_board_diag(board)
    if sum_diag_1 == 3:
        return Player(1)
    if sum_diag_2 == 3:
        return Player(2)

    # no winner
    return None


def get_next_player(game: Game) -> Player:
    return (Player(1), Player(2))[game.player == Player(1)]


def _get_legal_moves(game: Game) -> Generator[Move, None, None]:
    for i, j in POSSIBLE_MOVES:
        if game.board.state[i][j] == 0:
            yield Move(i, j)


def get_legal_moves(game: Game) -> List[Move]:
    return list(_get_legal_moves(game))


def get_move(game: Game) -> Move:
    legal_moves = get_legal_moves(game)
    return random.choice(legal_moves)


def _make_row(row: _Row, player: Player, i: int) -> _Row:
    return (
        int(player) if i == 0 else row[0],
        int(player) if i == 1 else row[1],
        int(player) if i == 2 else row[2])


def apply_move(
        board: Board,
        move: Move,
        player: Player,
) -> _Board:
    state = board.state
    i_row, i_col = move

    if state[i_row][i_col] != 0:
        raise ValueError('illegal move')

    state_new = (
        _make_row(state[0], player, i_col) if i_row == 0 else state[0],
        _make_row(state[1], player, i_col) if i_row == 1 else state[1],
        _make_row(state[2], player, i_col) if i_row == 2 else state[2])

    return state_new


def make_move(game: Game, move: Move) -> Game:
    move = get_move(game)
    state_new = apply_move(board=game.board, move=move, player=game.player)
    board = Board(state=state_new)
    player = get_next_player(game)
    winner = determine_winner(board)
    return Game(
        player=player,
        winner=winner,
        board=board,
    )


def init_game() -> Game:
    return Game(
        player=Player(1),
        winner=None,
        board=Board(),
    )


if __name__ == '__main__':
    game = init_game()
    print(game)
    print(_sum_board_rows(game.board))
    print(_sum_board_cols(game.board))
    print(_sum_board_diag(game.board))
    print(determine_winner(game.board))

    board2 = Board(((0, 1, 2), (0, 1, 0), (2, 1, 2)))
    print(board2)
    print(_sum_board_rows(board2))
    print(_sum_board_cols(board2))
    print(_sum_board_diag(board2))
    print(determine_winner(board2))

    board3 = _transpose_board(board2)
    print(board3)
    print(_sum_board_rows(board3))
    print(_sum_board_cols(board3))
    print(_sum_board_diag(board3))
    print(determine_winner(board3))

    board4 = Board(((1, 1, 2), (1, 2, 1), (2, 0, 2)))
    print(board4)
    print(_sum_board_rows(board4))
    print(_sum_board_cols(board4))
    print(_sum_board_diag(board4))
    print(determine_winner(board4))

    move = Move(1, 2)
    ii, jj = move
    import pdb; pdb.set_trace()
