# type: ignore

# pylint: disable=import-outside-toplevel

from functools import partial
import pytest


@pytest.fixture(scope='session')
def node_cls():
    from aidoodle.ai.mcts import Node
    return Node


@pytest.fixture(scope='session')
def edge_cls():
    from aidoodle.ai.mcts import Edge
    return Edge


@pytest.fixture
def game():
    from aidoodle.games.tictactoe import init_game
    return init_game()


@pytest.fixture
def move():
    from aidoodle.games.tictactoe import Move
    return Move(0, 0)


@pytest.fixture
def root2(node_cls, edge_cls, game):
    root = node_cls(game=game)
    edge0 = edge_cls(move=move, w=1, s=2)
    edge1 = edge_cls(move=move, w=5, s=9)
    root.edges = [edge0, edge1]
    return root


@pytest.fixture
def root3(node_cls, edge_cls, game):
    root = node_cls(game=game)
    edge0 = edge_cls(move=move, w=1, s=2)
    edge1 = edge_cls(move=move, w=5, s=9)
    edge2 = edge_cls(move=move, w=0, s=0)
    root.edges = [edge0, edge1, edge2]
    return root


@pytest.fixture
def select_ucb1():
    from aidoodle.ai.mcts import select_ucb1
    return select_ucb1


class TestSelection:
    def test_select_ucb1_nodes3(self, root2, select_ucb1):
        selected = select_ucb1(root2.edges)
        expected = root2.edges[0]
        assert selected == expected

    def test_select_ucb1_nodes4(self, root3, select_ucb1):
        selected = select_ucb1(root3.edges)
        # last one has never been selected, hence highest priority
        expected = root3.edges[2]
        assert selected == expected


class TestAgentTicTacToe:
    @pytest.fixture(scope='session')
    def engine(self):
        from aidoodle.games import tictactoe as engine
        return engine

    @pytest.fixture
    def agent_cls(self, engine):
        from aidoodle.agents import MctsAgent
        return partial(MctsAgent, engine=engine, n_iter=1000)

    @pytest.fixture
    def agent1(self, agent_cls, engine):
        return agent_cls(player=engine.init_player(1))

    @pytest.fixture
    def agent2(self, agent_cls, engine):
        return agent_cls(player=engine.init_player(1))

    def test_mcts_situation_1(self, engine, agent1):
        # player 1 should make the wining move
        board = engine.Board(state=(
            (1, 1, 0),
            (0, 0, 0),
            (0, 2, 2)
        ))
        game = engine.init_game(board=board)
        move = agent1.next_move(game)
        expected = engine.Move(0, 2)
        assert move == expected

    def test_mcts_situation_2(self, engine, agent2):
        # player 2 should make the winning move
        board = engine.Board(state=(
            (1, 1, 0),
            (0, 1, 0),
            (0, 2, 2)
        ))
        game = engine.init_game(board=board, player_idx=1)
        move = agent2.next_move(game)
        expected = engine.Move(2, 0)
        assert move == expected

    def test_mcts_situation_3(self, engine, agent2):
        # player 2 shouldn't move 0,2 or 2,0 since this will lead to a
        # winning move for player 1 by placing on the opposite side
        board = engine.Board(state=(
            (1, 0, 0),
            (0, 2, 0),
            (0, 0, 1)
        ))
        game = engine.init_game(board=board, player_idx=1)
        move = agent2.next_move(game)
        assert move != engine.Move(0, 2)
        assert move != engine.Move(2, 0)

    @pytest.mark.slow
    @pytest.mark.parametrize('agent1, agent2', [
        ('random', 'mcts'),
        ('mcts', 'random'),
    ])
    def test_simulation_against_random(self, agent1, agent2):
        # mcts should mostly win against random
        from aidoodle.run import simulate

        _, n_wins1, n_wins2, _ = simulate.callback(
            game='tictactoe',
            agent1=agent1,
            agent2=agent2,
            n_iter1=100,
            n_iter2=100,
            n_runs=50,
        )
        if agent1 == 'mcts':
            assert n_wins1 > 25
        else:
            assert n_wins2 > 25

    @pytest.mark.slow
    @pytest.mark.parametrize('n_iter1, n_iter2', [
        (10, 100),
        (100, 10),
    ])
    def test_simulation_different_depths(self, n_iter1, n_iter2):
        # mcts 100 vs mcts 10 should mostly win
        from aidoodle.run import simulate

        _, n_wins1, n_wins2, _ = simulate.callback(
            game='tictactoe',
            agent1='mcts',
            agent2='mcts',
            n_iter1=n_iter1,
            n_iter2=n_iter2,
            n_runs=50,
        )
        if n_iter1 > n_iter2:
            assert n_wins1 > 30
        else:
            assert n_wins2 > 30

    @pytest.mark.slow
    def test_simulation_equal_depths(self):
        # mcts against itself should mostly tie

        # note that n_iter must be sufficiently high, otherwise the
        # starting player will mostly win
        from aidoodle.run import simulate

        _, _, _, n_ties = simulate.callback(
            game='tictactoe',
            agent1='mcts',
            agent2='mcts',
            n_iter1=500,
            n_iter2=500,
            n_runs=50,
        )
        assert n_ties > 20


class TestAgentNim:
    @pytest.fixture(scope='session')
    def engine(self):
        from aidoodle.games import nim
        return nim

    @pytest.fixture
    def agent_cls(self, engine):
        from aidoodle.agents import MctsAgent
        return partial(MctsAgent, engine=engine, n_iter=500)

    @pytest.fixture
    def agent(self, agent_cls, engine):
        return agent_cls(player=engine.init_player(1))

    def test_mcts_situation_1(self, engine, agent):
        # agent should make the wining move of leaving exactly one stone
        board = engine.Board(state=(0, 2, 0))
        game = engine.init_game(board=board)
        move = agent.next_move(game)
        expected = engine.Move(1, 1)
        assert move == expected

    def test_mcts_situation_2(self, engine, agent):
        # agent should make the wining move of leaving exactly one stone
        board = engine.Board(state=(0, 7, 0))
        game = engine.init_game(board=board)
        move = agent.next_move(game)
        expected = engine.Move(1, 6)
        assert move == expected

    def test_mcts_situation_3(self, engine, agent):
        # agent should make the wining move of leaving exactly one stone
        board = engine.Board(state=(0, 1, 9))
        game = engine.init_game(board=board)
        move = agent.next_move(game)
        expected = engine.Move(2, 9)
        assert move == expected

    def test_mcts_situation_4(self, engine, agent):
        # agent should force a winning position by removing 3 stones
        # from heap 2, which leaves (1, 1, 1), which leads to a
        # winning position
        board = engine.Board(state=(1, 1, 4))
        game = engine.init_game(board=board)
        move = agent.next_move(game)
        expected = engine.Move(2, 3)
        assert move == expected

    def test_mcts_situation_5(self, engine, agent):
        # agent should force a winning position by removing 1 stone
        # from heap 2, which leaves (1, 1, 1), which leads to a
        # winning position
        board = engine.Board(state=(1, 1, 2))
        game = engine.init_game(board=board)
        move = agent.next_move(game)
        expected = engine.Move(2, 1)
        assert move == expected

    @pytest.mark.slow
    @pytest.mark.parametrize('agent1, agent2', [
        ('random', 'mcts'),
        ('mcts', 'random'),
    ])
    def test_simulation_against_random(self, agent1, agent2):
        # mcts should mostly win against random
        from aidoodle.run import simulate

        _, n_wins1, n_wins2, _ = simulate.callback(
            game='nim',
            agent1=agent1,
            agent2=agent2,
            n_iter1=100,
            n_iter2=100,
            n_runs=50,
        )
        if agent1 == 'mcts':
            assert n_wins1 > 30
        else:
            assert n_wins2 > 30

    @pytest.mark.slow
    @pytest.mark.parametrize('n_iter1, n_iter2', [
        (10, 100),
        (100, 10),
    ])
    def test_simulation_different_depths(self, n_iter1, n_iter2):
        # mcts 100 vs mcts 10 should mostly win
        from aidoodle.run import simulate

        _, n_wins1, n_wins2, _ = simulate.callback(
            game='nim',
            agent1='mcts',
            agent2='mcts',
            n_iter1=n_iter1,
            n_iter2=n_iter2,
            n_runs=50,
        )
        if n_iter1 > n_iter2:
            assert n_wins1 > 30
        else:
            assert n_wins2 > 30

    @pytest.mark.slow
    def test_simulation_equal_depths(self):
        # mcts against itself should win and lose about equally
        from aidoodle.run import simulate

        _, n_wins1, n_wins2, _ = simulate.callback(
            game='nim',
            agent1='mcts',
            agent2='mcts',
            n_iter1=100,
            n_iter2=100,
            n_runs=50,
        )
        assert abs(n_wins1 - n_wins2) <= 15


class TestAgentDumbDice:
    @pytest.fixture(scope='session')
    def engine(self):
        from aidoodle.games import dumbdice
        return dumbdice

    @pytest.fixture
    def agent_cls(self, engine):
        from aidoodle.agents import MctsAgent
        return partial(MctsAgent, engine=engine, n_iter=2000)

    @pytest.fixture
    def agent(self, agent_cls, engine):
        return agent_cls(player=engine.init_player(1))

    def test_mcts_situation_1(self, engine, agent):
        # agent should reroll because of bad dice
        dice_ = engine.Die(2), engine.Die(2)
        board = engine.Board(state=(0, 4, 50), dice=dice_)
        game = engine.init_game(board=board)
        move = agent.next_move(game)
        assert move == 'r'

    def test_mcts_situation_2(self, engine, agent):
        # agent should continue because of good dice
        dice_ = engine.Die(5), engine.Die(5)
        board = engine.Board(state=(0, 4, 50), dice=dice_)
        game = engine.init_game(board=board)
        move = agent.next_move(game)
        assert move == 'c'

    def test_mcts_situation_3(self, engine, agent):
        # even though the agent has a good roll, it should reroll
        # because it can only win with at least 11
        dice_ = engine.Die(5), engine.Die(5)
        board = engine.Board(state=(39, 49, 50), dice=dice_)
        game = engine.init_game(board=board)
        move = agent.next_move(game)
        assert move == 'r'

    def test_mcts_situation_4(self, engine, agent):
        # similar situation as the last one but since there is still
        # some way left before the game ends, the agent should keep
        # the good 10 this time
        dice_ = engine.Die(5), engine.Die(5)
        board = engine.Board(state=(39, 49, 100), dice=dice_)
        game = engine.init_game(board=board)
        move = agent.next_move(game)
        assert move == 'c'

    def test_mcts_situation_5(self, engine, agent):
        # agent should keep because it will reach 48, which is a
        # guaranteed win next round. There is no risk since the
        # opponent cannot win this round. If the agent rerolls,
        # however, it could still lose with some bad rolls (e.g. d1,d1
        # and d1,d1).
        dice_ = engine.Die(3), engine.Die(2)
        board = engine.Board(state=(43, 37, 50), dice=dice_)
        game = engine.init_game(board=board)
        move = agent.next_move(game)
        assert move == 'c'

    @pytest.mark.slow
    @pytest.mark.parametrize('agent1, agent2', [
        ('random', 'mcts'),
        ('mcts', 'random'),
    ])
    def test_simulation_against_random(self, agent1, agent2):
        # mcts should mostly win against random
        from aidoodle.run import simulate

        _, n_wins1, n_wins2, _ = simulate.callback(
            game='dice',
            agent1=agent1,
            agent2=agent2,
            n_iter1=100,
            n_iter2=100,
            n_runs=100,
        )
        if agent1 == 'mcts':
            assert n_wins1 > 60
        else:
            assert n_wins2 > 60

    @pytest.mark.slow
    @pytest.mark.parametrize('n_iter1, n_iter2', [
        (10, 100),
        (100, 10),
    ])
    def test_simulation_different_depths(self, n_iter1, n_iter2):
        # mcts 100 vs mcts 10 should mostly win
        from aidoodle.run import simulate

        _, n_wins1, n_wins2, _ = simulate.callback(
            game='dice',
            agent1='mcts',
            agent2='mcts',
            n_iter1=n_iter1,
            n_iter2=n_iter2,
            n_runs=100,
        )
        if n_iter1 > n_iter2:
            assert n_wins1 > 60
        else:
            assert n_wins2 > 60

    @pytest.mark.slow
    def test_simulation_equal_depths(self):
        # mcts against itself should win and lose about equally
        from aidoodle.run import simulate

        _, n_wins1, n_wins2, _ = simulate.callback(
            game='dice',
            agent1='mcts',
            agent2='mcts',
            n_iter1=100,
            n_iter2=100,
            n_runs=50,
        )
        assert abs(n_wins1 - n_wins2) <= 15
