MASK_DOWN = 0x00000000000000ff
MASK_UP = 0xff00000000000000
MASK_RIGHT = 0x0101010101010101
MASK_LEFT = 0x8080808080808080
MASK_DOWN2 = 0x000000000000ff00
MASK_UP2 = 0x00ff000000000000
MASK_RIGHT2 = 0x0202020202020202
MASK_LEFT2 = 0x4040404040404040


class IllegalMoveException(Exception):
    pass


class State:
    """
    Class to represent the state of a board
    """

    def __init__(self, white=None, black=None, turn='w', **kwargs):
        assert (white is None) == (black is None)
        assert turn in ('w', 'b')
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
                               kwargs.get('bk', 0x0800000000000000))  # king}
        self.white_turn = turn == 'w'

    def list_moves(self):
        pass

    def list_moves(self, piece: int):
        """
        List the moves of a specific piece (specified by bitboard)
        Params:
        ------
        piece: int
            BitBoard of piece to move
        Returns:
        ------
        List[int]:
            List of legal destinations of piece
        """
        out = []
        white_ioi = -1
        black_ioi = -1
        white_pos = 0
        black_pos = 0
        for i in range(6):
            black_pos != self.black[i]
            if piece & self.black[i] != 0:
                black_ioi = i
        for i in range(6):
            white_pos != self.white[i]
            if piece & self.white[i] != 0:
                white_ioi = i
        if self.white_turn:
            if white_ioi == 0:  # pawn
                out.extend(self.pawn_moves(piece, white_pos, black_pos))
            if white_ioi == 1:  # knight
                out.extend(self.knight_moves(piece, white_pos, black_pos))
            if white_ioi == 5:  # king
                if not (piece << 8) & (white_pos | black_pos):
                    out.append(piece << 8)
                if not (piece >> 8) & (white_pos | black_pos):
                    out.append(piece >> 8)
                if not (piece << 9) & (white_pos | black_pos):
                    out.append(piece << 9)
                if not (piece << 7) & (white_pos | black_pos):
                    out.append(piece << 7)
                if not (piece >> 9) & (white_pos | black_pos):
                    out.append(piece >> 9)
                if not (piece >> 7) & (white_pos | black_pos):
                    out.append(piece >> 7)
                if not (piece << 1) & (white_pos | black_pos):
                    out.append(piece << 1)
                if not (piece << 1) & (white_pos | black_pos):
                    out.append(piece << 1)
        else:
            if black_ioi == 0:  # pawn
                out.extend(self.pawn_moves(piece, white_pos, black_pos))
            if black_ioi == 1:  # knight
                out.extend(self.knight_moves(piece, white_pos, black_pos))
            if black_ioi == 5:  # king
                if not (piece << 8) & (white_pos | black_pos):
                    out.append(piece << 8)
                if not (piece >> 8) & (white_pos | black_pos):
                    out.append(piece >> 8)
                if not (piece << 9) & (white_pos | black_pos):
                    out.append(piece << 9)
                if not (piece << 7) & (white_pos | black_pos):
                    out.append(piece << 7)
                if not (piece >> 9) & (white_pos | black_pos):
                    out.append(piece >> 9)
                if not (piece >> 7) & (white_pos | black_pos):
                    out.append(piece >> 7)
                if not (piece << 1) & (white_pos | black_pos):
                    out.append(piece << 1)
                if not (piece << 1) & (white_pos | black_pos):
                    out.append(piece << 1)
        return out

    def knight_moves(self, piece, white_pos, black_pos):
        out = []
        if self.white_turn:
            if (piece << 10) & (~white_pos) and piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_UP):
                out.append(piece << 10)
            if (piece << 6) & (~white_pos) and piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_DOWN):
                out.append(piece << 6)
            if (piece >> 10) & (~white_pos) and piece & ~(MASK_RIGHT | MASK_RIGHT2 | MASK_DOWN):
                out.append(piece >> 10)
            if (piece >> 6) & (~white_pos) and piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_DOWN):
                out.append(piece >> 6)
            if (piece << 18) & (~white_pos) and piece & ~(MASK_UP | MASK_UP2 | MASK_LEFT):
                out.append(piece << 18)
            if (piece << 14) & (~white_pos) and piece & ~(MASK_UP | MASK_UP2 | MASK_RIGHT):
                out.append(piece << 14)
            if (piece >> 18) & (~white_pos) and piece & ~(MASK_DOWN | MASK_DOWN2 | MASK_RIGHT):
                out.append(piece >> 18)
            if (piece >> 14) & (~white_pos) and piece & ~(MASK_DOWN | MASK_DOWN2 | MASK_LEFT):
                out.append(piece >> 14)
        else:
            if (piece << 10) & (~black_pos) and piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_UP):
                out.append(piece << 10)
            if (piece << 6) & (~black_pos) and piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_DOWN):
                out.append(piece << 6)
            if (piece >> 10) & (~black_pos) and piece & ~(MASK_RIGHT | MASK_RIGHT2 | MASK_DOWN):
                out.append(piece >> 10)
            if (piece >> 6) & (~black_pos) and piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_DOWN):
                out.append(piece >> 6)
            if (piece << 18) & (~black_pos) and piece & ~(MASK_UP | MASK_UP2 | MASK_LEFT):
                out.append(piece << 18)
            if (piece << 14) & (~black_pos) and piece & ~(MASK_UP | MASK_UP2 | MASK_RIGHT):
                out.append(piece << 14)
            if (piece >> 18) & (~black_pos) and piece & ~(MASK_DOWN | MASK_DOWN2 | MASK_RIGHT):
                out.append(piece >> 18)
            if (piece >> 14) & (~black_pos) and piece & ~(MASK_DOWN | MASK_DOWN2 | MASK_LEFT):
                out.append(piece >> 14)
        return out

    def pawn_moves(self, piece, white_pos, black_pos):
        out = []
        if self.white_turn:
            if (piece << 8) & ~(white_pos | black_pos):
                out.append(piece << 8)
            if (1 << 9) <= piece <= (1 << 16) and (piece << 2 * 8) & ~(white_pos | black_pos) and (piece << 8) & ~(white_pos | black_pos):
                out.append(piece << 2 * 8)
            if (piece << 9) & (black_pos):
                out.append(piece << 9)
            if (piece << 7) & (black_pos):
                out.append(piece << 7)
        else:
            if not (piece >> 8) & ~(white_pos | black_pos):
                out.append(piece >> 8)
            if (1 << 49) <= piece <= (1 << 56) and (piece >> 2 * 8) & ~(white_pos | black_pos) and (piece >> 8) & ~(white_pos | black_pos):
                out.append(piece >> 2 * 8)
            if (piece >> 9) & (white_pos):
                out.append(piece >> 9)
            if (piece >> 7) & (white_pos):
                out.append(piece >> 7)
        return out

    def is_legal(self, piece: int, target: int):
        """
        Check if a move is legal
        Params:
        -----
        piece: int
            Piece to move
        target: int
            Destination of piece
        """
        pass

    def is_check(self):
        """
        Determine whether or not the current player is in check
        """
        pass

    def get_child(self, piece: int, target: int):
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

    def get_children(self):
        """
        Get a list of all possible child states
        """
        pass

    def __str__(self):
        """
        String representation of board. White is uppercase, black lowercase
        """
        names = 'p,n,b,r,q,k'.split(',')
        output = ['*'] * 64
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
    b = State()
    print(b)
