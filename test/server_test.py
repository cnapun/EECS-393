import json
import unittest

from chess.state import State
from chess.server import app


class ServerTestTwoPlayer(unittest.TestCase):
    """
    Unittest class for two player server: Corresponds to STS-1
    """

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_valid_move(self):
        """
        STS-1 Test 1
        """
        s = State()
        request = s.to_dict()
        request.pop('winner', None)
        request['piece'] = 1
        request['target'] = 18

        result = self.app.post('/move', data=json.dumps(request), headers={'content-type': 'application/json'})

        self.assertEqual(200, result.status_code, 'Status is OK')
        expected = s.get_child(1 << 1, 1 << 18)
        expected = expected.to_dict()
        self.assertEqual(expected, json.loads(result.data), 'Returned response')

    def test_invalid_move(self):
        """
        STS-1 Test 2
        """
        s = State()
        request = s.to_dict()
        request.pop('winner', None)
        request['piece'] = 1
        request['target'] = 20

        result = self.app.post('/move', data=json.dumps(request), headers={'content-type': 'application/json'})
        self.assertEqual(400, result.status_code, 'Illegal request throws error')
        result_message = json.loads(result.data)['message']
        self.assertEqual(result_message, 'Completely and utterly illegal move', 'Illegal move message')

    def test_malformed(self):
        """
        STS-1 Test 3
        """
        request = {'hi': -1}
        result = self.app.post('/move', data=json.dumps(request), headers={'content-type': 'application/json'})
        self.assertEqual(400, result.status_code, 'Malformed request throws error')

    def test_white_win(self):
        """
        STS-1 Test 4
        """
        s = State(
            (0, 0, 0, 0, 2 << 16, 4 << 16),
            (0, 0, 0, 0, 0, 1),
            turn='w',
            in_check=False
        )
        request = s.to_dict()
        request.pop('winner', None)
        request['piece'] = 17
        request['target'] = 9
        result = self.app.post('/move', data=json.dumps(request), headers={'content-type': 'application/json'})
        self.assertEqual(200, result.status_code, 'Status is OK')
        data = json.loads(result.data)

        self.assertEqual(data['winner'], 'P1_WINS', 'White wins')

    def test_black_win(self):
        """
        STS-1 Test 5
        """
        s = State(
            (0, 0, 0, 0, 0, 1),
            (0, 0, 0, 0, 2 << 16, 4 << 16),
            turn='b',
            in_check=False
        )
        request = s.to_dict()
        request.pop('winner', None)
        request['piece'] = 17
        request['target'] = 9
        result = self.app.post('/move', data=json.dumps(request), headers={'content-type': 'application/json'})
        self.assertEqual(200, result.status_code, 'Status is OK')
        data = json.loads(result.data)

        self.assertEqual(data['winner'], 'P2_WINS', 'Black wins')

    def test_white_stalemate(self):
        """
        STS-1 Test 6
        """
        s = State(
            (0, 0, 0, 0, 1 << 24, 4 << 16),
            (0, 0, 0, 0, 0, 2),
            turn='w',
            in_check=False
        )
        request = s.to_dict()
        request.pop('winner', None)
        request['piece'] = 24
        request['target'] = 16
        result = self.app.post('/move', data=json.dumps(request), headers={'content-type': 'application/json'})
        self.assertEqual(200, result.status_code, 'Status is OK')
        data = json.loads(result.data)

        self.assertEqual(data['winner'], 'DRAW', 'White moves, stalemate ensues')

    def test_black_stalemate(self):
        """
        STS-1 Test 7
        """
        s = State(
            (0, 0, 0, 0, 0, 2),
            (0, 0, 0, 0, 1 << 24, 4 << 16),
            turn='b',
            in_check=False
        )
        request = s.to_dict()
        request.pop('winner', None)
        request['piece'] = 24
        request['target'] = 16
        result = self.app.post('/move', data=json.dumps(request), headers={'content-type': 'application/json'})
        self.assertEqual(200, result.status_code, 'Status is OK')
        data = json.loads(result.data)

        self.assertEqual(data['winner'], 'DRAW', 'Black moves, stalemate ensues')

    def test_reset(self):
        s = State()
        result = self.app.get('/reset')
        self.assertEqual(s.to_dict(), json.loads(result.data), 'Reset board state')
