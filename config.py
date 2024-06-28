from enum import Enum
from pathlib import Path

result_dir = Path("cats/")
result_dir.mkdir(parents=True, exist_ok=True)
unpack_dir = Path("polygon/")
result_xml = Path("problem.xml")


class Compiler(Enum):
    none = 1
    answer = 3
    gnu_cpp11 = 102
    ms_cpp15 = 103
    gnu_c11 = 105
    rust = 120
    free_pascal = 202
    free_pascal_delphi = 204
    pascal_abc = 205
    java8 = 401
    ms_csharp15 = 402
    java_testlib = 403
    go = 404
    kotlin = 406
    perl5 = 501
    python3 = 502
    haskell = 503
    ruby2 = 504
    php7 = 505
    pypy3 = 510
    r = 511

    @classmethod
    def _missing_(cls, value):
        return cls.none


compilers4languages = {
    "c.gcc": Compiler.gnu_c11,
    "cpp.g++": Compiler.gnu_cpp11,
    "cpp.g++11": Compiler.gnu_cpp11,
    "cpp.g++14": Compiler.gnu_cpp11,
    "cpp.g++17": Compiler.gnu_cpp11,
    "cpp.gcc11-64-winlibs-g++20": Compiler.gnu_cpp11,
    "cpp.ms2017": Compiler.ms_cpp15,
    "cpp.msys2-mingw64-9-g++17": Compiler.ms_cpp15,
    "csharp.mono": Compiler.ms_csharp15,
    "d": Compiler.none,
    "go": Compiler.go,
    "java11": Compiler.java8,
    "java8": Compiler.java8,
    "kotlin": Compiler.kotlin,
    "kotlin16": Compiler.kotlin,
    "kotlin17": Compiler.kotlin,
    "kotlin19": Compiler.kotlin,
    "ocaml": Compiler.none,
    "pas.dpr": Compiler.free_pascal_delphi,
    "pas.fpc": Compiler.free_pascal,
    "perl.5": Compiler.perl5,
    "php.5": Compiler.php7,
    "python.2": Compiler.python3,
    "python.3": Compiler.python3,
    "python.pypy2": Compiler.pypy3,
    "python.pypy3": Compiler.pypy3,
    "ruby.2": Compiler.ruby2,
    "rust": Compiler.rust,
    "scala": Compiler.none,
    "h.g++": Compiler.none
}


headings = {"notes": {"ru": "Примечание", "en": "Notes"},
            "interaction": {"ru": "Протокол взаимодействия", "en": "Interaction"}}


class Names(Enum):
    interactor = "interactor"
    checker = "check"


class Properties(Enum):
    saveInputPrefix = "255B"
    saveOutputPrefix = "255B"
    saveAnswerPrefix = "255B"


# logger = logging.getLogger("Polygon2Cats")
