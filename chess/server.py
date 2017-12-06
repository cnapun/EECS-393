"""
Requests should be of the form {'pieces':str[64],'piece':int,'turn':['w',
'b'], 'target':int,
'in_check':bool}
Responses will be of the form  {'pieces':str[64],'winner':[(one of)
'nonterminal', 'white', 'black',
'draw'], 'in_check':bool}
pieces will be lowercase for black, uppercase for white
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

from chess.state import State, ChessException, IllegalMoveException
from chess.agents import SampleMinimaxAgent

app = Flask(__name__)
CORS(app)

piece_image_lookup = {'p': 'pieces/bp',
                      'n': 'pieces/bn',
                      'q': 'pieces/bq',
                      'r': 'pieces/br',
                      'k': 'pieces/bk',
                      'b': 'pieces/bb',
                      'P': 'pieces/wp',
                      'N': 'pieces/wn',
                      'Q': 'pieces/wq',
                      'R': 'pieces/wr',
                      'K': 'pieces/wk',
                      'B': 'pieces/wb',
                      }
piece_image_lookup = {k: ('chess/' + v + '.svg') for k, v in
                      piece_image_lookup.items()}
c2ix = {
    'n': 1,
    'b': 2,
    'r': 3,
    'q': 4
}
c2ix.update({k.upper(): v for k, v in c2ix.items()})

piece_svgs = {}
for k, v in piece_image_lookup.items():
    with open(v) as f:
        piece_svgs[k] = f.read()

agent = SampleMinimaxAgent()


class MalformedRequestException(ChessException):
    status_code = 400

    def __init__(self, message='', status_code=None, payload=None):
        ChessException.__init__(self, message, status_code, payload)


@app.errorhandler(ChessException)
def handle_bad_move(error):
    if not app.testing:
        app.logger.exception(error)
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/load_pieces', methods=['GET'])
def get_pieces():
    response = jsonify(piece_svgs)
    response.status_code = 200
    return response


@app.route('/move', methods=['POST'])
def make_move():
    data = request.get_json()
    app.logger.debug(data)
    try:
        state = State.from_dict(data['pieces'], data['turn'], data['in_check'],
                                data['can_castle'], data['prev_move'])
    except Exception as e:
        if not app.testing:
            app.logger.exception(e)
        raise MalformedRequestException(str(e))

    piece = 1 << data['piece']
    target = 1 << data['target']

    an = state.to_algebraic_notation(piece, target)

    app.logger.debug(f'Piece: {data["piece"]}, Target: {data["target"]}, '
                     f'Turn: {data["turn"]}')
    app.logger.debug(state)
    app.logger.debug((state.white, state.black, state.castles))

    promo_type = data.get('promotion_type', 'q')
    if promo_type not in c2ix:
        raise IllegalMoveException()

    new_state = state.get_child(piece, target, c2ix[promo_type])

    moves = new_state.list_legal_moves()

    legal_move_dict = {}
    for piece, target in moves:
        legal_move_dict[piece.bit_length() - 1] = legal_move_dict.get(
            piece.bit_length() - 1, []) + [target.bit_length() - 1]

    d = new_state.to_dict()
    d['legal_moves'] = legal_move_dict
    d['AN'] = [an]
    response = jsonify(d)
    response.status_code = 200
    return response


@app.route('/moveai', methods=['POST'])
def make_move_ai():
    data = request.get_json()
    try:
        state = State.from_dict(data['pieces'], data['turn'], data['in_check'],
                                data['can_castle'], data['prev_move'])
    except Exception as e:
        if not app.testing:
            app.logger.exception(e)
        raise MalformedRequestException(str(e))

    piece = 1 << data['piece']
    target = 1 << data['target']

    an = state.to_algebraic_notation(piece, target)

    promo_type = data.get('promotion_type', 'q')
    if promo_type not in c2ix:
        raise IllegalMoveException()

    new_state = state.get_child(piece, target, c2ix[promo_type])
    ai_an = None
    if not new_state.is_terminal():
        ai_piece, ai_target = agent.select_move(new_state)
        ai_an = new_state.to_algebraic_notation(ai_piece, ai_target)
        new_state = new_state.get_child(ai_piece, ai_target)

    moves = new_state.list_legal_moves()
    legal_move_dict = {}
    for piece, target in moves:
        legal_move_dict[piece.bit_length() - 1] = legal_move_dict.get(
            piece.bit_length() - 1, []) + [target.bit_length() - 1]

    d = new_state.to_dict()
    d['legal_moves'] = legal_move_dict
    if ai_an is not None:
        d['AN'] = [an, ai_an]
    else:
        d['AN'] = [an]

    response = jsonify(d)
    response.status_code = 200
    return response


@app.route('/reset', methods=['GET'])
def reset():
    # s = State(wp=0x0800F000, bp=0x1000000000)
    s = State()
    moves = [i.prev_move for i in s.get_children()]

    legal_move_dict = {}
    for piece, target in moves:
        legal_move_dict[piece.bit_length() - 1] = legal_move_dict.get(
            piece.bit_length() - 1, []) + [target.bit_length() - 1]

    d = s.to_dict()
    d['legal_moves'] = legal_move_dict
    response = jsonify(d)
    response.status_code = 200
    return response
    return response


if __name__ == '__main__':
    app.run(debug=True)
