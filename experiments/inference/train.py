import torch
from torch import Tensor
from inference.data import process_data
from inference.batching import Sampler, collate_fn, Label
from inference.model import NLI
from torch.nn.functional import binary_cross_entropy_with_logits as bce

from torch.optim import AdamW


def f1(xs: Tensor, ys: Tensor) -> Tensor:
    tp = (xs * ys).sum(0)
    fp = (xs * ~ys).sum(0)
    fn = (~xs * ys).sum(0)
    prec = tp / (tp + fp + 1e-08)
    rec = tp / (tp + fn + 1e-08)
    return torch.stack((prec, rec, 2 * prec * rec / (prec + rec + 1e-08)), dim=0)


def main(device: str = 'cpu'):
    ((xnli_dev, xnli_test), (adapt, test)), test_raw = process_data()

    num_repeats: int = 3
    num_epochs: int = 30
    batch_size: int = 32
    patience: int = 5

    train_sampler = Sampler(xnli_test + adapt)
    dev_sampler = Sampler(xnli_dev)
    test_sampler = Sampler(test)

    print('Going ham...')
    for repeat in range(num_repeats):
        print(f'Initializing model {repeat}...')
        model = NLI().to(device)
        optim = AdamW(model.parameters(), lr=1e-5, weight_decay=1e-01)
        best_epoch, best_f1 = None, None

        for epoch in range(num_epochs):
            print(f'Epoch {epoch}')

            batch_iter = train_sampler.iter_epoch(batch_size)
            train_loss, train_preds, train_truths = 0, [], []
            model.train()
            for batch in batch_iter:
                sentences, labels, tags = collate_fn(batch, cast_to=device)
                predictions = model.infer(sentences)
                loss = bce(predictions, labels, reduction='mean')
                loss.backward()
                optim.step()
                optim.zero_grad(set_to_none=True)
                train_loss += loss.item()
                train_preds += predictions.sigmoid().round().bool().cpu().tolist()
                train_truths += labels.bool().cpu().tolist()
            print(f'Train loss = {train_loss}')
            print(f'Train F1 = {f1(torch.tensor(train_preds), torch.tensor(train_truths))}')

            batch_iter = dev_sampler.iter_epoch(batch_size, shuffle=False)
            dev_loss, dev_preds, dev_truths = 0, [], []
            model.eval()
            for batch in batch_iter:
                sentences, labels, tags = collate_fn(batch, cast_to=device)
                predictions = model.infer(sentences)
                loss = bce(predictions, labels, reduction='mean')
                dev_loss += loss.item()
                dev_preds += predictions.sigmoid().round().bool().cpu().tolist()
                dev_truths += labels.bool().cpu().tolist()
            print(f'Dev loss = {dev_loss}')
            print(f'Dev F1 = {(dev_f1 := f1(torch.tensor(dev_preds), torch.tensor(dev_truths)))}')

            this_f1 = dev_f1[-1].mean().item()
            if best_f1 is None or this_f1 > best_f1:
                print(f'New best: {this_f1}')
                best_epoch = epoch
                best_f1 = this_f1
                model.save(f'./nli_{repeat}.tmp')
            elif best_epoch + patience < epoch:
                break

    idx_to_label = {0: Label.Unknown, 1: Label.Entailment, 2: Label.Contradiction}
    for repeat in range(num_repeats):
        model = NLI().to(device)
        model.load(f'./nli_{repeat}.tmp')
        model.eval()

        batch_iter = test_sampler.iter_epoch(batch_size, shuffle=False)
        test_preds, test_truths = [], []
        for batch in batch_iter:
            sentences, _, _ = collate_fn(batch, cast_to=device)
            test_preds += model.infer(sentences).sigmoid().round().bool().cpu().tolist()
        labels = [{idx_to_label[i] for i, p in enumerate(ps) if p} for ps in test_preds]
        with open(f'./preds_{repeat}.tsv', 'w') as f:
            f.write('\n'.join(f'{sample.premise}'
                              f'\t{sample.hypothesis}'
                              f'\t{sample.tags}'
                              f'\t{sample.labels}'
                              f'\t{ls}' for sample, ls in zip(test_raw, labels)))


if __name__ == '__main__':
    main('cuda')
