from torch import Tensor
from torch.nn import Module, Linear
from torch.nn.functional import dropout
from transformers import BertModel


class Model(Module):
    def __init__(self):
        super(Model, self).__init__()
        self.core = BertModel.from_pretrained("nlpaueb/bert-base-greek-uncased-v1")
        self.classifier = Linear(768, 1)

    def bert(self, token_ids: Tensor, attention_mask: Tensor) -> Tensor:
        return self.core(input_ids=token_ids, attention_mask=attention_mask)['last_hidden_state']

    def forward(self, token_ids: Tensor, attention_mask: Tensor) -> Tensor:
        cls = self.bert(token_ids, attention_mask)[:, 0]
        cls = dropout(cls, p=0.25, training=self.training)
        return self.classifier(cls)
