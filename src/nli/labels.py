from enum import Enum


class Label(Enum):
    Entailment = 'Entailment'
    Contradiction = 'Contradiction'
    Unknown = 'Unknown'

    def __repr__(self) -> str: return self.value
