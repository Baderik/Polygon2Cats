from lxml import etree
from pathlib import Path

from parser.problem import Problem
from parser.statement import Statement

problem_path = Path("polygon/example-a-plus-b-11/")
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

for s in p.statements:
    st = Statement(problem_path / "statement-sections" / s.language, encoding=s.charset)
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


manual_count = sum(map(lambda el: el.method == "manual", p.tests))
if manual_count:
    if manual_count == 1:
        manual_count = "1"
    else:
        manual_count = f"1-{manual_count}"
manual_tests = etree.SubElement(problem, "Test", {
    "rank": manual_count
})
manual_tests_in = etree.SubElement(manual_tests, "In", {"src": "%0n.in"})
manual_tests_out = etree.SubElement(manual_tests, "Out", {"use": sol})

for t_i in range(len(p.tests)):
    if p.tests[t_i].method == "manual":
        continue
    test = etree.SubElement(problem, "Test", {"rank": str(t_i + 1)})
    g, *params = p.tests[t_i].arguments.split(" ")
    etree.SubElement(test, "In", {"param": " ".join(params), "use": g})
    etree.SubElement(test, "Out", {"use": sol})

print(etree.tostring(cats, pretty_print=True, encoding="unicode"))
