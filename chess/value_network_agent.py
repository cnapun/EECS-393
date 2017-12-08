from typing import List, Tuple
import os
import pickle

import numpy as np
from chess.state import GameResult, State
from chess.agents import LearningAgent


def relu(x):
    return np.maximum(0, x)


def sigmoid(x):
    return np.clip(1 / (1 + np.exp(-x)), 1e-6, 1 - 1e-6)


class ValueNetworkAgent(LearningAgent):
    def __init__(self, hidden_dim=50):
        self.wh = (np.random.randn(8 * 8, hidden_dim) / 100).astype(
            np.float32)
        self.wo = (np.random.randn(hidden_dim) / 100).astype(np.float32)
        self.wh_cache = np.zeros_like(self.wh)
        self.wo_cache = np.zeros_like(self.wo)

    def update(self, states: List['State'], result: GameResult,
               use_numerical=False):
        if result in (GameResult.DRAW, GameResult.NONTERMINAL):
            reward = (0.4, 0.4)  # Draws aren't good
        elif result == GameResult.P1_WINS:
            reward = (0, 1)  # (black, white) rewards
        else:
            reward = (1, 0)  # (black, white) rewards
        state_arrays = []
        for s in states:
            x = s.to_ndarray()
            if not s.white_turn:
                x = -x[::-1]
            state_arrays.append(x)

        rewards = []
        for s in states:
            rewards.append(reward[s.white_turn])

        xs = np.array(state_arrays, dtype=np.float32).reshape(len(states), -1)
        ys = np.array(rewards, dtype=np.float32)
        if not use_numerical:
            dwo, dwh = self.get_grads(xs, ys)
        else:
            dwo, dwh = self.get_grads_numerical(xs, ys)

        self.wh_cache *= 0.9
        self.wh_cache += 0.1 * dwh ** 2

        self.wo_cache *= 0.9
        self.wo_cache += 0.1 * dwo ** 2

        self.wh -= 0.001 * dwh / (np.sqrt(self.wh_cache + 1e-12))
        self.wo -= 0.001 * dwo / (np.sqrt(self.wo_cache + 1e-12))

    def get_grads(self, xs, ys):
        h = relu(xs @ self.wh)
        values = sigmoid(h @ self.wo)

        do = (values - ys) * values * (1 - values) / len(values)
        dwo = h.T @ do
        dh = np.outer(do, self.wo) * (h > 0)

        dwh = xs.T @ dh
        return dwo, dwh

    def get_grads_numerical(self, xs, ys):
        wh = self.wh.copy()
        wo = self.wo.copy()
        dwh = np.zeros_like(wh)
        dwo = np.zeros_like(wo)

        def forward(wo, wh):
            h = relu(xs @ wh)
            values = sigmoid(h @ wo)
            return np.mean(0.5 * (values - ys) ** 2)

        h = 1e-5
        for wh_ix in np.ndindex(wh.shape):
            wh[wh_ix] += h
            forward_loss = forward(wo, wh)
            wh[wh_ix] -= 2 * h
            backward_loss = forward(wo, wh)
            dwh[wh_ix] = (forward_loss - backward_loss) / (2 * h)

        for wo_ix in np.ndindex(wo.shape):
            wo[wo_ix] += h
            forward_loss = forward(wo, wh)
            wo[wo_ix] -= 2 * h
            backward_loss = forward(wo, wh)
            dwo[wo_ix] = (forward_loss - backward_loss) / (2 * h)
        return dwo, dwh

    def select_move(self, state: 'State') -> Tuple[int, int]:
        children = list(state.get_children())
        xs = []
        for s_prime in children:
            if state.white_turn:
                xs.append(s_prime.to_ndarray())
            else:
                xs.append(-s_prime.to_ndarray()[::-1])
        x = np.array(xs, dtype=np.float32).reshape(len(children), -1)
        h = relu(x @ self.wh)

        values = sigmoid(h @ self.wo)
        choice = children[values.argmax()]
        return choice.prev_move

    @property
    def max_iter(self) -> int:
        return 200

    @staticmethod
    def from_file(filename, **kwargs):
        a = ValueNetworkAgent(**kwargs)
        with open(filename, 'wb') as f:
            weight_tuple = pickle.load(f)
        a.wo, a.wh, a.wo_cache, a.wh_cache = weight_tuple
        return a

    def to_file(self, filename):
        # if os.path.isfile(filename):
        #     raise FileExistsError('%s already exists' % filename)
        with open(filename, 'wb') as f:
            pickle.dump((self.wo, self.wh, self.wo_cache, self.wh_cache), f)


if __name__ == '__main__':
    a = ValueNetworkAgent()
    a.train_n_games(10, 1, 'sampleagent.pkl')
