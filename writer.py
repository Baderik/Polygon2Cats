from lxml import etree
from pathlib import Path
from shutil import copy

from parser.problem import Problem, Solution, Checker
from parser.statement import Statement
from parser.example import copy_examples

problem_path = Path("polygon/strange-world-10/")
cats_path = Path("cats/test")


def import_testlib(parent: etree.ElementTree, t: str):
    etree.SubElement(parent, "Import", {"type": t, "guid": "std.testlib.h.last"})


def add_solution(problem_node: etree.ElementTree, sol: Solution, sol_dir: str = "solutions"):
    copy(problem_path / sol.path, cats_path / sol_dir)
    etree.SubElement(problem_node, "Solution", {
        "name": sol.tag,
        "src": f'{Path(sol_dir) / Path(sol.path).name}'
    })


def add_generators(problem_node: etree.ElementTree, gens, gen_dir: str = "generators"):
    for f in (problem_path / "files").iterdir():
        if f.suffix == ".exe" or not f.suffix:
            continue
        if f.stem in gens:
            copy(f, cats_path / gen_dir)
            etree.SubElement(problem_node, "Generator", {
                "name": f.stem,
                "src": f'{Path(gen_dir) / f.name}'
            })

def add_checker(problem_node: etree.ElementTree, check: Checker):
    kwargs = {}
    if check.is_testlib:
        kwargs["style"] = "testlib"
        import_testlib(problem, "checker")
    kwargs["src"] = check.path
    kwargs["name"] = "check"
    etree.SubElement(problem_node, "Checker", kwargs)


def gen_rank(n: int) -> str:
    if n:
        if n == 1:
            return "1"
        else:
            return f"1-{n}"


def copy_tests(tests_dir: str = "tests"):
    for t in (problem_path / "tests").iterdir():
        copy(t, cats_path / tests_dir / f"{t.stem}.in" )

# problem_path = Path("polygon/example-a-plus-b-11/")

p = Problem(problem_path / "problem.xml")
sol = "main"
# create the file structure
cats = etree.Element('CATS', {"version": "1.11"})
problem = etree.SubElement(cats, "Problem",
                           {
                               "title": p.names[0].value,
                               "lang": ",".join(map(lambda el: el.language, p.names)),
                               "tlimit": str(int(p.limits.tl) // 1000),
                               "mlimit": str(int(p.limits.ml) // 1024 // 1024) + "M",
                               "inputFile": p.io.input if p.io.input else "*STDIN",
                               "outputFile": p.io.output if p.io.output else "*STDOUT"
                           })

samples_count = 0
for s in p.statements:
    st = Statement(problem_path / "statement-sections" / s.language, encoding=s.charset)
    samples_count = st.count
    if st.legend:
        st_node = etree.SubElement(problem, "ProblemStatement", {"cats_if": f"lang={s.language}"})
        for el in st.legend.splitlines():
            etree.SubElement(st_node, "p").text = el
    if st.input:
        in_f = etree.SubElement(problem, "InputFormat", {"cats_if": f"lang={s.language}"})
        for el in st.input.splitlines():
            etree.SubElement(in_f, "p").text = el
    if st.output:
        out_f = etree.SubElement(problem, "OutputFormat", {"cats_if": f"lang={s.language}"})
        for el in st.output.splitlines():
            etree.SubElement(out_f, "p").text = el
    if st.tutorial:
        exp = etree.SubElement(problem, "Explanation", {"cats_if": f"lang={s.language}"})
        for el in st.output.splitlines():
            etree.SubElement(exp, "p").text = el


copy_examples(samples_count, problem_path / "statement-sections" / p.names[0].language, cats_path)
samp = etree.SubElement(problem, "Sample", {"rank": gen_rank(samples_count)})
etree.SubElement(samp, "SampleIn", {"src": "samples/example.%0n"})
etree.SubElement(samp, "SampleOUt", {"src": "samples/example.%0n.a"})


import_testlib(problem, "generator")
add_checker(problem, p.checker)
for s in p.solutions:
    add_solution(problem, s)


copy_tests()
manual_count = sum(map(lambda el: el.method == "manual", p.tests))
manual_tests = etree.SubElement(problem, "Test", {
    "rank": gen_rank(manual_count)
})
manual_tests_in = etree.SubElement(manual_tests, "In", {"src": "tests/%0n.in"})
manual_tests_out = etree.SubElement(manual_tests, "Out", {"use": sol})

generators = []
for t_i in range(len(p.tests)):
    if p.tests[t_i].method == "manual":
        continue
    test = etree.SubElement(problem, "Test", {"rank": str(t_i + 1)})
    g, *params = p.tests[t_i].arguments.split(" ")
    generators.append(g)
    etree.SubElement(test, "In", {"param": " ".join(params), "use": g})
    etree.SubElement(test, "Out", {"use": sol})

add_generators(problem, generators)

with open(cats_path / "task.xml", "w", encoding="utf-8") as out:
    print(etree.tostring(cats, pretty_print=True, encoding="unicode"), file=out)
