import typing
from pathlib import Path

__all__ = ["cats_rank", "names2languages", "proc_text", "cats_lang", "choose_name", "choose_properties", "choose_testset", "file_name", "str_format2cats", "get_generators", "get_groups_tests"]

if typing.TYPE_CHECKING:
    from parser.models import *
    from parser.statement import StatementProperties


def cats_rank(start: int, end: int = None) -> str:
    """Return the rank formatted according to CATS xml."""
    if end is None:
        end = start
        start = 1

    if end - start == 0:
        return str(start)
    else:
        return f"{start}-{end}"


def cats_lang(full_lang: str) -> str:
    """Return the full language formatted according to CATS xml."""
    return full_lang[:2]


def names2languages(names: list["NameTag"]) -> str:
    """Return the language title formatted according to CATS xml."""
    def one(node: "NameTag") -> str:
        return cats_lang(node.language)
    return ",".join(map(one, names))


def proc_text(txt: str) -> list[str]:
    """Process text from Polygon Tex format to list of paragraphs."""
    if not txt:
        return []
    txt = txt.splitlines()
    txt.append("")
    res = []
    temp = ""
    for el in txt:
        if el:
            temp += el
        elif temp:
            res.append(temp)
            temp = ""
    return res


def choose_name(names: list["NameTag"]) -> "NameTag":
    """Choose the name of polygon's names list."""
    return names[0]


def choose_properties(properties: list["StatementProperties"]) -> "StatementProperties":
    """Choose the properties of polygon's properties list."""
    return properties[0]


def choose_testset(testsets: list["TestSetTag"]) -> "TestSetTag":
    """Choose the test set of polygon's test sets list."""
    return testsets[0]


def file_name(path: Path) -> str:
    """Return the file name of a file without extension."""
    return path.name.rstrip(path.suffix)


def str_format2cats(data: str) -> str:
    """Convert formatting string to CATS context variables."""
    return data.replace("%02d", "%0n")


def get_generators(resources: list["ExecutableTag"],
                   tests: list["TestTag"]) -> list["ExecutableTag"]:
    """Filter and get generator resource tag."""
    generator_names = set()
    for t in tests:
        if t.is_generated:
            generator_names.add(t.generator)

    return [r for r in resources if file_name(r.path) in generator_names]


def get_groups_tests(test_set: "TestSetTag"):
    def proc_group(name: str, tests: list[int]) -> str:
        if len(tests) == 1:
            return str(*(t for t in tests))
        first = delta = last = None
        for t in tests:
            if first is None:
                first = t
            elif delta is None:
                delta = t - last
            else:
                if t - last != delta:
                    raise ValueError(f"Test group<{name}> cannot be added. "
                                     f"Impossible to set all the tests {tests}")
            last = t
        if delta == 1:
            return f"{first}-{last}"
        return f"{first}-{last}-{delta}"
    groups = {g.name: set() for g in test_set.groups}
    for i, test in enumerate(test_set.tests):
        groups[test.group].add(i + 1)

    return {k: proc_group(k, sorted(g)) for k, g in groups.items()}
