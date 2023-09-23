from __future__ import annotations

from .tags import Tag, TagBase, union_of_supertypes, str_to_tag
from .labels import Label

from dataclasses import dataclass

Sentence = str


@dataclass(eq=True, unsafe_hash=True)
class Sample:
    premise:    Sentence
    hypothesis: Sentence
    tags:       set[Tag]
    labels:     set[Label]

    def to_json(self) -> dict:
        return {'premise': self.premise,
                'hypothesis': self.hypothesis,
                'tags': [repr(tag) for tag in self.tags],
                'labels': [label.value for label in self.labels]}

    @staticmethod
    def from_json(json: dict) -> Sample:
        return Sample(premise=json['premise'],
                      hypothesis=json['hypothesis'],
                      tags={str_to_tag(tag.split(':')[-1]) for tag in json['tags']},
                      labels={Label[label] for label in json['labels']})

    @property
    def all_tags(self) -> set[TagBase]: return union_of_supertypes(self.tags)


@dataclass
class Dataset:
    samples:      list[Sample]

    def to_json(self) -> dict:
        return {'samples': [sample.to_json() for sample in self.samples]}

    @staticmethod
    def from_json(json: dict) -> Dataset:
        return Dataset(samples=[Sample.from_json(sample) for sample in json['samples']])
