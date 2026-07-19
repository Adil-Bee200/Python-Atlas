from __future__ import annotations

import argparse
import sys

from backend.app.analysis.analyzer import analyze_repo, print_graph_summary
from backend.app.config.loader import ConfigOverrides, load_config
from backend.app.export.graph_json import write_graph_as_json_file


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Code Atlas")
    parser.add_argument(
        "repo",
        type=str,
        help="Path to the Python repository to analyze",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="codeatlas.yaml",
        help="Path to YAML config file (default: codeatlas.yaml)",
    )
    parser.add_argument(
        "--entry-point",
        action="append",
        default=None,
        dest="entry_points",
        metavar="PATH",
        help="Entry point file or module (repeatable; overrides YAML entry_points)",
    )
    parser.add_argument(
        "--ignore-dir",
        action="append",
        default=None,
        dest="ignore_directories",
        metavar="NAME",
        help="Directory name to ignore (repeatable; overrides YAML ignore.directories)",
    )
    parser.add_argument(
        "--ignore-module",
        action="append",
        default=None,
        dest="ignore_modules",
        metavar="PATTERN",
        help="Module pattern to ignore (repeatable; overrides YAML ignore.modules)",
    )
    parser.add_argument(
        "--ignore-path",
        action="append",
        default=None,
        dest="ignore_paths",
        metavar="PATH",
        help="Relative path to ignore (repeatable; overrides YAML ignore.paths)",
    )
    return parser.parse_args(argv)


def overrides_from_args(args: argparse.Namespace) -> ConfigOverrides:
    return ConfigOverrides(
        entry_points=tuple(args.entry_points) if args.entry_points is not None else None,
        ignore_directories=(
            tuple(args.ignore_directories)
            if args.ignore_directories is not None
            else None
        ),
        ignore_modules=(
            tuple(args.ignore_modules) if args.ignore_modules is not None else None
        ),
        ignore_paths=(
            tuple(args.ignore_paths) if args.ignore_paths is not None else None
        ),
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    config = load_config(args.config, overrides=overrides_from_args(args))

    try:
        graph = analyze_repo(args.repo, config=config)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print_graph_summary(graph)
    write_graph_as_json_file(graph, "graph.json")


if __name__ == "__main__":
    main()
