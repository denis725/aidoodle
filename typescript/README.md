To install dependencies, run:

```bash
yarn install
```

To transpile the typescript code:

```bash
yarn tsc
# or
yarn tsc --watch  # daemon
```

To run a server and check the outcome:

```bash
python server.py
firefox http://0.0.0.0:8080/src/static/index.html
```

To run tests, from the typescript root, run:

```bash
yarn jest
```
