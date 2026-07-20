Code Atlas MVP

Goal: Build a Python-focused tool that helps developers understand a codebase by turning it into an interactive dependency map.

## Setup

From the repo root (with the project venv active):

```bash
pip install -e .
```

## Analyze a repository

```bash
atlas /path/to/target/repo
```

Writes a summary to stdout and `graph.json` by default.

Optional flags: `--config`, `--entry-point`, `--ignore-dir`, `--ignore-module`, `--ignore-path`, `--output` / `-o`.

## Diff two Git revisions

```bash
atlas diff [BASE] [TARGET]
```

`BASE` and `TARGET` are Git revisions. Defaults: `BASE=HEAD~1`, `TARGET=working tree`.

Examples:

```bash
atlas diff
atlas diff HEAD~3
atlas diff main
atlas diff origin/main HEAD
atlas diff feature/login HEAD
atlas diff a1b2c3d HEAD --repo /path/to/repo -o graph-diff.json
```

Writes a summary to stdout and `graph-diff.json` by default.
