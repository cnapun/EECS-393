var size = 80;
const draw = SVG('board').size(size * 8, size * 8);

var board;
var white_turn = true;
var in_check = false;
var selected = false;
var selected_piece;
var piece_svgs = null;
var promo_ix = null;
var prev_payload = null;
var undo_payload = null;
var moves_sofar = [];
var useAI = false;

const lookup = {
    'K': '\u2654',
    'Q': '\u2655',
    'R': '\u2656',
    'B': '\u2657',
    'N': '\u2658',
    'P': '\u2659',
    'k': '\u265a',
    'q': '\u265b',
    'r': '\u265c',
    'b': '\u265d',
    'n': '\u265e',
    'p': '\u265f'
};

function makeTextFile(text) {
    // From https://jsfiddle.net/UselessCode/qm5AG/
    var data = new Blob([text], {type: 'text/plain'});

    var textFile;
    if (textFile !== null) {
        window.URL.revokeObjectURL(textFile);
    }

    textFile = window.URL.createObjectURL(data);
    window.open(textFile);
    return textFile;
};


function downloadMoves() {
    turn_strings = [];
    if (moves_sofar.length % 2 === 0) {
        var maxn = moves_sofar.length;
    } else {
        var maxn = moves_sofar.length - 1;
    }
    for (var i = 0; i < maxn; i += 2) {
        turn_strings.push((i / 2 + 1).toString() + ' ' + moves_sofar[i] + ' ' + moves_sofar[i + 1] + '\n');
    }

    if (moves_sofar.length % 2 === 1) {
        turn_strings.push((i / 2 + 1).toString() + '. ' + moves_sofar[moves_sofar.length - 1]);
    }
    var fullString = turn_strings.join(' ');
    makeTextFile(fullString);
}

function toggleAI() {
    if (useAI) {
        Cookies.set('use-ai', false);
        $('#useAI').text('Enable AI');
        useAI = false;
    } else {
        Cookies.set('use-ai', true);
        $('#useAI').text('Disable AI');
        useAI = true;
    }
}

function clearAndReset() {
    $('#selectPiece').prop('selectedIndex', 0);
    Cookies.remove('board-state');
    Cookies.remove('moves-so-far');
    Cookies.remove('use-ai');
    moves_sofar = [];
    $.ajax({
        type: "GET",
        url: 'http://127.0.0.1:5000/reset',
        success: function (response) {
            // prev_payload = response;
            setBoard(response);
            drawBoard(response);
            updateEverything(response);
        }
    });
}

function startup() {
    $('#selectPiece').prop('selectedIndex', 0);
    if (Cookies.get('board-state') === undefined) {
        $.ajax({
            type: "GET",
            url: 'http://127.0.0.1:5000/reset',
            success: function (response) {
                // prev_payload = response;
                setBoard(response);
                drawBoard(response);
                updateEverything(response);
            }
        });
    } else {
        var state = Cookies.getJSON('board-state');
        moves_sofar = Cookies.getJSON('moves-so-far');
        var tmp = Cookies.getJSON('use-ai');
        useAI = tmp;
        if (tmp) {
            $('#useAI').text('Disable AI');
        } else {
            $('#useAI').text('Enable AI');
        }
        prev_payload = state;
        drawBoard(state);
        updateEverything(state);
    }
}

function setBoard(state) {
    white_turn = state['turn'] === 'w';
    board = state['pieces'];
    in_check = state['in_check'];
}

function contains(x, arr) {
    for (var i = 0; i < arr.length; i++) {
        if (x === arr[i]) {
            return true;
        }
    }
    return false;
}

function handlePromotion(promoType) {
    var data = {
        'piece': selected_piece,
        'target': promo_ix,
        'promotion_type': promoType
    };
    $.extend(data, prev_payload);
    selected = false;
    selected_piece = null;
    promo_ix = null;

    if (useAI) {
        var url = "http://127.0.0.1:5000/moveai";
    } else {
        var url = "http://127.0.0.1:5000/move";
    }
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(data),
        headers: {'Content-type': 'application/json'},
        success: function (response) {
            moves_sofar.push.apply(moves_sofar, response['AN']);
            updateEverything(response);
        },
        error: function () {
            alert("This move is illegal");
        }
    });
    $('#selectPiece').prop('selectedIndex', 0);
    $('#promoDialog').dialog('close');
}


function onTileClick(ix) {
    return function () {
        if (selected) {
            var tmp = prev_payload['legal_moves'][selected_piece];
            if (tmp === undefined || !contains(63 - ix, prev_payload['legal_moves'][selected_piece])) {
                selected_piece = null;
                selected = false;
                drawValid([]);
            } else {
                if (isPromotion(selected_piece, 63 - ix)) {
                    promo_ix = 63 - ix;
                    $('#promoDialog').dialog();

                } else {
                    var data = {
                        'piece': selected_piece,
                        'target': 63 - ix
                    };
                    $.extend(data, prev_payload);
                    selected = false;
                    selected_piece = null;

                    if (useAI) {
                        var url = "http://127.0.0.1:5000/moveai";
                    } else {
                        var url = "http://127.0.0.1:5000/move";
                    }
                    $.ajax({
                        type: "POST",
                        url: url,
                        data: JSON.stringify(data),
                        headers: {'Content-type': 'application/json'},
                        success: function (response) {
                            moves_sofar.push.apply(moves_sofar, response['AN']);
                            updateEverything(response);
                        },
                        error: function () {
                            alert("This move is illegal");
                        }
                    });
                }
            }
        }
        else {
            selected_piece = 63 - ix;
            selected = true;
            try {
                drawValid(prev_payload['legal_moves'][selected_piece]);
            } catch (TypeError) {
                selected = false;
                selected_piece = null;
            }
        }
    }
}


function isPromotion(piece, target) {
    return ((prev_payload['pieces'][63 - piece] === 'p') ||
        (prev_payload['pieces'][63 - piece] === 'P')) &&
        ((target < 8) || (target > 55));
}

function updateEverything(response) {
    undo_payload = prev_payload;

    Cookies.set('board-state', response);
    Cookies.set('moves-so-far', moves_sofar);

    if (response['winner'] !== 'NONTERMINAL') {
        var winner = response['winner'];
        if (winner === 'P1_WINS') {
            $('#whose_move').text("White wins");
            alert('White wins');
        } else if (winner === 'P2_WINS') {
            $('#whose_move').text("Black wins");
            alert('Black Wins');
        } else {
            $('#whose_move').text("Stalemate");
            alert('Stalemate');
        }
    } else {
        if (response['turn'] === 'w') {
            $('#whose_move').text("White to move");
        } else {
            $('#whose_move').text("Black to move");
        }
    }
    drawValid([]);

    prev_payload = response;
    drawPieces(response);
    setBoard(response)
}

function drawPieces(response) {
    board = response['pieces'];
    for (var i = 0; i < board.length; i++) {
        if (board[i] !== null) {
            SVG.get('t_' + i).text(lookup[board[i]]);
        } else {
            SVG.get('t_' + i).text('');
        }
    }
}

function drawValid(coords) {
    SVG.select('circle.move-marker').attr({
        'fill': '#000',
        'fill-opacity': '0.0'
    });
    for (var i = 0; i < coords.length; i++) {
        SVG.get('v_' + (63 - coords[i]).toString()).attr({
            fill: '#00f',
            'fill-opacity': '1.0'
        });
    }
}

function undo() {
    if (undo_payload === null) {
        alert('Cannot undo');
    } else {
        moves_sofar.pop();
        prev_payload = null;
        updateEverything(undo_payload);
    }
}

function drawBoard(initial) {
    draw.clear();
    for (var i = 0; i < 8; i++) {
        for (var j = 0; j < 8; j++) {
            var scale = 0.8;
            var vscale = 0.2;
            var fill_val;
            if ((i + j) % 2 === 0) fill_val = '#fff';
            else fill_val = '#666';
            draw.rect(size, size).move(i * size, j * size).attr({
                fill: fill_val,
                stroke: 'black'
            }).attr('class', 'back');

            draw.text('').font({
                anchor: 'middle',
                size: 72,
                family: 'Helvetica'
            }).move((i + 1.0 / 2) * size, (j + 1.0 / 2) * size - 72)
                .id('t_' + (j * 8 + i).toString()).attr({
                'fill': '#000'
            }).attr('class', 'piece');

            draw.circle(vscale * size).move((i + ((1 - vscale) / 2)) * size, (j + ((1 - vscale) / 2)) * size).id('v_' + (j * 8 + i).toString()).attr({
                'fill': '#000',
                'fill-opacity': '0.0'
            }).attr('class', 'move-marker');

            draw.rect(size, size).move(i * size, j * size).id('sq_' + (j * 8 + i)).attr({
                'fill': '#000',
                'fill-opacity': '0.0'
            }).on('click', onTileClick(j * 8 + i)).attr('class', 'button');

        }
    }
    drawPieces(initial);
}

$body = $("body");

$(document).on({
    ajaxStart: function () {
        $body.addClass("loading");
    },
    ajaxStop: function () {
        $body.removeClass("loading");
    }
});

startup();
