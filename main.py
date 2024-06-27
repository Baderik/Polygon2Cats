from sys import argv
from pathlib import Path
from shutil import unpack_archive, rmtree

import config as cfg
from parser.problem import Problem
from parser.services import get_properties

from writer.xml import CatsXml
from writer.utils import *

if len(argv) > 1:
    file_path = Path(argv[1])
else:
    file_path = Path(input("Please, Enter path to polygon package dir or zip"))

if not file_path.exists():
    raise AttributeError(f"Path `{file_path}` doesn't exist")

print("INFO: Started processing polygon package")
was_unpacked = False
original_file_path = file_path
if file_path.is_file() and file_path.suffix == ".zip":
    print("LOG: Package is archive")
    file_path = cfg.main.unpack_dir / file_path.stem
    unpack_archive(original_file_path, extract_dir=cfg.main.unpack_dir / file_path.name)
    was_unpacked = True
    print("LOG: Archive unpacked")

elif not file_path.is_dir():
    raise AttributeError("Path for converter must be |zip| or |dir| of polygon package")

problem = Problem(file_path / "problem.xml")
print("LOG: Parsed |problem.xml| of polygon package")

statements_properties = get_properties(problem)
print("LOG: Parsed |problem-properties.json| of polygon package")

cats = CatsXml()
print("LOG: Started to create cats.xml")

main_properties = choose_properties(statements_properties)
cats.set_title(problem, main_properties)
print("LOG: Set attributes for <Problem> tag of cats.xml")

print("LOG: Started adding |problem-properties.json| to cats.xml")
st_count = len(statements_properties)
for i, st_properties in enumerate(statements_properties):
    cats.add_txt_by_properties(st_properties)
    print(f"LOG: Added |{st_properties.language}|/problem-properties.json "
          f"({i + 1}/{st_count}) to cats.xml")

print("LOG: Finished adding |problem-properties.json| to cats.xml")

cats.add_samples_by_properties(main_properties)
print("LOG: Added |samples| for cats.xml from |problem-properties.json|")

cats.import_testlib()
print("LOG: Added import tags for use |testlib| to cats.xml")

cats.set_checker(problem.checker)
print("LOG: Added |Checker| tag to cats.xml")

print("LOG: Started adding |Solution| tag to cats.xml")
cats.add_solutions(problem.solutions)
print("LOG: Finished adding |Solution| tag to cats.xml")

if problem.is_interactive:
    cats.use_interactor(problem.interactor)
    print("LOG: Added |Interactor| and |Run| tag to cats.xml")

cats.add_resources(problem.resources)
print("LOG: Added resources files")

print("LOG: Started adding |Generator| tag to cats.xml")
main_testset = choose_testset(problem.judging.test_sets)
generators = get_generators(problem.executables, main_testset.tests)

for generator in generators:
    cats.add_generator(generator)
print("LOG: Finished adding |Generator| tag to cats.xml")

print("LOG: Started adding |Test| tag to cats.xml")
cats.add_all_test_out(main_testset)
for i, test in enumerate(main_testset.tests):
    cats.add_test_in(i + 1, test)
print("LOG: Finished adding |Test| tag to cats.xml")

if main_testset.groups:
    groups = get_groups_tests(main_testset)
    for group in main_testset.groups:
        cats.add_group(group, groups[group.name])

else:
    print("LOG: No groups found")

cats.add_label()
print("LOG: Added comments to xml")

if was_unpacked:
    rmtree(file_path)
    print("LOG: Archive dir deleted")

result_path = cfg.main.result_dir / cfg.main.result_xml
cats.save(result_path)
print(f"INFO: Finished processing polygon package. Save to {result_path}")
