from pathlib import Path
from shutil import copy
from typing import TYPE_CHECKING

from parser.statement import parse_statement_resources

if TYPE_CHECKING:
    from parser.models import *
    from parser.statement import StatementProperties


__all__ = ["Copier"]


def copy_source(source: "SourceTag", source_root: Path, result_path: Path) -> Path:
    copy(source_root / source.path, result_path)
    if result_path.is_file():
        return result_path
    return result_path / source.path.name


class Copier:
    def __init__(self, source_root: Path, result_root: Path):
        self.source = source_root
        self.result = result_root
        self.result.mkdir(parents=True, exist_ok=True)

    def checker(self, checker: "CheckerTag") -> None:
        copy_source(checker, self.source, self.result)
        checker.path = Path(checker.path.name)

    def interactor(self, interactor: "InteractorTag") -> None:
        copy_source(interactor, self.source, self.result)
        interactor.path = Path(interactor.path.name)

    def generators(self, generators: list["ExecutableTag"],
                   folder: Path | str = "generators") -> None:
        folder = Path(folder)
        result_dir = self.result / folder
        result_dir.mkdir(exist_ok=True)
        for gen in generators:
            copy_source(gen, self.source, result_dir)
            gen.path = folder / gen.path.name

    def solutions(self, solutions: list["SolutionTag"], folder: Path | str = "solutions") -> None:
        folder = Path(folder)
        result_dir = self.result / folder
        result_dir.mkdir(exist_ok=True)
        for sol in solutions:
            copy_source(sol, self.source, result_dir)
            sol.path = folder / sol.path.name

    def samples(self, properties: "StatementProperties", folder: Path | str = "samples") \
            -> tuple[Path, Path]:
        """
        Copy samples files from Polygon package to CATS package.
        Return path to samples input and answer.
        """
        folder = Path(folder)
        source_dir = self.source / "statements" / properties.language
        result_dir = self.result / folder
        result_dir.mkdir(exist_ok=True)

        for i in range(1, len(properties.sampleTests) + 1):
            copy(source_dir / ("example.%02d" % i), result_dir)
            copy(source_dir / ("example.%02d.a" % i), result_dir)
        return folder / "example.%0n", folder / "example.%0n.a"

    def tests(self, folder: Path | str = "tests") -> Path:
        """Copy tests files from Polygon package to CATS package. Return path to tests dir."""
        folder = Path(folder)
        source_dir = self.source / "tests"
        result_dir = self.result / folder
        result_dir.mkdir(exist_ok=True)
        for test_path in source_dir.iterdir():
            copy(test_path, result_dir)
        return folder

    def statement_resources(self, properties: "StatementProperties",
                            folder: Path | str = "files") -> list["ResourceTag"]:
        """
        Copy statement/lang/resources files from Polygon package to CATS package.
        Return the list of these resources.
        """
        folder = Path(folder)
        result_dir = self.result / folder
        result_dir.mkdir(exist_ok=True)
        resources = parse_statement_resources(properties.path.parent,
                                              len(properties.sampleTests), root_dir=self.source)

        for res in resources:
            copy_source(res, self.source, result_dir)
            res.path = folder / res.path.name
        return resources
