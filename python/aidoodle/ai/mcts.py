from dataclasses import dataclass, field
import enum
import math
import random
from typing import Any, List, Optional, Union, Iterable, TypeVar

from aidoodle import core


C = math.sqrt(2)  # from literature
C = 10
EPS = 1e-12  # for numerical stability
VERBOSE = 0

Numeric = Union[float, int]
T = TypeVar('T')


@dataclass
class Edge:
    move: core.Move
    w: float = 0.0
    s: int = 0

    def __repr__(self) -> str:
        return f"Edge({self.move}, w={self.w}, s={self.s})"


@dataclass
class Node:
    game: core.Game
    edges: List[Edge] = field(default_factory=list)

    def __repr__(self) -> str:
        g = str(hash(self.game) % 1000) + '..'
        return f"Node(n_children={len(self.edges)}, game={g})"


_Edges = List[Edge]
_Nodes = List[Node]
MaybeNode = Optional[Node]


class Strategy(enum.Enum):
    random = 0
    ucb1 = 1


def _selectmax(keys: Iterable[T], vals: Iterable[Numeric]) -> T:
    return max(zip(keys, vals), key=lambda tup: tup[1])[0]


def _ucb1_values(edges: _Edges, c: float = C) -> List[float]:
    s_tot = sum(edge.s for edge in edges)
    const = c * math.log(s_tot + 1)
    vals = [e.w / (e.s + EPS) + const / math.sqrt(e.s + EPS) for e in edges]
    return vals


def select_ucb1(edges: _Edges, c: float = C) -> Edge:
    vals = _ucb1_values(edges=edges, c=c)
    edge = _selectmax(edges, vals)
    return edge


def select(edges: _Edges, strategy: Strategy = Strategy.ucb1) -> Edge:
    if strategy == Strategy.random:
        return random.choice(edges)
    if strategy == Strategy.ucb1:
        return select_ucb1(edges)
    raise TypeError


def choose_edge(edges: _Edges) -> Edge:
    edge = _selectmax(edges, (e.s for e in edges))
    if VERBOSE:
        print(f"Number of visits: {edge.s}, wins: {100*edge.w/edge.s:.1f}%")
    return edge


def expand(node: Node, engine: Any) -> None:
    moves: List[core.Move] = engine.get_legal_moves(node.game)
    edges = [Edge(move) for move in moves]
    assert not node.edges
    node.edges = edges


def simulate(game: core.Game, engine: Any) -> float:
    # init a game with random players
    game = engine.init_game(
        board=game.board,
        player_idx=game.player_idx,
    )

    if VERBOSE:
        print("-" * 40)
        print(game.board)

    while not game.winner:
        # by default uses random play
        game = engine.make_move(game)

    if VERBOSE:
        print(game.board, end=' ')
        print(game.winner)

    score: float = engine.winner_to_score(game.winner)
    return score


def _update_edge(edge: Edge, value: float) -> None:
    edge.s += 1
    edge.w += value



COUNTER = 0
def update(edges: _Edges, players: List[Any], value: float, i=0) -> None:
    if not edges:
        return

    global COUNTER
    COUNTER += 1

    *edges, edge = edges
    *players, player = players

    if player == 1:
        _update_edge(edge, value=value)
    else:
        _update_edge(edge, value=1 - value)

    update(edges, players=players, value=value, i=i+1)


def search_iteration(
        node: Node,
        engine: Any,  # should be ModuleType but that causes issues with mypy
        strategy: Strategy = Strategy.ucb1,
) -> None:
    players: List[engine.Player] = []
    edges: List[Edge] = []

    # selection
    while node.edges:
        edge = select(node.edges, strategy=strategy)
        edges.append(edge)
        players.append(node.game.player)
        node = Node(game=engine.make_move(game=node.game, move=edge.move))

    # expansion
    expand(node, engine=engine)

    if node.edges:  # end game not reached
        # not end state -> choose random move
        edge = random.choice(node.edges)
        game = engine.make_move(game=node.game, move=edge.move)
        edges.append(edge)
        players.append(game.player)
    else:  # end state reached
        game = node.game

    # simulate
    value = simulate(game, engine=engine)

    # update
    assert len(edges) == len(players)
    update(edges, players=players, value=value)


@dataclass(frozen=True)
class MctsAgent:
    engine: Any
    n_iter: int = 1000

    def next_move(self, game: core.Game) -> core.Move:
        root = Node(game=game)
        for _ in range(self.n_iter):
            search_iteration(node=root, engine=self.engine)

        edge = choose_edge(root.edges)

        print("*" * 25, COUNTER, "*" * 25)
        return edge.move

    def __repr__(self) -> str:
        return f"MctsAgent(n_iter={self.n_iter})"
