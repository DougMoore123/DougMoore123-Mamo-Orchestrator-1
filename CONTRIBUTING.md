# Contributing

Thanks for your interest in contributing!

## Development setup

1) Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

2) Copy the example environment file and fill in values:

```bash
copy .env.example .env
```

## Running tests

```bash
pytest
```

## Code style

- Use `ruff` for linting.
- Keep functions small and focused.
- Prefer type hints for public functions.

## Submitting changes

- Create a branch for your changes.
- Make sure tests pass.
- Open a PR with a clear description.
