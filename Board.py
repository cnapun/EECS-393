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
    def list_moves(self, piece:int):
        pass
    def is_check(self):
        pass
    