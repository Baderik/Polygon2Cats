from pathlib import Path
from shutil import copy

__all__ = ["copy_examples"]


def copy_examples(count: int, from_path: Path, problem_path: Path, example_dir: Path = "samples"):
    (problem_path / example_dir).mkdir(exist_ok=True)
    for i in range(1, count + 1):
        if i < 10:
            i = f"0{i}"
        copy(from_path / f"example.{i}", problem_path / example_dir)
        copy(from_path / f"example.{i}.a", problem_path / example_dir)
