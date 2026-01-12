# -*- coding: utf-8 -*-
"""
Korean Text Normalizer

한국어 텍스트 정규화 패키지 (TTS 전처리용)
- 숫자 -> 한글 (2024 -> 이천 이십사)
- 영문 -> 한글 (KDH -> 케이 디 에이치)
- 복합명사 분리 (데이터베이스시스템 -> 데이터베이스 시스템)
- 의존명사 띄어쓰기 (할수있다 -> 할 수 있다)
"""

from .lexicon import Lexicon
from .transforms import (
    normalize,
    convert_numbers,
    convert_alphabet,
    split_compounds,
    apply_spacing,
)

__version__ = "1.0.0"
__all__ = [
    "Lexicon",
    "normalize",
    "convert_numbers",
    "convert_alphabet",
    "split_compounds",
    "apply_spacing",
]
