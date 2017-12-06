"""
Requests should be of the form {'pieces':str[64],'piece':int,'turn':['w',
'b'], 'target':int,
'in_check':bool}
Responses will be of the form  {'pieces':str[64],'winner':[(one of)
'nonterminal', 'white', 'black',
'draw'], 'in_check':bool}
pieces will be lowercase for black, uppercase for white
"""
import argparse

from flask import Flask, jsonify, request
from flask_cors import CORS

from chess.state import State, ChessException, IllegalMoveException
from chess.agents import SavingAgent, SampleMinimaxAgent
from chess.all_agents import agent_list

app = Flask(__name__)
CORS(app)

c2ix = {
    'n': 1,
    'b': 2,
    'r': 3,
    'q': 4
}
c2ix.update({k.upper(): v for k, v in c2ix.items()})

agent = None


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
    parser = argparse.ArgumentParser(
        description='Input agent to use. Enter optional arguments to the '
                    'constructor of the agent using --kwarg VAR_NAME=VALUE '
                    'for each necessary VAR_NAME')
    parser.add_argument('agent', metavar='agent', type=str,
                        help='Specify the agent from the dictionary in '
                             'all_agents.py to use',
                        default='SampleMinimaxAgent')
    parser.add_argument('--savefile', '-f', required=False,
                        help='File to load state from (only needed if agent '
                             'uses a from_file method')
    parser.add_argument("--kwarg", action='append',
                        type=lambda kv: kv.split("="), dest='kwargs',
                        default=[])
    args = parser.parse_args()

    agent_str = args.agent

    if agent_str not in agent_list:
        print('Please enter a valid agent')
    else:
        kwargs = dict(args.kwargs)
        agent_class = agent_list.get(agent_str)

        if issubclass(agent_class, SavingAgent):
            agent = agent_class.from_file(args.savefile)
        else:
            agent = agent_class(**kwargs)

        app.run(debug=True)
