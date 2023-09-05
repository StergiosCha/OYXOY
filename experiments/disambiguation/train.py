from disambiguation.data import process_data
from disambiguation.batching import Sampler, sample, collate_fn_1, collate_fn_2
from disambiguation.model import Disambiguator

from torch.nn.functional import nll_loss, binary_cross_entropy_with_logits as bce

from torch.optim import AdamW

from random import seed


def main(device: str = 'cpu'):
    definitions, examples = process_data()
    seed(1312)
    test_definitions = sample(list(range(len(definitions))), int(0.1 * len(definitions)))
    examples = sample(examples, len(examples))
    split1, split2 = int(0.6 * len(examples)), int(0.8 * len(examples))
    train, dev, test = examples[:split1], examples[split1:split2], examples[split2:]
    out_of_dist = [(ex, entry_id, sense_id) for (ex, entry_id, sense_id) in train if entry_id in test_definitions]
    test = [*test, *out_of_dist]
    train = [(ex, entry_id, sense_id) for (ex, entry_id, sense_id) in train if entry_id not in test_definitions]
    in_dist = {entry_id for _, entry_id, _ in train}
    test_in = [(ex, entry_id, sense_id) for ex, entry_id, sense_id in test if entry_id in in_dist]
    test_out = [(ex, entry_id, sense_id) for ex, entry_id, sense_id in test if entry_id not in in_dist]
    print(f'In: {len(test_in)}, Out: {len(test_out)}')

    num_repeats: int = 3
    num_epochs: int = 30
    batch_size: int = 32
    patience: int = 3

    train_sampler = Sampler(definitions, sorted(train, key=lambda x: x[1]))
    dev_sampler = Sampler(definitions, sorted(dev, key=lambda x: x[1]))
    test_in_sampler = Sampler(definitions, sorted(test_in, key=lambda x: x[1]))
    test_out_sampler = Sampler(definitions, sorted(test_out, key=lambda x: x[1]))
    pdb.set_trace()

    print('Going ham...')
    for repeat in range(num_repeats):
        print(f'Initializing model {repeat}...')
        model = Disambiguator().to(device)
        optim = AdamW(model.parameters(), lr=1e-5, weight_decay=1e-2)
        best_epoch, best_accu = None, None

        for epoch in range(num_epochs):
            print(f'Epoch {epoch}')

            batch_iter = train_sampler.iter_epoch_1(batch_size=batch_size)
            # batch_iter = train_sampler.iter_epoch_2(batch_size=batch_size)
            train_loss, train_correct, train_total = 0, 0, 0
            model.train()
            for raw in batch_iter:
                # examples, edge_index, matches = collate_fn_2(raw, cast_to=device)
                # scores = model.contrast(examples, edge_index)
                # loss = bce(scores, matches, reduction='mean')
                definitions, examples, edge_index, sense_index = collate_fn_1(raw, cast_to=device)
                scores = model.disambiguate(
                    definitions=definitions,
                    examples=examples,
                    edge_index=edge_index)
                loss = nll_loss(scores.log_softmax(-1), sense_index, reduction='mean')
                loss.backward()
                optim.step()
                optim.zero_grad(set_to_none=True)
                train_loss += loss.item()
                train_total += len(sense_index)
                train_correct += sum(scores.argmax(-1) == sense_index).item()
                # train_total += len(matches)
                # train_correct += sum(scores.sigmoid().round() == matches).item()
            print(f'Train loss = {train_loss}')
            print(f'Train accu = {train_correct/train_total}')

            # batch_iter = dev_sampler.iter_epoch_1(batch_size=batch_size, shuffle=False)
            batch_iter = dev_sampler.iter_epoch_2(batch_size=batch_size)
            dev_loss, dev_correct, dev_total = 0, 0, 0
            model.eval()
            for raw in batch_iter:
                examples, edge_index, matches = collate_fn_2(raw, cast_to=device)
                scores = model.contrast(examples, edge_index)
                loss = bce(scores, matches, reduction='mean')
                # definitions, examples, edge_index, sense_index = collate_fn_1(raw, cast_to=device)
                # scores = model.disambiguate(
                #     definitions=definitions,
                #     examples=examples,
                #     edge_index=edge_index)
                # loss = nll_loss(scores.log_softmax(-1), sense_index, reduction='mean')
                dev_loss += loss.item()
                # dev_total += len(sense_index)
                # dev_correct += sum(scores.argmax(-1) == sense_index).item()
                dev_total += len(matches)
                dev_correct += sum(scores.sigmoid().round() == matches).item()
            print(f'Dev loss = {dev_loss}')
            print(f'Dev accu = {(accu := dev_correct/dev_total)}')

            if best_accu is None or accu > best_accu:
                best_accu = accu
                best_epoch = epoch

                batch_iter = test_in_sampler.iter_epoch_1(batch_size=batch_size, shuffle=False)
                # batch_iter = test_in_sampler.iter_epoch_2(batch_size=batch_size)
                test_total, test_correct = 0, 0
                for raw in batch_iter:
                    # examples, edge_index, matches = collate_fn_2(raw, cast_to=device)
                    # scores = model.contrast(examples, edge_index)
                    definitions, examples, edge_index, sense_index = collate_fn_1(raw, cast_to=device)
                    scores = model.disambiguate(
                        definitions=definitions,
                        examples=examples,
                        edge_index=edge_index)
                    test_total += len(sense_index)
                    test_correct += sum(scores.argmax(-1) == sense_index).item()
                    # test_total += len(matches)
                    # test_correct += sum(scores.sigmoid().round() == matches).item()
                print(f'Test accu (in-dist) = {(test_correct / test_total)}')
                batch_iter = test_out_sampler.iter_epoch_1(batch_size=batch_size, shuffle=False)
                # batch_iter = test_out_sampler.iter_epoch_2(batch_size=batch_size)
                test_total, test_correct = 0, 0
                for raw in batch_iter:
                    # examples, edge_index, matches = collate_fn_2(raw, cast_to=device)
                    # scores = model.contrast(examples, edge_index)
                    definitions, examples, edge_index, sense_index = collate_fn_1(raw, cast_to=device)
                    scores = model.disambiguate(
                        definitions=definitions,
                        examples=examples,
                        edge_index=edge_index)
                    test_total += len(sense_index)
                    test_correct += sum(scores.argmax(-1) == sense_index).item()
                    # test_total += len(matches)
                    # test_correct += sum(scores.sigmoid().round() == matches).item()
                print(f'Test accu (out-of-dist) = {(test_correct / test_total)}')
            elif best_epoch + patience < epoch:
                break


if __name__ == '__main__':
    main('cuda')