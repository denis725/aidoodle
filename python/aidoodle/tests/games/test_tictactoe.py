import pytest


@pytest.fixture
def ttt():
    import aidoodle.games.tictactoe as ttt
    return ttt


@pytest.fixture
def board_empty(ttt):
    # no winner
    return ttt.Board()


@pytest.fixture
def board_non_empty(ttt):
    # no winner
    return ttt.Board(((0, 1, 1), (1, 2, 2), (2, 1, 2)))


@pytest.fixture
def board_col_win(ttt):
    # player 1 wins through column 2
    return ttt.Board(((0, 1, 2), (0, 1, 0), (2, 1, 2)))


@pytest.fixture
def board_row_win(ttt):
    # player 1 wins through row 3
    return ttt.Board(((2, 1, 2), (1, 2, 2), (1, 1, 1)))


@pytest.fixture
def board_diag_win(ttt):
    # player 2 wins through diag 2
    return ttt.Board(((1, 1, 2), (1, 2, 1), (2, 0, 2)))


class TestBoardWinner:
    @pytest.fixture
    def determine_winner(self, ttt):
        return ttt.determine_winner

    def test_winner_empty(self, board_empty, determine_winner):
        assert determine_winner(board_empty) is None

    def test_winner_non_emplty(self, board_non_empty, determine_winner):
        assert determine_winner(board_non_empty) is None

    def test_winner_col(self, board_col_win, determine_winner):
        assert determine_winner(board_col_win) == 1

    def test_winner_row(self, board_row_win, determine_winner):
        assert determine_winner(board_row_win) == 1

    def test_winner_diag(self, board_diag_win, determine_winner):
        assert determine_winner(board_diag_win) == 2


class TestLegalMoves:
    @pytest.fixture
    def get_legal_moves(self, ttt):
        return ttt.get_legal_moves

    def test_moves_board_empty(self, ttt, board_empty, get_legal_moves):
        game = ttt.init_game()
        game.board = board_empty
        assert set(get_legal_moves(game)) == ttt.POSSIBLE_MOVES

    def test_moves_board_non_empty(self, ttt, board_non_empty, get_legal_moves):
        game = ttt.init_game()
        game.board = board_non_empty
        assert get_legal_moves(game) == [(0, 0)]

    def test_no_moves(self, ttt, board_row_win, get_legal_moves):
        game = ttt.init_game()
        game.board = board_row_win
        assert get_legal_moves(game) == []


class TestApplyMove:
    @pytest.fixture
    def apply_move(self, ttt):
        return ttt.apply_move

    def test_it(self, board_empty, ttt, apply_move):
        board = board_empty
        state_new = apply_move(
            board=board,
            move=ttt.Move(0, 0),
            player=ttt.Player(1),
        )
        assert state_new == ((1, 0, 0), (0, 0, 0), (0, 0, 0))

        board = ttt.Board(state_new)
        state_new = apply_move(
            board=board,
            move=ttt.Move(1, 1),
            player=ttt.Player(2),
        )
        assert state_new == ((1, 0, 0), (0, 2, 0), (0, 0, 0))

        board = ttt.Board(state_new)
        state_new = apply_move(
            board=board,
            move=ttt.Move(0, 2),
            player=ttt.Player(1),
        )
        assert state_new == ((1, 0, 1), (0, 2, 0), (0, 0, 0))

        board = ttt.Board(state_new)
        state_new = apply_move(
            board=board,
            move=ttt.Move(0, 1),
            player=ttt.Player(2),
        )
        assert state_new == ((1, 2, 1), (0, 2, 0), (0, 0, 0))

        board = ttt.Board(state_new)
        state_new = apply_move(
            board=board,
            move=ttt.Move(2, 2),
            player=ttt.Player(1),
        )
        assert state_new == ((1, 2, 1), (0, 2, 0), (0, 0, 1))

        board = ttt.Board(state_new)
        state_new = apply_move(
            board=board,
            move=ttt.Move(2, 1),
            player=ttt.Player(2),
        )
        assert state_new == ((1, 2, 1), (0, 2, 0), (0, 2, 1))
