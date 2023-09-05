from wordsense.dataset import Dataset, Entry
from dataclasses import dataclass
from Levenshtein import distance
from json import load
from transformers import BertTokenizer
import unicodedata


Tokens = list[int]


def load_file(file: str) -> Dataset:
    with open(file, 'r') as f:
        return Dataset.from_json(load(f))


def _norm(input_str: str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c.lower() for c in nfkd_form if not unicodedata.combining(c)])


def filter_metaphors(entries: list[Entry]) -> list[tuple[list[str], list[str]]]:
    entries = [entry for entry in entries if any('μτφ' in sense.definition for sense in entry.senses)]
    ret = []
    for entry in entries:
        entry_metaphors, entry_nons = [], []
        for sense in entry.senses:
            is_metaphor = 'μτφ' in sense.definition
            (entry_metaphors if is_metaphor else entry_nons).extend(sense.examples)
        ret.append((entry_metaphors, entry_nons))
    return ret


def process_data() -> list[tuple[list[Tokens], list[Tokens]]]:
    tokenizer = BertTokenizer.from_pretrained("nlpaueb/bert-base-greek-uncased-v1")
    print('Tokenizing...')
    entries = load_file('../../datasets/wordsense/dataset.json').entries
    filtered = [([tokenizer.encode(m) for m in ms],
                 [tokenizer.encode(n) for n in ns])
                for ms, ns in filter_metaphors(entries)]
    return filtered
