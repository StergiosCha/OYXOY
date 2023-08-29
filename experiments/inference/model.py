from torch import Tensor, cat, save, load
from torch.nn import Module, Sequential, Linear, GELU
from torch.nn.functional import dropout
from transformers import BertModel


class NLI(Module):
    def __init__(self):
        super(NLI, self).__init__()
        self.core = BertModel.from_pretrained("nlpaueb/bert-base-greek-uncased-v1")
        self.head = Sequential(Linear(768, 3))

    def bert(self, token_ids: Tensor, attention_mask: Tensor) -> Tensor:
        return self.core(input_ids=token_ids, attention_mask=attention_mask)['pooler_output']

    def infer(self, sentences: tuple[Tensor, Tensor]) -> Tensor:
        sentence_reprs = self.bert(*sentences)
        sentence_reprs = dropout(sentence_reprs, p=0.15, training=self.training)
        premises, hypotheses = sentence_reprs.chunk(2, dim=0)
        return self.head(premises * hypotheses)

    def save(self, path: str, **kwargs):
        save(self.state_dict(), f=path, **kwargs)

    def load(self, path: str, **kwargs):
        self.load_state_dict(load(path, **kwargs), strict=True)