from sys import argv
from pathlib import Path
from shutil import unpack_archive, rmtree

import config
from parser.problem import Problem
from write import writer


if len(argv) > 1:
    file_path = Path(argv[1])
else:
    file_path = Path(input())

if not file_path.exists():
    raise AttributeError("Path doesn't exist.")

was_unpacked = False
original_file_path = file_path
if file_path.is_file() and file_path.suffix == ".zip":
    file_path = config.unpack_dir / file_path.stem
    unpack_archive(original_file_path, extract_dir=config.unpack_dir / file_path.name)
    was_unpacked = True
    print("archive unpacked")

elif not file_path.is_dir():
    raise AttributeError("Path for converter must be zip or dir of polygon package.")

problem = Problem(file_path / "problem.xml")
print(problem)

cats_xml = writer.create_xml(problem)
print(cats_xml)

writer.proc_statements(problem, cats_xml, file_path, config.result_dir)

cats_xml

if was_unpacked:
    rmtree(file_path)
    print("archive dir deleted")
