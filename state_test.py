import unittest
from state import *


class StateTest(unittest.TestCase):
    def test_tostring(self):
        string = str(State())
        expected_string = 'rnbqkbnr\npppppppp\n********\n********\n********\n********\nPPPPPPPP\nRNBQKBNR'
        self.assertEqual(string, expected_string, 'String of new board state')

    def test_unmoved_pawn_no_blocking(self):
        state = State()
        actual = state.list_moves(0x1000)
        expected = 0x100000 | 0x10000000
        self.assertEqual(actual, expected, "Unmoved white pawn")
        state.white_turn = False
        actual = state.list_moves(1 << 52)
        expected = (1 << 44) | (1 << 36)
        self.assertEqual(actual, expected, "Unmoved black pawn")

    def test_unmoved_pawn_blocking(self):
        state = State(bp=(0x10 << 24))
        actual = state.list_moves(0x1000)
        expected = 0x10 << 16
        self.assertEqual(actual, expected,
                         "Unmoved white pawn, blocked at row 4")
        state = State(bp=(0x10 << 16))
        actual = state.list_moves(0x1000)
        expected = 0
        self.assertEqual(actual, expected,
                         "Unmoved white pawn, blocked at row 3")

        state = State(wp=(0x10 << 32), turn='b')
        actual = state.list_moves(0x10 << 32 + 16)
        expected = 0x10 << (32 + 8)
        self.assertEqual(actual, expected,
                         "Unmoved black pawn, blocked at row 5")
        state = State(wp=(0x10 << (32 + 8)), turn='b')
        actual = state.list_moves(0x10 << 32 + 16)
        expected = 0
        self.assertEqual(actual, expected,
                         "Unmoved black pawn, blocked at row 6")

        self.assertRaises(NoSuchPieceException, state.list_moves, 0x100000)
    def test_pawn_capture(self):
        state = State(bp=(0x20 << 16))
        actual = state.list_moves(0x1000)
        expected = (0x1000<<8) | (0x1000<<16) | (0x1000<<9)
        self.assertEqual(actual, expected, "White pawn capturing")
        state.white_turn = False
        actual = state.list_moves(0x20 << 16)
        expected = 0x1000 | 0x4000
        self.assertEqual(actual, expected, "Black pawn capturing")