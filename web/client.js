var size = 80;
const draw = SVG('board').size(size * 8, size * 8);

var board;
var white_turn = true;
var in_check = false;
var selected = false;
var selected_piece;

function startup() {
    $.ajax({
        type: "GET",
        url: 'http://127.0.0.1:5000/reset',
        success: function (response) {
            drawBoard(response);
        }
    });
}

function setBoard(state) {
    white_turn = state['turn'] === 'w';
    board = state['pieces'];
    in_check = state['in_check'];

}

function contains(a, obj) {
    for (var i = 0; i < a.length; i++) {
        if ((a[i].x === obj.x) && (a[i].y === obj.y)) {
            return true;
        }
    }
    return false;
}

function onTileClick(ix) {
    return function () {
        ix = 63 - ix;
        if (selected) {
            var data = {
                'piece': selected_piece,
                'target': ix,
                'pieces': board,
                'in_check': in_check,
                'turn': white_turn ? 'w' : 'b'
            };
            selected = false;
            selected_piece = null;

            var url = "http://127.0.0.1:5000/move";
            $.ajax({
                type: "POST",
                url: url,
                data: JSON.stringify(data),
                headers: {'Content-type': 'application/json'},
                success: updateEverything,
                error: function (response) {
                    alert(response);
                }
            });
        } else {
            selected_piece = ix;
            selected = true;
        }
    }
}

function updateEverything(response) {
    drawPieces(response);
    white_turn = response.turn === 'w';
    in_check = response.in_check;
}

function drawPieces(response) {
    console.log(response);
    board = response['pieces'];
    for (var i = 0; i < board.length; i++) {
        if (board[i] !== null) {
            SVG.get('t_' + i).text(board[i]);
        } else {
            SVG.get('t_' + i).text('');
        }
    }
}

function drawValid(coords) {
    SVG.select('circle.move-marker').attr({'fill': '#000', 'fill-opacity': '0.0'});
    for (var i = 0; i < coords.length; i++) {
        SVG.get('v_' + coords[i].x.toString() + coords[i].y.toString()).attr({fill: '#00f', 'fill-opacity': '1.0'});
    }
}

function drawBoard(initial) {
    for (var i = 0; i < 8; i++) {
        for (var j = 0; j < 8; j++) {
            var scale = 0.8;
            var vscale = 0.1;
            var fill_val;
            if ((i + j) % 2 === 0) fill_val = '#fff';
            else fill_val = '#666';
            draw.rect(size, size).move(i * size, j * size).attr({
                fill: fill_val,
                stroke: 'black'
            }).attr('class', 'back');

            draw.text('')
                .move((i + 1.0 / 2) * size, (j + 1.0 / 2) * size)
                .id('t_' + (j * 8 + i).toString()).attr({
                'fill': '#000'
            }).attr('class', 'piece');

            // draw.circle(vscale * size).move((i + ((1 - vscale) / 2)) * size, (j + ((1 - vscale) / 2)) * size).id('v_' + i.toString() + j.toString()).attr({
            //     'fill': '#000',
            //     'fill-opacity': '0.0'
            // }).attr('class', 'move-marker');
            draw.rect(size, size).move(i * size, j * size).id('sq_' + (j * 8 + i)).attr({
                'fill': '#000',
                'fill-opacity': '0.0'
            }).on('click', onTileClick(j * 8 + i)).attr('class', 'button');

        }
    }
    drawPieces(initial);
}

startup();
