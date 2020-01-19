// -1->tied, 1->player 1, 2->player2
type Player = -1 | 1 | 2;
type Players = [Player, Player];
type MaybePlayer = Player | void;
type PlayerIdx = 0 | 1; // 0->player 1, 1->player 2

// coordinates of the board
type Idx = 0 | 1 | 2;
export interface Move {
    i: Idx;
    j: Idx;
}

// token, 0->empty, 1->token of player 1, 2->token of player 2
type Token = ' ' | 'x' | 'o';
type Row = [Token, Token, Token];
export type Board = [Row, Row, Row];
const tokenMap = {
    ' ': 0,
    x: 1,
    o: 2,
};

interface Game {
    players: Players;
    playerIdx: PlayerIdx;
    board: Board;
}

const sum = (arr: number[]): number => {
    return arr.reduce((x, y) => x + y, 0);
};

/* const transpose2 = <T extends unknown>(board: Array<Array<T>>): Array<Array<T>> => {
    // generic form doesn't work, have to investigate later
    return board[0].map((_, i) => board.map(row => row[i]));
};
 */

const transpose = (board: Board): Board => {
    return [
        [board[0][0], board[1][0], board[2][0]],
        [board[0][1], board[1][1], board[2][1]],
        [board[0][2], board[1][2], board[2][2]],
    ];
};

const _checkRow = (row: Row, player: Player): number => {
    return sum(row.map(token => (tokenMap[token] === player ? 1 : 0)));
};

const _getDiag = (board: Board): number[] => {
    return [board[0][0], board[1][1], board[2][2]].map(token => tokenMap[token]);
};

const _getContraDiag = (board: Board): number[] => {
    return [board[0][2], board[1][1], board[2][0]].map(token => tokenMap[token]);
};

const _checkDiag = (board: Board, player: Player) => {
    return Math.max(
        sum(_getDiag(board).map(token => (token === player ? 1 : 0))),
        sum(_getContraDiag(board).map(token => (token === player ? 1 : 0))),
    );
};

const sumBoardRow = (board: Board): [number, number] => {
    const sum1: number = Math.max(...board.map(row => _checkRow(row, 1)));
    const sum2: number = Math.max(...board.map(row => _checkRow(row, 2)));
    return [sum1, sum2];
};

const sumBoardCol = (board: Board): [number, number] => {
    const boardt: Board = transpose(board);
    const sum1: number = Math.max(...boardt.map(row => _checkRow(row, 1)));
    const sum2: number = Math.max(...boardt.map(row => _checkRow(row, 2)));
    return [sum1, sum2];
};

const sumBoardDiag = (board: Board): [number, number] => {
    const sum1 = _checkDiag(board, 1);
    const sum2 = _checkDiag(board, 2);
    return [sum1, sum2];
};

function* _movesPossible(board: Board): Generator<Move> {
    const indices: Idx[] = [0, 1, 2];
    for (const i of indices) {
        for (const j of indices) {
            if (tokenMap[board[i][j]] === 0) {
                //yield new Move(i, j)
                yield { i, j };
            }
        }
    }
}

const _NoPossibleMove = (board: Board): boolean => {
    const indices: Idx[] = [0, 1, 2];
    return sum(indices.map(i => sum(indices.map(j => (tokenMap[board[i][j]] === 0 ? 1 : 0))))) <= 0;
};

const determineWinner = (game: Game): MaybePlayer => {
    const board = game.board;
    const [player1, player2]: [Player, Player] = game.players;

    const [sumRow1, sumRow2]: [number, number] = sumBoardRow(board);
    if (sumRow1 === 3) {
        return player1;
    }
    if (sumRow2 === 3) {
        return player2;
    }

    const [sumCol1, sumCol2]: [number, number] = sumBoardCol(board);
    if (sumCol1 === 3) {
        return player1;
    }
    if (sumCol2 === 3) {
        return player2;
    }

    const [sumDiag1, sumDiag2]: [number, number] = sumBoardDiag(board);
    if (sumDiag1 === 3) {
        return player1;
    }
    if (sumDiag2 === 3) {
        return player2;
    }

    if (_NoPossibleMove(game.board)) {
        return -1;
    }

    
};

const getNextPlayerIdx = (game: Game): PlayerIdx => {
    return game.playerIdx === 0 ? 1 : 0;
};

const getLegalMoves = (game: Game): Move[] => {
    if (determineWinner(game)) {
        return [];
    }
    return Array.from(_movesPossible(game.board));
};

const _makeRow = (row: Row, player: Player, j: Idx): Row => {
    const token = player === 1 ? 'x' : 'o';
    return [j === 0 ? token : row[0], j === 1 ? token : row[1], j === 2 ? token : row[2]];
};

const applyMove = (board: Board, move: Move, player: Player): Board => {
    const [i, j] = [move.i, move.j];
    if (board[i][j] !== ' ') {
        throw new Error('Invalid move');
    }

    const row0: Row = i === 0 ? _makeRow(board[0], player, j) : board[0];
    const row1: Row = i === 1 ? _makeRow(board[1], player, j) : board[1];
    const row2: Row = i === 2 ? _makeRow(board[2], player, j) : board[2];
    const boardNew: Board = [row0, row1, row2];
    return boardNew;
};

const makeMove = (game: Game, move: Move): Game => {
    const player: Player = game.players[game.playerIdx];
    const board: Board = applyMove(game.board, move, player);
    const playerIdxNext: PlayerIdx = getNextPlayerIdx(game);
    const gameNew: Game = {
        players: game.players,
        playerIdx: playerIdxNext,
        board,
    };
    return gameNew;
};

const initGame = (board?: Board, playerIdx?: PlayerIdx): Game => {
    const players_: Players = [1, 2];
    const playerIdx_: PlayerIdx = playerIdx === undefined ? 0 : playerIdx;
    const board_: Board =
        board !== undefined
            ? board
            : [
                [' ', ' ', ' '],
                [' ', ' ', ' '],
                [' ', ' ', ' '],
            ];
    const game: Game = {
        players: players_,
        playerIdx: playerIdx_,
        board: board_,
    };
    return game;
};

const scoreGame = (game: Game): number => {
    const winner = determineWinner(game);
    if (winner === 1) {
        return 1.0;
    }
    if (winner === 2) {
        return 0.0;
    }
    if (winner === -1) {
        return 0.5;
    }
    throw Error('Illegal player');
};

interface BaseEngine {
    determineWinner: (game: Game) => MaybePlayer;
    getLegalMoves: (game: Game) => Move[];
    initGame: (board?: Board, playerIdx?: PlayerIdx) => Game;
    makeMove: (game: Game, move: Move) => Game;
    scoreGame: (game: Game) => number;
}

const TicTacToeEngine: BaseEngine = {
    determineWinner,
    getLegalMoves,
    initGame,
    makeMove,
    scoreGame,
};

export { determineWinner, TicTacToeEngine, Game, Players };
