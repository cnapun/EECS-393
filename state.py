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

# Bishop ray table
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


class IllegalMoveException(Exception):
    pass


class NoSuchPieceException(Exception):
    pass


class AutoName(enum.Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class GameResult(AutoName):
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
                 in_check=False,
                 **kwargs: int) -> None:
        assert (white is None) == (black is None)
        assert turn in ('w', 'b')
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

    def list_moves(self) -> List[Tuple[int, int]]:
        """
        Lists all moves, including some illegal ones that will leave the king in check
        :return:
        """
        if self.fake_moves is not None:
            return self.fake_moves
        current_player, other_player = (self.white, self.black) if self.white_turn else (self.black, self.white)
        out = []
        pinned_pieces = []
        for ix, pieces in enumerate(current_player):
            m = 1 << 63
            while m > 0:
                tmp = pieces & m
                if tmp:
                    move = (m, self.get_moves(m, True))
                    out.append(move)
                m >>= 1
        self.fake_moves = out
        return out

    def list_legal_moves(self) -> List[Tuple[int, int]]:
        if self.true_moves is None:
            self.get_children()
        return self.true_moves

    def get_moves(self, piece: int, update: bool = False) -> int:
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
                f'No {"white" if self.white_turn else "black"} piece at {piece}')
        if ioi == 0:  # pawn
            out = self.pawn_moves(piece, update)
        elif ioi == 1:  # knight
            out = self.knight_moves(piece, update)
        elif ioi == 2:
            out = self.bishop_moves(piece, update)
        elif ioi == 3:
            out = self.rook_moves(piece, update)
        elif ioi == 4:
            out = self.queen_moves(piece, update)
        elif ioi == 5:  # king
            out = self.king_moves(piece, update)
        return out

    def knight_moves(self, piece: int, update_attacks: bool = False) -> int:
        white_pos, black_pos = self.white_pos, self.black_pos
        if self.white_turn:
            tmp = KNIGHT_MOVES[piece] & ~white_pos
            if update_attacks:
                self.can_be_attacked |= tmp
            return tmp
        else:
            tmp = KNIGHT_MOVES[piece] & ~black_pos
            if update_attacks:
                self.can_be_attacked |= tmp
            return tmp

    def pawn_moves(self, piece: int, update_attacks: bool = False) -> int:
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

    def king_moves(self, piece: int, update_attacks: bool = False) -> int:
        white_pos, black_pos = self.white_pos, self.black_pos
        if self.white_turn:
            tmp = KING_MOVES[piece] & ~white_pos
            return tmp
        else:
            tmp = KING_MOVES[piece] & ~black_pos
            return tmp

    def rook_moves(self, piece: int, update_attacks: bool = False, include_endpoint: bool = False) -> int:
        white_pos, black_pos = self.white_pos & ~piece, self.black_pos
        moves = 0
        opponent = black_pos if self.white_turn else white_pos
        # Down
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_DOWN) >> 8
        if not include_endpoint:
            current_ray &= opponent
        moves |= current_ray

        # Up
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_UP) << 8
        if not include_endpoint:
            current_ray &= opponent
        moves |= current_ray

        # Left
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_RIGHT) >> 1
        if not include_endpoint:
            current_ray &= opponent
        moves |= current_ray

        # Right
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_LEFT) << 1
        if not include_endpoint:
            current_ray &= opponent
        moves |= current_ray

        return moves & ~piece

    def bishop_moves(self, piece: int, update_attacks: bool = False, include_endpoint: bool = False) -> int:
        white_pos, black_pos = self.white_pos & ~piece, self.black_pos
        moves = 0
        opponent = black_pos if self.white_turn else white_pos
        # Down Right
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_DR) >> 9
        if not include_endpoint:
            current_ray &= opponent
        moves |= current_ray

        # Up Left
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_UL) << 9
        if not include_endpoint:
            current_ray &= opponent
        moves |= current_ray

        # Down Left
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_DL) >> 7
        if not include_endpoint:
            current_ray &= opponent
        moves |= current_ray

        # Up Right
        current_ray = piece
        while current_ray & ~(black_pos | white_pos):
            moves |= current_ray
            current_ray = (current_ray & ~MASK_UR) << 7
        if not include_endpoint:
            current_ray &= opponent
        moves |= current_ray

        return moves & ~piece

    def queen_moves(self, piece: int, update_attacks: bool = False, include_endpoint: bool = False) -> int:
        return self.rook_moves(piece, update_attacks, include_endpoint) | self.bishop_moves(piece, update_attacks,
                                                                                            include_endpoint)

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
        return (self.get_moves(piece) | target) != 0

    def is_check(self) -> bool:
        """
        Determine whether or not the current player is in check
        """
        king = self.white_pos[-1] if self.white_turn else self.black_pos[-1]
        return False

    def find_ix(self, piece: int):
        for i in range(6):
            if self.white[i] & piece != 0:
                return i
            if self.black[i] & piece != 0:
                return i

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
        if not self.is_pseudolegal(piece, target):
            raise IllegalMoveException('Completely and utterly illegal move')
        ix = self.find_ix(piece)
        me = self.white if self.white_turn else self.black
        them = self.black if self.white_turn else self.white

        tmp_white = self.white
        tmp_black = self.black
        tmp_white_pos = self.white_pos
        tmp_black_pos = self.black_pos

        new_me = list(me)
        new_me[ix] = (new_me[ix] & ~piece) | target
        new_me = tuple(new_me)
        new_them = tuple(i & ~target for i in them)
        new_white = new_me if self.white_turn else new_them
        new_black = new_me if not self.white_turn else new_them
        new_state = State(new_white, new_black, 'b' if self.white_turn else 'w', (piece, target))

        self.white, self.black, self.black_pos, self.white_pos = new_white, new_black, new_state.black_pos, \
                                                                 new_state.white_pos
        them_king = new_them[-1]
        if ix == 0:
            new_state.in_check = self.pawn_moves(piece) & them_king
        elif ix == 1:
            new_state.in_check = self.knight_moves(piece) & them_king
        elif ix == 2:
            new_state.in_check = self.bishop_moves(piece) & them_king
        elif ix == 3:
            new_state.in_check = self.rook_moves(piece) & them_king
        elif ix == 4:
            new_state.in_check = self.queen_moves(piece) & them_king
        elif ix == 5:
            new_state.in_check = self.king_moves(piece) & them_king

        self.white, self.black, self.black_pos, self.white_pos = tmp_white, tmp_black, tmp_black_pos, tmp_white_pos

        opp_king = new_white[-1] if not state.white_turn else new_black[-1]

        for _, attacked in new_state.list_moves():
            if attacked & opp_king:
                raise IllegalMoveException('You would be in check after this move')
        return new_state

    def get_children(self) -> Iterable['State']:
        """
        Get a list of all possible child states
        """
        self.true_moves = []
        for from_move, to_move in self.list_moves():
            try:
                state = self.get_child(from_move, to_move)
                self.true_moves.append((from_move, to_move))
                yield state
            except IllegalMoveException:
                pass

    def is_terminal(self) -> GameResult:
        has_move = False
        for _ in self.get_children():
            has_move = True
            break
        if has_move:
            return GameResult.NONTERMINAL
        else:
            if self.in_check:
                return GameResult.P1_WINS if not self.white_turn else GameResult.P2_WINS
            else:
                return GameResult.DRAW

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

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.white, self.black, self.white_turn) == (other.white, other.black, other.white_turn)
        else:
            return False

    def __hash__(self):
        return hash((self.white, self.black, self.white_turn))


if __name__ == '__main__':
    state = State()
    # actual = state.get_moves(0x1000)
    print(state)
    # print(b)
