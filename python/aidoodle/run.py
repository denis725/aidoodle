from aidoodle.games import tictactoe as engine


def play_game() -> None:
    player1 = engine.Player(1, agent=engine.CliInputAgent())
    #player1 = engine.Player(1)
    game = engine.Game(
        players=(player1, engine.Player(2)),
        board=engine.Board(),
    )

    while not game.winner:
        print(game.board, flush=True)
        game = engine.make_move(game=game)
    print(game.board)
    print(f"Winner: {game.winner}")


def main() -> None:
    cont = 't'
    while cont not in {'f', 'q', 'quit'}:
        play_game()
        cont = input("(q) to quit playing: ")


if __name__ == '__main__':
    main()
