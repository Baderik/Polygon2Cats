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
Checker = namedtuple("Checker", ["is_testlib", "path", "type"])
Solution = namedtuple("Solution", ["tag", "path", "type"])


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


def _parse_checker(checker_node: ET.Element) -> Checker:
    for el in checker_node:
        if el.tag == "source":
            return Checker(checker_node.attrib["type"] == "testlib", **el.attrib)


def _parse_solutions(solutions_node: ET.Element) -> list[Solution]:
    res = []
    for el in solutions_node:
        if el.tag == "solution":
            for sub_el in el:
                if sub_el.tag == "source":
                    res.append(Solution(**el.attrib, **sub_el.attrib))
                    break
    return res


def _parse_assets(assets_node: ET.Element) -> tuple[Checker, list[Solution]]:
    checker = None
    solutions = None
    for el in assets_node:
        if el.tag == "checker":
            checker = _parse_checker(el)
        if el.tag == "solutions":
            solutions = _parse_solutions(el)
    return checker, solutions


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
            if el.tag == "assets":
                self.checker, self.solutions = _parse_assets(el)


if __name__ == '__main__':
    p = Problem(Path('problem.xml'))
    print(p.names)
    print(p.statements)
    print(p.io)
    print(p.limits)
    print(p.tests)
    print(p.checker)
    print(p.solutions)


