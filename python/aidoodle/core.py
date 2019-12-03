from typing import List, Optional, Union
from typing_extensions import Protocol

from aidoodle.games import tictactoe as ttt
from aidoodle.games import nim
from aidoodle.games import dumbdice as dice


Board = Union[ttt.Board, nim.Board, dice.Board]
Move = Union[ttt.Move, nim.Move, dice.Move]
Game = Union[ttt.Game, nim.Game, dice.Game]
Player = Union[ttt.Player, nim.Player, dice.Player]


class Engine(Protocol):
    @staticmethod
    def init_game(
            board: Optional[Board] = None,
            player_idx: int = 0,
    ) -> Game:
        ...

    @staticmethod
    def init_move(s: str, game: Optional[Game]) -> Move:
        ...

    @staticmethod
    def init_player(i: int) -> Player:
        ...

    @staticmethod
    def get_legal_moves(game: Game) -> List[Move]:
        ...

    @staticmethod
    def make_move(game: Game, move: Move) -> Game:
        ...

    @staticmethod
    def winner_to_score(winner: Player) -> float:
        ...
