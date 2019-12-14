from dataclasses import dataclass, field
import enum
import math
import random
from typing import List, Optional, Union, Iterable, TypeVar, Dict

from aidoodle.core import Engine, Game, Move, Player


C = math.sqrt(2)  # from literature
EPS = 1e-12  # for numerical stability
VERBOSE = 0
MAX_DEPTH = 10000

Numeric = Union[float, int]
T = TypeVar('T')


@dataclass
class Edge:
    move: Move
    w: float = 0.0
    s: int = 0

    def __repr__(self) -> str:
        return f"Edge({self.move}, w={self.w}, s={self.s})"


@dataclass
class Node:
    game: Game
    edges: List[Edge] = field(default_factory=list)

    def __repr__(self) -> str:
        g = str(hash(self.game) % 1000) + '..'
        return f"Node(n_children={len(self.edges)}, game={g})"

    def __hash__(self) -> int:
        return hash(self.game)


_Players = List[Player]
_Edges = List[Edge]
_Nodes = List[Node]
Cache = Dict[Game, Node]
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
    raise ValueError("Unknown strategy")


def choose_edge(edges: _Edges) -> Edge:
    edge = _selectmax(edges, (e.s for e in edges))
    if VERBOSE:
        print(f"Number of visits: {edge.s}, wins: {100*edge.w/edge.s:.1f}%")
    return edge


def expand(node: Node, engine: Engine) -> None:
    # Careful: if a move is the identity move, there will be an
    # infinite recursion
    moves: List[Move] = engine.get_legal_moves(node.game)
    edges = [Edge(move) for move in moves]
    assert not node.edges
    node.edges = edges


def simulate(game: Game, engine: Engine) -> float:
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
        move = random.choice(engine.get_legal_moves(game))
        game = engine.make_move(game=game, move=move)

    if VERBOSE:
        print(game.board, end=' ')
        print(game.winner)

    score: float = engine.game_score(game)
    return score


def _update_edge(edge: Edge, value: float) -> None:
    edge.s += 1
    edge.w += value



COUNTER = 0
def update(edges: _Edges, players: _Players, value: float) -> None:
    value_other = 1 - value
    for edge, player in zip(edges, players):
        if player == 1:
            _update_edge(edge=edge, value=value)
        elif player == 2:
            _update_edge(edge=edge, value=value_other)


def _retrieve_node(game: Game, cache: Cache) -> Node:
    maybe_node: MaybeNode = cache.get(game)
    if maybe_node is not None:
        return maybe_node

    node = Node(game=game)
    cache[game] = node
    return node


def search_iteration(
        node: Node,
        engine: Engine,
        cache: Cache,
        strategy: Strategy = Strategy.ucb1,
) -> None:
    cache[node.game] = node
    edges: _Edges = []
    players: _Players = []

    # selection
    while node.edges:
        edge = select(node.edges, strategy=strategy)
        edges.append(edge)
        players.append(node.game.player)
        game = engine.make_move(game=node.game, move=edge.move)
        node = _retrieve_node(game=game, cache=cache)  # updates cache if necessary

        if len(edges) > MAX_DEPTH:
            raise RuntimeError(f"Max depth of {MAX_DEPTH} in tree search encountered, "
                               "are there cycles in the game tree?")

    # expansion
    expand(node, engine=engine)

    if node.edges:  # game end not reached
        # -> choose random move
        edge = random.choice(node.edges)
        game = engine.make_move(game=node.game, move=edge.move)
        edges.append(edge)
        players.append(game.player)
    else:  # end state reached
        game = node.game

    # simulate
    value = simulate(game, engine=engine)

    # update
    update(edges, players=players, value=value)
