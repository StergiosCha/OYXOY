import pdb

import torch.nn.init
from torch import Tensor, empty
from torch.nn import Module, Parameter
from transformers import BertModel
from math import sqrt

from opt_einsum import contract

from torch_geometric.utils import softmax as sparse_softmax, to_dense_batch


class SenseDisambiguator(Module):
    def __init__(self):
        super(SenseDisambiguator, self).__init__()
        self.core = BertModel.from_pretrained("nlpaueb/bert-base-greek-uncased-v1")
        # self.weight = Parameter(empty(768,), requires_grad=True)
        # torch.nn.init.normal_(self.weight, 0, 1/sqrt(768))

    def bert(self, token_ids: Tensor, attention_mask: Tensor) -> Tensor:
        return self.core(input_ids=token_ids, attention_mask=attention_mask)['last_hidden_state']

    def contextualize(self, token_ids: Tensor, token_mask: Tensor, word_mask: Tensor) -> Tensor:
        contextualized = self.bert(token_ids=token_ids, attention_mask=token_mask)
        aggregated = (contextualized * word_mask[..., None]).sum(dim=-2)
        return aggregated

    def get_agreement_values(self, source: Tensor, target: Tensor) -> Tensor:
        return contract('bd,bd->b', source, target)  # type: ignore

    def disambiguate(self, definitions: tuple[Tensor, Tensor],
                     examples: tuple[Tensor, Tensor, Tensor],
                     edge_index: Tensor) -> Tensor:
        definition_reprs = self.bert(*definitions)[:, 0]
        example_reprs = self.contextualize(*examples)
        source = definition_reprs[edge_index[0]]
        target = example_reprs[edge_index[1]]
        agreements = self.get_agreement_values(source, target)
        return to_dense_batch(agreements, edge_index[1], fill_value=-1e08)[0]
