from dataclasses import dataclass, replace
import random
import sys
from typing import Any, List, Tuple, Optional, Set


POSSIBLE_PLAYERS: Set[int] = {1, 2}
POSSIBLE_MOVES: Set[str] = {'r', 'c'}  # reroll, continue
POSSIBLE_EYES = {1, 2, 3, 4, 5, 6}
THRESHOLD = 50


@dataclass(frozen=True)
class Die:
    eye: int

    def __post_init__(self) -> None:
        if self.eye not in POSSIBLE_EYES:
            raise ValueError("Eyes must be from 1 to 6")

    def __repr__(self) -> str:
        return f"Die({self.eye})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Die):
            return self.eye == other.eye
        if isinstance(other, int):
            return self.eye == other
        return False

    def __hash__(self) -> int:
        return hash(self.eye)


_Dice = Tuple[Die, Die]


def roll() -> _Dice:
    eyes = list(POSSIBLE_EYES)
    return Die(random.choice(eyes)), Die(random.choice(eyes))


@dataclass(frozen=True)
class Move:
    m: str

    def __post_init__(self) -> None:
        if self.m not in POSSIBLE_MOVES:
            raise ValueError("Illegal move")

    def __repr__(self) -> str:
        return f"Move({self.m})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Move):
            eq: bool = self.m == other.m
            return eq
        if isinstance(other, str):
            eq_str: bool = self.m == other
            return eq_str
        return False

    def __hash__(self) -> int:
        return hash(self.m)

    def __lt__(self, other: Any) -> bool:
        eq: bool = self.m < other.m
        return eq


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
    def _ask_input(self) -> Move:  # pylint: disable=no-self-use
        inp = input("choose next move: ")
        if inp == 'q':
            sys.exit(0)

        try:
            move = Move(inp)
        except (TypeError, NameError):
            sys.exit(1)
        return move

    def next_move(self, game: 'Game') -> Move:
        moves = get_legal_moves(game)
        print(f"playing last possible move: {moves[0]}", flush=True)
        if len(moves) == 1:
            return moves[0]

        print("possible moves: ", sorted(moves, key=lambda m: m.m), flush=True)

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
    dice: _Dice
    state: Tuple[int, int, int] = (0, 4, THRESHOLD)
    rerolled: bool = False

    def __repr__(self) -> str:
        line = "-" * 24
        dice = f"{self.dice[0].eye} + {self.dice[1].eye}"
        header = f"dice: {dice} | target: {self.state[2]}"
        players = "   player 1 | player 2"
        scores = "   {: >8} | {: <8}".format(self.state[0], self.state[1])
        return "\n".join((line, header, players, scores, ""))

    def __eq__(self, other: Any) -> bool:
        try:
            res: bool = self.state == other.state
            return res
        except (TypeError, AttributeError):
            return False

    def __len__(self) -> int:
        return len(self.state)

    def __hash__(self) -> int:
        return hash((self.state, self.rerolled, self.dice))


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


def determine_winner(game: Game) -> MaybePlayer:
    board = game.board

    s0, s1, target = board.state

    if (s0 < target) & (s1 < target):
        return None

    if s0 >= target:
        return Player(1)

    return Player(2)


def get_next_player_idx(game: Game) -> int:
    return int(game.player == Player(1))


def get_legal_moves(game: Game) -> List[Move]:
    if game.winner:
        return []

    if game.board.rerolled:
        return [Move('c')]

    return [Move('r'), Move('c')]


def apply_move(
        board: Board,
        move: Move,
        player: Player = Player(1),
) -> Board:
    state = board.state

    if (move == 'r') and board.rerolled:
        raise ValueError('Illegal move')

    dice = roll()
    if move == 'r':
        return replace(board, rerolled=True, dice=dice)

    eyes = sum(die.eye for die in board.dice)
    state_new = (
        state[0] + eyes if player == 1 else state[0],
        state[1] + eyes if player == 2 else state[1],
        state[2])

    return Board(state=state_new, dice=dice)


def init_move(s: str) -> Move:
    return Move(s)


def init_player(i: int) -> Player:
    return Player(i)


def make_move(game: Game, move: Move) -> Game:
    board = apply_move(board=game.board, move=move, player=game.player)

    if move == 'c':  # change player only on continue
        player_idx = get_next_player_idx(game)
    else:
        player_idx = game.player_idx

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
    board_: Board = board if board is not None else Board(dice=roll())
    return Game(
        players=(Player(1), Player(2)),
        board=board_,
        player_idx=player_idx,
    )
