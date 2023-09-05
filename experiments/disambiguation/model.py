from torch import Tensor
from torch.nn import Module, Linear
from torch.nn.functional import dropout
from transformers import BertModel
from math import sqrt

from opt_einsum import contract

from torch_geometric.utils import to_dense_batch


class Base(Module):
    def __init__(self):
        super(Base, self).__init__()
        self.core = BertModel.from_pretrained("nlpaueb/bert-base-greek-uncased-v1")
        self.param = Linear(768, 1)

    def bert(self, token_ids: Tensor, attention_mask: Tensor) -> Tensor:
        return self.core(input_ids=token_ids, attention_mask=attention_mask)['last_hidden_state']

    def contextualize(self, token_ids: Tensor, token_mask: Tensor, word_mask: Tensor) -> Tensor:
        contextualized = self.bert(token_ids=token_ids, attention_mask=token_mask)
        aggregated = (contextualized * word_mask[..., None]).mean(dim=-2)
        return aggregated
    
    def get_agreement_values(self, source: Tensor, target: Tensor) -> Tensor:
        source = dropout(source, p=0.25, training=self.training)
        return contract('bd,bd->b', source, target) / sqrt(768)


class Disambiguator(Base):
    def disambiguate(self, definitions: tuple[Tensor, Tensor],
                     examples: tuple[Tensor, Tensor, Tensor],
                     edge_index: Tensor) -> Tensor:
        definition_reprs = self.bert(*definitions)[:, 0]
        example_reprs = self.contextualize(*examples)
        source = definition_reprs[edge_index[0]]
        target = example_reprs[edge_index[1]]
        agreements = self.get_agreement_values(source, target)
        return to_dense_batch(agreements, edge_index[1], fill_value=-1e08)[0]

    def contrast(self, examples: tuple[Tensor, Tensor, Tensor], edge_index: Tensor) -> Tensor:
        example_reprs = self.contextualize(*examples)
        source = example_reprs[edge_index[0]]
        target = example_reprs[edge_index[1]]
        agreements = self.get_agreement_values(source, target)
        return agreements
