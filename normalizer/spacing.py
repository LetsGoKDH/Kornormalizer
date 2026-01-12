# -*- coding: utf-8 -*-
"""
의존명사 띄어쓰기 (Dependent Noun Spacing)

관형형 어미 + 의존명사 패턴을 찾아 띄어쓰기를 삽입합니다.
예: "할수있다" → "할 수 있다", "같은것" → "같은 것"
"""

import re


# 한글 유니코드 상수
HANGUL_BASE = 0xAC00
HANGUL_END = 0xD7A3

# 종성 인덱스 (0=없음, 4=ㄴ, 8=ㄹ)
JONGSEONG_N = 4   # ㄴ
JONGSEONG_L = 8   # ㄹ


def get_jongseong(char: str) -> int:
    """한글 글자의 종성 인덱스를 반환 (종성 없으면 0)"""
    if len(char) != 1:
        return -1
    code = ord(char)
    if not (HANGUL_BASE <= code <= HANGUL_END):
        return -1
    return (code - HANGUL_BASE) % 28


def has_jongseong_n(char: str) -> bool:
    """종성이 ㄴ인지 확인"""
    return get_jongseong(char) == JONGSEONG_N


def has_jongseong_l(char: str) -> bool:
    """종성이 ㄹ인지 확인"""
    return get_jongseong(char) == JONGSEONG_L


def ends_with_neun(char: str) -> bool:
    """'는'으로 끝나는지 확인 (현재 관형형)"""
    return char == '는'


# 의존명사별 허용되는 앞글자 조건
# key: 의존명사
# value: (check_function, description)
DEPENDENT_NOUNS = {
    # 수: ㄹ 받침 뒤에서만 (가장 엄격 - 오탐 방지)
    '수': (has_jongseong_l, "ㄹ 받침"),

    # 리, 터: ㄹ 받침 뒤
    '리': (has_jongseong_l, "ㄹ 받침"),
    '터': (has_jongseong_l, "ㄹ 받침"),

    # 것, 바, 듯, 뿐, 줄, 지, 데: ㄴ/ㄹ 받침 또는 '는' 뒤
    '것': (lambda c: has_jongseong_n(c) or has_jongseong_l(c) or ends_with_neun(c), "관형형"),
    '바': (lambda c: has_jongseong_n(c) or has_jongseong_l(c) or ends_with_neun(c), "관형형"),
    '듯': (lambda c: has_jongseong_n(c) or has_jongseong_l(c) or ends_with_neun(c), "관형형"),
    '뿐': (lambda c: has_jongseong_n(c) or has_jongseong_l(c), "ㄴ/ㄹ 받침"),
    '줄': (lambda c: has_jongseong_n(c) or has_jongseong_l(c) or ends_with_neun(c), "관형형"),
    '지': (lambda c: has_jongseong_n(c) or has_jongseong_l(c) or ends_with_neun(c), "관형형"),
    '데': (lambda c: has_jongseong_n(c) or has_jongseong_l(c) or ends_with_neun(c), "관형형"),
}

# 의존명사 뒤에 올 수 있는 조사/어미/동사 패턴
PARTICLES = [
    # 조사
    '은', '는', '이', '가', '을', '를', '도', '만', '조차', '마저', '까지',
    '처럼', '같이', '보다', '에', '에서', '로', '으로', '와', '과', '랑',
    '밖에', '뿐이다', '인데', '록',  # ~할수록
    # 어미/활용형
    '이다', '이라', '이고', '이며', '이니', '이면', '이야', '이지',
    '인', '일', '임',
    # 있다/없다 계열
    '있다', '있는', '있을', '있으면', '있으니', '있어', '있고', '있지', '있나',
    '없다', '없는', '없을', '없으면', '없으니', '없어', '없고', '없지', '없나',
    # 알다/모르다 계열 (할 줄 알다)
    '알다', '알았다', '알고', '알면', '아는', '알아',
    '모르다', '몰랐다', '모르고', '모르면', '모르는', '몰라',
    # 되다 계열 (한 지 오래 됐다 → 일단 '오래'는 제외)
    '됐다', '되다', '되면', '되고', '되는', '돼',
    # 하다 계열 (듯하다, 듯이)
    '하다', '한다', '해서', '하고', '하면', '해',
    '싶다', '싶어', '싶은', '싶으면',
    # 시간 관련 (한 지 오래됐다)
    '오래', '얼마', '한참', '꽤', '벌써', '이미', '아직',
]


def apply_dependent_noun_spacing(text: str) -> str:
    """
    의존명사 앞에 띄어쓰기를 삽입합니다.

    Args:
        text: 입력 텍스트

    Returns:
        의존명사가 띄어쓰기된 텍스트
    """
    result = text

    for dep_noun, (check_func, _) in DEPENDENT_NOUNS.items():
        # 의존명사 + 조사/어미 패턴
        for particle in PARTICLES:
            pattern = f'([가-힣])({dep_noun}{particle})'
            result = _apply_spacing(result, pattern, check_func)

        # 의존명사만 (뒤에 공백이나 문장부호가 오는 경우)
        pattern = f'([가-힣])({dep_noun})(?=\\s|[.,!?]|$)'
        result = _apply_spacing(result, pattern, check_func)

    return result


def _apply_spacing(text: str, pattern: str, check_func) -> str:
    """패턴을 찾아 조건에 맞으면 띄어쓰기 삽입"""
    def replacer(match):
        prev_char = match.group(1)
        rest = match.group(2)

        # 앞 글자가 조건에 맞으면 띄어쓰기 삽입
        if check_func(prev_char):
            return f'{prev_char} {rest}'
        return match.group(0)

    return re.sub(pattern, replacer, text)


if __name__ == '__main__':
    # 테스트
    test_cases = [
        "할수있다",          # → 할 수 있다
        "될수록",            # → 될 수록
        "같은것이",          # → 같은 것이
        "하는것을",          # → 하는 것을
        "있을뿐이다",        # → 있을 뿐이다
        "하는바와같이",      # → 하는 바와 같이
        "할줄알았다",        # → 할 줄 알았다
        "한지오래됐다",      # → 한 지 오래됐다
        "있는데",            # → 있는 데
        "할리없다",          # → 할 리 없다
        "수학",              # → 수학 (변경 없음)
        "수도권",            # → 수도권 (변경 없음)
    ]

    print("의존명사 띄어쓰기 테스트:")
    for text in test_cases:
        result = apply_dependent_noun_spacing(text)
        changed = "O" if result != text else "X"
        print(f"  [{changed}] {text} → {result}")
