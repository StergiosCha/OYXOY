from wordsense.dataset import Dataset, Entry
from dataclasses import dataclass
from Levenshtein import distance
from json import load
from transformers import BertTokenizer
import spacy
import unicodedata


Tokens = list[int]
Mask = list[bool]


@dataclass
class ProcessedEntry:
    definitions:    list[Tokens]
    examples:       list[list[tuple[Tokens, Mask]]]


def load_file(file: str) -> Dataset:
    with open(file, 'r') as f:
        return Dataset.from_json(load(f))


def process_data():
    entries = load_file('../../datasets/wordsense/dataset.json').entries
    print('Preparing lemmatizer...')
    lemmatizer = spacy.load('el_core_news_sm')
    print('Preparing tokenizer...')
    tokenizer = BertTokenizer.from_pretrained("nlpaueb/bert-base-greek-uncased-v1")
    print('Tokenizing...')
    return flatten_entries(process_entries(entries, lemmatizer, tokenizer))


def _norm(input_str: str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c.lower() for c in nfkd_form if not unicodedata.combining(c)])


def word_mask(lemma: str, sentence: str, language: spacy.Language) -> tuple[list[str], Mask]:
    doc = language(sentence)
    lemma = _norm(lemma)

    def dist(lm: str) -> int:
        return distance(lm, lemma)

    ws, ls = zip(*[(repr(w), _norm(w.lemma_)) for w in doc])
    mask = [lm == lemma for lm in ls]
    if not any(mask):
        idx = min(range(len(ls)), key=lambda i: dist(ls[i]))
        mask[idx] = True
    return ws, mask


def tokenize_with_mask(ws: list[str], mask: list[bool], tokenizer: BertTokenizer) -> tuple[Tokens, Mask]:
    tokens = [tokenizer.convert_tokens_to_ids(tokenizer.tokenize(w)) for w in ws]
    mask = [[flag] * seqlen for flag, seqlen in zip(mask, map(len, tokens))]
    return ([tokenizer.cls_token_id, *(t for ts in tokens for t in ts), tokenizer.sep_token_id],
            [False, *(m for ms in mask for m in ms), False])


def process_entries(entries: list[Entry], spacy_model: spacy.Language, tokenizer: BertTokenizer) \
        -> list[ProcessedEntry]:
    processed = []
    for entry in entries:
        examples = []
        definitions = []
        for sense in entry.senses:
            sense_examples = []
            for example in sense.examples:
                words, mask = word_mask(_norm(entry.lemma), example, spacy_model)
                if not any(mask) or len(mask) != len(words):
                    continue
                tokens, mask = tokenize_with_mask(words, mask, tokenizer)
                sense_examples.append((tokens, mask))
            if not sense_examples:
                continue
            examples.append(sense_examples)
            definitions.append(tokenizer.encode(sense.definition))
        if not examples:
            continue
        processed.append(ProcessedEntry(definitions=definitions, examples=examples))
    return processed


def flatten_entries(entries: list[ProcessedEntry]) -> tuple[list[list[Tokens]],
                                                            list[tuple[tuple[Tokens, Mask], int, int]]]:
    definitions = [entry.definitions for entry in entries]
    examples = [(example, entry_id, sense_id)
                for entry_id, entry in enumerate(entries)
                for sense_id, exs in enumerate(entry.examples) for example in exs]
    return definitions, examples
