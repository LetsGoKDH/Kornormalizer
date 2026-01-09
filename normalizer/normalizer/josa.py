# -*- coding: utf-8 -*-
"""
한국어 조사 분리 모듈

복합명사 + 조사 형태를 처리하기 위한 조사 분리 기능
예: "자작나무숲이" → stem="자작나무숲", josa="이"
"""

from typing import Optional, Tuple


# 한국어 조사 목록 (longest-match 우선순위 순서)
KOREAN_JOSA = [
    # 3음절 조사
    "에서부터",
    "으로부터",
    "로부터",

    # 2음절 조사
    "에서",
    "에게",
    "한테",
    "보다",
    "처럼",
    "마저",
    "조차",
    "까지",
    "부터",
    "에도",
    "에야",
    "에만",
    "만큼",
    "밖에",
    "대로",
    "따라",

    # 2음절 격조사
    "으로",
    "에는",
    "에도",
    "에서",
    "에게",
    "에서",
    "와는",
    "과는",
    "이나",
    "이든",
    "이라",
    "이며",
    "이면",
    "이야",
    "이요",

    # 1음절 조사
    "은",
    "는",
    "이",
    "가",
    "을",
    "를",
    "과",
    "와",
    "에",
    "도",
    "만",
    "나",
    "든",
    "야",
    "요",
]


def split_josa(token: str) -> Tuple[str, str]:
    """
    토큰에서 조사를 분리

    Args:
        token: 입력 토큰 (예: "자작나무숲이")

    Returns:
        (stem, josa): 어간과 조사 튜플
                     조사가 없으면 (token, "")

    Examples:
        >>> split_josa("자작나무숲이")
        ("자작나무숲", "이")
        >>> split_josa("데이터베이스에서")
        ("데이터베이스", "에서")
        >>> split_josa("컴퓨터")
        ("컴퓨터", "")
    """
    if len(token) < 2:
        return (token, "")

    # Longest-match: 긴 조사부터 매칭 시도
    for josa in KOREAN_JOSA:
        if token.endswith(josa):
            stem = token[:-len(josa)]

            # Stem이 최소 길이(2) 이상이어야 유효
            if len(stem) >= 2:
                return (stem, josa)

    return (token, "")


def is_valid_stem(stem: str, min_len: int = 2) -> bool:
    """
    분리된 어간이 유효한지 검사

    Args:
        stem: 어간
        min_len: 최소 길이

    Returns:
        유효 여부
    """
    if len(stem) < min_len:
        return False

    # 한글만으로 구성되어 있는지 확인
    if not all('가' <= c <= '힣' for c in stem):
        return False

    return True


def attach_josa_to_last_token(tokens: list[str], josa: str) -> list[str]:
    """
    분리된 토큰 리스트의 마지막 단어에 조사 재부착

    Args:
        tokens: 분리된 토큰 리스트 (예: ["자작나무", "숲"])
        josa: 조사 (예: "이")

    Returns:
        조사가 부착된 토큰 리스트 (예: ["자작나무", "숲이"])

    Examples:
        >>> attach_josa_to_last_token(["자작나무", "숲"], "이")
        ["자작나무", "숲이"]
        >>> attach_josa_to_last_token(["데이터베이스"], "")
        ["데이터베이스"]
    """
    if not tokens:
        return tokens

    if josa:
        result = tokens[:-1] + [tokens[-1] + josa]
        return result

    return tokens


def should_split_josa(token: str) -> bool:
    """
    토큰에서 조사 분리를 시도해야 하는지 판단

    Args:
        token: 입력 토큰

    Returns:
        조사 분리 시도 여부
    """
    # 최소 길이 체크 (조사 1음절 + 어간 2음절 = 최소 3음절)
    if len(token) < 3:
        return False

    # 한글만으로 구성되어 있는지 확인
    if not all('가' <= c <= '힣' for c in token):
        return False

    return True


# 테스트용 함수
def test_josa_split():
    """조사 분리 테스트"""
    test_cases = [
        ("자작나무숲이", ("자작나무숲", "이")),
        ("형사사법기구를", ("형사사법기구", "를")),
        ("데이터베이스에서", ("데이터베이스", "에서")),
        ("컴퓨터", ("컴퓨터", "")),
        ("숲", ("숲", "")),
        ("가", ("가", "")),
    ]

    print("=== 조사 분리 테스트 ===")
    for input_token, expected in test_cases:
        result = split_josa(input_token)
        status = "OK" if result == expected else "FAIL"
        print(f"{status} {input_token} -> stem={result[0]}, josa={result[1]}")
        if result != expected:
            print(f"  Expected: {expected}")


if __name__ == "__main__":
    test_josa_split()
