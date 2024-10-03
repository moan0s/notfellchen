# QZT Dokumentation

![Deploy Status](https://woodpecker.hyteck.de/api/badges/103/status.svg)

# Quickstart

Create & activate a virtual environment to avoid cluttering your system

```zsh
python -m venv venv
source venv/bin/activate
```

Install dependencies

```zsh
pip install -r requirements.txt
```

And serve a local development version

```zsh
cd docs
sphinx-autobuild ./ ./_build/html
```

You can now access the documentation on [http://127.0.0.1:8000](http://127.0.0.1:8000). It will be rebuilt automatically upon file changes.

If you only want to build the static files once you can do `make html`.

## Docker

Build the docker image with

```bash
docker build . -t sphinx-qzt
```

and use it to build the documentation like this

```bash
docker run --rm -v ./docs:/docs sphinx-qzt make html
```

# QZT Dokumentation

# Quickstart

Create & activate a virtual environment to avoid cluttering your system

```zsh
python -m venv venv
source venv/bin/activate
```

Install dependencies

```zsh
pip install -r requirements.txt
```

And serve a local development version

```zsh
cd docs
sphinx-autobuild ./ ./_build/html
```

You can now access the documentation on <http://127.0.0.1:8000>. It will be rebuilt automatically upon file changes.

If you only want to build the static files once you can do `make html`.

## Docker

Build the docker image with

```bash
docker build . -t sphinx-rtd
```

and use it to build the documentation like this

```bash
docker run --rm -v ./docs:/docs sphinx-rtd make html
```

# CI

Woodpecker can be used to deploy the documentation to a server