from aidoodle.games import tictactoe as ttt


def play_game() -> None:
    player1 = ttt.Player(1, agent=ttt.CliInputAgent())
    #player1 = ttt.Player(1)
    game = ttt.Game(
        players=(player1, ttt.Player(2)),
        board=ttt.Board(),
    )

    while not game.winner:
        print(game.board, flush=True)
        game = ttt.make_move(game=game)
    print(game.board)
    print(f"Winner: {game.winner}")


def main() -> None:
    cont = 't'
    while cont not in {'f', 'q', 'quit'}:
        play_game()
        cont = input("(q) to quit playing: ")


if __name__ == '__main__':
    main()
