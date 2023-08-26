import pdb

from disambiguation.data import process_data, load_file
from disambiguation.batching import Sampler, sample, collate
from disambiguation.model import SenseDisambiguator

from torch.nn.functional import nll_loss

from torch.optim import AdamW


def main(device: str = 'cpu'):
    out = process_data((raw := load_file('../datasets/wordsense/dataset.json').entries[:50]))
    out = sample(out, len(out))
    split1, split2 = int(0.6 * len(out)), int(0.8 * len(out))
    train, dev, test = out[:split1], out[split1:split2], out[split2:]

    num_epochs: int = 64
    batch_size: int = 32

    train_sampler = Sampler(train)
    dev_sampler = Sampler(dev)

    print('Initializing model...')
    model = SenseDisambiguator().to(device)
    optim = AdamW(model.parameters(), lr=1e-4)

    print('Going ham...')
    for epoch in range(num_epochs):
        print(f'Epoch {epoch}')
        batch_iter = train_sampler.iter_epoch(batch_size=batch_size)

        epoch_loss, epoch_correct, epoch_total = 0, 0, 0
        model.train()
        for b, raw in enumerate(batch_iter):
            definitions, examples, edge_index, sense_index = collate(raw, cast_to=device)
            scores = model.disambiguate(
                definitions=definitions,
                examples=examples,
                edge_index=edge_index)
            loss = nll_loss(scores.log_softmax(-1), sense_index, reduction='mean')
            loss.backward()
            optim.step()
            optim.zero_grad(set_to_none=True)
            epoch_loss += loss.item()
            epoch_total += len(sense_index)
            epoch_correct += sum(scores.argmax(-1) == sense_index).item()
        print(f'Train loss = {epoch_loss}')
        print(f'Train accu = {epoch_correct/epoch_total}')

        # batch_iter = dev_sampler.iter_epoch(batch_size=batch_size, shuffle=False)
        # epoch_loss, epoch_correct, epoch_total = 0, 0, 0
        # for raw in batch_iter:
        #     definitions, examples, edge_index, true_mask, sense_index = collate(raw, cast_to=device)
        #     scores, selection = model.disambiguate(
        #         definitions=definitions,
        #         examples=examples,
        #         edge_index=edge_index)
        #     loss = -(scores[true_mask].log()).mean()
        #     epoch_loss += loss.item()
        #     epoch_total += len(sense_index)
        #     epoch_correct += sum(selection == sense_index).item()
        # print(f'Dev loss = {epoch_loss}')
        # print(f'Dev accu = {epoch_correct/epoch_total}')
