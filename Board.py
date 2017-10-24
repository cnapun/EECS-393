class Board:
    def __init__(self):
        self.white = (0x000000000000ff00,  # pawns
                      0x0000000000000042,  # knights
                      0x0000000000000024,  # bishops
                      0x0000000000000081,  # rooks
                      0x0000000000000010,  # queen
                      0x0000000000000008)  # king
        self.black = (0x00ff000000000000,  # pawns
                      0x4200000000000000,  # knights
                      0x2400000000000000,  # bishops
                      0x8100000000000000,  # rooks
                      0x1000000000000000,  # queen
                      0x0800000000000000)  # king}
        self.white_turn = True

    def list_moves(self):
        pass

    def list_moves(self, piece: int):
        pass

    def is_check(self):
        pass

    def __str__(self):
        names = 'p,n,b,r,q,k'.split(',')
        output = ['*'] * 64
        for white, player in zip([True, False], (self.white, self.black)):
            for name, locs in zip(names, player):
                mask = 1 << 63
                i = 0
                while mask > 0:
                    if locs & mask != 0:
                        output[i] = name.upper() if white else name.lower()
                    mask >>= 1
                    i += 1
        return '\n'.join(''.join(output[8 * i:8 * (i + 1)]) for i in range(8))


if __name__ == '__main__':
    b = Board()
    print(b)
