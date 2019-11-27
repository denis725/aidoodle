from aidoodle.games import tictactoe as engine
from aidoodle.ai.mcts import MctsAgent


def play_game(player2) -> None:
    player1 = engine.Player(1, agent=engine.CliInputAgent())
    game = engine.Game(
        players=(player1, player2),
        board=engine.Board(),
    )

    print(f"Playing against {player2}")
    while not game.winner:
        print(game.board, flush=True)
        game = engine.make_move(game=game)
    print(game.board)
    print(f"Winner: {game.winner}")


def main() -> None:
    cont = 't'

    #player2 = engine.Player(2)  # random
    player2 = engine.Player(2, agent=MctsAgent(engine=engine, n_iter=1000))

    while cont not in {'f', 'q', 'quit'}:
        play_game(player2)
        cont = input("(q) to quit playing: ")


if __name__ == '__main__':
    main()
