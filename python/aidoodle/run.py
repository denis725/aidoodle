# type: ignore

import click

from aidoodle.games import tictactoe
from aidoodle.ai.mcts import MctsAgent


AGENTS = ['random', 'mcts']
GAMES = ['tictactoe']


def play_game(*args, **kwargs):
    cont = 't'
    while cont not in {'f', 'q', 'quit'}:
        _play_game(*args, **kwargs)
        cont = input("(q) to quit playing: ")


def _play_game(player1, player2, engine) -> None:
    game = engine.Game(
        players=(player1, player2),
        board=engine.Board(),
    )

    while not game.winner:
        print(game.board, flush=True)
        game = engine.make_move(game=game)
    print(game.board)
    print(f"Winner: {game.winner}")


@click.command()
@click.option('--start', default=True, type=click.BOOL, help="whether you start")
@click.option('--agent', default='mcts', type=click.Choice(AGENTS), help='which agent')
@click.option('--game', default='tictactoe', type=click.Choice(GAMES), help='which game')
@click.option('--n_iter', default=1000, type=click.INT, help='agent depth')
def run(start, agent, game, n_iter):
    if game == 'tictactoe':
        engine = tictactoe
    else:
        raise ValueError

    player_idx, agent_idx = (1, 2) if start else (2, 1)
    player = engine.Player(player_idx, agent=engine.CliInputAgent())

    if agent == 'random':
        player_agent = engine.Player(agent_idx)
    elif agent == 'mcts':
        player_agent = engine.Player(
            agent_idx, agent=MctsAgent(engine=engine, n_iter=n_iter))
    else:
        raise ValueError

    print(f"Playing against {player_agent.agent}")
    if start:
        play_game(player, player_agent, engine=engine)
    else:
        play_game(player_agent, player, engine=engine)
