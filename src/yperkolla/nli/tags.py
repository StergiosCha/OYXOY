"""
Class hierarchy implementing the following structure of tags.

    Lexical Semantics
        Lexical Entailment
            Hyponymy
            Hypernymy
            Synonymy
            Antonymy
            Meronymy
        Morphological Modification
        Factivity
            Factive
            Non-Factive
        Symmetry/Collectivity
        Redundancy
        FAO
    Predicate-Argument Structure
        Syntactic Ambiguity
        Core Arguments
        Alternations
        Ellipsis
        Anaphora/Coreference
        Intersectivity
            Intersective
            Non-Intersective
        Restrictivity
            Restrictive
            Non-Restrictive
    Logic
        Single Negation
        Multiple Negations
        Conjunction
        Disjunction
        Conditionals
        Negative Concord
        Quantification
            Universal
            Existential
            Non-Standard
        Comparatives
        Temporals
    Common Sense/Knowledge
"""
from __future__ import annotations
from abc import ABCMeta, ABC
from typing import NoReturn, Type


# abstract base class for all tags
class TagBase(ABCMeta):
    _str_: str

    def __repr__(cls) -> str: return ':'.join(ancestor._str_ for ancestor in reversed(supertypes(cls)))


# class denoting "leaves" in the tag hierarchy
class Tag: ...


# Entailment
class LexicalEntailment(metaclass=TagBase): _str_ = 'Lexical Entailment'
class LexicalSemantics(LexicalEntailment): _str_ = 'Lexical Semantics'
class Hyponymy(LexicalSemantics, Tag): _str_ = 'Hyponymy'
class Hypernymy(LexicalSemantics, Tag): _str_ = 'Hypernymy'
class Synonymy(LexicalSemantics, Tag): _str_ = 'Synonymy'
class Meronymy(LexicalSemantics, Tag): _str_ = 'Meronymy'
class Antonymy(LexicalSemantics, Tag): _str_ = 'Antonymy'
class MorphologicalModification(LexicalEntailment, Tag): _str_ = 'Morphological Modification'
class SymmetryCollectivity(LexicalEntailment, Tag): _str_ = 'Symmetry/Collectivity'
class Factivity(LexicalEntailment): _str_ = 'Factivity'
class Factive(Factivity, Tag): _str_ = 'Factive'
class NonFactive(Factivity, Tag): _str_ = 'Non-Factive'
class Redundancy(LexicalEntailment, Tag): _str_ = 'Redundancy'
class FAO(LexicalEntailment, Tag): _str_ = 'FAO'


# Predicate-Argument Structure
class PredicateArgumentStructure(metaclass=TagBase): _str_ = 'Predicate-Argument Structure'
class SyntacticAmbiguity(PredicateArgumentStructure, Tag): _str_ = 'Syntactic Ambiguity'
class CoreArguments(PredicateArgumentStructure, Tag): _str_ = 'Core Arguments'
class Alternations(PredicateArgumentStructure, Tag): _str_ = 'Alternations'
class Ellipsis(PredicateArgumentStructure, Tag): _str_ = 'Ellipsis'
class AnaphoraCoreference(PredicateArgumentStructure, Tag): _str_ = 'Anaphora/Coreference'
class Intersectivity(PredicateArgumentStructure): _str_ = 'Intersectivity'
class Intersective(Intersectivity, Tag): _str_ = 'Intersective'
class NonIntersective(Intersectivity, Tag): _str_ = 'Non-Intersective'
class Restrictivity(PredicateArgumentStructure): _str_ = 'Restrictivity'
class Restrictive(Restrictivity, Tag): _str_ = 'Restrictive'
class NonRestrictive(Restrictivity, Tag): _str_ = 'Non-Restrictive'


# Logic
class Logic(metaclass=TagBase): _str_ = 'Logic'
class SingleNegation(Logic, Tag): _str_ = 'Single Negation'
class MultipleNegations(Logic, Tag): _str_ = 'Multiple Negations'
class Conjunction(Logic, Tag): _str_ = 'Conjunction'
class Disjunction(Logic, Tag): _str_ = 'Disjunction'
class Conditionals(Logic, Tag): _str_ = 'Conditionals'
class NegativeConcord(Logic, Tag): _str_ = 'Negative Concord'
class Quantification(Logic): _str_ = 'Quantification'
class Universal(Quantification, Tag): _str_ = 'Universal'
class Existential(Quantification, Tag): _str_ = 'Existential'
class NonStandard(Quantification, Tag): _str_ = 'Non-Standard'
class Comparatives(Logic, Tag): _str_ = 'Comparatives'
class Temporal(Logic, Tag): _str_ = 'Temporal'


# CSK
class CSK(metaclass=TagBase): _str_ = 'Common Sense/Knowledge'


def supertypes(x: TagBase | Type[Tag]) -> tuple[TagBase, ...]:
    return tuple(ancestor for ancestor in x.mro() if ancestor not in {ABC, TagBase, object, Tag})  # type: ignore


def union_of_supertypes(xs: set[TagBase | Type[Tag]]) -> set[TagBase]:
    return {ancestor for x in xs for ancestor in supertypes(x)}


# a map from plain strings to final tags
_str_to_tag: dict[str, Type[Tag]] = {
    'Hyponymy': Hyponymy,
    'Hypernymy': Hypernymy,
    'Antonymy': Antonymy,
    'Meronymy': Meronymy,
    'Synonymy': Synonymy,
    'Morphological Modification': MorphologicalModification,
    'Factive': Factive,
    'Non-Factive': NonFactive,
    'Symmetry/Collectivity': SymmetryCollectivity,
    'Redundancy': Redundancy,
    'FAO': FAO,
    'Syntactic Ambiguity': SyntacticAmbiguity,
    'Core Arguments': CoreArguments,
    'Alternations': Alternations,
    'Ellipsis': Ellipsis,
    'Anaphora/Coreference': AnaphoraCoreference,
    'Intersective': Intersective,
    'Non-Intersective': NonIntersective,
    'Restrictive': Restrictive,
    'Non-Restrictive': NonRestrictive,
    'Single Negation': SingleNegation,
    'Multiple Negations': MultipleNegations,
    'Conjunction': Conjunction,
    'Disjunction': Disjunction,
    'Conditionals': Conditionals,
    'Negative Concord': NegativeConcord,
    'Universal': Universal,
    'Existential': Existential,
    'Non-Standard': NonStandard,
    'Comparatives': Comparatives,
    'Temporal': Temporal,
    'Common Sense/Knowledge': CSK,
}


def str_to_tag(x: str) -> Type[Tag]: return _str_to_tag[x]