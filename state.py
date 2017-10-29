import abc
import enum
from typing import List, Tuple, Iterable

MASK_DOWN = 0x00000000000000ff
MASK_UP = 0xff00000000000000
MASK_RIGHT = 0x0101010101010101
MASK_LEFT = 0x8080808080808080
MASK_DOWN2 = 0x000000000000ff00
MASK_UP2 = 0x00ff000000000000
MASK_RIGHT2 = 0x0202020202020202
MASK_LEFT2 = 0x4040404040404040
MASK_DL = MASK_DOWN | MASK_LEFT
MASK_DR = MASK_DOWN | MASK_RIGHT
MASK_UL = MASK_UP | MASK_LEFT
MASK_UR = MASK_UP | MASK_RIGHT


class IllegalMoveException(Exception):
    pass


class NoSuchPieceException(Exception):
    pass


class AutoName(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class GameResult(enum.AutoName):
    P1_WINS = enum.auto()
    P2_WINS = enum.auto()
    DRAW = enum.auto()
    NONTERMINAL = enum.auto()


def print_board(board: int) -> None:
    m = 1 << 63
    for _ in range(8):
        o = []
        for _ in range(8):
            o.append('1' if m & board else '.')
            m >>= 1
        print(''.join(o))


class State:
    """
    Class to represent the state of a board
    """

    def __init__(self, white: Tuple[int, int, int, int, int, int] = None,
                 black: Tuple[int, int, int, int, int, int] = None, turn: str = 'w', prev_move: Tuple[int, int] = None,
                 **kwargs: int) -> None:
        assert (white is None) == (black is None)
        assert turn in ('w', 'b')
        self.prev_move = prev_move
        self.white = white or (kwargs.get('wp', 0x000000000000ff00),  # pawns
                               kwargs.get('wn', 0x0000000000000042),  # knights
                               kwargs.get('wb', 0x0000000000000024),  # bishops
                               kwargs.get('wr', 0x0000000000000081),  # rooks
                               kwargs.get('wq', 0x0000000000000010),  # queen
                               kwargs.get('wk', 0x0000000000000008))  # king
        self.black = black or (kwargs.get('bp', 0x00ff000000000000),  # pawns
                               kwargs.get('bk', 0x4200000000000000),  # knights
                               kwargs.get('bb', 0x2400000000000000),  # bishops
                               kwargs.get('br', 0x8100000000000000),  # rooks
                               kwargs.get('bq', 0x1000000000000000),  # queen
                               kwargs.get('bk', 0x0800000000000000))  # king
        # Make sure board layout is valid (no overlap)
        self.white_pos = 0
        for e in self.white:
            assert (self.white_pos & e) == 0
            self.white_pos |= e
        self.black_pos = 0
        for e in self.black:
            assert (self.black_pos & e) == 0
            assert (e & self.white_pos) == 0
            self.black_pos |= e

        self.white_turn = turn == 'w'

    def list_moves(self) -> List[Tuple[int, int]]:
        current_player = self.white if self.white_turn else self.black
        out = []
        for pieces in current_player:
            m = 1 << 63
            while m > 0:
                if pieces & m:
                    out.append((m, self.get_moves(m)))
                m >>= 1
        return out

    def get_moves(self, piece: int) -> int:
        """
        List the moves of a specific piece (specified by bitboard)
        Params:
        ------
        piece: int
            BitBoard of piece to move
        Returns:
        ------
        int:
            Bitboard of legal destinations of piece
        """
        out = []
        white_ioi = -1
        black_ioi = -1
        white_pos = 0
        black_pos = 0
        for i in range(6):
            black_pos |= self.black[i]
            if piece & self.black[i] != 0:
                black_ioi = i
        for i in range(6):
            white_pos |= self.white[i]
            if piece & self.white[i] != 0:
                white_ioi = i
        ioi = white_ioi if self.white_turn else black_ioi
        if ioi < 0:
            raise NoSuchPieceException(
                f'No {"white" if self.white_turn else "black"} piece at {piece}')
        if ioi == 0:  # pawn
            out = self.pawn_moves(piece)
        elif ioi == 1:  # knight
            out = self.knight_moves(piece)
        elif ioi == 2:
            out = self.bishop_moves(piece)
        elif ioi == 3:
            out = self.rook_moves(piece)
        elif ioi == 4:
            out = self.queen_moves(piece)
        elif ioi == 5:  # king
            out = self.king_moves(piece)
        return out

    def knight_moves(self, piece: int) -> int:
        white_pos, black_pos = self.white_pos, self.black_pos
        out = 0
        if self.white_turn:
            if (piece << 10) & (~white_pos) and piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_UP):
                out |= (piece << 10)
            if (piece << 6) & (~white_pos) and piece & ~(MASK_RIGHT | MASK_RIGHT2 | MASK_UP):
                out |= (piece << 6)
            if (piece >> 10) & (~white_pos) and piece & ~(MASK_RIGHT | MASK_RIGHT2 | MASK_DOWN):
                out |= (piece >> 10)
            if (piece >> 6) & (~white_pos) and piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_DOWN):
                out |= (piece >> 6)
            if (piece << 17) & (~white_pos) and piece & ~(MASK_UP | MASK_UP2 | MASK_LEFT):
                out |= (piece << 17)
            if (piece << 15) & (~white_pos) and piece & ~(MASK_UP | MASK_UP2 | MASK_RIGHT):
                out |= (piece << 15)
            if (piece >> 17) & (~white_pos) and piece & ~(MASK_DOWN | MASK_DOWN2 | MASK_RIGHT):
                out |= (piece >> 17)
            if (piece >> 15) & (~white_pos) and piece & ~(MASK_DOWN | MASK_DOWN2 | MASK_LEFT):
                out |= (piece >> 15)
        else:
            if (piece << 10) & (~black_pos) and piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_UP):
                out |= (piece << 10)
            if (piece << 6) & (~black_pos) and piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_DOWN):
                out |= (piece << 6)
            if (piece >> 10) & (~black_pos) and piece & ~(MASK_RIGHT | MASK_RIGHT2 | MASK_DOWN):
                out |= (piece >> 10)
            if (piece >> 6) & (~black_pos) and piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_DOWN):
                out |= (piece >> 6)
            if (piece << 18) & (~black_pos) and piece & ~(MASK_UP | MASK_UP2 | MASK_LEFT):
                out |= (piece << 18)
            if (piece << 14) & (~black_pos) and piece & ~(MASK_UP | MASK_UP2 | MASK_RIGHT):
                out |= (piece << 14)
            if (piece >> 18) & (~black_pos) and piece & ~(MASK_DOWN | MASK_DOWN2 | MASK_RIGHT):
                out |= (piece >> 18)
            if (piece >> 14) & (~black_pos) and piece & ~(MASK_DOWN | MASK_DOWN2 | MASK_LEFT):
                out |= (piece >> 14)
        return out

    def pawn_moves(self, piece: int) -> int:
        white_pos, black_pos = self.white_pos, self.black_pos
        out = 0
        if self.white_turn:
            if (piece << 8) & ~(white_pos | black_pos):
                out |= (piece << 8)
                if (1 << 8) <= piece <= (1 << 15) and ((piece << 2 * 8)) & ~(white_pos | black_pos):
                    out |= (piece << 2 * 8)
            if ((piece & ~MASK_LEFT) << 9) & (black_pos):
                out |= (piece << 9)
            if ((piece & ~MASK_RIGHT) << 7) & (black_pos):
                out |= (piece << 7)
        else:
            if (piece >> 8) & ~(white_pos | black_pos):
                out |= (piece >> 8)
            if (1 << 49) <= piece <= (1 << 56) and (piece >> 2 * 8) & ~(white_pos | black_pos) and (piece >> 8) & ~(
                        white_pos | black_pos):
                out |= (piece >> 2 * 8)
            if ((piece & ~MASK_RIGHT) >> 9) & white_pos:
                out |= (piece >> 9)
            if ((piece & ~MASK_LEFT) >> 7) & white_pos:
                out |= (piece >> 7)
        return out

    def king_moves(self, piece: int) -> int:
        white_pos, black_pos = self.white_pos, self.black_pos
        if self.white_turn:
            out = (((piece & ~MASK_UP) << 8) & ~white_pos) | \
                  (((piece & ~MASK_DOWN) >> 8) & ~white_pos) | \
                  (((piece & ~MASK_UL) << 9) & ~white_pos) | \
                  (((piece & ~MASK_UR) << 7) & ~white_pos) | \
                  (((piece & ~MASK_DR) >> 9) & ~white_pos) | \
                  (((piece & ~MASK_DL) >> 7) & ~white_pos) | \
                  (((piece & ~MASK_RIGHT) >> 1) & ~white_pos) | \
                  (((piece & ~MASK_LEFT) << 1) & ~white_pos)
        else:
            out = (((piece & ~MASK_UP) << 8) & ~black_pos) | \
                  (((piece & ~MASK_DOWN) >> 8) & ~black_pos) | \
                  (((piece & ~MASK_UL) << 9) & ~black_pos) | \
                  (((piece & ~MASK_UR) << 7) & ~black_pos) | \
                  (((piece & ~MASK_DR) >> 9) & ~black_pos) | \
                  (((piece & ~MASK_DL) >> 7) & ~black_pos) | \
                  (((piece & ~MASK_RIGHT) >> 1) & ~black_pos) | \
                  (((piece & ~MASK_LEFT) << 1) & ~black_pos)
        return out

    def rook_moves(self, piece: int) -> int:
        white_pos, black_pos = self.white_pos & ~piece, self.black_pos
        moves = 0
        opponent = black_pos if self.white_turn else white_pos
        # Down
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_DOWN) >> 8
        moves |= current_ray & opponent

        # Up
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_UP) << 8
        moves |= current_ray & opponent

        # Left
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_RIGHT) >> 1
        moves |= current_ray & opponent

        # Right
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_LEFT) << 1
        moves |= current_ray & opponent
        return moves & ~piece

    def bishop_moves(self, piece: int) -> int:
        white_pos, black_pos = self.white_pos & ~piece, self.black_pos
        moves = 0
        opponent = black_pos if self.white_turn else white_pos
        # Down Right
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_DR) >> 9
            moves |= current_ray & opponent

        # Up Left
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_UL) << 9
        moves |= current_ray & opponent

        # Down Left
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_DL) >> 7
        moves |= current_ray & opponent

        # Up Right
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_UR) << 7
        moves |= current_ray & opponent
        return moves & ~piece

    def queen_moves(self, piece: int) -> int:
        return self.rook_moves(piece) | self.bishop_moves(piece)

    def is_legal(self, piece: int, target: int) -> bool:
        """
        Check if a move is legal
        Params:
        -----
        piece: int
            Piece to move
        target: int
            Destination of piece
        Returns:
        -------
        bool:
            True if move is legal else False
        """
        return (self.get_moves(piece) | target) != 0

    def is_check(self) -> bool:
        """
        Determine whether or not the current player is in check
        """
        pass

    def get_child(self, piece: int, target: int) -> 'State':
        """
        Get a single child state from a move
        Params:
        piece: int
            Piece to move
        target: int
            Destination of piece
        Returns:
        -------
        State:
            Resulting state after making move
        Raises:
        ------
        IllegalMoveException
        """
        pass

    def get_children(self) -> Iterable['State']:
        """
        Get a list of all possible child states
        """
        pass

    def is_terminal(self) -> GameResult:
        pass

    def __str__(self):
        """
        String representation of board. White is uppercase, black lowercase
        """
        names = 'p,n,b,r,q,k'.split(',')
        output = ['.'] * 64
        for white, player in zip([True, False], (self.white, self.black)):
            for name, locs in zip(names, player):
                mask = 1 << 63
                i = 0
                while mask > 0:  # check every single square
                    if locs & mask != 0:  # there's a piece at location specified by mask
                        output[i] = name.upper() if white else name.lower()
                    mask >>= 1
                    i += 1
        return '\n'.join(''.join(output[8 * i:8 * (i + 1)]) for i in range(8))


if __name__ == '__main__':
    state = State()
    actual = state.get_moves(0x1000)

    # print(b)
