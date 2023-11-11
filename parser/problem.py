from collections import namedtuple
import xml.etree.ElementTree as ET
from pathlib import Path

__all__ = ["Problem"]

ProblemName = namedtuple("ProblemName", ["language", "value"])
StatementNode = namedtuple("StatementNode",
                           ["charset", "language", "mathjax", "path", "type"])


def _parse_names(names_node: ET.Element) -> list[ProblemName]:
    """Parse <names> node from problem.xml"""
    return [ProblemName(**name.attrib) for name in names_node]


def _parse_statements(statements_node: ET.Element) -> list[StatementNode]:
    """Parse <statements> node from problem.txt"""
    return [StatementNode(**statement.attrib)
            for statement in statements_node
            if statement.attrib["type"] == "application/x-tex"]


class Problem:
    def __init__(self, problem_path: Path):
        if not problem_path.is_file() or not problem_path.with_suffix(".xml"):
            raise ValueError("Path of problem.xml must be .xml file, but found:", problem_path)
        self.tree = ET.parse(problem_path)
        self._parse()

    def _parse(self):
        for el in self.tree.getroot():
            if el.tag == "names":
                self.names = _parse_names(el)
            if el.tag == "statements":
                self.statements = _parse_statements(el)


tree = ET.parse('problem.xml')


