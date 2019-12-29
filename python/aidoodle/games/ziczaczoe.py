from dataclasses import dataclass
from functools import total_ordering
from itertools import product
import random
from typing import Any, List, Tuple, Optional, Generator, Set


POSSIBLE_PLAYERS: Set[int] = {-1, 1, 2}  # -1 <- tied
POSSIBLE_MOVES: Set[Tuple[int, int]] = set(product(range(5), range(5)))


@dataclass(frozen=True)
@total_ordering
class Move:
    i: int
    j: int

    def __post_init__(self) -> None:
        if (self.i, self.j) not in POSSIBLE_MOVES:
            raise ValueError("Impossible move")

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
        if not isinstance(other, Move):
            raise TypeError
        return (self.i, self.j) < (other.i, other.j)

    def __hash__(self) -> int:
        return hash((self.i, self.j))


@dataclass(frozen=True)
class Player:
    i: int

    def __post_init__(self) -> None:
        if self.i not in POSSIBLE_PLAYERS:
            raise ValueError("Illegal player")

    def __repr__(self) -> str:
        if self.i == -1:
            return "tied"
        return f"Player({self.i})"

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
_Row = Tuple[int, int, int, int, int]
_Triple = Tuple[int, int, int]


@dataclass(frozen=True)
@total_ordering
class Board:
    state: Tuple[_Row, _Row, _Row, _Row, _Row] = (
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0),
        (0, 0, 0, 0, 0))

    def _rrow(self, i: int) -> str:
        row = self.state[i]
        srow = "|{}|{}|{}|{}|{}|".format(*row)
        srow = srow.replace("0", " ").replace("1", "x").replace("2", "o").replace("9", "-")
        return srow

    def __repr__(self) -> str:
        return "\n".join((
            "",
            "   0 1 2 3 4",
            "0 " + self._rrow(0),
            "1 " + self._rrow(1),
            "2 " + self._rrow(2),
            "3 " + self._rrow(3),
            "4 " + self._rrow(4),
            "",
        ))

    def __iter__(self) -> Generator[_Row, None, None]:
        yield from self.state

    def __eq__(self, other: Any) -> bool:
        try:
            res: bool = self.state == other.state
            return res
        except (TypeError, AttributeError):
            return False

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Board):
            raise TypeError
        return self.state < other.state

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


def transpose_board(board: Board) -> Board:
    row0, row1, row2, row3, row4 = tuple(zip(*board.state))
    return Board((row0, row1, row2, row3, row4))


def mirror_board(board: Board) -> Board:
    state = board.state
    return Board((
        state[0][::-1],
        state[1][::-1],
        state[2][::-1],
        state[3][::-1],
        state[4][::-1]))


def _yield_triples(board: Board, n: int, w: int) -> Generator[_Triple, None, None]:
    state = board.state
    r = range(0, n - w + 1)
    r2 = range(n - 3, -1, -1)  # contra-diag

    for row in state:
        for i in r:
            yield row[i], row[i + 1], row[i + 2]

    for row in transpose_board(board):
        for i in r:
            yield row[i], row[i + 1], row[i + 2]

    for i, j in product(r, r):
        try:
            yield state[i][j], state[i + 1][j + 1], state[i + 2][j + 2]
        except IndexError:
            pass

    for i, j in product(r, r):
        try:
            yield state[i][j + 2], state[i + 1][j + 1], state[i + 2][j]
        except IndexError:
            pass


# pylint: disable=too-many-return-statements
def determine_winner(game: Game) -> MaybePlayer:
    board = game.board
    players = game.players
    s1 = {1}
    s2 = {2}

    n = len(board.state)
    w = 3  # need w in a row to win
    for row in _yield_triples(board, n=n, w=w):
        #if sum(t == 1 for t in row) == 3:
        if set(row) == s1:
            return players[0]
        #if sum(t == 2 for t in row) == 3:
        if set(row) == s2:
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
        legal_moves = list(_get_all_moves(game.board))
        return legal_moves
    return []


def _make_row(row: _Row, player: Player, i: int) -> _Row:
    return (
        int(player) if i == 0 else row[0],
        int(player) if i == 1 else row[1],
        int(player) if i == 2 else row[2],
        int(player) if i == 3 else row[3],
        int(player) if i == 4 else row[4])


def apply_move(
        board: Board,
        move: Move,
        player: Player,
) -> Board:
    state = board.state
    i_row, i_col = move

    if state[i_row][i_col] != 0:
        raise ValueError('Illegal move')

    state_new = (
        _make_row(state[0], player, i_col) if i_row == 0 else state[0],
        _make_row(state[1], player, i_col) if i_row == 1 else state[1],
        _make_row(state[2], player, i_col) if i_row == 2 else state[2],
        _make_row(state[3], player, i_col) if i_row == 3 else state[3],
        _make_row(state[4], player, i_col) if i_row == 4 else state[4])

    return Board(state=state_new)


def init_move(
        s: str,
        game: Optional[Game] = None,  # pylint: disable=unused-argument
) -> Move:
    i: int
    j: int
    i, j = eval(s)
    return Move(i, j)


def init_player(i: int) -> Player:
    return Player(i)


def make_move(game: Game, move: Move) -> Game:
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

    raise ValueError("Illegal player")


def game_score(game: Game) -> float:
    if game.winner is None:
        raise ValueError("Game is not over, no score yet")

    return winner_to_score(game.winner)


def _random_row() -> _Row:
    choices = [0, 0, 0, 9]
    c = random.choice
    return (c(choices), c(choices), c(choices), c(choices), c(choices))


def random_board() -> Board:
    # 9 codes for blocked
    return Board((
        _random_row(),
        _random_row(),
        _random_row(),
        _random_row(),
        _random_row()))


def init_game(board: MaybeBoard = None, player_idx: int = 0) -> Game:
    if board is None:
        return init_game(
            board=random_board(),
            player_idx=player_idx,
        )

    return Game(
        players=(Player(1), Player(2)),
        board=board,
        player_idx=player_idx,
    )
