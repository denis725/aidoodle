## Develop

```
conda env create
source activate aidoodle
pip install -e .

mypy --strict aidoodle
py.test --runslow aidoodle

mypy --strict aidoodle && py.test aidoodle
```

## Play against AI

Note: When a possible move is, e.g., `Move(0, 1)`, you should enter
`0,1` to make that move.

```
ai-play
ai-play --n_iter 5000 --start false
ai-play --agent random

ai-play --n_iter 3000 --game nim
```

## Simulate AI

```
ai-simulate
ai-simulate --n_iter1 500 --agent2 random --n_runs 10 --silent false
```

## Games

### Tic Tac Toe

First player to set 3 stones in a row or in a diagonale wins.

E.g., with this board:

```
   0 1 2
0 |o|o|x|
1 |x|o| |
2 | | |x|
```

player 1 ("x") should play `1,2`, because that secures 3 stones in the
right-most column.

### Nim

There are 3 heaps with a random amount of stones on each heap. Players
take turns removing an arbitrary amount of stones (> 0) from one
heap. The last player to take a stone loses.

E.g., on the following board, we have 3 stones on heap 0, 1 stone on
heap 1 and no stones on heap 2. If it's your turn, you should perform
move `0,3`, i.e. remove all 3 stones from heap 0. That way, the
opponent must take the last stone from heap 1 and loses.

```
|0|1|2|
|-|-|-|
|3|1|0|
```

### Dumb dice

Each player takes turn rolling two dice. After each roll, the player
can decide whether to keep the roll ("continue", `c`) or to reroll
(`r`). A player may only reroll exactly once. The eyes of the dice are
then added to a player's score. The first player to have a score of at
least 50 wins.

E.g., for this board:

```
------------------------
dice: 6 + 5 | target: 50
   player 1 | player 2
         40 | 47      
```

player 1 should continue (`c`) because that will result in a score of
51, which leads to a win. If player 1 rerolled, there is a good chance
that a non-winning sum of eyes will be rolled, in which case player 2
will most likely win, needing only a sum of 3.
