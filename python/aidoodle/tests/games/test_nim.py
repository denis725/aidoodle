# type: ignore


import pytest


@pytest.fixture(scope='session')
def nim():
    # pylint: disable=import-outside-toplevel
    from aidoodle.games import nim
    return nim


@pytest.fixture
def board_cls(nim):
    return nim.Board


@pytest.fixture
def move_cls(nim):
    return nim.Move


@pytest.fixture
def init_game(nim):
    return nim.init_game


class TestBoardWinner:
    @pytest.fixture
    def determine_winner(self, nim):
        return nim.determine_winner

    @pytest.mark.parametrize('state, player_idx, winner', [
        ((0, 0, 0), 0, 1),
        ((0, 0, 0), 1, 2),
        ((0, 1, 0), 1, None),
        ((0, 1, 0), 0, None),
        ((1, 2, 3), 0, None),
        ((3, 4, 5), 1, None),
    ])
    def test_determine_winner(
            self, state, player_idx, winner, board_cls, determine_winner, init_game,
    ):
        board = board_cls(state=state)
        game = init_game(board=board, player_idx=player_idx)
        result = determine_winner(game)
        assert result == winner


class TestLegalMoves:
    @pytest.fixture
    def get_legal_moves(self, nim):
        return nim.get_legal_moves

    def test_moves_board_empty(self, nim, board_cls, get_legal_moves):
        board = board_cls((0, 0, 0))
        game = nim.init_game(board=board)
        moves = set(get_legal_moves(game))
        assert moves == set()

    def test_moves_board1(self, nim, board_cls, move_cls, get_legal_moves):
        board = board_cls((2, 1, 2))
        game = nim.init_game(board=board)
        moves = set(get_legal_moves(game))
        expected = {
            move_cls(0, 1),
            move_cls(0, 2),
            move_cls(1, 1),
            move_cls(2, 1),
            move_cls(2, 2),
        }
        assert moves == expected

    def test_moves_board2(self, nim, board_cls, move_cls, get_legal_moves):
        board = board_cls((0, 4, 1))
        game = nim.init_game(board=board)
        moves = set(get_legal_moves(game))
        expected = {
            move_cls(1, 1),
            move_cls(1, 2),
            move_cls(1, 3),
            move_cls(1, 4),
            move_cls(2, 1),
        }
        assert moves == expected


class TestApplyMoves:
    @pytest.fixture
    def apply_move(self, nim):
        return nim.apply_move

    @pytest.fixture
    def board(self, board_cls):
        return board_cls((3, 4, 5))

    @pytest.mark.parametrize('heap, stones, state', [
        (0, 1, (2, 4, 5)),
        (0, 3, (0, 4, 5)),
        (1, 4, (3, 0, 5)),
        (2, 3, (3, 4, 2)),
    ])
    @pytest.mark.parametrize('player', [1, 2])
    def test_apply_move(
            self, heap, stones, state, player, apply_move, board, move_cls, nim,
    ):
        move = move_cls(heap, stones)
        state_new = apply_move(
            board=board,
            move=move,
            player=nim.Player(player),
        ).state
        assert state_new == state
