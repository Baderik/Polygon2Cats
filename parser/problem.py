from collections import namedtuple
import xml.etree.ElementTree as ET
from pathlib import Path

__all__ = ["Problem"]

ProblemName = namedtuple("ProblemName", ["language", "value"])
StatementNode = namedtuple("StatementNode",
                           ["charset", "language", "mathjax", "path", "type"])
TestNode = namedtuple("TestNode", ["method", "arguments"])
ProblemLimits = namedtuple("ProblemLimits", ["tl", "ml"])
ProblemIO = namedtuple("ProblemIO", ["input", "output"])


def _parse_names(names_node: ET.Element) -> list[ProblemName]:
    """Parse <names> node from problem.xml"""
    return [ProblemName(**name.attrib) for name in names_node]


def _parse_statements(statements_node: ET.Element) -> list[StatementNode]:
    """Parse <statements> node from problem.txt"""
    return [StatementNode(**statement.attrib)
            for statement in statements_node
            if statement.attrib["type"] == "application/x-tex"]


def _parse_tests(tests_node: ET.Element) -> list[TestNode]:
    res = [
        TestNode("manual", i + 1)
        if tests_node[i].attrib["method"] == "manual"
        else TestNode(tests_node[i].attrib["method"], tests_node[i].attrib["cmd"])
        for i in range(len(tests_node))
    ]
    return res


def _parse_test_set(test_set_node: ET.Element) -> tuple[ProblemLimits, list[TestNode]]:
    kwargs = {}
    tests = []
    for el in test_set_node:
        if el.tag == "time-limit":
            kwargs["tl"] = el.text
        if el.tag == "memory-limit":
            kwargs["ml"] = el.text
        if el.tag == "tests":
            tests = _parse_tests(el)
    return ProblemLimits(**kwargs), tests


def _parse_judging(judging_node: ET.Element) -> tuple[ProblemIO, ProblemLimits, list[TestNode]]:
    for el in judging_node:
        if el.tag == "testset":
            limits, tests = _parse_test_set(el)
            return (ProblemIO(judging_node.attrib["input-file"], judging_node.attrib["output-file"]),
                    limits, tests)


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
            if el.tag == "judging":
                self.io, self.limits, self.tests = _parse_judging(el)


if __name__ == '__main__':

    p = Problem(Path('problem.xml'))
    print(p.names)
    print(p.statements)
    print(p.io)
    print(p.limits)
    print(p.tests)


