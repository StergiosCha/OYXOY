from .dataset import Sample, Label
from .tags import Tag, Type, str_to_tag
from .annotators import Annotator

from random import sample as random_sample, seed

from typing import Iterator, Any


def read_tags(*lines: str) -> tuple[set[Type[Tag]], tuple[str, ...]]:
    index = lines.index('')
    tags = {str_to_tag(tag.split('::')[0]) for tag in lines[:index]}
    rest = lines[index+1:]
    return tags, rest


def parse_lines(*lines: str, author: Annotator) -> Iterator[Sample]:
    if not lines:
        return
    premise, hypothesis, labels, *rest = lines
    try:
        tags, rest = read_tags(*rest)

        yield Sample(premise=premise,
                     hypothesis=hypothesis,
                     author=author,
                     validators=set(),
                     tags=tags,
                     labels={Label(label.split('::')[0]) for label in labels.split(', ')})
    except Exception as e:
        print(premise, hypothesis)
        raise e
    yield from parse_lines(*rest, author=author)


def parse_file(path: str, author: Annotator):
    print(f'Parsing {path}')
    with open(path, 'r') as f:
        return parse_lines(*f.read().split('\n'), author=author)


def assign_annotators(sample: Sample, k: int, excluding: Annotator) -> Sample:
    candidates = tuple(annotator for annotator in Annotator.__members__.values() if annotator != excluding)
    validators = set(random_sample(candidates, k))
    return Sample(premise=sample.premise,
                  hypothesis=sample.hypothesis,
                  tags=set(),
                  labels=set(),
                  author=sample.author,
                  validators=validators)


def assign_annotators_many(samples: list[Sample]) -> list[Sample]:
    seed(1312)
    return [assign_annotators(s, 3, s.author) for s in samples]


def print_for_validation(sample: Sample) -> str:
    return f'{sample.premise}\n{sample.hypothesis}\n'


def print_many_for_validation(samples: list[Sample]) -> str:
    return '\n'.join(print_for_validation(sample) for sample in samples)


def aggregate(authored_samples: list[Sample], val_lists: tuple[list[Sample], ...]) -> list[Sample]:
    def match(s1: Sample, s2: Sample) -> bool:
        return s1.premise == s2.premise and s1.hypothesis == s2.hypothesis

    return [vote(original=original,
                 validated=validators)
            for original in authored_samples
            if (validators := [val for val_list in val_lists for val in val_list if match(original, val)])]


def vote(original: Sample, validated: list[Sample]) -> Sample:
    author = original.author
    validators = {validated.author for validated in validated}
    tags = [tag for sample in [original, *validated] for tag in sample.tags]
    labels = [label for sample in [original, *validated] for label in sample.labels]
    tag_counts = {tag: (tags.count(tag), (len(validators) + 1)) for tag in set(tags)}
    label_counts = {label: (labels.count(label), (len(validators) + 1)) for label in set(labels)}
    return Sample(author=author,
                  validators=validators,
                  hypothesis=original.hypothesis,
                  premise=original.premise,
                  labels=label_counts,
                  tags=tag_counts)


def show_aggregates(samples: list[Sample]) -> str:
    def show_one(sample: Sample) -> str:
        labels = sorted(sample.labels.items(), key=lambda key: key[1][0], reverse=True)
        tags = sorted(sample.tags.items(), key=lambda key: key[1][0], reverse=True)
        lstr = ', '.join(f'{k.value}::{v[0]}/{v[1]}' for k, v in labels)
        tstr = '\n'.join(f'{repr(k).split(":")[-1]}::{v[0]}/{v[1]}' for k, v in tags)
        return f'{sample.premise}\n{sample.hypothesis}\n{lstr}\n{tstr}\n'
    return '\n'.join(show_one(s) for s in samples)

