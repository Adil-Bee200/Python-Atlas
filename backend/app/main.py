from __future__ import annotations

import argparse
import sys
from pathlib import Path

from backend.app.analysis.analyzer import analyze_repo, print_graph_summary
from backend.app.analysis.diff_analyzer import (
    analyze_repo_diff,
    print_graph_difference_summary,
)
from backend.app.config.loader import ConfigOverrides, load_config
from backend.app.export.graph_json import (
    write_graph_as_json_file,
    write_graph_difference_as_json_file,
)


def _add_shared_config_flags(parser: argparse.ArgumentParser) -> None:
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
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="JSON output path (default: graph.json or graph-diff.json)",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] == "diff":
        parser = argparse.ArgumentParser(
            prog="atlas diff",
            description="Compare architecture between two Git revisions",
        )
        parser.add_argument(
            "base",
            nargs="?",
            default="HEAD~1",
            help="Base Git revision (default: HEAD~1)",
        )
        parser.add_argument(
            "target",
            nargs="?",
            default=None,
            help="Target Git revision (default: working tree)",
        )
        parser.add_argument(
            "--repo",
            type=str,
            default=".",
            help="Path to the Git repository (default: current directory)",
        )
        _add_shared_config_flags(parser)
        args = parser.parse_args(argv[1:])
        args.command = "diff"
        if args.output is None:
            args.output = "graph-diff.json"
        return args

    parser = argparse.ArgumentParser(description="Code Atlas")
    parser.add_argument(
        "repo",
        type=str,
        help="Path to the Python repository to analyze",
    )
    _add_shared_config_flags(parser)
    args = parser.parse_args(argv)
    args.command = "analyze"
    if args.output is None:
        args.output = "graph.json"
    return args


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
        if args.command == "diff":
            difference = analyze_repo_diff(
                Path(args.repo),
                config=config,
                base_revision=args.base,
                target_revision=args.target,
            )
            print_graph_difference_summary(difference)
            write_graph_difference_as_json_file(difference, args.output)
        else:
            graph = analyze_repo(args.repo, config=config)
            print_graph_summary(graph)
            write_graph_as_json_file(graph, args.output)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
