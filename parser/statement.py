from pathlib import Path
from json import load
from dataclasses import dataclass
import re

__all__ = ["Statement", "StatementProperties", "parse_properties"]

_service_files = ("name.tex", "legend.tex", "input.tex", "output.tex", "notes.tex", "tutorial.tex", "scoring.tex", "tree.mp")


class Statement:
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
    scoring: str | None
    authorLogin: str
    authorName: str
    timeLimit: int
    memoryLimit: int
    legend: str
    input: str
    output: str
    inputFile: str
    outputFile: str
    notes: str | None
    interaction: str | None
    tutorial: str | None
    sampleTests: list[SampleTest]


def parse_properties(properties_path: Path, encoding) -> StatementProperties:
    with open(properties_path, encoding=encoding) as prop_file:
        return StatementProperties(**load(prop_file))


if __name__ == '__main__':
    s = Statement(Path("../polygon/domino/statement-sections/russian/"), "UTF-8")
    print(s.legend)
    print(s.input)
    print(s.output)
    print(s.example_count)
    print(s.lang_path)
    print(s.notes)
    print(s.tutorial)
    props = parse_properties(Path("../polygon/domino/statements/russian/problem-properties.json"), "UTF-8")
    print(props)
