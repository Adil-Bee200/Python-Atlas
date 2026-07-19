Code Atlas MVP

Goal: Build a Python-focused tool that helps developers understand a codebase by turning it into an interactive dependency map.

## CLI

From the repo root (with the project venv active):

```bash
pip install -e .
atlas /path/to/target/repo
```

Optional flags: `--config`, `--entry-point`, `--ignore-dir`, `--ignore-module`, `--ignore-path`.


atlas diff [BASE] [TARGET]

BASE and TARGET are Git revisions.

Examples:

atlas diff
atlas diff HEAD~3
atlas diff main
atlas diff origin/main HEAD
atlas diff feature/login HEAD
atlas diff a1b2c3d HEAD