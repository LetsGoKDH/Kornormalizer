# -*- coding: utf-8 -*-
"""
Integrated Korean Text Normalizer

Features:
1. Number to Korean (2024 -> 이천 이십사)
2. Alphabet to Korean (KDH -> 케이 디 에이치)
3. Compound noun splitting (데이터베이스시스템 -> 데이터베이스 시스템)
4. Spacing normalization
"""

from __future__ import annotations
from typing import List, Optional, Tuple
import re

from .lexicon import Lexicon
from .splitter import CompoundNounSplitter
from .num2kor import NumberToKorean
from .alpha2kor import AlphabetToKorean
from .legal import LegalSpanDetector


def _tokenize_with_punct(text: str) -> List[Tuple[str, str]]:
    """
    텍스트를 (토큰, 타입)으로 분리

    타입: 'hangul', 'other'
    예: "자작나무숲," → [("자작나무숲", "hangul"), (",", "other")]
    """
    # 한글 덩어리 vs 나머지
    pattern = r'([가-힣]+)|([^가-힣]+)'
    tokens = []
    for match in re.finditer(pattern, text):
        if match.group(1):  # 한글
            tokens.append((match.group(1), 'hangul'))
        else:  # 나머지 (구두점, 숫자, 영문, 공백 등)
            tokens.append((match.group(2), 'other'))
    return tokens


class KoreanNormalizer:
    """통합 한국어 정규화기"""
    
    def __init__(
        self,
        lexicon: Optional[Lexicon] = None,
        enable_number: bool = True,
        enable_alphabet: bool = True,
        enable_compound_split: bool = True,
        enable_spacing: bool = True,
        enable_legal_span: bool = True,
    ):
        """
        Args:
            lexicon: 사전 (compound split에 필요)
            enable_number: 숫자 변환 활성화
            enable_alphabet: 알파벳 변환 활성화
            enable_compound_split: 복합명사 분리 활성화
            enable_spacing: 띄어쓰기 정규화 활성화
            enable_legal_span: 법률 구간 감지 활성화 (기본 True, lexicon 있을 때만)
        """
        self.lexicon = lexicon
        self.enable_number = enable_number
        self.enable_alphabet = enable_alphabet
        self.enable_compound_split = enable_compound_split
        self.enable_spacing = enable_spacing
        self.enable_legal_span = enable_legal_span

        # 변환기 초기화
        if self.enable_number:
            self.num_converter = NumberToKorean()

        if self.enable_alphabet:
            self.alpha_converter = AlphabetToKorean()

        if self.enable_compound_split and lexicon:
            self.splitter = CompoundNounSplitter(lexicon, min_length=4)

        # 법률 span 감지기 (lexicon 있을 때만)
        if self.enable_legal_span and lexicon:
            self.legal_detector = LegalSpanDetector(legal_terms=lexicon.legal_terms)
        else:
            self.legal_detector = None
    
    def normalize(self, text: str, debug: bool = False) -> str:
        """
        텍스트 정규화 메인 함수
        
        Args:
            text: 입력 텍스트
            debug: 디버그 모드 (단계별 출력)
        
        Returns:
            정규화된 텍스트
        """
        if debug:
            print(f"[Original] {text}")
        
        # 1. 알파벳 변환 (약어만)
        if self.enable_alphabet:
            text = self.alpha_converter.convert_acronyms(text)
            if debug:
                print(f"[Alphabet] {text}")
        
        # 2. 숫자 변환
        if self.enable_number:
            text = self.num_converter.convert(text)
            if debug:
                print(f"[Number] {text}")
        
        # 3. 복합명사 분리 (어절 단위로)
        if self.enable_compound_split and self.lexicon:
            text = self._split_compounds_in_text(text)
            if debug:
                print(f"[Compound] {text}")
        
        # 4. 띄어쓰기 정규화
        if self.enable_spacing:
            text = self._normalize_spacing(text)
            if debug:
                print(f"[Spacing] {text}")
        
        return text
    
    def _split_compounds_in_text(self, text: str) -> str:
        """
        텍스트 내의 복합명사를 분리

        구두점 분리 후 한글 덩어리만 처리:
        - 4글자 이상 한글
        - 법률 span 내부는 보호
        - 구두점은 원위치 유지
        """
        # 1. 한글/구두점 분리
        tokens_with_type = _tokenize_with_punct(text)

        # 2. 한글 토큰만 추출
        hangul_tokens = [tok for tok, typ in tokens_with_type if typ == 'hangul']

        # 3. 토큰 처리 (Splitter가 legal term을 자체적으로 인식함)
        result = []

        for token, typ in tokens_with_type:
            if typ == 'hangul':
                # 길이 4 이상이면 분리 시도 (Splitter가 legal term 처리)
                if len(token) >= 4:
                    split_result = self.splitter.split(token)
                    result.append(" ".join(split_result))
                else:
                    result.append(token)
            else:
                # 구두점/공백/기타는 그대로
                result.append(token)

        return "".join(result)
    
    def _normalize_spacing(self, text: str) -> str:
        """
        띄어쓰기 정규화
        
        - 연속 공백 제거
        - 문장부호 앞뒤 공백 정리
        """
        # 연속 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        return text


# 편의 함수
def normalize(text: str, lexicon: Optional[Lexicon] = None, debug: bool = False) -> str:
    """
    간단한 정규화 함수

    Args:
        text: 입력 텍스트
        lexicon: 사전 (없으면 compound split 비활성화)
        debug: 디버그 모드

    Returns:
        정규화된 텍스트

    Examples:
        >>> normalize("2024년 1월")
        "이천 이십사 년 일 월"

        >>> normalize("KDH 프로젝트")
        "케이 디 에이치 프로젝트"
    """
    normalizer = KoreanNormalizer(
        lexicon=lexicon,
        enable_number=True,
        enable_alphabet=True,
        enable_compound_split=(lexicon is not None),
        enable_spacing=True,
    )

    return normalizer.normalize(text, debug=debug)
