from pathlib import Path
from pydantic import BaseModel, AliasGenerator, AliasChoices, computed_field, field_validator

import config as cfg


__all__ = ["PolygonTag", "NameTag", "TexTag", "StatementTag", "TutorialTag", "TestTag", "GroupTag",
           "TestSetTag", "JudgingTag", "SourceTag", "ResourceTag", "ExecutableTag", "CheckerTag",
           "InteractorTag", "ValidatorTag", "SolutionTag", "Tag"]


def _hyphenize(field: str):
    return AliasChoices(field, field.replace("_", "-"))


class PolygonTag(BaseModel):
    class Config:
        alias_generator = AliasGenerator(None, _hyphenize, None)


class NameTag(PolygonTag):
    language: str
    value: str


class TexTag(PolygonTag):
    charset: str = None
    language: str
    mathjax: str = None
    path: Path
    type: str


class StatementTag(TexTag):
    pass


class TutorialTag(TexTag):
    pass


class TestTag(PolygonTag):
    method: str
    sample: bool = False
    cmd: str = None
    points: int = None
    description: str = None
    group: str = None

    @computed_field
    @property
    def generator(self) -> str:
        return self.cmd.split()[0]

    @computed_field
    @property
    def params(self) -> str:
        return " ".join(self.cmd.split()[1:])

    @computed_field
    @property
    def is_generated(self) -> bool:
        return self.method == "generated"


class GroupTag(PolygonTag):
    feedback_policy: str
    name: str
    points: int = None
    points_policy: str
    dependencies: list[str]


class TestSetTag(PolygonTag):
    name: str
    time_limit: int
    memory_limit: int
    test_count: int
    input_path_pattern: str
    output_path_pattern: str = None
    answer_path_pattern: str
    tests: list[TestTag] = []
    groups: list[GroupTag] = []


class JudgingTag(PolygonTag):
    cpu_name: str
    cpu_speed: int
    input_file: str
    output_file: str
    run_count: int
    test_sets: list[TestSetTag]


class SourceTag(PolygonTag):
    path: Path
    type: cfg.cats.Compiler | None

    @field_validator("type", mode="before")
    def choose_compiler(cls, value: str) -> cfg.cats.Compiler:
        if compiler := cfg.cats.compilers4languages.get(value.lower()):
            return compiler
        print(f"WARNING: compiler for type <{value}> not found")


class ResourceTag(SourceTag):
    type: cfg.cats.Compiler = None

    @computed_field
    @property
    def is_picture(self) -> bool:
        return (self.path.suffix.lower() in
                {".img", ".png", ".jpeg", ".jpg", ".gif", ".svg", ".webp"})


class ExecutableTag(SourceTag):
    pass


class CheckerTag(SourceTag):
    checkerType: str


class InteractorTag(SourceTag):
    pass


class ValidatorTag(SourceTag):
    pass


class SolutionTag(SourceTag):
    tag: str


class Tag(PolygonTag):
    value: str


if __name__ == '__main__':
    print(ResourceTag(**{'path': 'files/check.cpp'}))