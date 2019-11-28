## Develop

```
conda env create
source activate aidoodle
pip install -e .

mypy --strict aidoodle
py.test --runslow aidoodle

py.test aidoodle && mypy --strict aidoodle
```

## Play against AI

Note: When a possible move is, e.g., `Move(0, 1)`, you should enter
`0,1` to make that move.

```
ai-play
ai-play --n_iter 5000 --start false
ai-play --agent random
```

## Simulate AI

```
ai-simulate
ai-simulate --n_iter1 500 --agent2 random --n_runs 10 --silent false
```

## Games

### Tic Tac Toe

First player to set 3 stones in a row or in a diagonale wins.

### Nim

There are 3 heaps with a random amount of stones on each heap. Players
take turns removing an arbitrary amount of stones (> 0) from one
heap. The last player to take a stone loses.