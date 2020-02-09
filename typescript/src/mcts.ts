import { BaseEngine, Move, Game, Player, gameToString } from "./games/tictactoe";
import { randChoice, sum } from './utils';

const C = Math.SQRT2;
const EPS = 1e-12;
const MAX_DEPTH = 10000;
const N_ITER = 100;

interface Edge {
    move: Move;
    w: number;
    s: number;
};

interface Node {
    game: Game;
    edges: Edges;
};

interface Cache {
    [gameString: string]: Node;
};

type Players = Player[];
type Edges = Edge[];


const selectmax = (edges: Edges, vals: number[]): Edge => {
    if (vals.length < 1) {
        throw new Error("Cannot select from empty array");
    };
    if (vals.length !== edges.length) {
        throw new Error("Keys and values must be of equal length");
    }

    const argmax = vals.map(
        (x, i) => [x, i]
    ).reduce((r, a) => (a[0] > r[0] ? a : r))[1];
    return edges[argmax];
};

const ucb1Values = (edges: Edges): number[] => {
    const sVals = edges.map((edge) => edge.s);
    const sTot = sum(sVals);
    const c = C * Math.log(sTot + 1);
    const vals = edges.map((e) => e.w / (e.s + EPS) + c / Math.sqrt(e.s + EPS));
    return vals;
};

const selectUcb1 = (edges: Edges): Edge => {
    const vals = ucb1Values(edges);
    const edge = selectmax(edges, vals);
    return edge;
};

const expand = (node: Node, engine: BaseEngine) => {
    // Careful: if a move is the identity move, there will be an infinte loop
    if (node.edges.length > 0) {
        throw new Error("Node shouldn't have any edges");
    };

    const moves = engine.getLegalMoves(node.game);
    let edges: Edges = [];
    moves.forEach((move) => edges.push({ move: move, w: 0, s: 0 }));

    node.edges = edges;
};

const simulate = (game: Game, engine: BaseEngine): number => {
    var newGame = engine.initGame(game.board, game.playerIdx);

    let winner = engine.determineWinner(newGame);
    while (winner === undefined) {
        var move = randChoice(engine.getLegalMoves(newGame));
        var newGame = engine.makeMove(newGame, move);
        console.log(game);
        console.log(move);
    };

    const score = engine.scoreGame(newGame);
    return score;
};

const updateEdge = (edge: Edge, value: number) => {
    edge.s = edge.s + 1;
    edge.w = edge.w + value;
};

const update = (edges: Edges, players: Players, value: number) => {
    if (edges.length !== players.length) {
        throw new Error("Number of edges and number of players not equal");
    };

    const valueOther = 1 - value;
    for (let i = 0; edges.length; i++) {
        var edge = edges[i];
        var player = players[i];
        (player === 1) ? updateEdge(edge, value) : updateEdge(edge, valueOther);
    };
};

const retrieveNode = (game: Game, cache: Cache): Node => {
    const maybeNode: Node | undefined = cache[gameToString(game)];
    if (maybeNode !== undefined) {
        return maybeNode;
    };

    const node: Node = { game: game, edges: [] };
    cache[gameToString(game)] = node;
    return node;
}

export const search = (node: Node, engine: BaseEngine, cache: Cache) => {
    cache[gameToString(node.game)] = node;
    var edges: Edges = [];
    var players: Players = [];

    while (node.edges.length > 0) {
        const edge = selectUcb1(node.edges);
        edges.push(edge);
        const player = node.game.players[node.game.playerIdx];
        players.push(player);

        const game = engine.makeMove(node.game, edge.move);
        node = retrieveNode(game, cache);

        if (edges.length > MAX_DEPTH) {
            throw new Error("Max search depth has been exceeded, infinite loop?");
        };
    };

    expand(node, engine);
    if (node.edges.length > 0) {  // game has not ended
        const edge = randChoice(node.edges);
        var game = engine.makeMove(node.game, edge.move);
        edges.push(edge);
        players.push(game.players[game.playerIdx]);
        const value = simulate(game, engine);
        update(edges, players, value);
    } else {
        const game = node.game;
        const value = simulate(game, engine);
        update(edges, players, value);
    };
};

export const mctsMove = (game: Game, engine: BaseEngine): Move => {
    const edges: Edges = [];
    const root: Node = { game: game, edges: edges };
    const cache: Cache = {};

    for (let _ = 0; N_ITER; _++) {
        search(root, engine, cache);
    };

    const values = edges.map((edge) => edge.s)
    const edge = selectmax(root.edges, values);
    return edge.move;
}