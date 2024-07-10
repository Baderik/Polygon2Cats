import logging
from sys import argv
from pathlib import Path
from shutil import unpack_archive, rmtree

import config as cfg
from parser.problem import Problem
from parser.services import get_properties

from writer.xmler import CatsXml
from writer.utils import *
from writer.files import Copier

if len(argv) > 1:
    file_path = Path(argv[1])
else:
    file_path = Path(input("Please, Enter path to polygon package dir or zip"))

if not file_path.exists():
    raise AttributeError(f"Path `{file_path}` doesn't exist")

logging.root.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s] %(message)s'))
logging.root.addHandler(handler)

logger = logging.getLogger("main")
logger.info(f"Started processing polygon package ({file_path})")
was_unpacked = False
original_file_path = file_path
if file_path.is_file() and file_path.suffix == ".zip":
    logger.debug("Package is archive")
    file_path = cfg.unpack_dir / file_path.stem
    unpack_archive(original_file_path, extract_dir=cfg.unpack_dir / file_path.name)
    was_unpacked = True
    logger.debug("Archive unpacked")

elif not file_path.is_dir():
    raise AttributeError("Path for converter must be |zip| or |dir| of polygon package")

problem = Problem(file_path / "problem.xml")
logger.debug("Parsed polygon/|problem.xml| ")

statements_properties = get_properties(problem)
logger.debug("Finished parse all polygon/.../|problem-properties.json|")

logger.info("Started to create cats.xml")
cats = CatsXml()

cats.set_title(problem, main_properties := choose_properties(statements_properties))
logger.debug("Set attributes for <Problem> tag of cats.xml")

cop = Copier(file_path, result_root := cfg.result_dir / problem.problem.attrib["short-name"])
logger.info(f"Created |Directory| for cats package ({result_root})")

# TODO: Add multy language resources
resources = cop.statement_resources(main_properties)
logger.debug("Copied |resource| files to cats package")
cats.add_resources(resources)
logger.debug("Added |Picture| and |Attachment| tags to cats.xml")

logger.debug("Started adding |problem-properties.json| to cats.xml")
st_count = len(statements_properties)
for i, st_properties in enumerate(statements_properties):
    cats.add_txt_by_properties(st_properties)
    logger.debug(f"Added |{st_properties.language}|/problem-properties.json "
                 f"({i + 1}/{st_count}) to cats.xml")
logger.debug("Finished adding |problem-properties.json| to cats.xml")

inp_path, ans_path = cop.samples(main_properties)
logger.debug("Copied |sample| files to cats package")
cats.add_samples_by_properties(main_properties,
                               use_file=True, local_in=inp_path, local_ans=ans_path)
logger.debug("Added |samples| to cats.xml")

cats.import_testlib()
logger.debug("Added import tags for use |testlib| to cats.xml")

cop.checker(problem.checker)
logger.debug("Copied |checker| file to cats package")
cats.set_checker(problem.checker)
logger.debug("Added |Checker| tag to cats.xml")

cop.solutions(problem.solutions)
logger.debug("Started adding |Solution| tag to cats.xml")
cats.add_solutions(problem.solutions)
logger.debug("Finished adding |Solution| tag to cats.xml")

if problem.is_interactive:
    logger.debug("Package is interactive")
    cop.interactor(problem.interactor)
    logger.debug("Copied |interactor| file to cats package")
    cats.use_interactor(problem.interactor)
    logger.debug("Added |Interactor| and |Run| tag to cats.xml")

# TODO: Need copy module files
# print("LOG: Copied |module| files to cats package")
cats.add_modules(problem.resources)
logger.debug("Added modules files")

logger.debug("Started adding |Generator| to cats.xml")
main_testset = choose_testset(problem.judging.test_sets)
generators = get_generators(problem.executables, main_testset.tests)
cop.generators(generators)
logger.debug("Copied |generator| files to cats package")
for generator in generators:
    cats.add_generator(generator)
logger.debug("Finished adding |Generator| tag to cats.xml")

logger.debug("Started adding |Test| to cats.xml")
tests_path = cop.tests()
logger.debug("Copied |test| files to cats package")
cats.add_all_test_out(main_testset)
for i, test in enumerate(main_testset.tests):
    cats.add_test_in(i + 1, test, tests_path)
logger.debug("Finished adding |Test| to cats.xml")

if main_testset.groups:
    groups = get_groups_tests(main_testset)
    for group in main_testset.groups:
        cats.add_group(group, groups[group.name])

else:
    logger.info("No groups found")

cats.add_label()
logger.debug("Added comments to xml")

if was_unpacked:
    rmtree(file_path)
    logger.info("Unpacked dir deleted")

result_path = cop.result / cfg.result_xml
cats.save(result_path)
logger.info(f"INFO: Finished processing polygon package. Save to {result_path}")
