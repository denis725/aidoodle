from dataclasses import replace
from typing import Any, Optional, Tuple, Dict

import click

from aidoodle.agents import Agents, MctsAgent, RandomAgent, CliInputAgent
from aidoodle.core import Engine
from aidoodle.core import Player
from aidoodle.games import dumbdice
from aidoodle.games import nim
from aidoodle.games import tictactoe


AGENTS = ['random', 'mcts', 'cli']
ENGINES: Dict[str, Engine] = {
    'tictactoe': tictactoe,  # type: ignore
    'nim': nim,  # type: ignore
    'dice': dumbdice,  # type: ignore
}
GAMES = list(ENGINES)


def play_game(
        agent1: Agents,
        agent2: Agents,
        engine: Engine,
        silent: bool = False,
        n_runs: Optional[int] = None,
) -> Tuple[int, int, int, int]:
    n_games = 0
    n_wins1 = 0
    n_wins2 = 0
    n_ties = 0

    cont = 't'
    while cont not in {'f', 'q', 'quit'}:
        winner = _play_game(agent1=agent1, agent2=agent2, engine=engine, silent=silent)
        if n_runs is None:
            cont = input("(q) to quit playing: ")

        n_games += 1

        if winner == 1:
            n_wins1 += 1
        elif winner == 2:
            n_wins2 += 1
        elif winner == -1:
            n_ties += 1
        else:
            raise ValueError

        print(f"games: {n_games} | wins 1: {n_wins1} | wins 2: {n_wins2} "
              f"| ties: {n_ties}")

        if n_runs and (n_games >= n_runs):
            break

    return n_games, n_wins1, n_wins2, n_ties


def _void(*args: Any, **kwargs: Any) -> None:  # pylint: disable=unused-argument
    pass


def _play_game(
        agent1: Agents,
        agent2: Agents,
        engine: Engine,
        silent: bool = False,
) -> Player:
    sink: Any = _void if silent else print
    game = engine.init_game()
    game = replace(game, players=(agent1.player, agent2.player))

    while not game.winner:
        if game.player == agent1.player:
            agent = agent1
        elif game.player == agent2.player:
            agent = agent2
        else:
            raise ValueError

        sink(game.board, flush=True)
        move = agent.next_move(game)
        sink(f"{agent.player} performs move {move}", flush=True)
        game = engine.make_move(game=game, move=move)

    sink(game.board)
    sink(f"Winner: {agent1 if game.winner == 1 else agent2}")
    return game.winner


@click.command()
@click.option('--start', default=True, type=click.BOOL,
              help="whether you start")
@click.option('--agent', default='mcts', type=click.Choice(AGENTS),
              help="which agent")
@click.option('--game', default='tictactoe', type=click.Choice(list(GAMES)),
              help="which game")
@click.option('--n_iter', default=1000, type=click.INT,
              help="agent depth")
@click.option('--learning', default=False, type=click.BOOL,
              help="agent learns between games")
def run(
        start: bool,
        agent: str,
        game: str,
        n_iter: int,
        learning: bool = False,
) -> Tuple[int, int, int, int]:
    engine = ENGINES[game]

    player_idx, agent_idx = (1, 2) if start else (2, 1)

    agent1 = CliInputAgent(
        player=engine.init_player(player_idx),
        engine=engine,
    )

    agent2: Agents
    if agent == 'random':
        agent2 = RandomAgent(
            player=engine.init_player(agent_idx),
            engine=engine,
        )
    elif agent == 'mcts':
        agent2 = MctsAgent(
            player=engine.init_player(agent_idx),
            engine=engine,
            n_iter=n_iter,
            reuse_cache=learning,
        )
    else:
        raise ValueError

    print(f"Playing {game} against {agent2}")
    if start:
        n_games, n_wins1, n_wins2, n_ties = play_game(agent1, agent2, engine=engine)
    else:
        n_games, n_wins1, n_wins2, n_ties = play_game(agent2, agent1, engine=engine)
    return n_games, n_wins1, n_wins2, n_ties


@click.command()
@click.option('--game', default='tictactoe', type=click.Choice(GAMES),
              help="which game")
@click.option('--agent1', default='mcts', type=click.Choice(AGENTS),
              help="choose agent 1")
@click.option('--agent2', default='mcts', type=click.Choice(AGENTS),
              help="choose agent 2")
@click.option('--n_iter1', default=1000, type=click.INT,
              help="agent 1 depth")
@click.option('--n_iter2', default=1000, type=click.INT,
              help="agent 2 depth")
@click.option('--learning1', default=False, type=click.BOOL,
              help="agent 1 learns between game")
@click.option('--learning2', default=False, type=click.BOOL,
              help="agent 2 learns between game")
@click.option('--n_runs', default=100, type=click.INT,
              help="number of simulations")
@click.option('--silent', default=True, type=click.BOOL,
              help="show intermediate results")
def simulate(  # pylint: disable=too-many-arguments,too-many-locals
        game: str,
        agent1: str,
        agent2: str,
        n_iter1: int,
        n_iter2: int,
        n_runs: int,
        learning1: bool = False,
        learning2: bool = False,
        silent: bool = True,
) -> Tuple[int, int, int, int]:
    engine = ENGINES[game]

    agent1_: Agents
    if agent1 == 'random':
        agent1_ = RandomAgent(engine=engine, player=engine.init_player(1))
    elif agent1 == 'mcts':
        agent1_ = MctsAgent(
            player=engine.init_player(1),
            engine=engine,
            n_iter=n_iter1,
            reuse_cache=learning1,
        )
    else:
        raise ValueError

    agent2_: Agents
    if agent2 == 'random':
        agent2_ = RandomAgent(engine=engine, player=engine.init_player(2))
    elif agent2 == 'mcts':
        agent2_ = MctsAgent(
            player=engine.init_player(2),
            engine=engine,
            n_iter=n_iter2,
            reuse_cache=learning2,
        )
    else:
        raise ValueError

    n_games, n_wins1, n_wins2, n_ties = play_game(
        agent1_, agent2_, engine=engine, n_runs=n_runs, silent=silent)
    return n_games, n_wins1, n_wins2, n_ties
