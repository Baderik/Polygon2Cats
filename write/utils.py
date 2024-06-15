import typing
from pathlib import Path
from shutil import copy

__all__ = ["cats_rank", "cats_languages", "copy_examples_files", "copy_tests_files"]

if typing.TYPE_CHECKING:
    from parser.problem import TitleNode


def cats_rank(start: int, end: int = None) -> str:
    """Return the rank formatted according to CATS xml."""
    if end is None:
        end = start
        start = 1

    if end - start == 0:
        return str(start)
    else:
        return f"{start}-{end}"


def cats_languages(names: "TitleNode") -> str:
    """Return the language title formatted according to CATS xml."""
    def one(node: "TitleNode") -> str:
        return node.language[:2]
    return ",".join(map(one, names))


def copy_examples_files(count: int, source_root: Path, result_root: Path,
                        samples_dir_name: Path = "samples", lang: str = "russian"):
    """Copy examples files from Polygon package to Result dir."""
    (result_root / samples_dir_name).mkdir(exist_ok=True)
    for i in range(1, count + 1):
        copy(source_root / "statements" / lang / ("example.%02d" % i),
             result_root / samples_dir_name)
        copy(source_root / "statements" / lang / ("example.%02d.a" % i),
             result_root / samples_dir_name)


def copy_tests_files(source_root: Path, result_root: Path, test_dir_name: str = "tests",
                     file_name_format: str = "%s.in"):
    """Copy tests files from Polygon package to Result dir."""
    (result_root / test_dir_name).mkdir(exist_ok=True)
    for test_path in (source_root / "tests").iterdir():
        copy(test_path, result_root / test_dir_name / (file_name_format % test_path.stem))
