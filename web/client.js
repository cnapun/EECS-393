// var size = 80;
// const draw = SVG('board').size(size * 8, size * 8);

var board;
var white_turn = true;
var in_check = false;
var selected = false;
var selected_piece;
var piece_svgs = null;
var prev_payload = null;

const pawn = "<path d=\"M 22,9 C 19.79,9 18,10.79 18,13 C 18,13.89 18.29,14.71 18.78,15.38 C 16.83,16.5 15.5,18.59 15.5,21 C 15.5,23.03 16.44,24.84 17.91,26.03 C 14.91,27.09 10.5,31.58 10.5,39.5 L 33.5,39.5 C 33.5,31.58 29.09,27.09 26.09,26.03 C 27.56,24.84 28.5,23.03 28.5,21 C 28.5,18.59 27.17,16.5 25.22,15.38 C 25.71,14.71 26,13.89 26,13 C 26,10.79 24.21,9 22,9 z \"\n" +
    "      style=\"opacity:1; fill:#000000; fill-opacity:1; fill-rule:nonzero; stroke:#000000; stroke-width:1.5; stroke-linecap:round; stroke-linejoin:miter; stroke-miterlimit:4; stroke-dasharray:none; stroke-opacity:1;\"/>\n";

function clearAndReset() {
    Cookies.remove('board-state');
    $.ajax({
        type: "GET",
        url: 'http://127.0.0.1:5000/reset',
        success: function (response) {
            prev_payload = response;
            setBoard(response);
            drawBoard(response);
            updateEverything(response);
        }
    });
}

function startup() {
    $.ajax({
        type: "GET",
        url: 'http://127.0.0.1:5000/load_pieces',
        success: function (response) {
            piece_svgs = response;
        }
    });

    if (Cookies.get('board-state') === undefined) {
        $.ajax({
            type: "GET",
            url: 'http://127.0.0.1:5000/reset',
            success: function (response) {
                prev_payload = response;
                setBoard(response);
                drawBoard(response);
                updateEverything(response);
            }
        });
    } else {
        var state = Cookies.getJSON('board-state');
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

function onTileClick(ix) {
    return function () {
        if (selected) {
            var data = {
                'piece': selected_piece,
                'target': 63 - ix
            };
            $.extend(data, prev_payload);
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
                    console.log(response);
                }
            });
        } else {
            selected_piece = 63 - ix;
            selected = true;
            drawValid(prev_payload['legal_moves'][selected_piece]);
        }
    }
}

function updateEverything(response) {
    Cookies.set('board-state', response);
    if (response['turn'] === 'w') {
        $('#whose_move').text("White to move");
    } else {
        $('#whose_move').text("Black to move");
    }
    drawValid([]);

    prev_payload = response;
    drawPieces(response);
    setBoard(response)
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

function createDivs() {
    for (var i = 0; i < 8; i++) {
        var $row = $("<div />", {
            class: 'row',
            id: 'row' + (8 - i)
        });
        for (var j = 0; j < 8; j++) {
            var index = 63 - (i * 8 + j);
            if (((i + j) % 2) === 0) {
                var $wsquare = $("<div />", {
                    class: 'whiteSquare',
                    id: 'sq_' + index
                });
                $wsquare.click(
                    function () {
                        onTileClick(index);
                    }
                );

                $row.append($wsquare);
            } else {
                var $bsquare = $("<div/>", {
                    class: 'blackSquare',
                    id: 'sq_' + index,
                });
                $bsquare.click(
                    function () {
                        onTileClick(index);
                    }
                );
                $row.append($bsquare);
            }
        }

        $row.height(80);

        $('#board').append($row.clone());
    }

    for (var j = 0; j < 64; j++) {
        var validMove = $("<div/>", {
            class: 'validMove',
            id: 'v_' + j
        });
        $('#sq_' + j).append(validMove);
    }
    var $pawn = $("<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" width='70' height='70'>"
        + pawn + "</svg>");

    $('#sq_' + 36).append(
        $pawn
    );

}

function drawBoard(initial) {
    $('#board').empty();
    createDivs();
    var scale = 0.8;
    var vscale = 0.1;

    for (var i = 0; i < 64; i++) {

    }
    for (var i = 0; i < 8; i++) {
        for (var j = 0; j < 8; j++) {

            var fill_val;
            if ((i + j) % 2 === 0) fill_val = '#fff';
            else fill_val = '#666';

            draw.text('')
                .move((i + 1.0 / 2) * size, (j + 1.0 / 2) * size)
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

// startup();
createDivs();