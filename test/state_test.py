import contextlib
import os
import unittest

from chess.state import *


def one_set_state(ix, value):
    white = [0] * 6
    white[ix] = value
    black = [0] * 6
    return State(white, black)


class StateTest(unittest.TestCase):
    def test_tostring(self):
        string = str(State())
        expected_string = 'rnbqkbnr\npppppppp\n........\n........\n........\n........\nPPPPPPPP\nRNBQKBNR'
        self.assertEqual(string, expected_string, 'String of new board state')

    def test_print_board(self):
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stdout(devnull):
                s = print_board(0xff0000)
        expected = '........\n........\n........\n........\n........\n11111111\n........\n........'
        self.assertEqual(s, expected, 'Board to string')

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

    def test_queen(self):
        state = State(wq=0x8000000)
        actual = state.queen_moves(0x8000000)
        expected = 0x492a1cf71c0000
        self.assertEqual(actual, expected)

    def test_list(self):
        state = State((0xff00, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0), 'w')
        actual = sorted(state.list_moves())
        expected = sorted(
            [(p, (p << 8) | (p << 16)) for p in [0x100, 0x200, 0x400, 0x800, 0x1000, 0x2000, 0x4000, 0x8000]])
        self.assertEqual(actual, expected, 'List Moves')

    def test_eq(self):
        s1 = State()
        s2 = State()
        self.assertEqual(s1, s2, 'Equals states')
        self.assertNotEqual(s1, State(wp=0), 'Unequal States')
        self.assertNotEqual(s1, 21387, 'Not a state')
        self.assertEqual(hash(s1), hash(s2), 'Equals states, hash values')

    def test_get_child(self):
        s1 = State()
        s2 = s1.get_child(0x800, 0x80000)
        expected = State(wp=0x8f700, turn='b')
        self.assertEqual(s2, expected, 'Pawn Move')
        self.assertRaises(IllegalMoveException, s1.get_child, 0x1, 0x100)

    def test_get_child_pin(self):
        s = State((0, 0, 0, 0, 0x200, 0x1), (0, 0, 0, 0, 1 << 63, 0x80))
        actual = s.get_child(0x200, 0x40000)
        expected = State((0, 0, 0, 0, 0x40000, 0x1), (0, 0, 0, 0, 1 << 63, 0x80), turn='b')
        self.assertEqual(actual, expected, 'Pinned piece, valid move')
        self.assertRaises(IllegalMoveException, s.get_child, 0x200, 0x2)

    def test_get_children(self):
        s = State((0, 0, 0, 0, 1 << 63, 0x80), (0, 0, 0, 0, 0x200, 0x1), turn='b')
        actual = set(s.get_children())

        expected = {
            State((0, 0, 0, 0, 1 << 63, 0x80), (0, 0, 0, 0, 0x200, 0x2)),
            State((0, 0, 0, 0, 1 << 63, 0x80), (0, 0, 0, 0, 0x200, 0x100)),
            State((0, 0, 0, 0, 1 << 63, 0x80), (0, 0, 0, 0, 0x40000, 0x1)),
            State((0, 0, 0, 0, 1 << 63, 0x80), (0, 0, 0, 0, 0x8000000, 0x1)),
            State((0, 0, 0, 0, 1 << 63, 0x80), (0, 0, 0, 0, 0x1000000000, 0x1)),
            State((0, 0, 0, 0, 1 << 63, 0x80), (0, 0, 0, 0, 0x200000000000, 0x1)),
            State((0, 0, 0, 0, 1 << 63, 0x80), (0, 0, 0, 0, 0x40000000000000, 0x1)),
            State((0, 0, 0, 0, 0, 0x80), (0, 0, 0, 0, 0x8000000000000000, 0x1))
        }
        self.assertSetEqual(actual, expected, 'List of possible moves')

    def test_is_terminal(self):
        s = State((0, 0, 0, 0, 1 << 63, 0x80), (0, 0, 0, 0, 0x200, 0x1), turn='b')
        actual = s.is_terminal()
        expected = GameResult.NONTERMINAL
        self.assertEqual(actual, expected, 'Nonterminal State')

        s = State((0, 0, 0, 0, 0x100, 0x10000), (0, 0, 0, 0, 0, 0x1), turn='b')
        s.in_check = True
        actual = s.is_terminal()
        expected = GameResult.P1_WINS
        self.assertEqual(actual, expected, 'Someone Wins')

        s = State((0, 0, 0, 0, 0x10000 | 0x40000, 0), (0, 0, 0, 0, 0, 0x2), turn='b')
        s.in_check = False
        actual = s.is_terminal()
        expected = GameResult.DRAW
        self.assertEqual(actual, expected, 'Stalemate')

    def test_from_dict(self):
        pieces = ['r', 'p', 'n', 'q', 'k', 'b', 0, 0] + [0] * 48 + ['R', 'P', 'N', 'Q', 'K', 'B', 0, 0]
        in_check = False
        turn = 'w'
        actual = State.from_dict(pieces, turn, in_check)
        expected = State((0x40, 0x20, 0x4, 0x80, 0x10, 0x8),
                         (0x40 << 56, 0x20 << 56, 0x4 << 56, 0x80 << 56, 0x10 << 56, 0x8 << 56),
                         turn=turn, in_check=in_check)
        self.assertEqual(actual, expected, 'Dictionary to state')
        self.assertRaises(IllegalStateException, State.from_dict, pieces + [0], 'w', False)

    def test_to_dict(self):
        # Test the to_dict method (with knowledge that from_dict is correct
        expected = State()
        ed = expected.to_dict()
        actual = State.from_dict(ed['pieces'], ed['turn'], ed['in_check'])
        self.assertEqual(actual, expected, 'Convert state to dict and back')

    def test_result_bool(self):
        self.assertEqual(bool(GameResult.NONTERMINAL), False)
        self.assertEqual(bool(GameResult.DRAW), True)


if __name__ == "__main__":
    unittest.main()
