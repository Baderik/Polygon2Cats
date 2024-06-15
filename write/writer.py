from lxml import etree
from lxml.etree import _Element

from pathlib import Path
import typing

from parser.statement import Statement, parse_properties, StatementProperties
from write.utils import *

if typing.TYPE_CHECKING:
    from parser.problem import Problem, TestNode


def create_xml(
        problem_data: "Problem",
        cats_version: str = "1.11",
        input_prefix="50B",
        output_prefix="50B",
        answer_prefix="50B") \
        -> _Element:
    cats = etree.Element('CATS', {"version": cats_version})

    problem = etree.SubElement(cats, "Problem",
                               {
                                   "title": problem_data.names[0].value,
                                   "lang": cats_languages(problem_data.names),
                                   "tlimit": str(int(problem_data.limits.time_limit) / 1000),
                                   "mlimit": problem_data.limits.memory_limit + "B",
                                   "inputFile": problem_data.io.input_file,
                                   "outputFile": problem_data.io.output_file,
                                   "saveInputPrefix": input_prefix,
                                   "saveOutputPrefix": output_prefix,
                                   "saveAnswerPrefix": answer_prefix
                               })
    return problem


def add_samples_files(
        problem_xml: _Element,
        samples_count: int)\
        -> None:
    if samples_count:
        sample_xml = etree.SubElement(problem_xml, "Sample", {"rank": cats_rank(samples_count)})
        etree.SubElement(sample_xml, "SampleIn", {"src": "samples/example.%0n"})
        etree.SubElement(sample_xml, "SampleOut", {"src": "samples/example.%0n.a"})


def add_samples_from_properties(
        problem_xml: _Element,
        properties: StatementProperties)\
        -> None:
    for i, s_test in enumerate(properties.sampleTests):
        sample_xml = etree.SubElement(problem_xml, "Sample",
                                      {"rank": cats_rank(i + 1, i + 1)})
        etree.SubElement(sample_xml, "SampleIn").text = s_test.input
        etree.SubElement(sample_xml, "SampleOut").text = s_test.output


def proc_statements(
        problem_data: "Problem",
        cats_xml: _Element,
        polygon_root: Path,
        cats_root: Path,
        use_properties_file: bool = False)\
        -> None:
    samples_added = False
    for statement_node in problem_data.statements:
        if use_properties_file:
            statement_properties = parse_properties(
                polygon_root / "statements" / statement_node.language,
                encoding=statement_node.charset)
            if not samples_added:
                samples_added = True
                add_samples_from_properties(cats_xml, statement_properties)

        else:
            statement_data = Statement(polygon_root / "statement-sections" / statement_node.language,
                                       encoding=statement_node.charset)
            if not samples_added:
                samples_added = True
                copy_examples_files(statement_data.example_count, polygon_root, cats_root)
                add_samples_files(cats_xml, statement_data.example_count)


def add_import(problem_xml: _Element, guid: str, type_import: str) -> None:
    """Add a import tag formatted CATS xml."""
    etree.SubElement(problem_xml, "Import", {"guid": guid, "type": type_import})


def add_import_testlib(problem_xml: _Element) -> None:
    """Add tags for testlib."""
    add_import(problem_xml, "std.generator.testlib.h.last", "generator")
    add_import(problem_xml, "std.testlib.h.last", "checker")


def add_test(
        cats_xml: _Element,
        index: int,
        test: "TestNode",
        test_src: str = "tests/%0n.in")\
        -> _Element:
    rank = cats_rank(index, index)
    attribs = {"rank": rank}
    if test.points:
        attribs["points"] = test.points
    t = etree.SubElement(cats_xml, "Test", attribs)

    if test.method == "manual":
        etree.SubElement(t, "In", {"src": test_src})
    elif test.method == "generated":
        generator = test.cmd.split()[0]
        etree.SubElement(t, "In", {"use": generator, "param": test.cmd.lstrip(generator)})
    etree.SubElement(t, "Out", {"use": "main"})
    return t


def proc_tests(
        problem_data: "Problem",
        cats_xml: _Element,
        polygon_root: Path,
        cats_root: Path)\
        -> None:
    for i, test in enumerate(problem_data.tests):
        add_test(cats_xml, i, test)
    copy_tests_files(polygon_root, cats_root)
