from dataclasses import replace
import gc
import json
import os
import time
from typing import Any, Optional, Tuple, Dict, List, Set

import click

from aidoodle.agents import Agents, MctsAgent, RandomAgent, CliInputAgent
from aidoodle.core import Board
from aidoodle.core import Engine
from aidoodle.core import Player
from aidoodle.games import battle
from aidoodle.games import dumbdice
from aidoodle.games import nim
from aidoodle.games import tictactoe
from aidoodle.games import ziczaczoe


AGENTS = ['random', 'mcts', 'cli']
ENGINES: Dict[str, Engine] = {
    'tictactoe': tictactoe,  # type: ignore
    'nim': nim,  # type: ignore
    'dice': dumbdice,  # type: ignore
    'battle': battle,  # type: ignore
    'ziczaczoe': ziczaczoe,  # type: ignore
}
GAMES = list(ENGINES)
PAUSE = 0.5  # human play


def play_game(
        agent1: Agents,
        agent2: Agents,
        engine: Engine,
        board: Optional[Board] = None,
        silent: bool = False,
        n_runs: Optional[int] = None,
        pause: float = 0.0,
) -> Tuple[int, int, int, int]:
    n_games = 0
    n_wins1 = 0
    n_wins2 = 0
    n_ties = 0

    cont = 't'
    while cont not in {'f', 'q', 'quit'}:
        winner = _play_game(
            agent1=agent1,
            agent2=agent2,
            engine=engine,
            board=board,
            silent=silent,
            pause=pause,
        )
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
        board: Optional[Board] = None,
        silent: bool = False,
        pause: float = 0.0,
) -> Player:
    sink: Any = _void if silent else print
    game = engine.init_game(board=board)
    game = replace(game, players=(agent1.player, agent2.player))
    waited = 0.0

    while not game.winner:
        if game.player == agent1.player:
            agent = agent1
        elif game.player == agent2.player:
            agent = agent2
        else:
            raise ValueError

        sink(game.board, flush=True)
        time.sleep(max(0.0, pause - waited))

        tic = time.time()
        move = agent.next_move(game)
        waited = time.time() - tic

        sink(f"{agent.player} performs move {move}", flush=True)
        game = engine.make_move(game=game, move=move)
        gc.collect()

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
        n_games, n_wins1, n_wins2, n_ties = play_game(
            agent1, agent2, engine=engine, pause=PAUSE)
    else:
        n_games, n_wins1, n_wins2, n_ties = play_game(
            agent2, agent1, engine=engine, pause=PAUSE)
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


def available_memory() -> float:
    """System memory in MB"""
    import psutil
    return psutil.virtual_memory().available / 2 ** 20


@click.command()
@click.option('--output', default='zzz-boards.tsv', type=click.STRING,
              help="tsv file to load/save results to")
@click.option('--n_iter', default=5000, type=click.INT,
              help="agent depth")
@click.option('--n_runs', default=100, type=click.INT,
              help="number of simulations per board")
@click.option('--n_sims', default=100, type=click.INT,
              help="number of boards tested")
@click.option('--silent', default=True, type=click.BOOL,
              help="show intermediate results")
def generate_zzz_boards(
        output: str,
        n_iter: int,
        n_runs: int,
        n_sims: int,
        silent: bool,
) -> None:
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("For this functionality, you need to install pandas")

    engine = ENGINES['ziczaczoe']
    agent1 = MctsAgent(
        player=engine.init_player(1),
        engine=engine,
        n_iter=n_iter,
        reuse_cache=False,
    )
    agent2 = MctsAgent(
        player=engine.init_player(2),
        engine=engine,
        n_iter=n_iter,
        reuse_cache=False,
    )

    if not os.path.exists(output):
        df = pd.DataFrame({
            'wins1': [], 'wins2': [], 'ties': [], 'board': [], 'dur': [], 'iter': [],
        })
    else:
        df = pd.read_table(output)
    wins1: List[int] = df['wins1'].tolist()
    wins2: List[int] = df['wins2'].tolist()
    ties: List[int] = df['ties'].tolist()
    dur: List[float] = df['dur'].tolist()
    iters: List[int] = df['iter'].tolist()
    boards: List[str] = df['board'].tolist()
    board_set: Set[str] = set(boards)
    counter = 1

    while counter < n_sims:
        board_i = ziczaczoe.random_board()
        board_t = ziczaczoe.transpose_board(board_i)
        board_m = ziczaczoe.mirror_board(board_i)
        board_tm = ziczaczoe.mirror_board(board_t)
        board = sorted((board_i, board_t, board_m, board_tm))[0]
        if board in board_set:
            continue

        tic = time.time()
        print(f"Running test #{counter}")
        print(f"Using the following board")
        print("*" * 30)
        print(str(board))
        time.sleep(1)

        _, n_wins1, n_wins2, n_ties = play_game(
            agent1, agent2, engine=engine, n_runs=n_runs, board=board, silent=silent)
        wins1.append(n_wins1)
        wins2.append(n_wins2)
        ties.append(n_ties)
        iters.append(n_iter)
        boards.append(str(board))
        board_set.add(str(board))
        dur.append(float("{:.0f}".format(time.time() - tic)))
        pd.DataFrame({
            'wins1': wins1, 'wins2': wins2, 'ties': ties, 'dur': dur, 'iter': iters,
            'board': boards,
        }).to_csv(output, sep='\t', index=False)
        counter += 1

        mem = available_memory()
        if mem < 500:
            raise RuntimeError(
                "Running out of memory, only {:.0f}MB left, stopping".format(mem))
