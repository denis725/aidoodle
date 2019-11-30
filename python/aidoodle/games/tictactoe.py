from dataclasses import dataclass
from functools import total_ordering
from itertools import product
import random
import sys
from typing import Any, List, Tuple, Optional, Generator, Set


POSSIBLE_PLAYERS: Set[int] = {-1, 1, 2}  # -1 <- tied
POSSIBLE_MOVES: Set[Tuple[int, int]] = set(product(range(3), range(3)))


@dataclass(frozen=True)
@total_ordering
class Move:
    i: int
    j: int

    def __post_init__(self) -> None:
        if (self.i, self.j) not in POSSIBLE_MOVES:
            raise ValueError

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

    def __lt__(self, other: Any) -> bool:
        return (self.i, self.j) < (other.i, other.j)

    def __hash__(self) -> int:
        return hash((self.i, self.j))


class Agent:
    def next_move(self, game: 'Game') -> Move:
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.__class__.__name__


class RandomAgent(Agent):
    def next_move(self, game: 'Game') -> Move:
        legal_moves = get_legal_moves(game)
        return random.choice(legal_moves)


class CliInputAgent(Agent):
    def _ask_input(self) -> Move:
        inp = input("choose next move: ")
        if inp == 'q':
            sys.exit(0)

        try:
            move = Move(*eval(inp))
        except (TypeError, NameError):
            sys.exit(1)
        return move

    def next_move(self, game: 'Game') -> Move:
        moves = get_legal_moves(game)
        print("possible moves: ", sorted(moves), flush=True)

        move = self._ask_input()
        while move not in moves:
            move = self._ask_input()

        print(f"performing move {move}", flush=True)
        return move

    def __repr__(self) -> str:
        return "You"


@dataclass(frozen=True)
class Player:
    i: int
    agent: Agent = RandomAgent()

    def __post_init__(self) -> None:
        if self.i not in POSSIBLE_PLAYERS:
            raise ValueError

    def __repr__(self) -> str:
        if self.i == -1:
            return "tied"
        return f"Player({self.i}, {self.agent})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Player):
            return self.i == other.i
        if isinstance(other, int):
            return self.i == other
        return False

    def __int__(self) -> int:
        return self.i

    def __hash__(self) -> int:
        return hash(self.i)


MaybePlayer = Optional[Player]
_Row = Tuple[int, int, int]


@dataclass(frozen=True)
class Board:
    state: Tuple[_Row, _Row, _Row] = (
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0))

    def _rrow(self, i: int) -> str:
        row = self.state[i]
        srow = "|{}|{}|{}|".format(*row)
        srow = srow.replace("0", " ").replace("1", "x").replace("2", "o")
        return srow

    def __repr__(self) -> str:
        return "\n".join((
            "",
            "   0 1 2",
            "0 " + self._rrow(0),
            "1 " + self._rrow(1),
            "2 " + self._rrow(2),
        ))

    def __iter__(self) -> Generator[_Row, None, None]:
        yield from self.state

    def __eq__(self, other: Any) -> bool:
        try:
            res: bool = self.state == other.state
            return res
        except (TypeError, AttributeError):
            return False

    def __hash__(self) -> int:
        return hash(self.state)


MaybeBoard = Optional[Board]


@dataclass(frozen=True)
class Game:
    players: Tuple[Player, Player]
    board: Board
    player_idx: int = 0

    @property
    def winner(self) -> MaybePlayer:
        return determine_winner(self)

    @property
    def player(self) -> Player:
        return self.players[self.player_idx]


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


def determine_winner(game: Game) -> MaybePlayer:
    board = game.board
    players = game.players

    # test row winner
    sum_row_1, sum_row_2 = _sum_board_rows(board)
    if sum_row_1 == 3:
        return players[0]
    if sum_row_2 == 3:
        return players[1]

    # test col winner
    sum_col_1, sum_col_2 = _sum_board_cols(board)
    if sum_col_1 == 3:
        return players[0]
    if sum_col_2 == 3:
        return players[1]

    # test diag winner
    sum_diag_1, sum_diag_2 = _sum_board_diag(board)
    if sum_diag_1 == 3:
        return players[0]
    if sum_diag_2 == 3:
        return players[1]

    if not get_possible_moves(game):
        # codes for tied
        return Player(-1)

    # no winner
    return None


def get_next_player_idx(game: Game) -> int:
    return int(game.player == Player(1))


def _get_all_moves(board: Board) -> Generator[Move, None, None]:
    for i, j in POSSIBLE_MOVES:
        if board.state[i][j] == 0:
            yield Move(i, j)


def get_possible_moves(game: Game) -> List[Move]:
    return list(_get_all_moves(game.board))


def get_legal_moves(game: Game) -> List[Move]:
    if not game.winner:
        return list(_get_all_moves(game.board))
    return []


def get_move(game: Game) -> Move:
    return game.player.agent.next_move(game)


def _make_row(row: _Row, player: Player, i: int) -> _Row:
    return (
        int(player) if i == 0 else row[0],
        int(player) if i == 1 else row[1],
        int(player) if i == 2 else row[2])


def apply_move(
        board: Board,
        move: Move,
        player: Player,
) -> Board:
    state = board.state
    i_row, i_col = move

    if state[i_row][i_col] != 0:
        raise ValueError('illegal move')

    state_new = (
        _make_row(state[0], player, i_col) if i_row == 0 else state[0],
        _make_row(state[1], player, i_col) if i_row == 1 else state[1],
        _make_row(state[2], player, i_col) if i_row == 2 else state[2])

    return Board(state=state_new)


def make_move(game: Game, move: Optional[Move] = None) -> Game:
    if move is None:
        move = get_move(game)

    board = apply_move(board=game.board, move=move, player=game.player)
    player_idx = get_next_player_idx(game)
    return Game(
        players=game.players,
        board=board,
        player_idx=player_idx,
    )


def winner_to_score(winner: Player) -> float:
    if winner == 1:
        return 1.0
    if winner == 2:
        return 0.0
    if winner == -1:  # tie
        return 0.5

    raise ValueError



def init_game(board: MaybeBoard = None, player_idx: int = 0) -> Game:
    board_: Board = board if board is not None else Board()
    return Game(
        players=(Player(1), Player(2)),
        board=board_,
        player_idx=player_idx,
    )
