import random
import unittest

from chess.agents import MinimaxAgent
from chess.mcts import RandomMoveAgent, RandomPlayoutAgent
from chess.value_network_agent import *
from chess.state import State, IllegalMoveException


class SampleMinimaxAgent(MinimaxAgent):
    def __init__(self, max_depth: int = 3):
        super().__init__()
        self._max_depth = max_depth

    @property
    def max_depth(self):
        return self._max_depth

    def heuristic(self, state: 'State'):
        return 0


class MinimaxTest(unittest.TestCase):
    def test_search(self):
        s = State(
            (0, 0, 0, 0, 2 << 16, 4 << 16),
            (0, 0, 0, 0, 0, 1),
            turn='w',
            in_check=False
        )
        agent = SampleMinimaxAgent()
        selected_move = agent.select_move(s)
        self.assertEqual(selected_move, (2 << 16, 2 << 8), 'Checkmate in 1')


class RandomAgentTest(unittest.TestCase):
    def test_select_move_random(self):
        agent = RandomMoveAgent()
        s = State()
        random.seed(124915)
        moves = set()
        for i in range(10):
            moves.add(agent.select_move(s))
        self.assertTrue(len(moves) > 1)

    def test_select_move_playout(self):
        agent = RandomPlayoutAgent(max_time=1, max_depth=2)
        s = State(
            (0, 0, 0, 0, 2 << 16, 4 << 16),
            (0, 0, 0, 0, 0, 1),
            turn='w',
            in_check=False
        )
        random.seed(124915)
        selected_move = agent.select_move(s)
        self.assertEqual(selected_move, (2 << 16, 2 << 8), 'Checkmate in 1')


class LearningAgentTest(unittest.TestCase):
    def test_relu(self):
        a = relu(np.array([-1, 1]))
        self.assertEqual(a[0], 0, 'Test ReLU')
        self.assertEqual(a[1], 1, 'Test ReLU')

    def test_sigmoid(self):
        a = sigmoid(0)
        self.assertAlmostEqual(a, 0.5, 8, 'Test Sigmoid')

    def test_gradients(self):
        state_list = [State(), State(turn='b')]
        reward = GameResult.P1_WINS

        np.random.seed(185192)
        a1 = ValueNetworkAgent()
        a1.update(state_list, reward, use_numerical=False)
        actual_dwo, actual_dwh = a1.wo, a1.wh

        np.random.seed(185192)
        a2 = ValueNetworkAgent()
        a2.update(state_list, reward, use_numerical=True)
        expected_dwo, expected_dwh = a1.wo, a1.wh

        dwo_equal = np.allclose(actual_dwo, expected_dwo, 1e-8)
        dwh_equal = np.allclose(actual_dwh, expected_dwh, 1e-8)
        self.assertTrue(dwo_equal, 'dW_o almost equal')
        self.assertTrue(dwh_equal, 'dW_h almost equal')

    def test_select_move_white(self):
        s = State()
        a = ValueNetworkAgent()
        move = a.select_move(s)
        is_legal = True
        try:
            s.get_child(*move)
        except IllegalMoveException:
            is_legal = False
        self.assertTrue(is_legal, 'White select move')

    def test_select_move_black(self):
        s = State(turn='b')
        a = ValueNetworkAgent()
        move = a.select_move(s)
        is_legal = True
        try:
            s.get_child(*move)
        except IllegalMoveException:
            is_legal = False
        self.assertTrue(is_legal, 'White select move')

    def test_framework(self):  # can't really test this, but we're just
        # making sure eveerything runs without errors, because we have
        # already tested the update function
        a = ValueNetworkAgent()
        a.train_n_games(1, 1, save_filename='')


if __name__ == "__main__":
    unittest.main()
