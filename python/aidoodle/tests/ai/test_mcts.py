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
