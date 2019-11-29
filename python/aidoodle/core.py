from typing import Union

from aidoodle.games import tictactoe as ttt
from aidoodle.games import nim


Move = Union[ttt.Move, nim.Move]
Game = Union[ttt.Game, nim.Game]
Agent = Union[ttt.Agent, nim.Agent]
Player = Union[ttt.Player, nim.Player]
