import unittest
from state import *


def one_set_state(ix, value):
    white = [0] * 6
    white[ix] = value
    black = [0] * 6
    return State(white, black)


class StateTest(unittest.TestCase):
    def test_tostring(self):
        string = str(State())
        expected_string = 'rnbqkbnr\npppppppp\n********\n********\n********\n********\nPPPPPPPP\nRNBQKBNR'.replace('*', '.')
        self.assertEqual(string, expected_string, 'String of new board state')

    def test_unmoved_pawn_no_blocking(self):
        state = State()
        actual = state.get_moves(0x1000)
        expected = 0x100000 | 0x10000000
        self.assertEqual(actual, expected, "Unmoved white pawn")
        state.white_turn = False
        actual = state.get_moves(1 << 52)
        expected = (1 << 44) | (1 << 36)
        self.assertEqual(actual, expected, "Unmoved black pawn")

    def test_unmoved_pawn_blocking(self):
        state = State(bp=(0x10 << 24))
        actual = state.get_moves(0x1000)
        expected = 0x10 << 16
        self.assertEqual(actual, expected,
                         "Unmoved white pawn, blocked at row 4")
        state = State(bp=(0x10 << 16))
        actual = state.get_moves(0x1000)
        expected = 0
        self.assertEqual(actual, expected,
                         "Unmoved white pawn, blocked at row 3")

        state = State(wp=(0x10 << 32), turn='b')
        actual = state.get_moves(0x10 << 32 + 16)
        expected = 0x10 << (32 + 8)
        self.assertEqual(actual, expected,
                         "Unmoved black pawn, blocked at row 5")
        state = State(wp=(0x10 << (32 + 8)), turn='b')
        actual = state.get_moves(0x10 << 32 + 16)
        expected = 0
        self.assertEqual(actual, expected,
                         "Unmoved black pawn, blocked at row 6")

        self.assertRaises(NoSuchPieceException, state.get_moves, 0x100000)

    def test_pawn_capture(self):
        state = State(bp=(0x20 << 16))
        actual = state.get_moves(0x1000)
        expected = (0x1000 << 8) | (0x1000 << 16) | (0x1000 << 9)
        self.assertEqual(actual, expected, "White pawn capturing")
        state.white_turn = False
        actual = state.get_moves(0x20 << 16)
        expected = 0x1000 | 0x4000
        self.assertEqual(actual, expected, "Black pawn capturing")

    def test_king(self):
        state = State()
        actual = state.get_moves(0x08)
        self.assertEqual(actual, 0, "King with no moves")
        state = State(wp=0)
        actual = state.get_moves(0x08)
        expected = 0x400 | 0x800 | 0x1000
        self.assertEqual(actual, expected, "King with some moves")

    def test_knight(self):
        state = one_set_state(1, 0x1 << 16)
        actual = state.get_moves(0x1 << 16)
        expected = 0x2 | 0x400 | 0x4000000 | 0x200000000
        self.assertEqual(actual, expected, "Knight on right edge")

        state = State()
        actual = state.get_moves(0x2)
        expected = 0x40000 | 0x10000
        self.assertEqual(actual, expected, "Right knight in starting position")

        actual = state.get_moves(0x40)
        expected = 0x800000 | 0x200000
        self.assertEqual(actual, expected, "Left knight in starting position")

        state = one_set_state(1, 0x8 << 16)
        actual = state.get_moves(0x8 << 16)
        expected = 0x1422002214
        self.assertEqual(actual, expected, "Knight in centerin starting position")

    def test_rook(self):
        state = State(wr=0x40000)
        actual = state.get_moves(0x40000)
        expected = (0xff0000 | 0x0004040404040000) & ~0x40000
        self.assertEqual(actual, expected, "Rook in middle of board")
        state = State()
        actual = state.get_moves(1)
        expected = 0
        self.assertEqual(actual, expected, "Rook with no moves")

    def test_bishop(self):
        state = State(wb=0x40000)
        actual = state.get_moves(0x40000)
        expected = 0x4020110a000000
        self.assertEqual(actual, expected, "Bishop in middle of baord")
        state = State()
        actual = state.get_moves(0x4)
        expected = 0
        self.assertEqual(actual, expected, "Bishop with no moves")
