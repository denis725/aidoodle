import { Game, Board, Players, determineWinner } from './tictactoe.js';

const players: Players = [1, 2];

// testing determining the winner

test('no winner', () => {
    let board: Board = [
        [' ', ' ', ' '],
        [' ', ' ', ' '],
        [' ', ' ', ' '],
    ];
    let game: Game = { players: players, playerIdx: 0, board: board };
    expect(1).toBe(1);
    let winner = determineWinner(game);
    expect(winner).toBe(null);
});

// end
