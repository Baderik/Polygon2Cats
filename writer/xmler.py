import xml.etree.ElementTree as ET

from pathlib import Path
import typing

from writer.utils import *
import config as cfg

if typing.TYPE_CHECKING:
    from parser.problem import Problem
    from parser.statement import StatementProperties
    from parser.models import *

__all__ = ["CatsXml"]


class CatsBaseXml:
    def __init__(self, version: str = "1.11"):
        self.cats = ET.Element("CATS", {"version": version})
        self.problem = ET.SubElement(self.cats, "Problem")
        self.names = set()
        self.run = None

    def _proc_name(self, name: str) -> None:
        if name in self.names:
            raise AttributeError(f"Name({name}) of tag must be unique.")
        self.names.add(name)

    def _set_problem(self, title: str = None, tLimit: int = None, mLimit: str = None,
                     inputFile: str = None, outputFile: str = None, lang: str = None,
                     wLimit: str = None, author: str = None, difficulty: int = None,
                     stdChecker: str = None, maxPoints: int = None,
                     saveInputPrefix: str = None, saveOutputPrefix: str = None,
                     saveAnswerPrefix: str = None) -> ET.Element:
        attrib = {
            "title": title, "lang": lang,
            "tlimit": None if tLimit is None else str(tLimit),
            "mlimit": mLimit, "wlimit": wLimit,
            "author": author,
            "inputFile": inputFile, "outputFile": outputFile,
            "difficulty": None if difficulty is None else str(difficulty),
            "stdChecker": stdChecker,
            "maxPoints": None if maxPoints is None else str(maxPoints),
            "saveInputPrefix": saveInputPrefix,
            "saveOutputPrefix": saveOutputPrefix,
            "saveAnswerPrefix": saveAnswerPrefix
        }

        attrib = {k: (el if el else self.problem.attrib.get(k))
                  for k, el in attrib.items()}
        self.problem.attrib.update({k: el for k, el in attrib.items() if el})

        return self.problem

    def _add_text_tag(self, tag: str, data: list[str], lang: str = None) -> ET.Element:
        attrib = {"cats_if": f"lang={lang}"} if lang else {}
        root_el = ET.SubElement(self.problem, tag, attrib)
        _add_text(root_el, data)
        return root_el

    def _add_import(self, guid: str, type_import: str = None, name: str = None) -> ET.Element:
        """Add a import tag formatted CATS xml."""
        attrib = {"guid": guid}
        if type_import:
            attrib["type_import"] = type_import
        if name:
            attrib["name"] = name
            self._proc_name(name)
        return ET.SubElement(self.problem, "Import", attrib)

    def _add_file(self, tag: str, name: str, path: Path,
                  compiler: "cfg.Compiler" = None, **kwargs) -> ET.Element:
        if compiler:
            kwargs["de_code"] = str(compiler.value)
        kwargs["name"] = name
        kwargs["src"] = path.as_posix()
        self._proc_name(name)
        return ET.SubElement(self.problem, tag, attrib=kwargs)

    def _set_run(self, method: str) -> ET.Element:
        self.run = ET.SubElement(self.problem, "Run", {"method": method})
        return self.run

    def _add_test(self, in_kwargs: dict = None, out_kwargs: dict = None, **kwargs) -> ET.Element:
        if out_kwargs is None:
            out_kwargs = {}
        if in_kwargs is None:
            in_kwargs = {}
        test = ET.SubElement(self.problem, "Test", attrib=kwargs)
        if in_kwargs:
            ET.SubElement(test, "In", attrib=in_kwargs)
        if out_kwargs:
            ET.SubElement(test, "Out", attrib=out_kwargs)
        return test


class CatsXml(CatsBaseXml):
    def __init__(self, cats_version: str = "1.11"):
        super().__init__(cats_version)
        self.added_samples = False
        self.run = None
        self.checker = None
        self.interactor = None

    def set_title(self, problem: "Problem", properties: "StatementProperties") -> ET.Element:
        name = choose_name(problem.names)
        test_set = choose_testset(problem.judging.test_sets)
        return self._set_problem(
            title=name.value,
            lang=names2languages(problem.names),
            tLimit=int(test_set.time_limit) // 1000,
            mLimit=str(test_set.memory_limit) + "B",
            author=properties.authorName,
            inputFile=problem.judging.input_file
            if problem.judging.input_file
            else f"*{properties.inputFile.upper()}",
            outputFile=problem.judging.input_file
            if problem.judging.output_file
            else f"*{properties.outputFile.upper()}",
            saveInputPrefix=cfg.Properties.saveInputPrefix.value,
            saveOutputPrefix=cfg.Properties.saveOutputPrefix.value,
            saveAnswerPrefix=cfg.Properties.saveAnswerPrefix.value
        )

    def add_txt_by_properties(self, properties: "StatementProperties") -> None:
        lang = cats_lang(properties.language)
        if legend := proc_text(properties.legend):
            self._add_text_tag("ProblemStatement", legend, lang)
        if inp := proc_text(properties.input):
            self._add_text_tag("InputFormat", inp, lang)
        output = proc_text(properties.output)
        if output:
            output = self._add_text_tag("OutputFormat", output, lang)

        if interaction := proc_text(properties.interaction):
            if len(output) == 0:
                output = self._add_text_tag("OutputFormat", [], lang)
            _add_txt_block(output, cfg.headings["interaction"][lang], interaction)
        if notes := proc_text(properties.notes):
            if len(output) == 0:
                output = self._add_text_tag("OutputFormat", [], lang)
            _add_txt_block(output, cfg.headings["notes"][lang], notes)
        if tutorial := proc_text(properties.tutorial):
            self._add_text_tag("Explanation", tutorial, lang)

    def add_samples_by_properties(self, properties: "StatementProperties", use_file: bool = False,
                                  local_in: Path = None, local_ans: Path = None) -> None:
        def _with_file(samples_count: int, lang_if: str = None):
            attrib = {"rank": cats_rank(samples_count)}
            if lang_if:
                attrib["cats_if"] = f"lang={lang_if}"
            samp = ET.SubElement(self.problem, "Sample", attrib)
            ET.SubElement(samp, "SampleIn", {"src": local_in.as_posix()})
            ET.SubElement(samp, "SampleOut", {"src": local_ans.as_posix()})

        def _with_txt(rank: int, inp: str, out: str, lang_if: str = None):
            attrib = {"rank": str(rank)}
            if lang_if:
                attrib["cats_if"] = f"lang={lang_if}"
            samp = ET.SubElement(self.problem, "Sample", attrib)
            ET.SubElement(samp, "SampleIn").text = inp
            ET.SubElement(samp, "SampleOut").text = out

        lang = cats_lang(properties.language)
        if use_file:
            _with_file(len(properties.sampleTests), lang_if=lang)
        else:
            for i, sample in enumerate(properties.sampleTests):
                _with_txt(i + 1, sample.input, sample.output, lang_if=lang)

    def import_testlib(self) -> None:
        """Add tags for import testlib."""
        self._add_import("std.generator.testlib.h.last", "generator")
        self._add_import("std.testlib.h.last", "checker")

    def set_checker(self, checker: "CheckerTag",
                    name: str = cfg.Names.checker.value, **kwargs) -> None:
        """Set Checker for problem."""
        self.checker = self._add_file("Checker", name,
                                      checker.path,
                                      checker.type,
                                      style="testlib", **kwargs)

    def use_interactor(self, interactor: "InteractorTag",
                       name: str = cfg.Names.interactor.value, **kwargs) -> None:
        """Use Interactor for problem."""
        self.run = self._set_run("interactive")
        self.interactor = self._add_file("Interactor", name,
                                         interactor.path, interactor.type, **kwargs)

    def add_generator(self, generator: "ExecutableTag", **kwargs) -> ET.Element:
        """Add Generator tag to cats xml."""
        if "name" not in kwargs:
            kwargs["name"] = file_name(generator.path)
        return self._add_file("Generator", path=generator.path,
                              compiler=generator.type, **kwargs)

    def add_solutions(self, solutions: list["SolutionTag"]) -> None:
        """Add Solution tags to cats xml."""
        sols = {}
        for sol in solutions:
            sols[sol.tag] = sols.get(sol.tag, [])
            sols[sol.tag].append(sol)

        for tag, solves in sols.items():
            if len(solves) == 1:
                self._add_file("Solution", f"{tag}", solves[0].path,
                               compiler=solves[0].type)
            else:
                for i, sol in enumerate(solves):
                    self._add_file("Solution", f"{tag}-{i + 1}",
                                   sol.path,
                                   compiler=sol.type)

    def add_picture(self, picture: "ResourceTag", **kwargs) -> ET.Element:
        """Add Picture tag to cats xml."""
        if "name" not in kwargs:
            kwargs["name"] = picture.path.name
        return self._add_file("Picture",
                              path=picture.path,
                              compiler=picture.type, **kwargs)

    def add_attachment(self, attachment: "ResourceTag", **kwargs) -> ET.Element:
        """Add Attachment tag to cats xml."""
        if "name" not in kwargs:
            kwargs["name"] = attachment.path.name
        return self._add_file("Attachment",
                              path=attachment.path,
                              compiler=attachment.type, **kwargs)

    def add_all_test_out(self, test_set: "TestSetTag") -> ET.Element:
        """Add Test Set tag to cats xml."""
        return self._add_test(out_kwargs={"use": "main"}, rank=cats_rank(int(test_set.test_count)))

    def add_test_in(self, rank: int, test: "TestTag", test_path: Path) -> ET.Element:
        """Add Test and Test/<In> to cats xml."""
        match test.method:
            case "generated":
                attribs = {"use": test.generator, "param": test.params}
                if test.points:
                    attribs["points"] = str(test.points)
                return self._add_test(rank=str(rank), in_kwargs=attribs)
            case "manual":
                attribs = {"src": (test_path / f"{rank:0>2}").as_posix()}
                if test.points is not None:
                    attribs["points"] = str(test.points)
                return self._add_test(rank=str(rank), in_kwargs=attribs)
            case _:
                raise ValueError(f"Test tag has not processed method: <{test.method}>")

    def add_group(self, group: "GroupTag", tests: str) -> ET.Element:
        """Add <Testset> to cats xml."""
        attrib = {"name": group.name, "tests": tests}
        if group.points is not None:
            attrib["points"] = str(group.points)
        if group.dependencies:
            attrib["dependencies"] = ",".join(group.dependencies)
        return ET.SubElement(self.problem, "Testset", attrib=attrib)

    def add_label(self, version: str = "0.2") -> None:
        self.cats.append(ET.Comment(f"This packet auto-generated by Baderik v{version}"))
        self.cats.append(ET.Comment(f"https://github.com/Baderik/polygon2cats"))

    def save(self, path: Path) -> None:
        with open(path, "wb") as out:
            ET.indent(self.cats)
            out.write(ET.tostring(self.cats, encoding="utf-8", xml_declaration=True))

    def add_resources(self, resources: list["ResourceTag"]) -> None:
        for res in resources:
            if res.is_picture:
                self.add_picture(res)
            else:
                self.add_attachment(res)

    def add_modules(self, modules: list["ResourceTag"]) -> None:
        services = {"files/olymp.sty", "files/problem.tex", "files/statements.ftl",
                    "files/testlib.h", "files/tutorial.tex"}
        for module in modules:
            if module.path.as_posix() in services:
                continue

            self._add_file("Module", module.path.name,
                           module.path,
                           compiler=module.type)


def _add_text(root: ET.Element, data: list[str], tag: str = "p") -> None:
    for txt in data:
        ET.SubElement(root, tag).text = txt


def _add_heading(root: ET.Element, txt: str, tag: str = "h3") -> None:
    ET.SubElement(root, tag).text = txt


def _add_txt_block(root: ET.Element, heading: str, data: list[str]) -> None:
    _add_heading(root, heading)
    _add_text(root, data)
