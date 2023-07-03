from enum import Enum


class Label(Enum):
    Entailment = 'Entailment'
    Contradiction = 'Contradiction'
    Unknown = 'Unknown'
    Requires_Attention = 'Requires Attention'

    def __repr__(self) -> str: return self.value
