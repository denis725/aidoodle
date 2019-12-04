# type: ignore


import pytest


REQUIRED_ATTRS = [
    'init_game',
    'init_move',
    'init_player',
    'get_legal_moves',
    'make_move',
    'winner_to_score',
]

def engines():
    # pylint: disable=import-outside-toplevel
    from aidoodle.games import tictactoe
    from aidoodle.games import nim
    from aidoodle.games import dumbdice
    from aidoodle.games import battle
    from aidoodle.core import Engine

    return [tictactoe, nim, dumbdice, battle, Engine]


class TestCommon:
    @pytest.mark.parametrize('engine', engines())
    @pytest.mark.parametrize('attr', REQUIRED_ATTRS)
    def test_required_attrs(self, engine, attr):
        assert hasattr(engine, attr)
