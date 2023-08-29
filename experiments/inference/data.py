from json import load
from nli.dataset import Sample, Label, Dataset, Tag
from collections import Counter
from random import sample as _sample, seed
from transformers import BertTokenizer


def permute(xs: list) -> list: return _sample(xs, len(xs))


def fields_to_sample(fields: list[str]) -> Sample:
    s1, s2 = fields[6:8]
    match fields[1]:
        case 'neutral':
            label = Label.Unknown
        case 'contradiction':
            label = Label.Contradiction
        case 'entailment':
            label = Label.Entailment
        case _:
            raise ValueError(fields[1])
    return Sample(premise=s1, hypothesis=s2, labels={label}, tags=set())


def read_xnl(file: str) -> list[Sample]:
    with open(file, 'r') as f:
        fields = [line.split('\t') for line in f.read().split('\n')[1:-1]]
        return [fields_to_sample(fs) for fs in fields if fs[0] == 'el']


def iterative_filter(samples: list[Sample]) -> tuple[list[Sample], list[Sample]]:
    tagset = Counter(tag for sample in samples for tag in sample.tags)
    dev, test = [], []
    for tag in sorted(tagset.keys(), key=lambda key: tagset[key]):
        subset = [s for s in samples if tag in s.tags and s not in dev and s not in test]
        subset = permute(subset)
        dev += subset[:int(0.3 * len(subset))]
        test += subset[int(0.3 * len(subset)):]
    return dev, test


TokenizedSample = tuple[list[int], list[int], set[Tag], set[Label]]


def tokenize_sample(tokenizer: BertTokenizer, sample: Sample) -> TokenizedSample:
    return (tokenizer.encode(sample.premise),
            tokenizer.encode(sample.hypothesis),
            sample.tags,
            sample.labels)


def tokenize_samples(tokenizer: BertTokenizer, samples: list[Sample]) -> list[TokenizedSample]:
    return [tokenize_sample(tokenizer, sample) for sample in samples]


def process_data() -> tuple[tuple[tuple[list[TokenizedSample], list[TokenizedSample]],
                            tuple[list[TokenizedSample], list[TokenizedSample]]],
                            list[Sample]]:
    seed(42)
    print('Preparing tokenizer...')
    tokenizer = BertTokenizer.from_pretrained("nlpaueb/bert-base-greek-uncased-v1")
    with open('../../datasets/nli/gold.json', 'r') as f:
        gold = Dataset.from_json(load(f))
    with open('../../datasets/nli/FraCaS.json', 'r') as f:
        fracas = Dataset.from_json(load(f))
    dev, test = iterative_filter(gold.samples + fracas.samples)
    xnli_dev = read_xnl('../../xnli.dev.tsv')
    xnli_test = read_xnl('../../xnli.test.tsv')
    print('Tokenizing...')
    return (((tokenize_samples(tokenizer, xnli_dev),
              tokenize_samples(tokenizer, xnli_test)),
             (tokenize_samples(tokenizer, dev),
              tokenize_samples(tokenizer, test))),
            test)
