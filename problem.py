from collections import namedtuple
import xml.etree.ElementTree as ET


ProblemName = namedtuple("ProblemName", ["language", "value"])
StatementNode = namedtuple("StatementNode",
                           ["charset", "language", "mathjax", "path", "type"])


def parse_names(names_node: ET.Element) -> list[ProblemName]:
    """Parse <names> node from problem.xml"""
    return [ProblemName(**name.attrib) for name in names_node]


def parse_statements(statements_node: ET.Element) -> list[StatementNode]:
    """Parse <statements> node from problem.txt"""
    return [StatementNode(**statement.attrib)
            for statement in statements_node
            if statement.attrib["type"] == "application/x-tex"]
