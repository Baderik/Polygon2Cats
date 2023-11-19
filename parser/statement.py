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

    def _parse(self):
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
        self.count = 0
        for f in self.lang_path.iterdir():
            if f.name not in _service_files:
                self.count += 1
        self.count //= 2


if __name__ == '__main__':
    s = Statement(Path("../polygon/example-a-plus-b-11/statement-sections/english/"), "UTF-8")
    print(s.legend)
    print(s.input)
    print(s.output)
    print(s.count)
    print(s.lang_path)
    print(s.notes)
    print(s.tutorial)