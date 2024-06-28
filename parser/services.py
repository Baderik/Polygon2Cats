from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from parser.problem import Problem
    from parser.statement import StatementProperties

from parser.statement import from_file_properties

__all__ = ["get_properties"]


def get_properties(problem: "Problem") -> list["StatementProperties"]:
    return [from_file_properties(
        statement_tag.path.parent / "problem-properties.json",
        statement_tag.charset, root_dir=problem.path.parent)
            for statement_tag in problem.statements if statement_tag.type == "application/x-tex"]
