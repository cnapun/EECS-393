"""
Requests should be of the form {'pieces':str[64],'piece':int,'turn':['w', 'b'], 'target':int,
'in_check':bool}
Responses will be of the form  {'pieces':str[64],'winner':[(one of) 'nonterminal', 'white', 'black',
'draw'], 'in_check':bool}
pieces will be lowercase for black, uppercase for white
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

from chess.state import State, ChessException

app = Flask(__name__)
CORS(app)


class MalformedRequestException(ChessException):
    status_code = 400

    def __init__(self, message='', status_code=None, payload=None):
        ChessException.__init__(self, message, status_code, payload)


@app.errorhandler(ChessException)
def handle_bad_move(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/move', methods=['POST'])
def get_result():
    data = request.get_json()

    state = State.from_dict(data['pieces'], data['turn'], data['in_check'])
    piece = 1 << data['piece']
    target = 1 << data['target']

    new_state = state.get_child(piece, target)

    response = jsonify(new_state.to_dict())
    response.status_code = 200
    return response


if __name__ == '__main__':
    app.run(debug=True)
