from io import StringIO
from pathlib import Path
from unittest.mock import patch

from backend.app.analysis.diff_analyzer import (
    compare_graphs,
    print_graph_difference_summary,
)
from backend.app.export.graph_json import (
    graph_difference_to_dict,
    write_graph_difference_as_json_file,
)
from backend.app.main import parse_args
from backend.app.metrics.metrics_aggregator import analyze_metrics
from backend.tests.utils import _graph


def test_parse_args_analyze_defaults_output():
    args = parse_args(["some/repo"])

    assert args.command == "analyze"
    assert args.repo == "some/repo"
    assert args.output == "graph.json"


def test_parse_args_diff_defaults():
    args = parse_args(["diff"])

    assert args.command == "diff"
    assert args.base == "HEAD~1"
    assert args.target is None
    assert args.repo == "."
    assert args.output == "graph-diff.json"


def test_parse_args_diff_with_revisions_and_repo():
    args = parse_args(
        ["diff", "main", "HEAD", "--repo", "samples/foo", "-o", "out.json"]
    )

    assert args.command == "diff"
    assert args.base == "main"
    assert args.target == "HEAD"
    assert args.repo == "samples/foo"
    assert args.output == "out.json"


def test_graph_difference_to_dict_and_write(tmp_path: Path):
    import json
    from dataclasses import replace

    base = replace(
        _graph(("a", "b"), (("a", "b"),)),
        metrics=analyze_metrics(_graph(("a", "b"), (("a", "b"),))),
    )
    target = replace(
        _graph(("a", "c"), (("a", "c"),)),
        metrics=analyze_metrics(_graph(("a", "c"), (("a", "c"),))),
    )
    difference = compare_graphs(
        base, target, base_revision="base", target_revision="target"
    )

    payload = graph_difference_to_dict(difference)
    assert payload["base_revision"] == "base"
    assert payload["target_revision"] == "target"
    assert payload["structure"]["added_modules"] == ["c"]
    assert payload["structure"]["removed_modules"] == ["b"]
    assert "metrics" in payload

    out = tmp_path / "graph-diff.json"
    write_graph_difference_as_json_file(difference, out)
    loaded = json.loads(out.read_text())
    assert loaded["structure"]["added_modules"] == ["c"]


def test_print_graph_difference_summary_smoke():
    from dataclasses import replace

    base = replace(
        _graph(("a", "b"), (("a", "b"),)),
        metrics=analyze_metrics(_graph(("a", "b"), (("a", "b"),))),
    )
    target = replace(
        _graph(("a", "c"), (("a", "c"),)),
        metrics=analyze_metrics(_graph(("a", "c"), (("a", "c"),))),
    )
    difference = compare_graphs(
        base, target, base_revision="HEAD~1", target_revision="WORKING_TREE"
    )

    buffer = StringIO()
    with patch("sys.stdout", buffer):
        print_graph_difference_summary(difference)

    text = buffer.getvalue()
    assert "Comparing HEAD~1 -> WORKING_TREE" in text
    assert "Structure:" in text
    assert "Modules added: 1" in text
    assert "Architecture: skipped" in text
    assert "Metrics:" in text
