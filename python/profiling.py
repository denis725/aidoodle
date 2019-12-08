import sys

from aidoodle.run import simulate


def main(game):
    return simulate.callback(
        game=game,
        agent1='mcts',
        agent2='random',
        n_iter1=100,
        n_iter2=-55,  # doesn't matter
        n_runs=1,
        silent=True,
    )


if __name__ == '__main__':
    if len(sys.argv) < 2:
        game = 'battle'
    else:
        game = sys.argv[1]
    main(game)
