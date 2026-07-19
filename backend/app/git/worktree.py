from git import Repo
from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import contextmanager
from typing import Generator
from git.objects import Commit

@contextmanager
def create_worktree(repo: Repo, commit: Commit) -> Generator[Path, None, None]:
    with TemporaryDirectory(prefix="codeatlas-") as temp_dir:
        worktree_path = Path(temp_dir) / "worktree"

        repo.git.worktree("add", "--detach", str(worktree_path), commit.hexsha)

        try:
            yield worktree_path
        finally:
            repo.git.worktree("remove", "--force", str(worktree_path))
