import json
import unittest

from chess.state import State
from chess.server import app


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_valid_move(self):
        s = State()
        my_requst = s.to_dict()
        my_requst.pop('winner', None)
        my_requst['piece'] = 1
        my_requst['target'] = 18
        my_requst['pieces'] = [i or '.' for i in my_requst['pieces']]

        result = self.app.post('/move', data=json.dumps(my_requst), headers={'content-type': 'application/json'})

        self.assertEqual(200, result.status_code, 'Status is 200')
        expected = s.get_child(1 << 1, 1 << 18)
        expected = expected.to_dict()
        self.assertEqual(expected, json.loads(result.data), 'Returned response')
        # self.assertEqual(result)

    def test_error(self):
        s = State()
        my_requst = s.to_dict()
        my_requst.pop('winner', None)
        my_requst['piece'] = 1
        my_requst['target'] = 20
        my_requst['pieces'] = [i or '.' for i in my_requst['pieces']]

        result = self.app.post('/move', data=json.dumps(my_requst), headers={'content-type': 'application/json'})
        self.assertEqual(400, result.status_code, 'Illegal request throws error')
        result_message = json.loads(result.data)['message']
        self.assertEqual(result_message, 'Completely and utterly illegal move', 'Illegal move message')

    def test_reset(self):
        s = State()
        result = self.app.get('/reset')
        self.assertEqual(s.to_dict(), json.loads(result.data), 'Reset board state')
