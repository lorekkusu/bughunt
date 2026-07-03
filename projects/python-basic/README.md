# vault-api

A tiny account & file "vault" backend built with Flask + SQLite. It exposes a
handful of endpoints for authentication, viewing accounts, transferring funds,
and downloading uploaded files. Intended as a compact, realistic service.

## Features

- User login with token issuance
- Account balance lookup
- Fund transfers between accounts
- File upload/download storage
- YAML-based configuration
- Simple maintenance tasks (host ping, backups)

## Layout

```
src/vault_api/
  app.py            # Flask routes
  auth.py           # password hashing, tokens, sessions
  banking.py        # money transfer logic
  db.py             # SQLite persistence
  files.py          # file storage
  tasks.py          # maintenance / background helpers
  config_loader.py  # YAML config loading
  utils.py          # misc helpers
```

## Getting started

```bash
uv sync
uv run python -m vault_api.app      # starts the dev server
uv run pytest                       # run the test suite
```

## Configuration

Copy `config.example.yaml` to `config.yaml` and adjust values as needed.
