import { Game, Board, Players, determineWinner } from './tictactoe';

const players: Players = [1, 2];

// testing determining the winner

test('no winner', () => {
    const board: Board = [
        [' ', ' ', ' '],
        [' ', ' ', ' '],
        [' ', ' ', ' '],
    ];
    const game: Game = { players, playerIdx: 0, board };
    expect(1).toBe(1);
    const winner = determineWinner(game);
    expect(winner).toBe(undefined);
});

// end
