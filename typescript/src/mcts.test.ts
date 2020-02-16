import { BaseEngine, Game, Player, TicTacToeEngine } from './games/tictactoe';
import { Agent, nextMove } from './agents';

const playGame = (agent0: Agent, agent1: Agent, engine: BaseEngine): Player => {
    var game: Game = engine.initGame();
    var idx = 0;
    const agents = [agent0, agent1]

    while (!engine.determineWinner(game)) {
        const agent = agents[idx];
        const move = nextMove(agent, game, engine);
        var game = engine.makeMove(game, move);
        var idx = 1 - idx;
    };

    const winner = engine.determineWinner(game);
    if (!winner) {
        throw new Error("This can never be reached, just for tsc");
    };
    return winner;
};

test('test that mcts beats random on average', () => {
    const agent1: Agent = { kind: 'random' };
    const agent2: Agent = { kind: 'mcts' };
    const n = 100;
    var wins1 = 0;
    var wins2 = 0;
    var ties = 0;
    for (let i = 0; i < n; i++) {
        let winner = playGame(agent1, agent2, TicTacToeEngine);
        if (winner === -1) {
            ties += 1;
        } else if (winner === 1) {
            wins1 += 1;
        } else if (winner === 2) {
            wins2 += 1;
        };
    };
    expect(wins2).toBeGreaterThan(60);
    expect(wins1).toBeLessThan(30);
    expect(ties).toBeLessThan(30);
})