# TODO: Add code of files for cats tags
# TODO: Add processing points
from lxml import etree
from pathlib import Path
from shutil import copy

from parser.problem import Problem, Solution, Checker
from parser.statement import Statement
from parser.example import copy_examples

dir_name = "strange-matrix"
problem_path = Path("polygon/") / dir_name
cats_path = Path("cats/") / dir_name
cats_path.mkdir(parents=True, exist_ok=True)


def import_testlib(parent: etree.ElementTree, t: str):
    testlibs = {"checker": "std.testlib.h.last",
                "generator": "std.generator.testlib.h.last"}
    etree.SubElement(parent, "Import", {"type": t, "guid": testlibs[t]})


def add_solution(problem_node: etree.ElementTree, sol: Solution, sol_dir: str = "solutions"):
    (cats_path / sol_dir).mkdir(exist_ok=True)
    copy(problem_path / sol.path, cats_path / sol_dir)
    etree.SubElement(problem_node, "Solution", {
        "name": sol.tag,
        "src": (Path(sol_dir) / Path(sol.path).name).as_posix()
    })


def add_generators(problem_node: etree.ElementTree, gens, gen_dir: str = "generators"):
    (cats_path / gen_dir).mkdir(exist_ok=True)
    checker_index = -1
    if gens:
        for i in range(len(problem_node)):
            if problem_node[i].tag == "Checker":
                checker_index = i + 1
    for f in (problem_path / "files").iterdir():
        if f.suffix == ".exe" or not f.suffix:
            continue
        if f.stem in gens:
            copy(f, cats_path / gen_dir)
            g = etree.Element("Generator", {
                "name": f.stem,
                "src": (Path(gen_dir) / f.name).as_posix()
            })
            problem_node.insert(checker_index, g)
            checker_index += 1


def add_checker(problem_node: etree.ElementTree, check: Checker):
    kwargs = {"name": "check", "src": Path(check.path).name}
    if check.is_testlib:
        kwargs["style"] = "testlib"
        import_testlib(problem, "checker")
    copy(problem_path / check.path, cats_path)

    etree.SubElement(problem_node, "Checker", kwargs)


def gen_rank(n: int) -> str:
    if n:
        if n == 1:
            return "1"
        else:
            return f"1-{n}"


def copy_tests(tests_dir: str = "tests"):
    (cats_path / tests_dir).mkdir(exist_ok=True)
    for t in (problem_path / "tests").iterdir():
        # TODO: Fix the moment when there are files with answers in the tests folder
        copy(t, cats_path / tests_dir / f"{t.stem}.in")


def cats_lang(language: str) -> str:
    return language[:2]


def add_tex(parent_node: etree.ElementTree, txt: str) -> None:
    for line in txt.splitlines():
        if line:
            etree.SubElement(parent_node, "p").text = line


p = Problem(problem_path / "problem.xml")
sol = "main"
# create the file structure
cats = etree.Element('CATS', {"version": "1.11"})
problem = etree.SubElement(cats, "Problem",
                           {
                               "title": p.names[0].value,
                               "lang": ",".join(map(lambda el: cats_lang(el.language), p.names)),
                               "tlimit": str(int(p.limits.tl) // 1000),
                               "mlimit": str(int(p.limits.ml) // 1024 // 1024) + "M",
                               "inputFile": p.io.input if p.io.input else "*STDIN",
                               "outputFile": p.io.output if p.io.output else "*STDOUT",
                               "saveInputPrefix": "50B",
                               "saveOutputPrefix": "50B",
                               "saveAnswerPrefix": "50B"
                           })

samples_count = 0
for s in p.statements:
    st = Statement(problem_path / "statement-sections" / s.language, encoding=s.charset)
    samples_count = st.count
    if st.legend:
        st_node = etree.SubElement(problem, "ProblemStatement",
                                   {"cats_if": f"lang={cats_lang(s.language)}"})
        add_tex(st_node, st.legend)
    if st.input:
        in_f = etree.SubElement(problem, "InputFormat",
                                {"cats_if": f"lang={cats_lang(s.language)}"})
        add_tex(in_f, st.input)
    if st.output:
        out_f = etree.SubElement(problem, "OutputFormat",
                                 {"cats_if": f"lang={cats_lang(s.language)}"})
        add_tex(out_f, st.output)
    if st.tutorial:
        exp = etree.SubElement(problem, "Explanation",
                               {"cats_if": f"lang={cats_lang(s.language)}"})
        add_tex(exp, st.tutorial)


copy_examples(samples_count, problem_path / "statement-sections" / p.names[0].language, cats_path)
if samples_count:
    samp = etree.SubElement(problem, "Sample", {"rank": gen_rank(samples_count)})
    etree.SubElement(samp, "SampleIn", {"src": "samples/example.%0n"})
    etree.SubElement(samp, "SampleOut", {"src": "samples/example.%0n.a"})


import_testlib(problem, "generator")
add_checker(problem, p.checker)


def add_solutions(problem_node: etree.Element, solutions: list[Solution], sol_dir: str = "solutions"):
    (cats_path / sol_dir).mkdir(exist_ok=True)
    tags = {}
    for sol in solutions:
        copy(problem_path / sol.path, cats_path / sol_dir)
        tags[sol.tag] = tags.get(sol.tag, [])
        tags[sol.tag].append(sol)

    for tag, sols in tags.items():
        if len(sols) == 1:
            etree.SubElement(problem_node, "Solution", {
                "name": tag,
                "src": (Path(sol_dir) / Path(sols[0].path).name).as_posix()
            })
        else:
            for i in range(len(sols)):
                etree.SubElement(problem_node, "Solution", {
                    "name": f"{tag}-{i + 1}",
                    "src": (Path(sol_dir) / Path(sols[i].path).name).as_posix()
                })


add_solutions(problem, p.solutions)


copy_tests()
manual_count = sum(map(lambda el: el.method == "manual", p.tests))
if manual_count:
    manual_tests = etree.SubElement(problem, "Test", {
        "rank": gen_rank(manual_count)
    })
    manual_tests_in = etree.SubElement(manual_tests, "In", {"src": "tests/%0n.in"})

generators = []
groups = {}
for t_i in range(len(p.tests)):
    if p.tests[t_i].method == "manual":
        continue
    test = etree.SubElement(problem, "Test", {"rank": str(t_i + 1)})
    g, *params = p.tests[t_i].arguments.split(" ")
    generators.append(g)
    etree.SubElement(test, "In", {"param": " ".join(params), "use": g})
if len(p.tests) == 1:
    test = etree.SubElement(problem, "Test", {"rank": str(1)})
else:
    test = etree.SubElement(problem, "Test", {"rank": f"1-{len(p.tests)}"})
    etree.SubElement(test, "Out", {"use": sol})
add_generators(problem, generators)

cats.append(etree.Comment("This packet auto-generated by Baderik v0.1"))
with open(cats_path / "task.xml", "wb") as out:
    out.write(etree.tostring(cats, pretty_print=True, xml_declaration=True, encoding="UTF-8"))
