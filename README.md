Code Atlas MVP

Goal: Build a Python-focused tool that helps developers understand a codebase by turning it into an interactive dependency map.

Core MVP features
Repo scanner
User enters/selects a local Python project.
Tool scans .py files and ignores virtual environments, caches, migrations, etc.
Python dependency parser
Parse imports using Python ast.
Detect relationships like:
file_a.py imports file_b.py
module_a depends on module_b
Dependency graph builder
Represent files/modules as nodes.
Represent imports/dependencies as edges.
Store graph data as JSON.
Interactive graph UI
Visualize the codebase as a graph.
Click a node to show:
file path
imports
imported by
dependency count
importance score
Architecture insights
Detect circular dependencies.
Rank most central files/modules.
Show orphan/isolated files.
Show high fan-in / high fan-out modules.
Git comparison
Compare current codebase against previous commit.
Highlight:
new files
deleted files
new dependencies
removed dependencies
Suggested stack

Backend / analysis engine

Python
ast
NetworkX
GitPython
FastAPI

Frontend

React + TypeScript
React Flow or Cytoscape.js

Storage

JSON first
SQLite later if needed
MVP resume bullet

Built a Python architecture explorer that parses codebases into dependency graphs, visualizes module relationships, detects circular dependencies, and compares graph changes across Git commits.

Optional future features
Incremental indexing: only recompute changed files instead of rebuilding the full graph.
Function-level call graph.
Git evolution timeline showing architecture changes over weeks/months.
Complexity metrics: LOC, churn, fan-in, fan-out, centrality.
Test coverage overlay.
AI-assisted explanations grounded in the dependency graph.
TypeScript support.
VS Code extension.
Desktop app with Tauri or Electron.



Phase 0 — Project setup

Goal: create the skeleton.

Tasks:

Create repo: code-atlas
Set up backend package
Set up frontend app
Add README with project thesis
Add sample Python repos for testing
Add basic CI: backend tests + frontend build

Deliverable:

Empty but runnable full-stack project.

Phase 1 — Python repo scanner

Goal: find Python files safely.

Tasks:

Input local repo path
Recursively scan .py files
Ignore:
.venv
venv
__pycache__
.git
node_modules
migrations
Convert file paths to module paths
Return list of discovered files/modules

Deliverable:

“Here are all Python modules in this project.”

Phase 2 — Import parser

Goal: extract dependencies.

Tasks:

Use Python ast
Parse:
import x
import x.y
from x import y
from . import x
from .x import y
Resolve imports to local project files when possible
Mark unresolved/external imports separately

Deliverable:

For each file, show what local modules it depends on.

Phase 3 — Dependency graph engine

Goal: build the actual graph.

Tasks:

Create graph model:
nodes = Python files/modules
edges = imports/dependencies
Store graph as JSON
Compute:
fan-in
fan-out
centrality
isolated files
circular dependencies
Add unit tests with small fake repos

Deliverable:

A JSON dependency graph with basic architecture metrics.

Phase 4 — Backend API

Goal: expose graph data to UI.

Tasks:

Create FastAPI endpoints:
POST /analyze
GET /graph
GET /nodes/{id}
GET /cycles
GET /metrics
Add error handling for invalid paths
Add basic request/response schemas
Add backend tests

Deliverable:

Frontend can request a repo analysis and receive graph data.

Phase 5 — Interactive graph UI

Goal: make the project demoable.

Tasks:

Build React frontend
Add repo path input
Render graph using React Flow or Cytoscape.js
Support:
zoom
pan
click node
search module
highlight incoming/outgoing dependencies
Sidebar shows:
file path
imports
imported by
fan-in/fan-out
centrality

Deliverable:

User can visually explore a Python project.

Phase 6 — Architecture insights

Goal: make it useful, not just pretty.

Tasks:

Add dashboard cards:
most imported modules
modules with highest fan-out
circular dependencies
isolated modules
external dependency count
Add filters:
show only internal deps
show external deps
hide isolated nodes
show cycles only
Add “impact view”:
click a file
see what could be affected if it changes

Deliverable:

Tool gives useful architecture insights.

Phase 7 — Git diff mode

Goal: show codebase evolution.

Tasks:

Use GitPython
Compare current working tree vs previous commit
Detect:
added files
deleted files
changed files
added dependencies
removed dependencies
Highlight graph changes in UI
Add summary:
“3 modules added”
“5 dependencies removed”
“1 new circular dependency introduced”

Deliverable:

User can see how architecture changed between commits.

Phase 8 — Incremental indexing

Goal: make it technically impressive.

Tasks:

Cache parsed file results
Hash file contents
On re-analysis:
only re-parse files whose hashes changed
update affected graph edges
Show performance comparison:
full rebuild time
incremental rebuild time
Add tests proving unchanged files are skipped

Deliverable:

Tool recomputes only changed nodes instead of rebuilding everything.

Phase 9 — Polish and resume readiness

Goal: make it presentable.

Tasks:

Add screenshots/GIF to README
Add architecture diagram
Add sample analysis on your own financial project
Add clean error states
Add loading states
Add demo video
Deploy frontend/backend if possible
Write final resume bullets

Deliverable:

Project is ready for GitHub, resume, and interviews.

Optional future features
Function-level call graph
Complexity metrics
Git history timeline
Test coverage overlay
AI explanations grounded in graph data
TypeScript support
VS Code extension
Tauri desktop app
Export graph as PNG/SVG/JSON
“Where should I change code?” query mode