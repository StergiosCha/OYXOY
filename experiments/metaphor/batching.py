import torch
from torch import Tensor
from torch.nn.utils.rnn import pad_sequence as _pad_seq
from torch.utils.data import DataLoader, Dataset

from .data import Tokens


def pad_sequence(xs: list[Tensor], pad: int):
    return _pad_seq(xs, batch_first=True, padding_value=pad)


def collate_fn(xs: list[tuple[Tokens, bool]], pad: int = 0, cast_to: str = 'cpu') -> tuple[tuple[Tensor, Tensor], Tensor]:
    tokens, ys = zip(*xs)
    padded = pad_sequence([torch.tensor(ts, device=cast_to) for ts in tokens], pad=pad)
    return (padded, padded != pad), torch.tensor(ys, dtype=torch.float, device=cast_to)


def make_dl(xs: list[tuple[Tokens, bool]], batch_size: int, shuffle: bool, cast_to: str) -> DataLoader:
    def c_fn(_xs: list[tuple[Tokens, bool]]) -> tuple[tuple[Tensor, Tensor], Tensor]:
        return collate_fn(_xs, cast_to=cast_to)
    return DataLoader(xs, collate_fn=c_fn, batch_size=batch_size, shuffle=shuffle)
