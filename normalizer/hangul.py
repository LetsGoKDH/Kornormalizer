# -*- coding: utf-8 -*-
"""
한글 유틸리티 함수

한글 유니코드 분석 및 조사 처리
"""

from typing import Tuple, List

# ============================================================
# 한글 유니코드 상수
# ============================================================

HANGUL_BASE = 0xAC00
HANGUL_END = 0xD7A3

# 종성 인덱스
JONGSEONG_NONE = 0
JONGSEONG_N = 4   # ㄴ
JONGSEONG_L = 8   # ㄹ


# ============================================================
# 한글 분석 함수
# ============================================================

def get_jongseong(char: str) -> int:
    """한글 글자의 종성 인덱스 반환 (종성 없으면 0, 한글 아니면 -1)"""
    if len(char) != 1:
        return -1
    code = ord(char)
    if not (HANGUL_BASE <= code <= HANGUL_END):
        return -1
    return (code - HANGUL_BASE) % 28


def has_jongseong(char: str) -> bool:
    """받침이 있는지 확인"""
    return get_jongseong(char) > 0


def has_jongseong_n(char: str) -> bool:
    """종성이 ㄴ인지 확인"""
    return get_jongseong(char) == JONGSEONG_N


def has_jongseong_l(char: str) -> bool:
    """종성이 ㄹ인지 확인"""
    return get_jongseong(char) == JONGSEONG_L


def is_hangul(char: str) -> bool:
    """한글 음절인지 확인"""
    if len(char) != 1:
        return False
    return HANGUL_BASE <= ord(char) <= HANGUL_END


def is_hangul_string(text: str) -> bool:
    """문자열이 전부 한글인지 확인"""
    return all(is_hangul(c) for c in text)


# ============================================================
# 조사 처리
# ============================================================

# 한국어 조사 목록 (longest-match 우선)
JOSA_LIST = [
    # 3음절
    "에서부터", "으로부터", "로부터",
    # 2음절
    "에서", "에게", "한테", "보다", "처럼", "마저", "조차", "까지",
    "부터", "에도", "에야", "에만", "만큼", "밖에", "대로", "따라",
    "으로", "에는", "와는", "과는", "이나", "이든", "이라", "이며",
    "이면", "이야", "이요",
    # 1음절
    "은", "는", "이", "가", "을", "를", "과", "와", "에", "도",
    "만", "나", "든", "야", "요",
]


def split_josa(token: str) -> Tuple[str, str]:
    """
    토큰에서 조사 분리

    Args:
        token: 입력 토큰 (예: "자작나무숲이")

    Returns:
        (stem, josa): 어간과 조사. 조사 없으면 (token, "")

    Examples:
        >>> split_josa("자작나무숲이")
        ("자작나무숲", "이")
    """
    if len(token) < 2:
        return (token, "")

    for josa in JOSA_LIST:
        if token.endswith(josa):
            stem = token[:-len(josa)]
            if len(stem) >= 2:
                return (stem, josa)

    return (token, "")


def attach_josa(tokens: List[str], josa: str) -> List[str]:
    """
    토큰 리스트의 마지막에 조사 부착

    Args:
        tokens: 토큰 리스트 (예: ["자작나무", "숲"])
        josa: 조사 (예: "이")

    Returns:
        조사 부착된 리스트 (예: ["자작나무", "숲이"])
    """
    if not tokens or not josa:
        return tokens
    return tokens[:-1] + [tokens[-1] + josa]
