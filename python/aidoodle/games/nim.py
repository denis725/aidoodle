from dataclasses import dataclass
from functools import total_ordering
import random
from typing import Any, List, Tuple, Optional, Generator, Set


POSSIBLE_PLAYERS: Set[int] = {1, 2}
POSSIBLE_HEAPS: Set[int] = {0, 1, 2}


@dataclass(frozen=True)
@total_ordering
class Move:
    i: int  # the heap
    j: int  # the amount

    def __post_init__(self) -> None:
        if self.i not in POSSIBLE_HEAPS:
            raise ValueError("Impossible heap")
        if self.j < 1:
            raise ValueError("You have to take at least one stone")

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


@dataclass(frozen=True)
class Board:
    state: Tuple[int, int, int] = (3, 4, 5)

    def __repr__(self) -> str:
        header = "\n|" + "|".join(map(str, range(len(self)))) + "|\n"
        header += "|" + "+".join('-' for _ in range(len(self))) + "|\n"
        return header + "|" + "|".join(map(str, self.state)) + "|\n"

    def __eq__(self, other: Any) -> bool:
        try:
            res: bool = self.state == other.state
            return res
        except (TypeError, AttributeError):
            return False

    def __iter__(self) -> Generator[int, None, None]:
        yield from self.state

    def __len__(self) -> int:
        return len(self.state)

    def __hash__(self) -> int:
        return hash(self.state)


MaybeBoard = Optional[Board]


def make_random_board() -> Board:
    return Board(state=(
        random.randint(3, 6),
        random.randint(3, 6),
        random.randint(3, 6)))


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


def determine_winner(game: Game) -> MaybePlayer:
    board = game.board

    if sum(board) != 0:  # not yet empty
        return None

    # last player to have taken a stone loses
    return game.player


def get_next_player_idx(game: Game) -> int:
    return int(game.player == Player(1))


def _get_all_moves(board: Board) -> Generator[Move, None, None]:
    for i, n in enumerate(board):
        if n == 0:
            continue

        for j in range(1, n + 1):
            yield Move(i, j)


def get_legal_moves(game: Game) -> List[Move]:
    if game.winner:
        return []

    return list(_get_all_moves(game.board))


def apply_move(
        board: Board,
        move: Move,
        player: Player = Player(1),  # pylint: disable=unused-argument
) -> Board:
    state = board.state
    i_heap, n_stones = move

    if state[i_heap] < n_stones:
        raise ValueError('illegal move')

    state_new = (
        state[0] - n_stones if i_heap == 0 else state[0],
        state[1] - n_stones if i_heap == 1 else state[1],
        state[2] - n_stones if i_heap == 2 else state[2])

    return Board(state=state_new)


def init_move(s: str) -> Move:
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

    raise ValueError("Illegal player")


def init_game(board: MaybeBoard = None, player_idx: int = 0) -> Game:
    board_: Board = board if board is not None else make_random_board()
    return Game(
        players=(Player(1), Player(2)),
        board=board_,
        player_idx=player_idx,
    )
