from __future__ import annotations

from .annotators import Annotator
from .tags import Tag, TagBase, union_of_supertypes, str_to_tag

from typing import Literal, Type
from dataclasses import dataclass

Sentence = str
Label = Literal['Entailment', 'Unknown', 'Contradiction']


@dataclass(eq=True, unsafe_hash=True)
class Sample:
    premise:    Sentence
    hypothesis: Sentence
    tags:       set[Type[Tag]]
    labels:     set[Label]
    author:     Annotator
    validators: set[Annotator]

    def to_json(self) -> dict:
        return {'premise': self.premise,
                'hypothesis': self.hypothesis,
                'tags': {repr(tag) for tag in self.tags},
                'labels': self.labels,
                'author': self.author.value,
                'validators': {validator.value for validator in self.validators}}

    @staticmethod
    def from_json(json: dict) -> Sample:
        return Sample(premise=json['premise'],
                      hypothesis=json['hypothesis'],
                      tags={str_to_tag(tag.split(':')[-1]) for tag in json['tags']},
                      labels=json['labels'],
                      author=Annotator(json['author']),
                      validators={Annotator(value) for value in json['validators']})

    @property
    def all_tags(self) -> set[TagBase]: return union_of_supertypes(self.tags)


@dataclass
class Dataset:
    train:      list[Sample]
    dev:        list[Sample]
    test:       list[Sample]

    def to_json(self) -> dict:
        return {'train': [sample.to_json() for sample in self.train],
                'dev': [sample.to_json() for sample in self.dev],
                'test': [sample.to_json() for sample in self.test]}

    @staticmethod
    def from_json(json: dict) -> Dataset:
        return Dataset(train=[Sample.from_json(sample) for sample in json['train']],
                       dev=[Sample.from_json(sample) for sample in json['dev']],
                       test=[Sample.from_json(sample) for sample in json['test']])
