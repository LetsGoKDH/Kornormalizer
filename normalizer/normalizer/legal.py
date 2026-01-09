# -*- coding: utf-8 -*-
"""
Legal Context Detection and Handling

법률 문맥 감지 및 법률 용어 보호 모듈
"""

from __future__ import annotations
from typing import Set, List, Tuple
from pathlib import Path
import re


class LegalTerms:
    """법률 용어 사전"""

    def __init__(self, strict_terms: Set[str]):
        self.strict_terms = strict_terms

    @classmethod
    def from_file(cls, strict_path: Path) -> LegalTerms:
        """파일에서 법률 용어 로드"""
        strict_terms = set()

        if strict_path.exists():
            with open(strict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    term = line.strip()
                    if term:
                        strict_terms.add(term)

        return cls(strict_terms)

    def is_legal_term(self, term: str) -> bool:
        """정확 매칭: 용어가 법률 용어인지 확인"""
        return term in self.strict_terms


class LegalSpanDetector:
    """
    법률 문맥 감지기 (휴리스틱 기반)

    점수 기반으로 문장/토큰 구간이 법률 문맥인지 판단
    """

    # 강한 신호 패턴
    ARTICLE_PATTERNS = [
        r'제\s*\d+\s*조',
        r'제\s*\d+\s*항',
        r'제\s*\d+\s*호',
        r'제\s*\d+\s*목',
        # 숫자 변환 후 패턴
        r'제\s+[일이삼사오육칠팔구십백천만억]+\s+조',
        r'제\s+[일이삼사오육칠팔구십백천만억]+\s+항',
        r'제\s+[일이삼사오육칠팔구십백천만억]+\s+호',
    ]

    LAW_SUFFIXES = [
        '시행령', '시행규칙', '대통령령', '총리령', '부령',
        '조례', '규칙', '고시', '훈령', '예규', '헌법', '법률',
    ]

    # 중간 신호 키워드
    LEGAL_KEYWORDS = [
        '법원', '검찰', '검사', '재판', '판결', '기소', '항소', '상고',
        '구속', '영장', '혐의', '수사', '입건', '송치', '공소', '선고',
        '헌재', '위헌', '합헌', '피고', '원고', '변호사', '변호인',
    ]

    # 오탐 억제 키워드 (일반어)
    FALSE_POSITIVE_WORDS = [
        '방법', '사용법', '해법', '문법', '기법', '수법', '활용법', '공부법',
    ]

    def __init__(self, legal_terms: Set[str] = None):
        # 조문 패턴 컴파일
        self.article_regex = [re.compile(p) for p in self.ARTICLE_PATTERNS]
        # 법률 용어 사전
        self.legal_terms = legal_terms if legal_terms else set()

    def calculate_score(self, text: str) -> float:
        """
        텍스트의 법률 문맥 점수 계산

        Returns:
            점수 (높을수록 법률 문맥 가능성 높음)
        """
        score = 0.0

        # 1. 조문 패턴 (+5)
        for regex in self.article_regex:
            if regex.search(text):
                score += 5
                break  # 중복 카운트 방지

        # 2. 법령 접미사 (+3)
        for suffix in self.LAW_SUFFIXES:
            if suffix in text:
                score += 3
                break

        # 3. 법률 용어 사전 매칭 (+4)
        for term in self.legal_terms:
            if len(term) >= 4 and term in text:  # 4글자 이상만
                score += 4
                break

        # 4. 법률 키워드 (+1, 최대 3)
        keyword_count = sum(1 for kw in self.LEGAL_KEYWORDS if kw in text)
        score += min(keyword_count, 3)

        # 5. 오탐 억제 (-3)
        for word in self.FALSE_POSITIVE_WORDS:
            if word in text:
                score -= 3
                break

        return score

    def is_legal_context(self, text: str, threshold: float = 5.0) -> bool:
        """
        텍스트가 법률 문맥인지 판단

        Args:
            text: 판단할 텍스트
            threshold: 점수 임계값 (기본 5.0)

        Returns:
            법률 문맥 여부
        """
        score = self.calculate_score(text)
        return score >= threshold

    def detect_spans(self, tokens: List[str], window_size: int = 5) -> List[Tuple[int, int]]:
        """
        토큰 리스트에서 법률 구간(span) 감지

        Args:
            tokens: 토큰 리스트
            window_size: 윈도우 크기 (전후 토큰 몇 개씩 볼지)

        Returns:
            [(start_idx, end_idx), ...] 법률 구간 인덱스 리스트
        """
        legal_spans = []

        for i in range(len(tokens)):
            # 윈도우 추출 (현재 토큰 기준 전후)
            start = max(0, i - window_size)
            end = min(len(tokens), i + window_size + 1)
            window_text = " ".join(tokens[start:end])

            # 점수 계산
            score = self.calculate_score(window_text)

            if score >= 4.0:  # 윈도우는 임계값 낮춤
                legal_spans.append((start, end))

        # 겹치는 span 병합
        if not legal_spans:
            return []

        merged = []
        current_start, current_end = legal_spans[0]

        for start, end in legal_spans[1:]:
            if start <= current_end:  # 겹침
                current_end = max(current_end, end)
            else:  # 새로운 span
                merged.append((current_start, current_end))
                current_start, current_end = start, end

        merged.append((current_start, current_end))
        return merged
