import unittest
from agents import MinimaxAgent


class SampleMinimaxAgent(MinimaxAgent):
    def __init__(self, max_depth: int = 2):
        self._max_depth = max_depth

    @property
    def max_depth(self):
        return self._max_depth

    def heuristic(self, state: 'State'):
        if (state.white[0] == 0xff00 and state.white_turn) or (
                state.black[0] == 0xff000000000000 and not state.white_turn):
            return 10
        else:
            return -10


class MinimaxTest(unittest.TestCase):
    def test_search(self):
        pass
