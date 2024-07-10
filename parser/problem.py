from pathlib import Path
import xml.etree.ElementTree as ET

from parser.models import *
from parser.services import pre_attrib
from core import *

__all__ = ["Problem"]


class _Parser(Logged):
    @classmethod
    def names(cls, names_node: ET.Element) -> list[NameTag]:
        """Parse <names> node from problem.xml"""
        return [NameTag(**name.attrib) for name in names_node]

    @classmethod
    def statements(cls, statements_node: ET.Element) -> list[StatementTag]:
        """Parse <statements> node from problem.xml"""
        return [StatementTag(**statement.attrib) for statement in statements_node]

    @classmethod
    def tutorials(cls, tutorials_node: ET.Element) -> list[TutorialTag]:
        """Parse <tutorials> node from problem.xml"""
        return [TutorialTag(**tutorial.attrib) for tutorial in tutorials_node]

    @classmethod
    def tests(cls, tests_node: ET.Element) -> list[TestTag]:
        """Parse judging/testset/<tests> node from problem.xml"""
        return [TestTag(**tests_node[i].attrib) for i in range(len(tests_node))]

    @classmethod
    def groups(cls, groups_node: ET.Element) -> list[GroupTag]:
        """Parse judging/testset/<groups> node from problem.xml"""
        groups = []
        for el in groups_node:
            if el.tag != "group":
                cls.logger.warning(f"In <groups> tag found <{el.tag}>, must be <group>")
                continue
            dep = []
            for sub_el in el:
                if sub_el.tag != "dependencies":
                    cls.logger.warning(f"In <group> tag found <{el.tag}>, must be <dependencies>")
                    continue
                dep = list(map(lambda g: g.attrib["group"], sub_el))
            groups.append(GroupTag(**el.attrib, dependencies=dep))
        return groups

    @classmethod
    def test_set(cls, test_set_node: ET.Element) -> TestSetTag:
        """Parse judging/<testset> node from problem.xml"""
        kwargs = {}
        for el in test_set_node:
            match el.tag:
                case "time-limit" | "memory-limit" | "test-count" | \
                     "input-path-pattern" | "output-path-pattern" | "answer-path-pattern":
                    kwargs[el.tag] = el.text
                case "tests":
                    kwargs["tests"] = cls.tests(el)
                case "groups":
                    kwargs["groups"] = cls.groups(el)

        return TestSetTag(**test_set_node.attrib, **pre_attrib(kwargs))

    @classmethod
    def judging(cls, judging_node: ET.Element) -> JudgingTag:
        """Parse <judging> node from problem.xml"""
        test_sets = list(map(cls.test_set, judging_node))
        return JudgingTag(**pre_attrib(judging_node.attrib), test_sets=test_sets)

    @classmethod
    def resources(cls, resources_node: ET.Element) -> list[ResourceTag]:
        """Parse files/<resources> node from problem.xml"""
        return [ResourceTag(**el.attrib) for el in resources_node]

    @classmethod
    def executable(cls, executable_node: ET.Element) -> ExecutableTag:
        """Parse files/executables/<executable> node from problem.xml"""
        for el in executable_node:
            if el.tag == "source":
                return ExecutableTag(**el.attrib)

    @classmethod
    def executables(cls, executables_node: ET.Element) -> list[ExecutableTag]:
        """Parse files/<executables> node from problem.xml"""
        return [cls.executable(el) for el in executables_node]

    @classmethod
    def files(cls, files_node: ET.Element) -> tuple[list[ResourceTag], list[ExecutableTag]]:
        """Parse <files> node from problem.xml"""
        resources = executables = None

        for el in files_node:
            match el.tag:
                case "resources":
                    resources = cls.resources(el)
                case "executables":
                    executables = cls.executables(el)

        return resources, executables

    @classmethod
    def checker(cls, checker_node: ET.Element) -> CheckerTag:
        """Parse assets/<checker> node from problem.xml"""
        for el in checker_node:
            if el.tag == "source":
                return CheckerTag(checkerType=checker_node.attrib["type"], **el.attrib)

    @classmethod
    def interactor(cls, interactor_node: ET.Element) -> InteractorTag:
        """Parse assets/<interactor> node from problem"""
        for el in interactor_node:
            if el.tag == "source":
                return InteractorTag(**el.attrib)

    @classmethod
    def validator(cls, validator_node: ET.Element) -> ValidatorTag:
        """Parse assets/validators/<validator> node from problem.xml"""
        for el in validator_node:
            if el.tag == "source":
                return ValidatorTag(**el.attrib)

    @classmethod
    def validators(cls, validators_node: ET.Element) -> list[ValidatorTag]:
        """Parse assets/<validators> node from problem.xml"""
        return [cls.validator(el) for el in validators_node]

    @classmethod
    def solution(cls, solution_node: ET.Element) -> SolutionTag:
        """Parse assets/solutions/<solution> node from problem.xml"""
        for el in solution_node:
            if el.tag == "source":
                return SolutionTag(**solution_node.attrib, **el.attrib)

    @classmethod
    def solutions(cls, solutions_node: ET.Element) -> list[SolutionTag]:
        """Parse assets/<solutions> node from problem.xml"""
        return [cls.solution(el) for el in solutions_node]

    @classmethod
    def assets(cls, assets_node: ET.Element) \
            -> tuple[CheckerTag, InteractorTag, list[ValidatorTag], list[SolutionTag]]:
        """Parse <assets> node from problem.xml"""
        checker = interactor = validators = solutions = None
        for el in assets_node:
            match el.tag:
                case "checker":
                    checker = cls.checker(el)
                case "interactor":
                    interactor = cls.interactor(el)
                case "validators":
                    validators = cls.validators(el)
                case "solutions":
                    solutions = cls.solutions(el)
        return checker, interactor, validators, solutions

    @classmethod
    def tags(cls, tags_node: ET.Element) -> list[Tag]:
        """Parse <tags> node from problem.xml"""
        return [Tag(**el.attrib) for el in tags_node]


class Problem(Logged):
    def __init__(self, problem_path: Path):
        super().__init__()
        if not problem_path.is_file() or not problem_path.with_suffix(".xml"):
            raise ValueError("Path of problem.xml must be .xml file, but found:", problem_path)
        self._tree = ET.parse(problem_path)
        self.logger.debug(f"problem.xml is parsed ({problem_path})")
        self._problem = self._tree.getroot()
        self._path = problem_path if type(problem_path) is Path else Path(problem_path)
        self._names = self._statements = self._tutorials = self._judging = self._resources =\
            self._executables = self._checker = self._interactor = self._validators =\
            self._solutions = self._tags = None
        self._parse()

    def _parse(self):
        """
        Iterate over the problem.xml tags and parse all required tags.
        """
        for el in self.problem:
            match el.tag:
                case "names":
                    self._names = _Parser.names(el)
                case "statements":
                    self._statements = _Parser.statements(el)
                case "tutorials":
                    self._tutorials = _Parser.tutorials(el)
                case "judging":
                    self._judging = _Parser.judging(el)
                case "files":
                    self._resources, self._executables = _Parser.files(el)
                case "assets":
                    (self._checker, self._interactor,
                     self._validators, self._solutions) = _Parser.assets(el)
                case "tags":
                    self._tags = _Parser.tags(el)

    @property
    def problem(self) -> ET.Element:
        if self._problem.tag != "problem":
            raise ValueError("Root tag is not Problem")
        return self._problem

    @property
    def names(self) -> list[NameTag]:
        if self._names is None:
            self.logger.warning("The <NAMES> tag was not found in problem.xml")
        elif len(self._names) == 0:
            self.logger.warning("The names/<NAME> tags were not found in problem.xml")
        else:
            return self._names
        return []

    @property
    def statements(self) -> list[StatementTag]:
        if self._statements is None:
            self.logger.warning("The <STATEMENTS> tag was not found in problem.xml")
        elif len(self._statements) == 0:
            self.logger.warning("The statements/<STATEMENT> tags were not found in problem.xml")
        else:
            return self._statements
        return []

    @property
    def tutorials(self) -> list[TutorialTag]:
        if self._tutorials is None:
            self.logger.warning("The <TUTORIALS> tag was not found in problem.xml")
        elif len(self._tutorials) == 0:
            self.logger.warning("The tutorials/<TUTORIAL> tags were not found in problem.xml")
        else:
            return self._tutorials
        return []

    @property
    def judging(self) -> JudgingTag:
        if self._judging is None:
            self.logger.warning("The <JUDGING> tag was not found in problem.xml")
        return self._judging

    @property
    def resources(self) -> list[ResourceTag]:
        if self._resources is None:
            self.logger.warning("The <RESOURCES> tag was not found in problem.xml")
        elif len(self._resources) == 0:
            self.logger.warning("The resources/<FILE> tags were not found in problem.xml")
        else:
            return self._resources
        return []

    @property
    def executables(self) -> list[ExecutableTag]:
        if self._executables is None:
            self.logger.warning("The <EXECUTABLES> tag was not found in problem.xml")
        elif len(self._executables) == 0:
            self.logger.warning("The executables/<EXECUTABLE> tags were not found in problem.xml")
        else:
            return self._executables
        return []

    @property
    def checker(self) -> CheckerTag:
        if self._checker is None:
            self.logger.warning("The assets/<CHECKER> tag was not found in problem.xml")
        return self._checker

    @property
    def interactor(self) -> InteractorTag:
        if self._interactor is None:
            self.logger.warning("The assets/<INTERACTOR> tag was not found in problem.xml")
        return self._interactor

    @property
    def is_interactive(self) -> bool:
        return self._interactor is not None

    @property
    def validators(self) -> list[ValidatorTag]:
        if self._validators is None:
            self.logger.warning("The assets/<VALIDATORS> tag was not found in problem.xml")
        elif len(self._validators) == 0:
            self.logger.warning("The assets/validators/<VALIDATOR> "
                                "tags were not found in problem.xml")
        else:
            return self._validators
        return []

    @property
    def solutions(self) -> list[SolutionTag]:
        if self._solutions is None:
            self.logger.warning("The assets/<SOLUTIONS> tag was not found in problem.xml")
        elif len(self._solutions) == 0:
            self.logger.warning("The assets/solutions/<SOLUTION> "
                                "tags were not found in problem.xml")
        else:
            return self._solutions
        return []

    @property
    def tags(self) -> list[Tag]:
        if self._tags is None:
            self.logger.warning("The <TAGS> tag was not found in problem.xml")
        elif len(self._tags) == 0:
            self.logger.warning("The tags/<TAG> tags were not found in problem.xml")
        else:
            return self._tags
        return []

    @property
    def path(self):
        return self._path


if __name__ == '__main__':
    p = Problem(Path(input("Enter path to polygon problem.xml\n")))
    print(p.names)
    print(p.statements)
    print(p.tutorials)
    print(p.judging)
    print(p.resources)
    print(p.executables)
    print(p.checker)
    print(p.interactor)
    print(p.validators)
    print(p.solutions)
    print(p.tags)
