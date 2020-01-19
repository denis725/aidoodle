import { Game, Move } from './games/tictactoe';


interface RandomAgent {
    kind: "random";
}

interface FooAgent {
    kind: "foo";
}

export type Agent = RandomAgent | FooAgent;

function choice<T>(options: Array<T>): T {
    const idx = Math.floor(Math.random() * options.length);
    return options[idx];
}

export const nextMove = (agent: Agent, game: Game, engine: any): Move => {
    switch (agent.kind) {
        case "random": {
            const move: Move = choice(engine.getLegalMoves(game));
            return move;
        }
        case "foo": {
            const move: Move = engine.getLegalMoves(game)[0];
            return move;
        }
    }
};