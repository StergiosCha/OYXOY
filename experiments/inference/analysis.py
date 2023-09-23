import torch

from nli.dataset import Label, Tag, str_to_tag
from math import sqrt
from inference.train import f1


def read_tsv(file: str) -> list[tuple[str, str, set[Tag], set[Label], set[Label]]]:
    with open(file, 'r') as f:
        contents = f.read()

    def read_line(line: str) -> tuple[str, str, set[Tag], set[Label], set[Label]]:
        premise, hypothesis, tags, labels, preds = line.split('\t')
        tags = tags[1:-1].split(', ')
        labels = labels[1:-1].split(', ')
        preds = preds[1:-1].split(', ') if preds != 'set()' else []
        return (premise,
                hypothesis,
                {str_to_tag(x.split(':')[-1]) for x in tags},
                {eval(f'Label.{x}') for x in labels},
                {eval(f'Label.{x}') for x in preds})

    return [read_line(line) for line in contents.split('\n')]


def read_tsvs() -> list[tuple[str, str, set[Tag], set[Label], list[set[Label]]]]:
    out1 = read_tsv('./inference/preds_0.tsv')
    out2 = read_tsv('./inference/preds_1.tsv')
    out3 = read_tsv('./inference/preds_2.tsv')
    assert out1[42][0] == out3[42][0]
    return [(x[0], x[1], x[2], x[3], [x[4], y[4], z[4]]) for x, y, z in zip(out1, out2, out3)]


def jaccard(x: set, y: set) -> float:
    return len(x & y) / len(x | y)


def mean_error(xs: list[float]) -> tuple[float, float]:
    return (mu := sum(xs) / len(xs)), sum(abs(x - mu) for x in xs) / len(xs) * 100


def per_tag_scores(analyses: list[tuple[str, str, set[Tag], set[Label], list[set[Label]]]]):
    scores = tuple(zip(*[[jaccard(truth, p) for p in preds] for _, _, _, truth, preds in analyses]))
    scores = [mean_error(s)[0] for s in scores]
    print(f'Average :: {mean_error(scores)}')
    tagset = {tag for _, _, tags, _, _ in analyses for tag in tags}
    for tag in tagset:
        subset = [single for single in analyses if tag in single[2]]
        scores = tuple(zip(*[[jaccard(truth, p) for p in preds] for _, _, _, truth, preds in subset]))
        scores = [mean_error(s)[0] for s in scores]
        print(f'{tag} :: {mean_error(scores)}')
    always_wrong = [(premise, hypothesis, tags, truth, preds) for (premise, hypothesis, tags, truth, preds) in analyses
                    if all(jaccard(p, truth) == 0 for p in preds)]
    print(len(always_wrong))
    with open('./always_wrong.tsv', 'w') as f:
        f.write('\n'.join('\t'.join(map(repr, sample)) for sample in always_wrong))

    truths = torch.tensor([(Label.Unknown in ls,
                            Label.Entailment in ls,
                            Label.Contradiction in ls)
                           for _, _, _, ls, _ in analyses])
    preds = torch.tensor([[(Label.Unknown in p,
                            Label.Entailment in p,
                            Label.Contradiction in p)
                           for p in ps]
                          for _, _, _, _, ps in analyses])
    f1s = [f1(truths, preds[:, i]) for i in range(3)]
    print(f1s)
