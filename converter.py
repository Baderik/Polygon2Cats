from sys import argv
from pathlib import Path
from shutil import unpack_archive, rmtree

import config
from parser.problem import Problem
file_path = Path(argv[1])

if not file_path.exists():
    raise AttributeError("Path doesn't exist.")

was_unpacked = False
if file_path.is_file() and file_path.suffix == ".zip":
    unpack_archive(file_path, extract_dir=config.unpack_dir)
    was_unpacked = True

elif not file_path.is_dir():
    raise AttributeError("Path for converter must be zip or dir of polygon package.")

problem = Problem(file_path / "problem.xml")




if was_unpacked:
    rmtree(config.unpack_dir)
