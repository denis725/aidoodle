import { TicTacToeEngine, Board } from './games/tictactoe.js';
import { Agent, nextMove } from './agents.js';

const ttt = TicTacToeEngine;

const agent1: Agent = {
    kind: "random",
};

const agent2: Agent = {
    kind: "foo",
};


function sleep(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const boardToString = (board: Board) => {
    let boardString = board.map(row => row.join("|"));
    let boardStringString = boardString.join("\n");
    return boardStringString;
};

const mapBoardToTable = (board: Board) => {
    let f01: HTMLElement | null = document.getElementById("f01");
    const indices = [
        [0, 0], [0, 1], [0, 2],
        [1, 0], [1, 1], [1, 2],
        [2, 0], [2, 1], [2, 2]];
    indices.forEach(indices => {
        var elemName = "f" + indices.join("");
        var elem = document.getElementById(elemName);
        if (elem) {
            elem.innerText = board[indices[0]][indices[1]];
        };
    });
};

const playGame = async () => {
    let table = document.getElementById("tttTable");
    var game = ttt.initGame();
    var idx: number = 0;
    let players = [1, 2];
    let agents = [agent1, agent2];
    let phead = document.getElementById("phead");
    if (phead) { phead.innerText = agents[0].kind + " vs. " + agents[1].kind };

    while (!ttt.determineWinner(game)) {
        //var player = players[idx];
        var agent = agents[idx];
        var move = nextMove(agent, game, TicTacToeEngine);
        var game = ttt.makeMove(game, move);
        var idx: number = 1 - idx;
        mapBoardToTable(game.board);
        await sleep(500);
    };

    let ptail = document.getElementById("ptail");
    const winner = ttt.determineWinner(game);
    if (winner === 1) {
        const winnerAgent = agents[0].kind;
        if (ptail) { ptail.innerText = "The winner is agent " + winnerAgent };
    } else if (winner === 2) {
        const winnerAgent = agents[1].kind;
        if (ptail) { ptail.innerText = "The winner is agent " + winnerAgent };
    } else {
        const winnerAgent = "tied";
        if (ptail) { ptail.innerText = "The winner is agent " + winnerAgent };
    };
};

playGame();
