from pathlib import Path
from dataclasses import dataclass, field as dtField
import config as cfg

__all__ = ["PolygonTag", "NameTag", "TexTag", "StatementTag", "TutorialTag", "TestTag", "GroupTag",
           "TestSetTag", "JudgingTag", "SourceTag", "ResourceTag", "ExecutableTag", "CheckerTag",
           "InteractorTag", "ValidatorTag", "SolutionTag", "Tag"]


# TODO: Add types validation


@dataclass
class PolygonTag:
    pass


@dataclass
class NameTag(PolygonTag):
    language: str
    value: str


@dataclass
class TexTag(PolygonTag):
    language: str
    path: Path
    type: str
    charset: str = None
    mathjax: str = None

    def __post_init__(self):
        self.path = Path(self.path)


@dataclass
class StatementTag(TexTag):
    pass


@dataclass
class TutorialTag(TexTag):
    pass


@dataclass
class TestTag(PolygonTag):
    method: str
    sample: bool = False
    cmd: str = None
    points: int = None
    description: str = None
    group: str = None
    from_file: str = None
    generator: str = dtField(init=False)
    params: str = dtField(init=False)
    is_generated: bool = dtField(init=False)

    def __post_init__(self):
        self.sample = self.sample == "true"
        self.generator = self.cmd.split()[0] if self.cmd else None
        self.params = " ".join(self.cmd.split()[1:]) if self.cmd else None
        self.is_generated = self.method == "generated"


@dataclass
class GroupTag(PolygonTag):
    feedback_policy: str
    name: str
    points_policy: str
    dependencies: list[str]
    points: int = None


@dataclass
class TestSetTag(PolygonTag):
    name: str
    time_limit: int
    memory_limit: int
    test_count: int
    input_path_pattern: str
    answer_path_pattern: str
    output_path_pattern: str = None
    tests: list[TestTag] = dtField(default_factory=list)
    groups: list[GroupTag] = dtField(default_factory=list)


@dataclass
class JudgingTag(PolygonTag):
    cpu_name: str
    cpu_speed: int
    input_file: str
    output_file: str
    run_count: int
    test_sets: list[TestSetTag]


@dataclass
class SourceTag(PolygonTag):
    path: Path
    type: cfg.Compiler

    def __post_init__(self):
        self.path = Path(self.path)
        if self.type is None:
            pass
        elif compiler := cfg.compilers4languages.get(self.type.lower()):
            self.type = compiler
        else:
            print(f"WARNING: compiler for type <{self.type}> not found")
            self.type = None


@dataclass
class ResourceTag(SourceTag):
    type: cfg.Compiler | None = None
    is_picture: bool = dtField(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.is_picture = (self.path.suffix.lower() in
                           {".img", ".png", ".jpeg", ".jpg", ".gif", ".svg", ".webp"})


@dataclass
class ExecutableTag(SourceTag):
    pass


@dataclass
class CheckerTag(SourceTag):
    checkerType: str


@dataclass
class InteractorTag(SourceTag):
    pass


@dataclass
class ValidatorTag(SourceTag):
    pass


@dataclass
class SolutionTag(SourceTag):
    tag: str


@dataclass
class Tag(PolygonTag):
    value: str
