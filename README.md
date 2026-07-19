Code Atlas MVP

Goal: Build a Python-focused tool that helps developers understand a codebase by turning it into an interactive dependency map.

## CLI

From the repo root (with the project venv active):

```bash
pip install -e .
atlas /path/to/target/repo
```

Optional flags: `--config`, `--entry-point`, `--ignore-dir`, `--ignore-module`, `--ignore-path`.
