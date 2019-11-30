# type: ignore

import pytest


@pytest.fixture(scope='session')
def dice():
    from aidoodle.games import dumbdice
    return dumbdice


@pytest.fixture
def roll(dice):
    return dice.roll


@pytest.fixture
def init_game(dice):
    return dice.init_game


@pytest.fixture
def board_cls(dice):
    return dice.Board


class TestBoardWinner:
    @pytest.fixture
    def determine_winner(self, dice):
        return dice.determine_winner

    @pytest.mark.parametrize('state, winner', [
        ((40, 35, 50), None),
        ((45, 58, 59), None),
        ((40, 35, 37), 1),
        ((45, 58, 58), 2),
    ])
    def test_determine_winner(
            self, state, winner, dice, roll, init_game, board_cls, determine_winner,
    ):
        # rolled dice don't matter
        board = board_cls(state=state, dice=roll())
        game = init_game(board=board)
        result = determine_winner(game)
        assert result == winner


class TestLegalMoves:
    @pytest.fixture
    def get_legal_moves(self, dice):
        return dice.get_legal_moves

    def test_moves_reroll(self, dice, board_cls, roll, init_game, get_legal_moves):
        board = board_cls(state=(0, 0, 1), dice=roll(), rerolled=False)
        game = init_game(board=board)
        moves = set(get_legal_moves(game))
        assert moves == {'c', 'r'}

    def test_moves_no_reroll(self, dice, board_cls, roll, init_game, get_legal_moves):
        board = board_cls(state=(0, 0, 1), dice=roll(), rerolled=True)
        game = init_game(board=board)
        moves = set(get_legal_moves(game))
        assert moves == {'c'}

    def test_moves_won(self, dice, board_cls, roll, init_game, get_legal_moves):
        # player 1 has won
        board = board_cls(state=(2, 0, 1), dice=roll(), rerolled=True)
        game = init_game(board=board)
        moves = get_legal_moves(game)
        assert moves == []


class TestApplyMoves:
    @pytest.fixture
    def apply_move(self, dice):
        return dice.apply_move

    @pytest.fixture
    def die_cls(self, dice):
        return dice.Die

    @pytest.fixture
    def move_cls(self, dice):
        return dice.Move

    @pytest.mark.parametrize(
        'state, d0, d1, player, move, state_expected, rerolled_expected', [
            ((10, 20, 30), 1, 6, 1, 'c', (17, 20, 30), False),
            ((10, 20, 30), 6, 6, 1, 'c', (22, 20, 30), False),
            ((10, 20, 30), 6, 1, 2, 'c', (10, 27, 30), False),
            ((10, 20, 30), 6, 5, 2, 'c', (10, 31, 30), False),
            ((10, 20, 30), 6, 1, 1, 'r', (10, 20, 30), True),
            ((10, 20, 30), 6, 1, 2, 'r', (10, 20, 30), True),
    ])
    def test_apply_move(
            self, apply_move, die_cls, board_cls, move_cls,
            state, d0, d1, player, move, state_expected, rerolled_expected,
    ):
        dice_ = die_cls(d0), die_cls(d1)
        move = move_cls(move)

        board = board_cls(state=state, dice=dice_)

        board_new = apply_move(board=board, move=move, player=player)
        assert board_new.state == state_expected
        assert board_new.rerolled == rerolled_expected
