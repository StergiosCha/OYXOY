from __future__ import annotations
from dataclasses import dataclass
from typing import TypedDict


@dataclass
class Entry:
    lemma: str
    senses: list[Sense]

    @staticmethod
    def from_json(json: _EntryJson) -> Entry:
        return Entry(lemma=json['lemma'], senses=[Sense.from_json(s) for s in json['senses']])

    def json(self) -> _EntryJson:
        return {'lemma': self.lemma, 'senses': [s.json() for s in self.senses]}


@dataclass
class Sense:
    definition: str
    examples: list[str]

    @staticmethod
    def from_json(json: _SenseJson) -> Sense:
        return Sense(definition=json['definition'], examples=json['examples'])

    def json(self) -> _SenseJson:
        return {'definition': self.definition, 'examples': self.examples}


@dataclass
class Dataset:
    entries: list[Entry]

    @staticmethod
    def from_json(json: _DatasetJson) -> Dataset:
        return Dataset(entries=[Entry.from_json(entry) for entry in json['entries']])

    def json(self) -> _DatasetJson:
        return {'entries': [entry.json() for entry in self.entries]}


class _EntryJson(TypedDict):
    lemma: str
    senses: list[_SenseJson]


class _SenseJson(TypedDict):
    definition: str
    examples: list[str]


class _DatasetJson(TypedDict):
    entries: list[_EntryJson]
