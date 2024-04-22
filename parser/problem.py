from collections import namedtuple
import xml.etree.ElementTree as ET
from pathlib import Path

__all__ = ["Problem"]


TitleNode = namedtuple("TitleNode", ["language", "value"])
TexNode = namedtuple("StatementNode",
                     ["charset", "language", "mathjax", "path", "type"])
TestNode = namedtuple("TestNode",
                      ["method", "from_file", "cmd",
                       "description", "arguments", "points", "group", "sample"],
                      defaults=(None, None, None, None, None, None, None, False))
GroupNode = namedtuple("GroupNode",
                       ["name", "feedback_policy", "points_policy", "dependencies"],
                       defaults=("",))
ProblemTests = namedtuple("ProblemTests", ["tests", "groups"])
ProblemLimits = namedtuple("ProblemLimits", ["time_limit", "memory_limit"])
ProblemIO = namedtuple("ProblemIO",
                       ["input_file", "output_file", "test_format"])
TestFormats = namedtuple("TestFormats",
                         ["input_path_pattern", "output_path_pattern", "answer_path_pattern"],
                         defaults=("%02d", "%02d.o", "%02d.a"))
Checker = namedtuple("Checker", ["is_testlib", "path", "type"])
Solution = namedtuple("Solution", ["tag", "path", "type", "note"], defaults=(None,))

FileNode = namedtuple("File", ["path", "section", "type"], defaults=(None,))


def _pre_attrib(kwargs: dict) -> dict:
    """Preprocessing attributes of xml nodes: replace - to _"""
    return {key.replace("-", "_"): item for key, item in kwargs.items()}


def _parse_titles(names_node: ET.Element) -> list[TitleNode]:
    """Parse <titles> node from problem.xml"""
    return [TitleNode(**name.attrib) for name in names_node]


def _parse_statements(statements_node: ET.Element) -> list[TexNode]:
    """Parse <statements> node from problem.xml"""
    return [TexNode(**statement.attrib)
            for statement in statements_node
            if statement.attrib["type"] == "application/x-tex"]


def _parse_tutorials(tutorials_node: ET.Element) -> list[TexNode]:
    """Parse <tutorials> node from problem.xml"""
    return [TexNode(_pre_attrib(tutorial.attrib))
            for tutorial in tutorials_node
            if tutorial.attrib["type"] == "application/x-tex"]


def _parse_tests(tests_node: ET.Element) -> list[TestNode]:
    """Parse judging/testset/<tests> node from problem.xml"""
    res = [TestNode(**_pre_attrib(tests_node[i].attrib))
           for i in range(len(tests_node))]
    return res


def _parse_groups(groups_node: ET.Element) -> list[GroupNode]:
    """Parse judging/testset/<groups> node from problem.xml"""
    groups = []
    for el in groups_node:
        if el.tag == "group":
            for sub_el in el:
                if sub_el.tag == "dependencies":
                    dep = ",".join(ssub_el.attrib["group"]
                                   for ssub_el in el if ssub_el.tag == "dependency")
                    groups.append(
                        GroupNode(el.attrib["name"], el.attrib["feedback-policy"],
                                  el.attrib["points-policy"], dependencies=dep))
    return groups


def _parse_test_set(test_set_node: ET.Element) \
        -> tuple[ProblemLimits, ProblemTests, TestFormats]:
    """Parse judging/<testset> node from problem.xml"""
    kwargs = {}
    formats_kwargs = {}
    tests = []
    groups = []
    for el in test_set_node:
        if el.tag in ("time-limit", "memory-limit"):
            kwargs[el.tag.replace("-", "_")] = el.text
        elif el.tag == "groups":
            groups = _parse_groups(el)
        elif el.tag in ("input-path-pattern", "output-path-pattern", "answer-path-pattern"):
            formats_kwargs[el.tag.replace("-", "_")] = el.text
        elif el.tag == "tests":
            tests = _parse_tests(el)

    return ProblemLimits(**kwargs), ProblemTests(tests, groups), TestFormats(**formats_kwargs)


def _parse_judging(judging_node: ET.Element) \
        -> tuple[ProblemIO, ProblemLimits, ProblemTests]:
    """Parse <judging> node from problem.xml"""
    test_set_count = 0
    limits = tests = file_formats = None
    for el in judging_node:
        if el.tag == "testset":
            test_set_count += 1
            limits, tests, file_formats = _parse_test_set(el)
    if test_set_count != 1:
        raise ValueError(f"WARNING: There is an incorrect number of test sets"
                         f" in the polygon package. curr: {test_set_count}, but must: 1")
    return (ProblemIO(judging_node.attrib["input-file"],
                      judging_node.attrib["output-file"],
                      file_formats),
            limits, tests)


def _parse_checker(checker_node: ET.Element) -> Checker:
    """Parse assets/<checker> node from problem.xml"""
    for el in checker_node:
        if el.tag == "source":
            return Checker(checker_node.attrib["type"] == "testlib", **el.attrib)


def _parse_solutions(solutions_node: ET.Element) -> list[Solution]:
    """Parse assets/<solution> node from problem.xml"""
    res = []
    for el in solutions_node:
        if el.tag == "solution":
            for sub_el in el:
                if sub_el.tag == "source":
                    res.append(Solution(**el.attrib, **sub_el.attrib))
                    break
    return res


def _parse_assets(assets_node: ET.Element) -> tuple[Checker, list[Solution]]:
    """Parse <assets> node from problem.xml"""
    checker = solutions = None

    for el in assets_node:
        if el.tag == "checker":
            checker = _parse_checker(el)
        if el.tag == "solutions":
            solutions = _parse_solutions(el)
    return checker, solutions


def _parse_resources(resources_node: ET.Element) -> list[FileNode]:
    """Parse files/<resources> node from problem.xml"""
    return [FileNode(**_pre_attrib(el.attrib), section="resources") for el in resources_node]


def _parse_execute(executable_node: ET.Element) -> FileNode:
    """Parse files/executables/<executable> node from problem.xml"""
    for el in executable_node:
        if el.tag == "source":
            return FileNode(**_pre_attrib(el.attrib), section="executables")


def _parse_executables(executables_node: ET.Element) -> list[FileNode]:
    """Parse files/<executables> node from problem.xml"""
    return [_parse_execute(el) for el in executables_node]


def _parse_files(files_node: ET.Element) -> tuple[list[FileNode], list[FileNode]]:
    """Parse <files> node from problem.xml"""
    resources = executables = None

    for el in files_node:
        match el.tag:
            case "resources":
                resources = _parse_resources(el)
            case "executables":
                executables = _parse_executables(el)

    return resources, executables


class Problem:
    def __init__(self, problem_path: Path):
        if not problem_path.is_file() or not problem_path.with_suffix(".xml"):
            raise ValueError("Path of problem.xml must be .xml file, but found:", problem_path)
        self.tree = ET.parse(problem_path)
        self._parse()

    def _parse(self):
        for el in self.tree.getroot():
            match el.tag:
                case "names":
                    self.names = _parse_titles(el)
                case "statements":
                    self.statements = _parse_statements(el)
                case "judging":
                    self.io, self.limits, self.tests = _parse_judging(el)
                case "assets":
                    self.checker, self.solutions = _parse_assets(el)
                case "files":
                    self.resources, self.executables = _parse_files(el)


if __name__ == '__main__':
    p = Problem(Path('../polygon/domino/problem.xml'))
    print(p.names)
    print(p.statements)
    print(p.io)
    print(p.limits)
    print(p.tests)
    print(p.checker)
    print(p.solutions)
    print(p.tests.tests)
    print(p.tests.groups)
    print(p.resources)
    print(p.executables)
