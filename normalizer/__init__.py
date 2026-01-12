# -*- coding: utf-8 -*-
"""Korean Text Normalizer with Compound Noun Splitting"""

from .lexicon import Lexicon
from .splitter import CompoundNounSplitter
from .num2kor import NumberToKorean
from .alpha2kor import AlphabetToKorean
from .legal import LegalTerms, LegalSpanDetector
from .normalizer import KoreanNormalizer, normalize
from .spacing import apply_dependent_noun_spacing

__version__ = "0.3.0"
__all__ = [
    "Lexicon",
    "CompoundNounSplitter",
    "NumberToKorean",
    "AlphabetToKorean",
    "LegalTerms",
    "LegalSpanDetector",
    "KoreanNormalizer",
    "normalize",
    "apply_dependent_noun_spacing",
]
