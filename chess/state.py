import enum
import random
from typing import List, Tuple, Iterable, Union
import numpy as np

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

KNIGHT_MOVES = {}
BISHOP_MOVES = {}
KING_MOVES = {}
QUEEN_MOVES = {}
ROOK_MOVES = {}

for i in range(64):
    out = 0
    piece = 1 << i
    if piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_UP):
        out |= (piece << 10)
    if piece & ~(MASK_RIGHT | MASK_RIGHT2 | MASK_UP):
        out |= (piece << 6)
    if piece & ~(MASK_RIGHT | MASK_RIGHT2 | MASK_DOWN):
        out |= (piece >> 10)
    if piece & ~(MASK_LEFT | MASK_LEFT2 | MASK_DOWN):
        out |= (piece >> 6)
    if piece & ~(MASK_UP | MASK_UP2 | MASK_LEFT):
        out |= (piece << 17)
    if piece & ~(MASK_UP | MASK_UP2 | MASK_RIGHT):
        out |= (piece << 15)
    if piece & ~(MASK_DOWN | MASK_DOWN2 | MASK_RIGHT):
        out |= (piece >> 17)
    if piece & ~(MASK_DOWN | MASK_DOWN2 | MASK_LEFT):
        out |= (piece >> 15)
    KNIGHT_MOVES[piece] = out

# Bishop ray table to be used for easy access
for i in range(64):
    moves = 0
    piece = 1 << i

    # Down Right
    current_ray = piece
    while current_ray:
        moves |= current_ray
        current_ray = (current_ray & ~MASK_DR) >> 9
    moves |= current_ray

    # Up Left
    current_ray = piece
    while current_ray:
        moves |= current_ray
        current_ray = (current_ray & ~MASK_UL) << 9
    moves |= current_ray

    # Down Left
    current_ray = piece
    while current_ray:
        moves |= current_ray
        current_ray = (current_ray & ~MASK_DL) >> 7
    moves |= current_ray

    # Up Right
    current_ray = piece
    while current_ray:
        moves |= current_ray
        current_ray = (current_ray & ~MASK_UR) << 7
    moves |= current_ray
    BISHOP_MOVES[piece] = moves

# Rook ray table
for i in range(64):
    moves = 0
    piece = 1 << i
    # Down
    current_ray = piece
    while current_ray:
        moves |= current_ray
        current_ray = (current_ray & ~MASK_DOWN) >> 8
    moves |= current_ray

    # Up
    current_ray = piece
    while current_ray:
        moves |= current_ray
        current_ray = (current_ray & ~MASK_UP) << 8
    moves |= current_ray

    # Left
    current_ray = piece
    while current_ray:
        moves |= current_ray
        current_ray = (current_ray & ~MASK_RIGHT) >> 1
    moves |= current_ray

    # Right
    current_ray = piece
    while current_ray:
        moves |= current_ray
        current_ray = (current_ray & ~MASK_LEFT) << 1
    moves |= current_ray

    ROOK_MOVES[piece] = moves

# King move table
for i in range(64):
    piece = 1 << i
    KING_MOVES[piece] = ((piece & ~MASK_UP) << 8) | \
                        ((piece & ~MASK_DOWN) >> 8) | \
                        ((piece & ~MASK_UL) << 9) | \
                        ((piece & ~MASK_UR) << 7) | \
                        ((piece & ~MASK_DL) >> 7) | \
                        ((piece & ~MASK_DR) >> 9) | \
                        ((piece & ~MASK_RIGHT) >> 1) | \
                        ((piece & ~MASK_LEFT) << 1)

# Queen ray table
for i in range(64):
    piece = 1 << i
    QUEEN_MOVES[piece] = BISHOP_MOVES[piece] | ROOK_MOVES[piece]

FILES = [
    0x8080808080808080,
    0x4040404040404040,
    0x2020202020202020,
    0x1010101010101010,
    0x0808080808080808,
    0x0404040404040404,
    0x0202020202020202,
    0x0101010101010101
]

RANKS = [
    0xff,
    0xff << 8,
    0xff << 16,
    0xff << 24,
    0xff << 32,
    0xff << 40,
    0xff << 48,
    0xff << 56
]


def bitboard_to_AN(board: int):
    if board & FILES[0]:
        file = 'a'
    elif board & FILES[1]:
        file = 'b'
    elif board & FILES[2]:
        file = 'c'
    elif board & FILES[3]:
        file = 'd'
    elif board & FILES[4]:
        file = 'e'
    elif board & FILES[5]:
        file = 'f'
    elif board & FILES[6]:
        file = 'g'
    else:
        file = 'h'

    if board & RANKS[0]:
        rank = 1
    elif board & RANKS[1]:
        rank = 2
    elif board & RANKS[2]:
        rank = 3
    elif board & RANKS[3]:
        rank = 4
    elif board & RANKS[4]:
        rank = 5
    elif board & RANKS[5]:
        rank = 6
    elif board & RANKS[6]:
        rank = 7
    else:
        rank = 8

    return '%s%d' % (file, rank)


class ChessException(Exception):
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code or self.status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class IllegalMoveException(ChessException):
    status_code = 400

    def __init__(self, message='Illegal Move', status_code=None, payload=None):
        ChessException.__init__(self, message, status_code, payload)


class NoSuchPieceException(ChessException):
    status_code = 400

    def __init__(self, message='No Such Piece', status_code=None, payload=None):
        ChessException.__init__(self, message, status_code, payload)


class IllegalStateException(ChessException):
    status_code = 400

    def __init__(self, message='Illegal State', status_code=None, payload=None):
        ChessException.__init__(self, message, status_code, payload)


class AutoName(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class GameResult(AutoName):
    P1_WINS = enum.auto()
    P2_WINS = enum.auto()
    DRAW = enum.auto()
    NONTERMINAL = enum.auto()

    def __bool__(self):
        return self != GameResult.NONTERMINAL


def print_board(board: int) -> str:
    m = 1 << 63
    out = []
    for _ in range(8):
        o = []
        for _ in range(8):
            o.append('1' if m & board else '.')
            m >>= 1
        out.append(''.join(o))
    out = '\n'.join(out)
    print(out)
    return out


class State:
    """
    Class to represent the state of a board
    """

    def __init__(self, white: Tuple[int, int, int, int, int, int] = None,
                 black: Tuple[int, int, int, int, int, int] = None,
                 turn: str = 'w',
                 prev_move: Tuple[int, int] = None,
                 in_check: bool = False,
                 can_castle: Tuple[bool, bool] = (True, True),
                 **kwargs: int) -> None:
        if (white is None) != (black is None):
            raise IllegalStateException('Please specify both black and white')
        if turn not in ('w', 'b'):
            raise IllegalStateException(
                'Please input one of ("w", "b") as the turn')

        self.prev_move = prev_move
        self.white = white
        self.black = black

        self.true_moves = None
        self.fake_moves = None
        self.in_check = in_check

        if self.white is None:
            self.white = (kwargs.get('wp', 0x000000000000ff00),  # pawns
                          kwargs.get('wn', 0x0000000000000042),  # knights
                          kwargs.get('wb', 0x0000000000000024),  # bishops
                          kwargs.get('wr', 0x0000000000000081),  # rooks
                          kwargs.get('wq', 0x0000000000000010),  # queen
                          kwargs.get('wk', 0x0000000000000008))  # king
        if self.black is None:
            self.black = (kwargs.get('bp', 0x00ff000000000000),  # pawns
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

        self.castles = (can_castle[0] and (self.white[-1] == 0x8),
                        can_castle[1] and (self.black[-1] == (0x8 << 56)))
        if self.white_turn:
            self.can_castle = self.castles[0]
        else:
            self.can_castle = self.castles[1]
        self.can_castle = self.can_castle and not self.in_check
        self.castle_moves = []
        self.rook_castle_moves = []
        self.children = None
        self.moves_complete = False
        self.en_passant_moves = set()

    def list_moves(self) -> List[Tuple[int, int]]:
        """
        Lists all moves, including some illegal ones that will leave the king
        in check
        :return:
        """
        if self.fake_moves is not None:
            return self.fake_moves
        current_player, other_player = (
            self.white, self.black) if self.white_turn else (
            self.black, self.white)
        out = []
        for ix, pieces in enumerate(current_player):
            m = 1 << 63
            while m > 0:
                tmp = pieces & m
                if tmp:
                    move = (m, self.get_moves(m))
                    out.append(move)
                m >>= 1
        self.fake_moves = out
        return out

    def list_legal_moves(self) -> List[Tuple[int, int]]:
        if not self.moves_complete:
            list(self.get_children())
        return self.true_moves

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
        # out = []
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
                f'No {"white" if self.white_turn else "black"} piece '
                f'at {piece}')
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
        if self.white_turn:
            tmp = KNIGHT_MOVES[piece] & ~white_pos
            return tmp
        else:
            tmp = KNIGHT_MOVES[piece] & ~black_pos
            return tmp

    def pawn_moves(self, piece: int) -> int:
        white_pos, black_pos = self.white_pos, self.black_pos
        out = 0
        if self.white_turn:
            if (piece << 8) & ~(white_pos | black_pos):
                out |= (piece << 8)
                if (1 << 8) <= piece <= (1 << 15) and (piece << 2 * 8) & ~(
                            white_pos | black_pos):
                    out |= (piece << 2 * 8)
            if ((piece & ~MASK_LEFT) << 9) & black_pos:
                out |= (piece << 9)
            if ((piece & ~MASK_RIGHT) << 7) & black_pos:
                out |= (piece << 7)
            # En Passant
            if self.prev_move is not None:
                left_prev_pawn = ((self.black[0] & self.prev_move[1]
                                   & 0xFF00000000)
                                  & ((piece & ~MASK_LEFT) << 1)) != 0
                right_prev_pawn = ((self.black[0] & self.prev_move[1] &
                                    0xFF00000000)
                                   & ((piece & ~MASK_RIGHT) >> 1)) != 0
                if left_prev_pawn:
                    tmp = piece << 9
                    self.en_passant_moves.add((piece, tmp))
                    out |= tmp
                elif right_prev_pawn:  # prev pawn can't be on left and right
                    tmp = piece << 7
                    self.en_passant_moves.add((piece, tmp))
                    out |= tmp
        else:
            if (piece >> 8) & ~(white_pos | black_pos):
                tmp = piece >> 8
                out |= tmp
            if (1 << 48) <= piece <= (1 << 56) and (piece >> 2 * 8) & ~(
                        white_pos | black_pos) and (piece >> 8) & ~(
                        white_pos | black_pos):
                tmp = piece >> 2 * 8
                out |= tmp
            if ((piece & ~MASK_RIGHT) >> 9) & white_pos:
                tmp = piece >> 9
                out |= tmp
            if ((piece & ~MASK_LEFT) >> 7) & white_pos:
                tmp = piece >> 7
                out |= tmp

            # En Passant
            if self.prev_move is not None:
                left_prev_pawn = ((self.white[0] & self.prev_move[
                    1] & 0xFF000000)
                                  & ((piece & ~MASK_LEFT) << 1)) != 0
                right_prev_pawn = ((self.white[0] & self.prev_move[1] &
                                    0xFF000000)
                                   & ((piece & ~MASK_RIGHT) >> 1)) != 0
                if left_prev_pawn:
                    tmp = piece >> 7
                    self.en_passant_moves.add((piece, tmp))
                    out |= tmp
                elif right_prev_pawn:  # prev pawn can't be on left and right
                    tmp = piece >> 9
                    self.en_passant_moves.add((piece, tmp))
                    out |= tmp
        return out

    def king_moves(self, piece: int) -> int:
        white_pos, black_pos = self.white_pos, self.black_pos
        if self.white_turn:
            tmp = KING_MOVES[piece] & ~white_pos
            if self.can_castle and (piece == 0x8):
                castle_king = piece >> 2
                castle_queen = piece << 2
                pseudo_can_castle_king = ((self.white_pos | self.black_pos)
                                          & (0x2 | 0x4)) == 0 and \
                                         (self.white[3] & 0x1) != 0
                pseudo_can_castle_queen = ((self.white_pos | self.black_pos)
                                           & (0x10 | 0x20 | 0x40)) == 0 and \
                                          (self.white[3] & 0x80) != 0
                if pseudo_can_castle_king:
                    tmp |= castle_king
                    self.castle_moves.append((piece, castle_king))
                    self.rook_castle_moves.append((0x1, 0x4))
                if pseudo_can_castle_queen:
                    tmp |= castle_queen
                    self.castle_moves.append((piece, castle_queen))
                    self.rook_castle_moves.append((0x80, 0x10))
        else:
            tmp = KING_MOVES[piece] & ~black_pos
            if self.can_castle and (piece == (0x8 << 56)):
                castle_king = piece >> 2
                castle_queen = piece << 2
                pseudo_can_castle_king = (((self.white_pos | self.black_pos) &
                                           ((0x2 | 0x4) << 56)) == 0) and \
                                         (self.black[3] & (0x1 << 56)) != 0
                pseudo_can_castle_queen = ((self.white_pos | self.black_pos)
                                           & (((0x10 << 56) | (0x20 << 56) |
                                               (0x40 << 56)))) == 0 and \
                                          (self.black[3] & (0x80 << 56)) != 0

                if pseudo_can_castle_king:
                    tmp |= castle_king
                    if (piece, castle_king) not in self.castle_moves:
                        self.castle_moves.append((piece, castle_king))
                        self.rook_castle_moves.append((0x1 << 56, 0x1 << 58))
                if pseudo_can_castle_queen:
                    tmp |= castle_queen
                    if (piece, castle_queen) not in self.castle_moves:
                        self.castle_moves.append((piece, castle_queen))
                        self.rook_castle_moves.append((0x80 << 56, 0x80 << 53))
        return tmp

    def rook_moves(self, piece: int) -> int:
        white_pos, black_pos = self.white_pos & ~piece, self.black_pos & ~piece

        moves = 0
        if self.white_turn:
            opponent = black_pos
        else:
            opponent = white_pos

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
        white_pos, black_pos = self.white_pos & ~piece, self.black_pos & ~piece
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

    def to_algebraic_notation(self, piece: int, target: int,
                              promotion_piece: int = 4):
        QUEEN_CASTLE = 'O-O-O'
        KING_CASTLE = 'O-O'

        piece_type = self.find_ix(piece)
        if piece_type == 5 and self.white_turn:
            if piece == 0x8 and target == 0x2:
                return KING_CASTLE
            elif piece == 0x8 and target == 0x20:
                return QUEEN_CASTLE
        elif piece_type == 5 and not self.white_turn:
            if piece == (0x8 << 56) and target == (0x2 << 56):
                return KING_CASTLE
            elif piece == (0x8 << 56) and target == (0x20 << 56):
                return QUEEN_CASTLE

        piece_names = [
            '',
            'N',
            'B',
            'R',
            'Q',
            'K'
        ]

        if self.white_turn:
            me = self.white
            them = self.black
        else:
            me = self.black
            them = self.white

        if self.white_turn:
            other_pos = self.black_pos
        else:
            other_pos = self.white_pos

        row_ambiguity = False
        col_ambiguity = False
        any_ambiguity = False

        this_piece_an = bitboard_to_AN(piece)

        for other_piece in self.iter_pieces(me[piece_type] & ~piece):
            other_moves = self.get_moves(other_piece)
            same_attack = (other_moves & target) != 0
            other_piece_an = bitboard_to_AN(other_piece)

            if same_attack:
                any_ambiguity = True
                if other_piece_an[0] == this_piece_an[0]:
                    col_ambiguity = True
                if other_piece_an[1] == this_piece_an[1]:
                    row_ambiguity = True

        from_identifier = piece_names[piece_type]
        if any_ambiguity:
            if col_ambiguity and row_ambiguity:
                from_identifier += this_piece_an
            elif col_ambiguity:
                from_identifier += this_piece_an[1]
            else:
                from_identifier += this_piece_an[0]

        components = [from_identifier]
        is_capture = (other_pos & target) != 0
        resulting_state = self.get_child(piece, target, promotion_piece)
        becomes_check = resulting_state.in_check

        en_passant = False
        if piece_type == 0 and (target & other_pos) == 0 and (
                        (them[0] & target << 8) != 0 or
                        (them[0] & target >> 8) != 0):
            en_passant = True
            is_capture = True

        if is_capture:
            if piece_type == 0 and not any_ambiguity:
                components.append(this_piece_an[0])
            components.append('x')

        is_promotion = piece_type == 0 and (((target & 0xff) != 0) or
                                            ((target & (0xff << 56)) != 0))

        components.append(bitboard_to_AN(target))
        if en_passant:
            components.append('e.p.')
        elif is_promotion:
            components.append('=')
            components.append(piece_names[promotion_piece])
        if becomes_check:
            components.append('+')
        tmp = resulting_state.is_terminal()
        if tmp:
            if tmp == GameResult.DRAW:
                components.append(" 1/2 - 1/2")
            elif tmp == GameResult.P1_WINS:
                components.append(" # 1-0")
            elif tmp == GameResult.P2_WINS:
                components.append(" # 0-1")
        return ''.join(components)

    def from_algebraic_notation(self, an_move: str) -> Tuple[int, int]:
        pass

    def iter_pieces(self, piece: int):
        """
        Generator to split piece into multiple pieces
        :param piece:
        :return:
        """
        m = 1 << 63
        while m > 0:
            if m & piece:
                yield m
            m >>= 1

    def is_pseudolegal(self, piece: int, target: int) -> bool:
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
        return (self.get_moves(piece) & target) != 0 \
               or (piece, target) in self.castle_moves

    def find_ix(self, piece: int):
        for i in range(6):
            if self.white[i] & piece != 0:
                return i
            if self.black[i] & piece != 0:
                return i

    def get_child(self, piece: int, target: int,
                  promotion_ix: int = 4) -> 'State':
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
        if not self.is_pseudolegal(piece, target):
            raise IllegalMoveException('Completely and utterly illegal move')
        if not 0 < promotion_ix < 5:
            raise IllegalMoveException('Cannot promote to such a piece')
        castling = (piece, target) in self.castle_moves
        en_passant = (piece, target) in self.en_passant_moves

        if castling:
            rook, rook_target = self.rook_castle_moves[
                self.castle_moves.index((piece, target))]

        ix = self.find_ix(piece)
        promoting = (ix == 0) and (target & ((0xFF << 56) | 0xff)) != 0

        if self.white_turn:
            me = self.white
            them = self.black
        else:
            me = self.black
            them = self.white

        if castling:
            if target > me[-1]:  # queen side castle
                self.get_child(me[-1], me[-1] << 1)
            else:  # king side castle
                self.get_child(me[-1], me[-1] >> 1)

        tmp_white = self.white
        tmp_black = self.black
        tmp_white_pos = self.white_pos
        tmp_black_pos = self.black_pos

        assert target == (1 << (target.bit_length() - 1))

        new_me = list(me)
        new_me[ix] = (new_me[ix] & ~piece) | target
        new_them = [i & ~target for i in them]

        if castling:
            new_me[3] = (new_me[3] & ~rook) | rook_target
        if en_passant:
            if self.white_turn:
                new_them[0] &= ~(target >> 8)
            else:
                new_them[0] &= ~(target << 8)
        if promoting:
            new_me[promotion_ix] |= target
            new_me[ix] = new_me[ix] & (~target)

        new_me = tuple(new_me)
        new_them = tuple(new_them)
        me_king = new_me[-1]

        if self.white_turn:
            new_white = new_me
        else:
            new_white = new_them

        if not self.white_turn:
            new_black = new_me
        else:
            new_black = new_them

        if self.white_turn:
            new_can_castle = ((ix != 5) and self.castles[0], self.castles[1])
            new_state = State(new_white, new_black, 'b',
                              prev_move=(piece, target),
                              can_castle=new_can_castle)
        else:
            new_can_castle = (self.castles[0], (ix != 5) and self.castles[1])
            new_state = State(new_white, new_black, 'w',
                              prev_move=(piece, target),
                              can_castle=new_can_castle)

        self.white = new_white
        self.black = new_black
        self.black_pos = new_state.black_pos
        self.white_pos = new_state.white_pos

        them_king = new_them[-1]

        move_fns = [
            self.pawn_moves,
            self.knight_moves,
            self.bishop_moves,
            self.rook_moves,
            self.queen_moves,
            self.king_moves
        ]

        new_state.in_check = (move_fns[ix](target) & them_king) != 0
        self.white = tmp_white
        self.black = tmp_black
        self.black_pos = tmp_black_pos
        self.white_pos = tmp_white_pos

        for _, attacked in new_state.list_moves():
            if attacked & me_king:
                raise IllegalMoveException(
                    'You would be in check after this move')
        return new_state

    def get_children(self) -> Iterable['State']:
        """
        Get a list of all possible child states
        """
        if self.moves_complete:
            return self.children
        else:
            self.true_moves = []
            self.children = []
            move_list = self.list_moves()
            for from_move, to_move in move_list:
                for target in self.iter_pieces(to_move):
                    try:
                        state = self.get_child(from_move, target)
                        self.true_moves.append((from_move, target))
                        self.children.append(state)
                        yield state
                    except IllegalMoveException:
                        pass
            self.moves_complete = True

    def get_random_child(self) -> 'State':
        move_list = self.list_moves()
        random.shuffle(move_list)
        for from_move, to_move in move_list:
            ipm = list(self.iter_pieces(to_move))
            random.shuffle(ipm)
            for target in ipm:
                try:
                    return self.get_child(from_move, target)
                except IllegalMoveException:
                    pass

    def is_terminal(self) -> GameResult:
        if (self.black[5] == self.black_pos) and (
                    self.white[5] == self.white_pos):
            return GameResult.DRAW
        for _ in self.get_children():
            break

        if len(self.children) > 0:
            return GameResult.NONTERMINAL
        elif self.in_check:
            return GameResult.P1_WINS if not self.white_turn else \
                GameResult.P2_WINS
        else:
            return GameResult.DRAW

    def to_dict(self):
        white = [None] * 64
        black = [None] * 64
        ix_to_letter = ['p', 'n', 'b', 'r', 'q', 'k']

        for ix, pieces in enumerate(self.white):
            for piece in self.iter_pieces(pieces):
                white[64 - piece.bit_length()] = ix_to_letter[ix]

        for ix, pieces in enumerate(self.black):
            for piece in self.iter_pieces(pieces):
                black[64 - piece.bit_length()] = ix_to_letter[ix]

        winner = str(self.is_terminal()).split('.')[-1]
        in_check = self.in_check
        turn = 'w' if self.white_turn else 'b'
        pieces = []
        for w, b in zip(white, black):
            if w is not None:
                pieces.append(w.upper())
            else:
                pieces.append(b)
        return {
            'pieces': pieces,
            'winner': winner,
            'in_check': in_check,
            'turn': turn,
            'prev_move': self.prev_move,
            'can_castle': self.castles
        }

    @staticmethod
    def from_dict(pieces: List[str], turn: str, in_check: bool,
                  can_castle: Iterable[bool],
                  prev_move: Tuple[int, int] = None) -> 'State':
        if len(pieces) != 64:
            raise IllegalStateException()

        ix_lookup = {'p': 0, 'n': 1, 'b': 2, 'r': 3, 'q': 4, 'k': 5}
        ix_lookup.update({k.upper(): v for k, v in ix_lookup.items()})
        white = [0] * 6
        black = [0] * 6
        m = 1 << 63
        for ix in range(64):
            piece_ix = ix_lookup.get(pieces[ix], None)
            if piece_ix is not None and isinstance(pieces[ix], str):
                if pieces[ix].upper() == pieces[ix]:
                    white[piece_ix] |= m
                else:
                    black[piece_ix] |= m
            m >>= 1
        return State(white=tuple(white),
                     black=tuple(black),
                     turn=turn,
                     in_check=in_check,
                     prev_move=prev_move,
                     can_castle=tuple(can_castle))

    def to_ndarray(self):
        out = np.zeros(64)
        for i in range(6):
            for pt in self.iter_pieces(self.white[i]):
                out[64 - pt.bit_length()] = i
            for pt in self.iter_pieces(self.black[i]):
                out[64 - pt.bit_length()] = -i
        return out.reshape(8, 8)

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
                    if locs & mask != 0:  # there's a piece at location
                        # specified by mask
                        output[i] = name.upper() if white else name.lower()
                    mask >>= 1
                    i += 1
        return '\n'.join(''.join(output[8 * i:8 * (i + 1)]) for i in range(8))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.white, self.black, self.white_turn) == (
                other.white, other.black, other.white_turn)
        else:
            return False

    def __hash__(self):
        return hash((self.white, self.black, self.white_turn))


if __name__ == '__main__':
    s = State()
    print(s.castles)
