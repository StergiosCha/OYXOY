from metaphor.batching import make_dl
from metaphor.data import process_data
from metaphor.model import Model

from torch.nn.functional import binary_cross_entropy_with_logits as bce
from torch.optim import AdamW

from random import seed, sample


def main(device: str = 'cpu'):
    data = process_data()
    seed(1312)
    data = sample(data, len(data))
    oov_split = int(len(data) * 0.95)
    iv_entries, oov_entries = data[:oov_split], data[oov_split:]
    iv_examples = [(m, True) for ms, _ in iv_entries for m in ms] + [(n, False) for _, ns in iv_entries for n in ns]
    split1, split2 = int(len(iv_examples) * 0.6), int(len(iv_examples) * 0.8)
    train, dev, test = iv_examples[:split1], iv_examples[split1:split2], iv_examples[split2:]
    oov_examples = [(m, True) for ms, _ in oov_entries for m in ms] + [(n, False) for _, ns in oov_entries for n in ns]
    print(len(train), len(dev), len(test), len(oov_examples))

    num_repeats: int = 3
    num_epochs: int = 30
    batch_size: int = 32
    patience: int = 5

    train_dl = make_dl(train, batch_size=batch_size, shuffle=True, cast_to=device)
    dev_dl = make_dl(dev, batch_size=batch_size, shuffle=False, cast_to=device)
    test_dl = make_dl(test, batch_size=batch_size, shuffle=False, cast_to=device)
    oov_dl = make_dl(oov_examples, batch_size=batch_size, shuffle=False, cast_to=device)

    print('Going ham...')
    for repeat in range(num_repeats):
        print(f'Initializing model {repeat}...')
        model = Model().to(device)
        optim = AdamW(model.parameters(), lr=1e-4, weight_decay=1e-2)
        best_epoch, best_accu = None, None
        for epoch in range(num_epochs):
            model.train()
            train_loss, train_total, train_correct = 0, 0, 0
            for xs, targets in train_dl:
                ys = model.forward(*xs).squeeze(-1)
                loss = bce(ys, targets, reduction='mean')
                loss.backward()
                optim.step()
                optim.zero_grad(set_to_none=True)
                train_loss += loss.item()
                train_total += len(ys)
                train_correct += sum(ys.sigmoid().round() == targets).item()
            print(f'Train loss = {train_loss}')
            print(f'Train accu = {train_correct / train_total}')
            model.eval()
            dev_loss, dev_total, dev_correct = 0, 0, 0
            for xs, targets in dev_dl:
                ys = model.forward(*xs).squeeze(-1)
                loss = bce(ys, targets, reduction='mean')
                dev_loss += loss.item()
                dev_total += len(ys)
                dev_correct += sum(ys.sigmoid().round() == targets).item()
            print(f'Dev loss = {dev_loss}')
            print(f'Dev accu = {dev_correct / dev_total}')

            if best_accu is None or dev_correct/dev_total > best_accu:
                best_accu = dev_correct/dev_total
                best_epoch = epoch
                test_correct, test_total = 0, 0
                for xs, targets in test_dl:
                    ys = model.forward(*xs).squeeze(-1)
                    test_total += len(ys)
                    test_correct += sum(ys.sigmoid().round() == targets).item()
                print(f'Test accu = {test_correct / test_total}')
                test_correct, test_total = 0, 0
                for xs, targets in oov_dl:
                    ys = model.forward(*xs).squeeze(-1)
                    test_total += len(ys)
                    test_correct += sum(ys.sigmoid().round() == targets).item()
                print(f'OOV accu = {test_correct / test_total}')

            elif best_epoch + patience < epoch:
                break




if __name__ == '__main__':
    main('cuda')