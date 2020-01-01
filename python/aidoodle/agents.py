from dataclasses import dataclass, field
import math
import random
import sys
from typing import Union

from aidoodle.core import Engine, Game, Move, Player
from aidoodle.ai.mcts import Cache, Node, choose_edge, search_iteration


CONCESSION_THRESHOLD = 0.4


@dataclass(frozen=True)
class Agent:
    player: Player
    engine: Engine

    def next_move(self, game: Game) -> Move:
        raise NotImplementedError

    def __repr__(self) -> str:
        return self.__class__.__name__


@dataclass(frozen=True)
class RandomAgent(Agent):
    def next_move(self, game: Game) -> Move:
        legal_moves = self.engine.get_legal_moves(game)
        return random.choice(legal_moves)


@dataclass(frozen=True)
class CliInputAgent(Agent):
    def _ask_input(self, game: Game) -> Move:  # pylint: disable=no-self-use
        inp = input("choose next move: ")
        if inp == 'q':
            sys.exit(0)

        try:
            move: Move = self.engine.init_move(inp, game)
        except (TypeError, NameError):
            sys.exit(1)
        return move

    def next_move(self, game: Game) -> Move:
        moves = self.engine.get_legal_moves(game)
        if len(moves) == 1:
            return moves[0]

        print("possible moves: ", sorted(moves), flush=True)

        move = self._ask_input(game)
        while move not in moves:
            move = self._ask_input(game)

        return move

    def __repr__(self) -> str:
        return "You"


class Concession(RuntimeError):
    """Hack the control flow by raising error when conceding"""


def _upper_conf_bound(v: float, n: int, z: float = 1.96) -> float:
    """Calculate the approximate 95% upper bound of expected value"""
    # not to be confused with ucb1 values
    p = v / n
    return p + z * math.sqrt(p * (1 - p) / n)


@dataclass(frozen=True)
class MctsAgent(Agent):
    n_iter: int = 1000
    reuse_cache: bool = False
    cache: Cache = field(default_factory=dict)
    allow_concession: bool = False

    def next_move(self, game: Game) -> Move:
        root = Node(game=game)
        cache: Cache = self.cache if self.reuse_cache else {}

        for _ in range(self.n_iter):
            search_iteration(node=root, engine=self.engine, cache=cache)

        edge = choose_edge(root.edges)
        if not self.allow_concession:
            return edge.move

        # estimate worst best case probability to win, if below
        # threshold, concede
        ucb = _upper_conf_bound(v=edge.w, n=edge.s)
        if ucb < CONCESSION_THRESHOLD:
            raise Concession("{:.4f}".format(ucb))
        return edge.move

    def __repr__(self) -> str:
        return f"MctsAgent(n_iter={self.n_iter}, learning={self.reuse_cache})"


Agents = Union[CliInputAgent, MctsAgent, RandomAgent]
