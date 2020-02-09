import { Game, Move } from './games/tictactoe';
import { randChoice } from './utils';
import { mctsMove } from './mcts';


interface RandomAgent {
    kind: "random";
}

interface FooAgent {
    kind: "foo";
}

interface MctsAgent {
    kind: "mcts";
}

export type Agent = RandomAgent | FooAgent | MctsAgent;

export const nextMove = (agent: Agent, game: Game, engine: any): Move => {
    switch (agent.kind) {
        case "random": {
            const move: Move = randChoice(engine.getLegalMoves(game));
            return move;
        }
        case "foo": {
            const move: Move = engine.getLegalMoves(game)[0];
            return move;
        }
        case "mcts": {
            const move = mctsMove(game, engine);
            return move;
        }
    };
};