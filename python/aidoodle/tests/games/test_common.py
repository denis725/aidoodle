# type: ignore


import pytest


REQUIRED_ATTRS = [
    'Game',
    'Board',
    'Player',
    'Move',
    'get_legal_moves',
    'init_game',
    'make_move',
    'winner_to_score',
]

def engines():
    # pylint: disable=import-outside-toplevel
    from aidoodle.games import tictactoe
    from aidoodle.games import nim
    from aidoodle.games import dumbdice

    return [tictactoe, nim, dumbdice]


class TestCommon:
    @pytest.mark.parametrize('engine', engines())
    @pytest.mark.parametrize('attr', REQUIRED_ATTRS)
    def test_required_attrs(self, engine, attr):
        assert hasattr(engine, attr)
