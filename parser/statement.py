from pathlib import Path
from json import load
# from pydantic import BaseModel
from dataclasses import dataclass
import re

from parser.models import *
from core import Logged

__all__ = ["Statement", "StatementProperties", "from_file_properties", "parse_statement_resources"]


class Statement(Logged):
    def __init__(self, lang_dir: Path, encoding: str):
        if not lang_dir.is_dir():
            raise ValueError("Path of statement dir must be dir, but found:", lang_dir)

        self.lang_path = lang_dir
        self.encoding = encoding
        self._parse_sections()
        self._calc_example_count()

    def _parse_sections(self):
        self.name = self._parse_file("name.tex")
        self.legend = self._parse_file("legend.tex")
        self.input = self._parse_file("input.tex")
        self.output = self._parse_file("output.tex")
        self.notes = self._parse_file("notes.tex")
        self.tutorial = self._parse_file("tutorial.tex")

    def _parse_file(self, name: str) -> str:
        f_name = self.lang_path / name
        if f_name.exists():
            with open(f_name, encoding=self.encoding) as inp:
                return inp.read()
        else:
            self.logger.warning(f"Statement section file does not exist: {f_name}")

    def _calc_example_count(self):
        self.example_count = 0
        for f in self.lang_path.iterdir():
            if re.fullmatch("example\\.((0[1-9])|([1-9]\\d{1,}))\\.a", f.name):
                self.example_count += 1


@dataclass
class SampleTest:
    input: str
    output: str
    inputFile: str
    outputFile: str


@dataclass
class StatementProperties:
    name: str
    language: str
    authorLogin: str
    authorName: str
    timeLimit: int
    memoryLimit: int
    legend: str
    input: str
    output: str
    inputFile: str
    outputFile: str
    scoring: str | None
    notes: str | None
    interaction: str | None
    tutorial: str | None
    sampleTests: list[SampleTest]
    path: Path | None

    def __post_init__(self):
        self.sampleTests = [SampleTest(**el) for el in self.sampleTests]


def from_file_properties(local_properties_path: Path, encoding: str,
                         root_dir: Path = Path("")) -> StatementProperties:
    with open(root_dir / local_properties_path, encoding=encoding) as prop_file:
        return StatementProperties(**load(prop_file), path=local_properties_path)


def parse_statement_resources(local_statement_dir: Path, samples_count: int,
                              root_dir: Path = Path("")) -> list["ResourceTag"]:
    _services_files = {"problem-properties.json", "problem.tex", "input.tex", "interaction.tex",
                       "legend.tex", "name.tex", "notes.tex", "output.tex", "tutorial.tex",
                       "scoring.tex"}

    for i in range(1, samples_count + 1):
        _services_files.add("example.%02d" % i)
        _services_files.add("example.%02d.a" % i)

    return [ResourceTag(path=local_statement_dir / file.name)
            for file in (root_dir / local_statement_dir).iterdir()
            if file.name not in _services_files]


if __name__ == '__main__':
    t = input("Enter type of statement: s (statement-sections) | P (problem-properties)")
    match t.lower():
        case "s":
            s = Statement(Path(input("Enter path to polygon statement-sections/language dir\n")),
                          "UTF-8")
            print(s.name)
            print(s.legend)
            print(s.input)
            print(s.output)
            print(s.example_count)
            print(s.lang_path)
            print(s.notes)
            print(s.tutorial)
        case _:
            p = from_file_properties(Path(input("Enter path to polygon problem-properties.json\n")),
                                     "UTF-8")
            print(p)
