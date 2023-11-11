from pathlib import Path

__all__ = ["Statement"]

_service_files = ("name.tex", "legend.tex", "input.tex", "output.tex", "notes.tex", "tutorial.tex")


class Statement:
    def __init__(self, lang_path: Path, encoding: str):
        if not lang_path.is_dir():
            raise ValueError("Path of statement dir must be dir, but found:", lang_path)

        self.lang_path = lang_path
        self.encoding = encoding
        self._parse()
        self._calc_example_count()

    def _parse_name(self):
        with open(self.lang_path / "name.tex", encoding=self.encoding) as inp:
            self.name = inp.read()

    def _parse_legend(self):
        with open(self.lang_path / "legend.tex", encoding=self.encoding) as inp:
            self.legend = inp.read()

    def _parse_input(self):
        with open(self.lang_path / "input.tex", encoding=self.encoding) as inp:
            self.input = inp.read()

    def _parse_output(self):
        with open(self.lang_path / "output.tex", encoding=self.encoding) as inp:
            self.output = inp.read()

    def _parse_notes(self):
        with open(self.lang_path / "notes.tex", encoding=self.encoding) as inp:
            self.notes = inp.read()

    def _parse_tutorial(self):
        with open(self.lang_path / "tutorial.tex", encoding=self.encoding) as inp:
            self.tutorial = inp.read()

    def _parse(self):
        self._parse_name()
        self._parse_legend()
        self._parse_input()
        self._parse_output()
        self._parse_notes()
        self._parse_tutorial()

    def _calc_example_count(self):
        self.count = 0
        for f in self.lang_path.iterdir():
            if f.name not in _service_files:
                self.count += 1
        self.count //= 2
