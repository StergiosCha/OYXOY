import torch
from torch import Tensor
from torch.nn.utils.rnn import pad_sequence as _pad_seq

from inference.data import TokenizedSample, Label, Tag, permute


def pad_sequence(xs: list[Tensor], pad: int):
    return _pad_seq(xs, batch_first=True, padding_value=pad)


def collate_fn(raw: list[TokenizedSample], pad: int = 0, cast_to: str = 'cpu') \
        -> tuple[tuple[Tensor, Tensor], Tensor, list[set[Tag]]]:
    premises, hypotheses, tags, labels = zip(
        *[(premise, hypothesis, ts, ls) for premise, hypothesis, ts, ls in raw])
    sentences = premises + hypotheses
    tokens = pad_sequence([torch.tensor(x, device=cast_to) for x in sentences], pad=pad)
    attention_mask = tokens != pad
    labels = torch.tensor([(Label.Unknown in ls,
                           Label.Entailment in ls,
                           Label.Contradiction in ls)
                           for ls in labels]).float().to(cast_to)
    return (tokens, attention_mask), labels, tags


class Sampler:
    def __init__(self, samples: list[TokenizedSample]):
        self.samples = sorted(samples, key=lambda x: max(len(x[0]), len(x[1])))

    def iter_epoch(self, batch_size: int, shuffle: bool = True):
        if shuffle:
            samples = permute(self.samples)
        else:
            samples = self.samples
        start = 0
        while start < len(samples):
            yield samples[start: (start := start+batch_size)]
