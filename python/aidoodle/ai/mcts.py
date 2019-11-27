from dataclasses import dataclass, field
import enum
import math
import random
from typing import Any, List, Optional, Union, Iterable, TypeVar

from aidoodle import core


C = math.sqrt(2)  # from literature
EPS = 1e-12  # for numerical stability

Numeric = Union[float, int]
T = TypeVar('T')


MaybeNode = Optional['Node']
MaybeMove = Optional[core.Move]


@dataclass
class Node:
    game: core.Game
    w: float = 0.0  # number of winning sims
    s: int = 0  # total number of sims
    children: List['Node'] = field(default_factory=list)
    parent: MaybeNode = None
    move: MaybeMove = None

    def __repr__(self) -> str:
        g = str(hash(self.game) % 1000) + '..'
        return f"Node(w={self.w}, s={self.s}, n_children={len(self.children)}, game={g})"


_Nodes = List[Node]


class Strategy(enum.Enum):
    random = 0
    ucb1 = 1


def add_node(parent: Node, child: Node) -> None:
    if child in parent.children:
        raise ValueError

    parent.children = parent.children.copy() + [child]
    child.parent = parent


def add_nodes(parent: Node, children: Iterable[Node]) -> None:
    for child in children:
        add_node(parent=parent, child=child)


def _selectmax(keys: Iterable[T], vals: Iterable[Numeric]) -> T:
    return max(zip(keys, vals), key=lambda tup: tup[1])[0]


def select_ucb1(nodes: _Nodes, c: float = C) -> Node:
    s_tot = sum(node.s for node in nodes)
    const = c * math.log(s_tot + 1)
    vals = [node.w / (node.s + EPS) + const / math.sqrt(node.s + EPS) for node in nodes]
    node = _selectmax(nodes, vals)
    return node


def select(nodes: _Nodes, strategy: Strategy = Strategy.ucb1) -> Node:
    if strategy == Strategy.random:
        return random.choice(nodes)
    if strategy == Strategy.ucb1:
        return select_ucb1(nodes)
    raise TypeError


def choose_node(root: Node) -> Node:
    return _selectmax(root.children, (c.s for c in root.children))


def expand(node: Node, engine: Any) -> None:
    moves: List[core.Move] = engine.get_legal_moves(node.game.board)
    games: List[core.Game] = [engine.make_move(game=node.game, move=move)
                               for move in moves]
    children = [Node(game=game, move=move) for game, move in zip(games, moves)]
    add_nodes(node, children=children)


def simulate(node: Node, engine: Any) -> float:
    # init a game with random players
    game = engine.init_game(board=node.game.board)
    while not game.winner:
        # by default uses random play
        game = engine.make_move(game)

    score = engine.winner_to_score(game.winner)
    return score


def _update_one(node: Node, value: float) -> None:
    if node.game.player == 1:
        value = 1 - value
    elif node.game.player != 2:
        raise ValueError

    node.s += 1
    node.w += value


def update(node: Node, value: float) -> None:
    _update_one(node, value=value)
    if node.parent is not None:
        update(node.parent, value=value)


def search_iteration(
        node: Node,
        engine: Any,  # should be ModuleType but that causes issues with mypy
        strategy: Strategy = Strategy.ucb1,
) -> None:
    # selection
    while node.children:
        node = select(node.children, strategy=strategy)

    # expansion
    expand(node, engine=engine)
    if not node.children:  # end state reached
        return

    # simulate
    value = simulate(node, engine=engine)

    # update
    update(node, value=value)


@dataclass(frozen=True)
class MctsAgent:
    engine: Any
    n_iter: int = 1000

    def next_move(self, game: core.Game) -> core.Move:
        root = Node(game=game)
        for _ in range(self.n_iter):
            search_iteration(node=root, engine=self.engine)
        node_selected = choose_node(root)
        move = node_selected.move

        if move is None:
            raise TypeError
        return move

    def __repr__(self) -> str:
        return f"MctsAgent(n_iter={self.n_iter})"
