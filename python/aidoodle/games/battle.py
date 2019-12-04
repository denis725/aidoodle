from dataclasses import dataclass, replace
import enum
import random
from typing import Any, Dict, Generator, List, Tuple, Optional, Set, Union


StrOrInt = Union[str, int]
POSSIBLE_PLAYERS: Set[int] = {1, 2}
POSSIBLE_ROWS: Set[int] = {0, 1}
POSSIBLE_POSITIONS: Set[int] = {0, 1, 2, 3, 4}
POSSIBLE_OTHER_ACTIONS: Set[str] = {'h'}
POSSIBLE_ACTIONS = POSSIBLE_POSITIONS | POSSIBLE_OTHER_ACTIONS
HEAL = 2


class Attack(enum.Enum):
    sword = 0
    bow = 1


@dataclass
class DamageRange:
    i: int  # min damage, inclusive
    j: int  # max damage, inclusive

    def __post_init__(self) -> None:
        if self.i > self.j:
            raise ValueError("Min damage must be less than or equal to max")
        if self.j < 0:
            raise ValueError("Damage cannot be negative")


DAMAGE: Dict[Attack, DamageRange] = {
    Attack.sword: DamageRange(2, 4),
    Attack.bow: DamageRange(1, 3),
}


@dataclass(frozen=True)
class Unit:
    owner: 'Player'
    hp: int
    hp_max: int
    attack: Attack

    def __post_init__(self) -> None:
        if self.hp > self.hp_max:
            raise ValueError("HPs exceed max HPs")


@dataclass(frozen=True)
class Melee(Unit):
    hp: int = 9
    hp_max: int = 9
    attack: Attack = Attack.sword

    def __repr__(self) -> str:
        return f"{self.__class__.__name__[:1]}({self.hp})"


@dataclass(frozen=True)
class Ranger(Unit):
    hp: int = 5
    hp_max: int = 5
    attack: Attack = Attack.bow

    def __repr__(self) -> str:
        return f"{self.__class__.__name__[:1]}({self.hp})"


MaybeUnit = Optional[Unit]


@dataclass(frozen=True)
class Move:
    row_idx: int
    pos: StrOrInt

    def __post_init__(self) -> None:
        if self.row_idx not in POSSIBLE_ROWS:
            raise ValueError("Illegal move")
        if self.pos not in POSSIBLE_ACTIONS:
            raise ValueError("Illegal move")

    def __repr__(self) -> str:
        if self.pos == 'h':
            return "(h)eal"
        if isinstance(self.pos, int):
            return f"Attack {self.pos}"
        raise ValueError("Illegal move")

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Move):
            eq: bool = self.pos == other.pos
            return eq
        return False

    def __hash__(self) -> int:
        return hash((self.row_idx, self.pos))

    @staticmethod
    def _pos_lt(pos: StrOrInt) -> int:
        if pos == 'h':
            return -999
        if isinstance(pos, int):
            return pos
        raise ValueError("Illegal move")

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Move):
            raise TypeError

        rs, ps = self.row_idx, self._pos_lt(self.pos)
        ro, po = other.row_idx, self._pos_lt(other.pos)
        eq: bool = (rs, ps) < (ro, po)
        return eq


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
Row = Tuple[MaybeUnit, MaybeUnit, MaybeUnit, MaybeUnit, MaybeUnit]


def init_player(i: int) -> Player:
    return Player(i)


@dataclass(frozen=True)
class Board:
    state: Tuple[Row, Row]
    active_idx: Tuple[int, int]
    last_action: str = "start"
    # unfortunately, we need to keep track of rounds, otherwise there
    # can be cycles in the game tree
    round: int = 0

    def __post_init__(self) -> None:
        i, j = self.active_idx
        if i not in (0, 1):
            raise ValueError("Illegal board")
        if j not in POSSIBLE_POSITIONS:
            raise ValueError("Illegal board")
        for unit in self.state[0]:
            if (unit is not None) and (unit.owner != 1):
                raise ValueError("Unit assigned to wrong player")
        for unit in self.state[1]:
            if (unit is not None) and (unit.owner != 2):
                raise ValueError("Unit assigned to wrong player")

    @property
    def active(self) -> Unit:
        i, j = self.active_idx
        unit = self.state[i][j]
        if unit is None:
            raise ValueError("Active unit not found")
        return unit

    def _repr_units(self, row_idx: int) -> Generator[str, None, None]:
        for unit in self.state[row_idx]:
            if unit is None:
                yield " " * 6
            elif unit is self.active:
                yield f" {unit}*"
            else:
                yield f" {unit} "

    def __repr__(self) -> str:
        s_round = f"Round {self.round} | {self.last_action}"
        positions = "|".join("   {}  ".format(i) for i in range(5))
        header = positions + "     " + positions
        units = "|".join(self._repr_units(0))
        units += " > < "
        units += "|".join(self._repr_units(1))
        return "\n".join((
            "",
            s_round,
            header,
            units,
            "",
        ))

    def __eq__(self, other: Any) -> bool:
        try:
            res: bool = (
                (self.state == other.state)
                and (self.active == other.active)
                and (self.round == other.round)
            )
            return res
        except (TypeError, AttributeError):
            return False

    def __hash__(self) -> int:
        return hash((self.state, self.active, self.round))


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
    row0, row1 = game.board.state

    if not any(row0):
        if not any(row1):
            return Player(-1)  # tied
        return Player(2)

    if not any(row1):
        return Player(1)

    return None


def yield_enemy_unit_positions(game: Game) -> Generator[int, None, None]:
    row0, row1 = game.board.state
    row = row1 if game.player == 1 else row0
    for i, maybe_unit in enumerate(row):
        if maybe_unit is not None:
            yield i


def get_next_player_idx(game: Game) -> int:
    active = game.board.active
    row0, row1 = game.board.state

    if active in row0:
        return 0
    if active in row1:
        return 1
    raise ValueError("Illegal active unit")


def get_legal_moves(game: Game) -> List[Move]:
    if game.winner:
        return []

    player = game.player
    enemy_idx = 1 if player == 1 else 0
    enemy_unit_positions = tuple(yield_enemy_unit_positions(game))

    unit = game.board.active
    if unit.hp < unit.hp_max:
        heal = [Move(enemy_idx, 'h')]
    else:
        heal = []

    if isinstance(unit, Ranger):
        return heal + [Move(enemy_idx, pos) for pos in enemy_unit_positions]

    if isinstance(unit, Melee):
        if player == 1:
            return heal + [Move(enemy_idx, pos) for pos in enemy_unit_positions[:2]]
        return heal + [Move(enemy_idx, pos) for pos in enemy_unit_positions[-2:]]

    raise ValueError("Unknown unit type")


def place_unit(row: Row, pos: int, unit: MaybeUnit) -> Row:
    return (
        unit if pos == 0 else row[0],
        unit if pos == 1 else row[1],
        unit if pos == 2 else row[2],
        unit if pos == 3 else row[3],
        unit if pos == 4 else row[4])


def resolve_damage(unit: Unit, damage: int) -> MaybeUnit:
    hp_new = unit.hp - damage
    if hp_new < 1:
        return None
    return replace(unit, hp=hp_new)


def next_active_unit_idx(board: Board) -> Tuple[int, int]:
    units_and_indices = [
        (u, (0, i)) for i, u in enumerate(board.state[0]) if u is not None]
    units_and_indices += [
        (u, (1, i)) for i, u in enumerate(board.state[1]) if u is not None]

    if not units_and_indices:
        raise ValueError("No units on board")

    i = 0
    for i, (unit, _) in enumerate(units_and_indices):
        if unit is board.active:
            break

    return units_and_indices[(i + 1) % len(units_and_indices)][1]


def _apply_non_attack(board: Board, row_idx: int, pos: str) -> Board:
    if pos not in POSSIBLE_OTHER_ACTIONS:
        raise ValueError("Illegal move")

    # apply healing
    unit_before = board.active
    hp_new = min(unit_before.hp + HEAL, unit_before.hp_max)
    unit_after = replace(unit_before, hp=hp_new)

    row = board.state[row_idx]
    unit_pos = row.index(unit_before)
    row_after = place_unit(row=row, pos=unit_pos, unit=unit_after)
    state_new = (
        row_after if row_idx == 0 else board.state[0],
        row_after if row_idx == 1 else board.state[1])

    last_action = f"healed {unit_before} for {HEAL} HP"
    return replace(
        board,
        state=state_new,
        last_action=last_action,
    )


def _resolve_damage(attack: Attack) -> int:
    damage_range = DAMAGE[attack]
    damage = random.randint(damage_range.i, damage_range.j)
    return damage


def _apply_attack(board: Board, row_idx: int, pos: int) -> Board:
    unit_target = board.state[row_idx][pos]
    if unit_target is None:
        raise ValueError("illegal move")

    damage = _resolve_damage(board.active.attack)
    unit_after = resolve_damage(unit=unit_target, damage=damage)
    row_after = place_unit(board.state[row_idx], pos=pos, unit=unit_after)
    state_new = (
        row_after if row_idx == 0 else board.state[0],
        row_after if row_idx == 1 else board.state[1])

    last_action = f"attacked {unit_target} for {damage} damage"
    return replace(
        board,
        state=state_new,
        last_action=last_action,
    )


def apply_move(
        board: Board,
        move: Move,
        player: Player = Player(1),  # pylint: disable=unused-argument
) -> Board:
    row_idx, pos = move.row_idx, move.pos
    if isinstance(pos, str):  # non-attack move
        board_new = _apply_non_attack(board=board, row_idx=1 - row_idx, pos=pos)
    elif isinstance(pos, int):
        board_new = _apply_attack(board=board, row_idx=row_idx, pos=pos)
    else:
        raise ValueError

    active_idx = next_active_unit_idx(board_new)
    return replace(board_new, round=board.round + 1, active_idx=active_idx)


def init_move(
        s: str,
        game: Game,
) -> Move:
    row_idx: int = 1 - game.player_idx
    if s in POSSIBLE_OTHER_ACTIONS:
        return Move(row_idx=row_idx, pos=s)

    try:
        pos = int(s)
    except (TypeError, ValueError):
        raise ValueError(f"Illegal move {s}")
    return Move(row_idx=row_idx, pos=pos)


def make_move(game: Game, move: Move) -> Game:
    board = apply_move(board=game.board, move=move, player=game.player)
    game = replace(game, board=board)
    player_idx = get_next_player_idx(game)
    game = replace(game, player_idx=player_idx)
    return game


def winner_to_score(winner: Player) -> float:
    if winner == 1:
        return 1.0
    if winner == 2:
        return 0.0
    if winner == -1:  # tie
        return 0.5

    raise ValueError("Illegal player")


def init_game(board: MaybeBoard = None, player_idx: int = 0) -> Game:
    p1 = Player(1)
    p2 = Player(2)
    if board is not None:
        board_ = board
    else:
        row0 = (Ranger(owner=p1), Ranger(owner=p1), Melee(owner=p1), None, None)
        row1 = (Melee(owner=p2), Ranger(owner=p2), Ranger(owner=p2), None, None)
        board_ = Board(
            state=(row0, row1),
            active_idx=(0, 2),
        )

    return Game(
        players=(p1, p2),
        board=board_,
        player_idx=player_idx,
    )
