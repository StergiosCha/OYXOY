from .dataset import Sample, Label
from .tags import Tag, Type, str_to_tag
from .annotators import Annotator

from random import sample

from typing import Iterator


def read_tags(*lines: str) -> tuple[set[Type[Tag]], tuple[str, ...]]:
    index = lines.index('')
    tags = {str_to_tag(tag) for tag in lines[:index]}
    rest = lines[index+1:]
    return tags, rest


def parse_lines(*lines: str, author: Annotator) -> Iterator[Sample]:
    if not lines:
        return
    premise, hypothesis, labels, *rest = lines
    tags, rest = read_tags(*rest)

    yield Sample(premise=premise,
                 hypothesis=hypothesis,
                 author=author,
                 validators=set(),
                 tags=tags,
                 labels={Label(label) for label in labels.split(', ')})
    yield from parse_lines(*rest, author=author)


def parse_file(path: str, author: Annotator):
    with open(path, 'r') as f:
        return parse_lines(*f.read().split('\n'), author=author)


def assign_annotators(k: int, excluding: Annotator) -> set[Annotator]:
    candidates = tuple(annotator for annotator in Annotator.__members__.values() if annotator != excluding)
    return set(sample(candidates, k))
