import torch
from torch import Tensor
from torch.nn.utils.rnn import pad_sequence as _pad_seq
from random import sample
from typing import Iterator
from itertools import takewhile

from .data import Tokens, Mask


def pad_sequence(xs: list[Tensor], pad: int):
    return _pad_seq(xs, batch_first=True, padding_value=pad)


def collate_fn_1(raw: tuple[list[list[int]],
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


def collate_fn_2(raw: tuple[tuple[list[int], list[bool]], list[tuple[int, int]], list[bool]],
                 pad: int = 0,
                 cast_to: str = 'cpu') -> tuple[tuple[Tensor, Tensor, Tensor], Tensor, Tensor]:
    examples, edge_index, ground_truth = raw
    example_tokens = pad_sequence([torch.tensor(x) for x, _ in examples], pad).to(cast_to)
    attention_mask = example_tokens != pad
    word_mask = pad_sequence([torch.tensor(m) for _, m in examples], False).to(cast_to)
    edge_index = torch.tensor(edge_index, device=cast_to).t()
    ground_truth = torch.tensor(ground_truth, device=cast_to, dtype=torch.float)
    return (example_tokens, attention_mask, word_mask), edge_index, ground_truth


class Sampler:
    def __init__(self, definitions: list[list[Tokens]], examples: list[tuple[tuple[Tokens, Mask], int, int]]):
        self.definitions = definitions
        self.examples = examples

    def iter_epoch_1(self, batch_size: int, shuffle: bool = True) \
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
            batch = sorted(batch, key=lambda x: (x[1], x[2]))

            unique_entries = sorted({entry_id for _, entry_id, _ in batch})

            examples, ex_to_group, sense_ids = zip(
                *((example, unique_entries.index(entry_id), sense_id)
                  for example, entry_id, sense_id in batch))
            definitions, def_to_group = zip(
                *((definition, unique_entries.index(entry_id))
                  for entry_id in unique_entries for definition in self.definitions[entry_id]))
            edge_index = [(i, j)
                          for j, ex_group in enumerate(ex_to_group)
                          for i, def_group in enumerate(def_to_group)
                          if def_group == ex_group]
            yield definitions, examples, edge_index, sense_ids

    def iter_epoch_2(self,
                     batch_size: int) \
            -> Iterator[tuple[tuple[list[int], list[bool]], list[tuple[int, int]], list[bool]]]:
        start = 0
        while start < len(self.examples):
            batch = []
            while len(batch) < batch_size and start < len(self.examples):
                lemma_id = self.examples[start][1]
                batch += list(takewhile(lambda ex: ex[1] == lemma_id, self.examples[start:]))
                start += len(batch)

            examples = [ex for ex, _, _ in batch]
            edge_index, ground_truth = zip(
                *[((i, j), sense_i == sense_j)
                  for i, (_, _, sense_i) in enumerate(batch)
                  for j, (_, _, sense_j) in enumerate(batch)
                  if i != j])
            yield examples, edge_index, ground_truth

