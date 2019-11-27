from dataclasses import dataclass, replace, field
import enum
import math
import random
from types import ModuleType
from typing import Any, List, Tuple, Optional, Generator, Set, Union, Iterable, TypeVar

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


def expand(node: Node, engine: Any) -> Node:
    moves: List[core.Move] = engine.get_legal_moves(node.game.board)
    games: List[core.Game] = [engine.make_move(game=node.game, move=move)
                               for move in moves]
    children = [Node(game=game, move=move) for game, move in zip(games, moves)]
    add_nodes(node, children=children)
    return node


def simulate(node: Node, engine: Any) -> float:
    game = node.game
    while not game.winner:
        # by default uses random play
        game = engine.make_move(game)

    if game.winner == 1:
        return 1.0
    if game.winner == 2:
        return 0.0
    if game.winner == -1:  # tie
        return 0.5
    raise ValueError


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
    node = expand(node, engine=engine)
    if not node.children:
        return

    # simulate
    value = simulate(node, engine=engine)

    # update
    update(node, value=value)


class MctsAgent:
    n_iter: int = 1000
    engine: Any

    def next_move(self, game: core.Game) -> core.Move:
        root = Node(game=game)
        for i in range(1000):
            search_iteration(node=root, engine=self.engine)
        node_selected = choose_node(root)
        move = node_selected.move

        if move is None:
            raise TypeError
        return move


def main() -> None:
    from aidoodle.games import tictactoe as engine
    game: core.Game = engine.init_game()
    while not game.winner:
        root = Node(game=game)
        for _ in range(1000):
            search_iteration(node=root, engine=engine)
        node_selected = choose_node(root)
        game = node_selected.game
        print(game.board)
    print(game.winner)


if __name__ == '__main__':
    main()
