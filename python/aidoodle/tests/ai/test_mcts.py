# type: ignore


from dataclasses import replace

import pytest


@pytest.fixture(scope='session')
def node_cls():
    from aidoodle.ai.mcts import Node
    return Node


@pytest.fixture
def add_node():
    from aidoodle.ai.mcts import add_node
    return add_node


@pytest.fixture
def add_nodes():
    from aidoodle.ai.mcts import add_nodes
    return add_nodes


@pytest.fixture
def game():
    from aidoodle.games.tictactoe import init_game
    return init_game()


@pytest.fixture
def root3(node_cls, add_nodes, game):
    root = node_cls(game=game)
    child0 = node_cls(game=game, w=1, s=2)
    child1 = node_cls(game=game, w=5, s=9)
    add_nodes(root, (child0, child1))
    return root


@pytest.fixture
def root4(node_cls, add_nodes, game):
    root = node_cls(game=game)
    child0 = node_cls(game=game, w=1, s=2)
    child1 = node_cls(game=game, w=5, s=9)
    child2 = node_cls(game=game, w=0, s=0)
    add_nodes(root, (child0, child1, child2))
    return root


@pytest.fixture
def select_ucb1():
    from aidoodle.ai.mcts import select_ucb1
    return select_ucb1


class TestSelection:
    def test_select_ucb1_nodes3(self, root3, select_ucb1):
        selected = select_ucb1(root3.children)
        expected = root3.children[0]
        assert selected == expected

    def test_select_ucb1_nodes4(self, root4, select_ucb1):
        selected = select_ucb1(root4.children)
        # last one has never been selected, hence highest priority
        expected = root4.children[2]
        assert selected == expected


class TestAddNodes:
    @pytest.fixture
    def root(self, game):
        from aidoodle.ai.mcts import Node
        return Node(game=game, s=123)

    @pytest.fixture
    def child1(self, game):
        from aidoodle.ai.mcts import Node
        return Node(game=game, s=234)

    @pytest.fixture
    def child2(self, game):
        from aidoodle.ai.mcts import Node
        return Node(game=game, s=345)

    def test_add_node(self, root, child1, add_node):
        add_node(root, child1)
        assert child1 in root.children
        assert root.s == 123
        assert child1.s == 234

    def test_add_nodes(self, root, child1, child2, add_nodes):
        add_nodes(root, (child1, child2))
        for child in (child1, child2):
            assert child in root.children

    def test_add_node_keeps_parent(self, root, child1, child2, add_node):
        add_node(root, child1)
        add_node(child1, child2)

        assert root.s == 123
        assert child1.s == 234
        assert child2.s == 345


class TestAgentTicTacToe:
    @pytest.fixture
    def engine(self):
        from aidoodle.games import tictactoe as engine
        return engine

    @pytest.fixture
    def agent(self, engine):
        from aidoodle.ai.mcts import MctsAgent
        return MctsAgent(engine, n_iter=500)

    def test_mcts_situation_1(self, engine, agent):
        # player 1 should make the wining move
        board = engine.Board(state=(
            (1, 1, 0),
            (0, 0, 0),
            (0, 2, 2)),
        )
        game = engine.init_game(board=board)
        move = agent.next_move(game)
        expected = engine.Move(0, 2)
        assert move == expected

    def test_mcts_situation_2(self, engine, agent):
        # player 2 should make the winning move
        board = engine.Board(state=(
            (1, 1, 0),
            (0, 1, 0),
            (0, 2, 2)),
        )
        game = engine.init_game(board=board, player_idx=1)
        move = agent.next_move(game)
        expected = engine.Move(2, 0)
        assert move == expected

    def test_mcts_situation_3(self, engine, agent):
        # player 2 shouldn't move 0,2 or 2,0 since this will lead to a
        # winning move for player 1 by placing on the opposite side
        board = engine.Board(state=(
            (1, 0, 0),
            (0, 2, 0),
            (0, 0, 1)),
        )
        game = engine.init_game(board=board, player_idx=1)
        move = agent.next_move(game)
        assert move != engine.Move(0, 2)
        assert move != engine.Move(2, 0)

    @pytest.mark.slow
    @pytest.mark.parametrize('agent1, agent2', [
        ('random', 'mcts'),
        ('mcts', 'random'),
    ])
    def test_simulation_against_random(self, engine, agent1, agent2):
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
    def test_simulation_different_depths(self, engine, n_iter1, n_iter2):
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
            assert n_wins1 > 25
        else:
            assert n_wins2 > 25

    @pytest.mark.slow
    def test_simulation_equal_depths(self, engine):
        # mcts against itself should mostly tie

        # note that n_iter must be sufficiently high, otherwise the
        # starting player will mostly win
        from aidoodle.run import simulate

        _, _, _, n_ties = simulate.callback(
            game='tictactoe',
            agent1='mcts',
            agent2='mcts',
            n_iter1=200,  # dumb
            n_iter2=200,  # smarter
            n_runs=50,
        )
        assert n_ties > 20
