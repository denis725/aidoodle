from dataclasses import dataclass, field, replace
import enum
from functools import partial
import random
from typing import Any, Dict, Generator, List, Optional, Set, Tuple, Type, Union


POSSIBLE_PLAYERS: Set[int] = {1, 2}
POSSIBLE_POSITIONS: Set[int] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}


class Attack(enum.Enum):
    sword = "sword"
    bow = "bow"


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


class Defense(enum.Enum):
    heal = 0

HEAL = 2


class _Buff(enum.Enum):
    damage = "damage"
    shield = "shield"


@dataclass(frozen=True)
class Buff:
    round: int
    buff: _Buff


DamageBuff = partial(Buff, buff=_Buff.damage)
ShieldBuff = partial(Buff, buff=_Buff.shield)


BUFF_DAMAGE = 1
BUFF_SHIELD = 2


class UnitRel(enum.Enum):
    "Relationship of unit to other units"
    none = enum.auto()
    itself = enum.auto()
    ally = enum.auto()
    enemy = enum.auto()


@dataclass(frozen=True)
class Unit:
    # pylint: disable=too-many-instance-attributes
    owner: 'Player'
    hp: int
    hp_max: int
    range: int

    attack: Attack   # on enemy
    defend: Defense  # on itself
    buff: _Buff    # on ally

    buffs: Tuple[Buff, ...] = field(default_factory=tuple)
    queued: bool = True

    def __post_init__(self) -> None:
        if self.hp > self.hp_max:
            raise ValueError("HPs exceed max HPs")

    def _repr_buffs(self) -> str:
        if not self.buffs:
            return ""

        repr_buffs: List[str] = []

        buffs_damage = [b for b in self.buffs if b.buff == _Buff.damage]
        if buffs_damage:
            repr_buffs.append(f"D:{BUFF_DAMAGE * len(buffs_damage)}")

        buffs_shield = [b for b in self.buffs if b.buff == _Buff.shield]
        if buffs_shield:
            repr_buffs.append(f"S:{BUFF_SHIELD * len(buffs_shield)}")

        return "|".join(repr_buffs)

    def __repr__(self) -> str:
        reprs: List[str] = [f"{self.hp}HP"]
        buffs = self._repr_buffs()
        if buffs:
            reprs.append(buffs)
        r = f"{self.__class__.__name__[:1]}(" + " ".join(reprs) + ")"
        return r


@dataclass(frozen=True)
class Melee(Unit):
    hp: int = 9
    hp_max: int = 9
    range: int = 2

    attack: Attack = Attack.sword
    defend: Defense = Defense.heal
    buff: _Buff = _Buff.shield

    def __repr__(self) -> str:
        return super().__repr__()


@dataclass(frozen=True)
class Ranger(Unit):
    hp: int = 5
    hp_max: int = 5
    range: int = 10

    attack: Attack = Attack.bow
    defend: Defense = Defense.heal
    buff: _Buff = _Buff.damage

    def __repr__(self) -> str:
        return super().__repr__()


MaybeUnit = Optional[Unit]


@dataclass(frozen=True)
class Move:
    pos: int

    def __post_init__(self) -> None:
        if self.pos not in POSSIBLE_POSITIONS:
            raise ValueError("Illegal move")

    def __repr__(self) -> str:
        return f"Move({self.pos})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Move):
            eq: bool = self.pos == other.pos
            return eq
        return False

    def __hash__(self) -> int:
        return hash(self.pos)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Move):
            raise TypeError

        eq: bool = self.pos < other.pos
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
Row = Tuple[MaybeUnit, MaybeUnit, MaybeUnit, MaybeUnit, MaybeUnit,
            MaybeUnit, MaybeUnit, MaybeUnit, MaybeUnit, MaybeUnit]


def init_player(i: int) -> Player:
    return Player(i)


@dataclass(frozen=True)
class Board:
    state: Row
    active_idx: int
    last_action: str = "start"
    # unfortunately, we need to keep track of turns, otherwise there
    # can be cycles in the game tree
    turn: int = 1
    round: int = 1

    def __post_init__(self) -> None:
        if self.active_idx not in POSSIBLE_POSITIONS:
            raise ValueError("Illegal board")
        for unit in self.state:
            if (unit is not None) and (unit.owner not in (1, 2)):
                raise ValueError("Unit assigned to illegal player")

    @property
    def active(self) -> Unit:
        i = self.active_idx
        unit = self.state[i]
        if unit is None:
            raise ValueError("Active unit not found")
        return unit

    def target(self, i: int) -> Unit:
        unit = self.state[i]
        if unit is None:
            raise ValueError("Illegal target")

        return unit

    @property
    def state_dense(self) -> List[Unit]:
        return [unit for unit in self.state if unit is not None]

    def _repr_units(self, i: int) -> Generator[str, None, None]:
        side = self.state[:5] if i == 0 else self.state[5:]
        for unit in side:
            if unit is None:
                yield " " * 3
            elif unit is self.active:
                yield f" {unit!r}*"
            elif unit.queued:
                yield f" {unit!r}+"
            else:
                yield f" {unit!r} "

    def __repr__(self) -> str:
        s_round = f"Round {self.round} | {self.last_action}"

        repr_units_l = list(self._repr_units(0))
        repr_units_r = list(self._repr_units(1))

        numbers_l = (f" {i}" + " " * (len(r) - 2) for i, r in enumerate(
            repr_units_l))
        numbers_r = (f" {i}" + " " * (len(r) - 2) for i, r in enumerate(
            repr_units_r, start=5))
        sep = " | "

        return "\n".join((
            "",
            s_round,
            "",
            f"Player 1",
            sep.join(numbers_l),
            sep.join(repr_units_l),
            "",
            f"Player 2",
            sep.join(numbers_r),
            sep.join(repr_units_r),
            "\n",
        ))

    def __eq__(self, other: Any) -> bool:
        try:
            res: bool = (
                (self.state == other.state)
                and (self.active_idx == other.active_idx)
                and (self.round == other.round)
            )
            return res
        except (TypeError, AttributeError):
            return False

    def __hash__(self) -> int:
        return hash((self.state, self.active_idx, self.turn))


MaybeBoard = Optional[Board]


@dataclass(frozen=True)
class Game:
    players: Tuple[Player, Player]
    board: Board
    board_init: Board
    player_idx: int = 0

    @property
    def winner(self) -> MaybePlayer:
        return determine_winner(self)

    @property
    def player(self) -> Player:
        return self.players[self.player_idx]


def determine_winner(game: Game) -> MaybePlayer:
    state = game.board.state
    units_player1 = sum(1 for unit in state if unit and unit.owner == 1)
    units_player2 = sum(1 for unit in state if unit and unit.owner == 2)

    if not units_player1:
        if not units_player2:
            return Player(-1)  # tied
        return Player(2)

    if not units_player2:
        return Player(1)

    return None


def get_next_player_idx(game: Game) -> int:
    active = game.board.active
    return game.players.index(active.owner)


def get_unit_rel(unit: Unit, target: MaybeUnit) -> UnitRel:
    if target is None:
        return UnitRel.none

    if unit is target:
        return UnitRel.itself

    if unit.owner == target.owner:
        return UnitRel.ally

    return UnitRel.enemy


def _yield_rels(unit: Unit, board: Board) -> Generator[UnitRel, None, None]:
    return (get_unit_rel(unit=unit, target=target) for target in board.state)


def within_distance(board: Board, target: Unit) -> bool:
    unit = board.active
    idx_unit = board.state_dense.index(unit)
    idx_target = board.state_dense.index(target)
    return abs(idx_unit - idx_target) <= unit.range


def _yield_legal_moves(board: Board) -> Generator[int, None, None]:
    for idx_target, rel in enumerate(_yield_rels(board.active, board)):
        if rel is UnitRel.none:
            continue

        target = board.target(idx_target)

        if rel == UnitRel.enemy:
            if within_distance(board, target):
                yield idx_target
                continue

        if rel == UnitRel.itself:
            if target.hp < target.hp_max:
                yield idx_target
                continue

        if rel == UnitRel.ally:
            yield idx_target


def get_legal_moves(game: Game) -> List[Move]:
    if game.winner:
        return []

    board = game.board
    moves = [Move(idx_target) for idx_target in _yield_legal_moves(board)]
    return moves


def place_unit(row: Row, pos: int, unit: MaybeUnit) -> Row:
    return (
        unit if pos == 0 else row[0],
        unit if pos == 1 else row[1],
        unit if pos == 2 else row[2],
        unit if pos == 3 else row[3],
        unit if pos == 4 else row[4],
        unit if pos == 5 else row[5],
        unit if pos == 6 else row[6],
        unit if pos == 7 else row[7],
        unit if pos == 8 else row[8],
        unit if pos == 9 else row[9])


def _next_active_unit(row: Row, i: int) -> int:
    j = i + 1
    if row[j % 10] is None:
        return _next_active_unit(row, j)
    return j % 10


def next_active_unit_idx(board: Board) -> int:
    return _next_active_unit(board.state, i=board.active_idx)


def _apply_defense(board: Board) -> Board:
    if board.active.defend == Defense.heal:
        return _apply_heal(board)

    raise ValueError("Illegal defense")


def _apply_heal(board: Board) -> Board:
    # apply healing
    unit = board.active
    hp_after = min(unit.hp + HEAL, unit.hp_max)
    unit_after = replace(unit, hp=hp_after)
    healed = unit_after.hp - unit.hp

    row = board.state
    unit_pos = row.index(unit)
    row_after = place_unit(row=row, pos=unit_pos, unit=unit_after)

    last_action = f"healed {unit_after.__class__.__name__} for {healed} HP"
    return replace(
        board,
        state=row_after,
        last_action=last_action,
    )


def _resolve_damage(unit: Unit, target: Unit) -> int:
    attack = unit.attack
    damage_range = DAMAGE[attack]
    damage_raw = random.randint(damage_range.i, damage_range.j)
    blocked = sum(BUFF_SHIELD for b in target.buffs if b.buff == _Buff.shield)
    damage_extra = sum(BUFF_DAMAGE for b in unit.buffs if b.buff == _Buff.damage)
    damage = max(0, damage_raw - blocked + damage_extra)
    return damage


def _apply_damage_to(unit: Unit, damage: int) -> MaybeUnit:
    hp_new = unit.hp - damage
    if hp_new < 1:
        return None
    return replace(unit, hp=hp_new)


def _apply_attack(board: Board, move: Move) -> Board:
    unit = board.active
    target = board.target(move.pos)

    damage = _resolve_damage(unit, target)
    target_after = _apply_damage_to(unit=target, damage=damage)
    state_new = place_unit(board.state, pos=move.pos, unit=target_after)

    last_action = (f"attacked {target.__class__.__name__} with {unit.attack.name} "
                   f"for {damage} damage")
    return replace(
        board,
        state=state_new,
        last_action=last_action,
    )


def _apply_buff(board: Board, move: Move) -> Board:
    active = board.active
    target = board.target(move.pos)

    buff: Buff
    if active.buff == _Buff.shield:
        buff = ShieldBuff(round=board.round)
    elif active.buff == _Buff.damage:
        buff = DamageBuff(round=board.round)
    else:
        raise ValueError(f"Unknown buff {active.buff}")

    buffs_after = target.buffs + (buff,)
    target_after = replace(target, buffs=buffs_after)
    state_new = place_unit(board.state, pos=move.pos, unit=target_after)

    last_action = (f"applied buff '{active.buff.name}' "
                   f"to {target_after.__class__.__name__}")
    return replace(
        board,
        state=state_new,
        last_action=last_action,
    )


def _resolve_intent(
        move: Move,
        board: Board,
) -> Union[Type[Defense], Type[Attack], Type[Buff]]:
    unit = board.active
    target = board.state[move.pos]
    rel = get_unit_rel(unit, target)

    if rel == UnitRel.itself:
        return Defense
    if rel == UnitRel.enemy:
        return Attack
    if rel == UnitRel.ally:
        return Buff

    raise ValueError("Illegal move")


def _num_active_units(board: Board) -> int:
    return sum(unit.queued for unit in board.state if unit is not None)


def _set_buffs_round_end(
        buffs: Tuple[Buff, ...],
        board: Board,
) -> Generator[Buff, None, None]:
    # ATMO, keep damage, remove shield at the end of next round
    current_round = board.round
    for buff in buffs:
        if buff.buff != _Buff.shield:
            yield buff
            continue

        if buff.round == current_round:
            yield buff


def _set_unit_round_end(unit: MaybeUnit, board: Board) -> MaybeUnit:
    if unit is None:
        return None

    buffs_after = tuple(_set_buffs_round_end(buffs=unit.buffs, board=board))
    return replace(unit, queued=True, buffs=buffs_after)


def _set_units_round_end(board: Board) -> Row:
    state = board.state
    return (
        _set_unit_round_end(state[0], board=board),
        _set_unit_round_end(state[1], board=board),
        _set_unit_round_end(state[2], board=board),
        _set_unit_round_end(state[3], board=board),
        _set_unit_round_end(state[4], board=board),
        _set_unit_round_end(state[5], board=board),
        _set_unit_round_end(state[6], board=board),
        _set_unit_round_end(state[7], board=board),
        _set_unit_round_end(state[8], board=board),
        _set_unit_round_end(state[9], board=board))


def _apply_round_end(board: Board) -> Board:
    active_idx = next_active_unit_idx(board)

    if _num_active_units(board) > 0:
        round_after = board.round
        state = board.state
    else:
        round_after = board.round + 1
        state = _set_units_round_end(board)

    return replace(
        board,
        state=state,
        turn=board.turn + 1,
        round=round_after,
        active_idx=active_idx,
    )


def apply_move(
        board: Board,
        move: Move,
        player: Player = Player(1),  # pylint: disable=unused-argument
) -> Board:
    intent = _resolve_intent(move=move, board=board)

    if intent == Defense:
        board_new = _apply_defense(board)
    elif intent == Attack:
        board_new = _apply_attack(board, move)
    elif intent == Buff:
        board_new = _apply_buff(board, move)
    else:
        raise ValueError("Illegal intent")

    unit = board_new.state[board_new.active_idx]
    unit_after = replace(unit, queued=False)
    state_after = place_unit(board_new.state, pos=board.active_idx, unit=unit_after)
    board_after = replace(board_new, state=state_after)

    return _apply_round_end(board_after)


def init_move(
        s: str,
        game: Game,  # pylint: disable=unused-argument
) -> Move:
    try:
        pos = int(s)
    except (TypeError, ValueError):
        raise ValueError(f"Illegal move {s}")
    return Move(pos=pos)


def make_move(game: Game, move: Move) -> Game:
    board = apply_move(board=game.board, move=move, player=game.player)
    game = replace(game, board=board)
    player_idx = get_next_player_idx(game)
    game = replace(game, player_idx=player_idx)
    return game


def _units_left_right(state: Row) -> Tuple[int, int]:
    left, right = state[:5], state[5:]
    n_units_left = sum(1 for u in left if u is not None)
    n_units_right = sum(1 for u in right if u is not None)
    return n_units_left, n_units_right


def game_score(game: Game) -> float:
    if game.winner is None:
        raise ValueError("Game is not over, no score yet")

    if game.winner == -1:  # tie
        return 0.5

    # the logic here is as follow: The more units a side has lost
    # compared to the other side, the worse its score
    state_init = game.board_init.state
    state_final = game.board.state
    n_left_init, n_right_init = _units_left_right(state_init)
    n_left_final, n_right_final = _units_left_right(state_final)
    n_lost_left = n_left_init - n_left_final
    n_lost_right = n_right_init - n_right_final
    return n_lost_right / (n_lost_left + n_lost_right)


def _standard_board(p1: Player, p2: Player) -> Board:
    left = (
        None,
        None,
        Ranger(owner=p1, queued=False),
        Ranger(owner=p1),
        Melee(owner=p1))
    right = (
        Melee(owner=p2),
        None,
        Ranger(owner=p2),
        Ranger(owner=p2),
        None)
    board = Board(
        state=left + right,
        active_idx=3,
    )
    return board


def init_game(board: MaybeBoard = None, player_idx: int = 0) -> Game:
    p1 = Player(1)
    p2 = Player(2)
    board_ = board if board is not None else _standard_board(p1, p2)
    return Game(
        players=(p1, p2),
        board=board_,
        board_init=board_,
        player_idx=player_idx,
    )
