import pdb

import torch
from torch import Tensor
from torch.nn.utils.rnn import pad_sequence as _pad_seq
from random import sample
from typing import Iterator

from .data import ProcessedEntry


def pad_sequence(xs: list[Tensor], pad: int):
    return _pad_seq(xs, batch_first=True, padding_value=pad)


def collate(raw: tuple[list[list[int]],
                       list[tuple[list[int], list[bool]]],
                       list[tuple[int, int]],
                       list[int]],
            pad: int = 0,
            cast_to: str = 'cpu') \
        -> tuple[tuple[Tensor, Tensor], tuple[Tensor, Tensor, Tensor], Tensor, Tensor]:

    definitions, examples, edge_index, sense_idx = raw
    definition_tokens = pad_sequence([torch.tensor(definition) for definition in definitions], pad).to(cast_to)
    definition_mask = definition_tokens != pad
    example_tokens = pad_sequence([torch.tensor(x) for x, _ in examples], pad).to(cast_to)
    attention_mask = example_tokens != pad
    word_mask = pad_sequence([torch.tensor(m) for _, m in examples], False).to(cast_to)
    edge_index = torch.tensor(edge_index, device=cast_to).t()
    sense_idx = torch.tensor(sense_idx, device=cast_to)
    return ((definition_tokens, definition_mask),
            (example_tokens, attention_mask, word_mask),
            edge_index,
            sense_idx)


class Sampler:
    def __init__(self, entries: list[ProcessedEntry]):
        self.entries = entries
        self.examples = [(entry_id, sense_id, example)
                         for entry_id, entry in enumerate(self.entries)
                         for sense_id, examples in enumerate(entry.examples)
                         for example in examples]

    def iter_epoch(self, batch_size: int, shuffle: bool = True) \
            -> Iterator[tuple[list[list[int]],
                              list[tuple[list[int], list[bool]]],
                              list[tuple[int, int]],
                              list[int]]]:

        if shuffle:
            shuffled = sample(self.examples, len(self.examples))
        else:
            shuffled = self.examples
        start = 0
        while start < len(shuffled):
            batch = shuffled[start:(start := start + batch_size)]
            batch = sorted(batch, key=lambda x: (x[0], x[1]))

            unique_entries = sorted({entry_id for entry_id, _, _ in batch})
            # def_lengths = [len(self.entries[entry_id].definitions) for entry_id in unique_entries]
            # def_offsets = [sum(def_lengths[:i]) for i in range(len(def_lengths))]

            examples, sense_ids, ex_to_group = zip(
                *((example, sense_id, unique_entries.index(entry_id))
                  for entry_id, sense_id, example in batch))
            definitions, def_to_group = zip(
                *((definition, i) for i, entry_id in enumerate(unique_entries)
                  for definition in self.entries[entry_id].definitions))
            edge_index = [(i, j)
                          for j, ex_group in enumerate(ex_to_group)
                          for i, def_group in enumerate(def_to_group)
                          if def_group == ex_group]
            yield definitions, examples, edge_index, sense_ids
