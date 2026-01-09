# -*- coding: utf-8 -*-
"""
복합명사 분리 - 강승식(1998) 알고리즘 기반

조사 분리 -> 후보 생성 -> 점수 계산 -> 최적 선택 -> 조사 재부착
"""

from dataclasses import dataclass
from typing import List
import re

from .lexicon import Lexicon
from .josa import split_josa, is_valid_stem, attach_josa_to_last_token


@dataclass
class SplitCandidate:
    tokens: List[str]
    score: float

    def __str__(self):
        return f"{self.tokens} ({self.score:.2f})"


class CompoundNounSplitter:
    def __init__(self, lexicon: Lexicon, min_length=4, max_length=20):
        self.lexicon = lexicon
        self.min_length = min_length
        self.max_length = max_length

    def split(self, text: str, debug: bool = False) -> List[str]:
        """복합명사를 의미 단위로 쪼갬"""
        # 조사 먼저 떼어냄 (있으면)
        stem, josa = split_josa(text)

        if josa and is_valid_stem(stem):
            tokens = self._split_stem(stem, debug=debug)
            return attach_josa_to_last_token(tokens, josa)
        else:
            return self._split_stem(text, debug=debug)

    def _split_stem(self, stem: str, debug: bool = False) -> List[str]:
        """어간 분리 (조사 떼어낸 상태)"""
        # 분해 대상이 아니면 그대로 반환
        if not self._should_split(stem):
            return [stem]

        # nosplit 리스트에 있으면 분해 금지
        if self.lexicon.is_nosplit(stem):
            return [stem]

        # 여러 분해 방법 생성
        candidates = self._generate_candidates(stem)
        if not candidates:
            return [stem]

        # 디버그: 상위 후보 출력
        if debug:
            sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)[:5]
            print(f"\n[DEBUG] Candidates for '{stem}':")
            for i, cand in enumerate(sorted_candidates, 1):
                print(f"  {i}. {' + '.join(cand.tokens):30s} → score={cand.score:.2f}")

        # 점수가 가장 높은 거 선택
        best = max(candidates, key=lambda c: c.score)

        # 그래도 안 쪼개는 게 나으면 원본 유지
        if len(best.tokens) == 1 or best.score <= 0:
            return [stem]

        return best.tokens

    def _should_split(self, text: str) -> bool:
        """분해할지 말지 결정"""
        # 한글 아니면 패스
        if not re.match(r"^[가-힣]+$", text):
            return False

        # 너무 짧거나 길면 안 함
        if len(text) < self.min_length or len(text) > self.max_length:
            return False

        # 이미 사전에 있으면 그대로 둠
        if self.lexicon.is_noun(text):
            return False

        # 법률 용어도 건드리지 않음
        if self.lexicon.is_legal_term(text):
            return False

        return True

    def _generate_candidates(self, text: str) -> List[SplitCandidate]:
        """
        분해 후보 생성 (재귀적 분해)

        Algorithm:
        - 왼쪽부터 greedy하게 사전에 있는 명사를 찾아 분해
        - 끝 1음절 특례: 마지막 위치에서만 end_mono_nouns 허용

        Args:
            text: 분해할 텍스트

        Returns:
            분해 후보 리스트
        """
        candidates = []

        # 1. 분해하지 않는 경우 (baseline)
        candidates.append(SplitCandidate(tokens=[text], score=0.0))

        # 2. 재귀적 분해
        def recursive_split(remaining: str, tokens: List[str]):
            if not remaining:
                # 종료 조건: 모두 분해됨
                score = self._score_candidate(tokens)
                candidates.append(SplitCandidate(tokens=tokens, score=score))
                return

            # 왼쪽부터 가능한 분리 찾기
            # Legal term이 있으면 우선적으로 고려하지만, 다른 후보도 생성
            for i in range(1, len(remaining) + 1):
                left = remaining[:i]
                right = remaining[i:]

                # Legal term이면 우선 처리
                is_legal = self.lexicon.is_legal_term(left)

                # left가 유효한 토큰인지 확인 (마지막 위치 여부 전달)
                is_final = (len(right) == 0)
                if is_legal or self._is_valid_token(left, is_final=is_final):
                    recursive_split(right, tokens + [left])

        recursive_split(text, [])

        return candidates

    def _is_valid_token(self, token: str, is_final: bool = False) -> bool:
        """
        토큰이 유효한 단위명사인지 확인

        Args:
            token: 확인할 토큰
            is_final: 마지막 위치 여부 (끝 1음절 특례 판단용)

        Returns:
            유효 여부
        """
        # 2음절 이상: 사전에 있거나 head noun 패턴 (X+나무)
        if len(token) >= 2:
            # 법률 용어면 항상 유효 (합쳐진 상태로 유지)
            if self.lexicon.is_legal_term(token):
                return True

            # 사전에 있으면 OK
            if self.lexicon.is_noun(token):
                return True

            # Head noun 패턴 인식: 마지막 1~2음절이 head noun이면 OK
            # 예: "자작나무" → "나무"가 head noun이고 "자작"이 사전에 있는 명사
            # 단, prefix도 사전에 있어야 함 (임의 조합 방지)
            for suffix_len in [1, 2]:
                if len(token) > suffix_len:
                    suffix = token[-suffix_len:]
                    prefix = token[:-suffix_len]
                    # suffix가 head noun이고, prefix가 사전에 있는 명사이면 유효
                    if self.lexicon.is_head_noun(suffix) and self.lexicon.is_noun(prefix):
                        return True

            return False

        # 1음절: 마지막 위치이고 end_mono_nouns에 있어야 함
        if len(token) == 1:
            if is_final and self.lexicon.is_end_mono_allowed(token):
                return True
            return False

        return False

    def _score_candidate(self, tokens: List[str]) -> float:
        """
        후보 점수 계산

        Heuristics:
        - 토큰 개수가 적을수록 좋음 (과분해 방지)
        - 긴 토큰을 선호 (의미 보존)
        - 1음절 토큰은 페널티 (끝 1음절은 약한 페널티)
        - 모든 토큰이 사전에 있으면 보너스
        - Head noun이 중간 위치에 오면 페널티 (끝 위치는 정상)

        Args:
            tokens: 분해된 토큰 리스트

        Returns:
            점수 (높을수록 좋음)
        """
        if not tokens:
            return 0.0

        score = 0.0

        # 1. 토큰 개수 페널티 (많이 쪼갤수록 감점) - GPT 제안: 더 강하게
        score -= len(tokens) * 1.0  # 0.5 → 1.0으로 증가

        # 2. 평균 토큰 길이 보너스 (긴 단어 선호)
        avg_len = sum(len(t) for t in tokens) / len(tokens)
        score += avg_len * 2.0  # 1.0 → 2.0으로 증가 (긴 토큰 강하게 선호)

        # 3. 1음절 토큰 페널티
        for i, t in enumerate(tokens):
            if len(t) == 1:
                # 마지막 1음절은 약한 페널티
                if i == len(tokens) - 1:
                    score -= 0.5
                else:
                    # 중간 1음절은 강한 페널티
                    score -= 2.0

        # 4. 모든 토큰이 사전에 있으면 보너스
        # Note: head noun 패턴도 "유효한 토큰"으로 간주
        def is_valid_in_dict(t):
            if len(t) >= 2:
                # 사전에 있거나 head noun 패턴이면 OK
                if self.lexicon.is_noun(t):
                    return True
                # Head noun 패턴 체크: prefix도 사전에 있어야 함
                for suffix_len in [1, 2]:
                    if len(t) > suffix_len:
                        suffix = t[-suffix_len:]
                        prefix = t[:-suffix_len]
                        if self.lexicon.is_head_noun(suffix) and self.lexicon.is_noun(prefix):
                            return True
                return False
            else:
                return self.lexicon.is_end_mono_allowed(t)

        all_valid = all(is_valid_in_dict(t) for t in tokens)
        if all_valid:
            score += 2.0

        # 4.5. Legal term 보너스 (법률 용어 우선)
        for token in tokens:
            if self.lexicon.is_legal_term(token):
                score += 3.0  # 강한 보너스로 legal term 우선

        # 5. Head noun 위치 기반 점수
        # Head noun은 끝에 오는 게 자연스러움 (예: [자작나무][숲] OK, [자작][나무][숲] NG)
        for i, token in enumerate(tokens):
            if self.lexicon.is_head_noun(token):
                if i < len(tokens) - 1:
                    # 중간 위치: 페널티
                    score -= 3.0
                else:
                    # 끝 위치: 보너스 (1음절 페널티를 상쇄하고 약간 더)
                    score += 1.0

        return score
