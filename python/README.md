py.test && mypy --strict aidoodle/

ai-play
ai-play --n_iter 5000 --start false
ai-play --agent random

ai-simulate
ai-simulate --n_iter1 5000 --agent2 random --n_runs 10