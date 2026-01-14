# -*- coding: utf-8 -*-
"""
텍스트 변환 함수 모음

모든 변환은 str -> str 형태의 순수 함수
"""

from __future__ import annotations
from typing import List, TYPE_CHECKING
import re

from .hangul import (
    has_jongseong_n, has_jongseong_l,
    split_josa, attach_josa, is_hangul_string,
)

if TYPE_CHECKING:
    from .lexicon import Lexicon


# ============================================================
# 숫자 변환 (Number -> Korean)
# ============================================================

# 상수
_DIGITS = ["영", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
_UNITS_SMALL = ["", "십", "백", "천"]
_UNITS_LARGE = ["", "만", "억", "조", "경"]
_TEXT_UNITS = ["년", "월", "일", "시", "분", "초", "원", "명", "개", "권", "장", "살", "세", "조", "항", "호", "점"]
_NATIVE_UNITS = ["개", "명", "살", "시"]

# 고유어 수사 (1~99)
_NATIVE_NUMS = {
    1: "한", 2: "두", 3: "세", 4: "네", 5: "다섯",
    6: "여섯", 7: "일곱", 8: "여덟", 9: "아홉", 10: "열",
    11: "열 한", 12: "열 두", 13: "열 세", 14: "열 네", 15: "열 다섯",
    16: "열 여섯", 17: "열 일곱", 18: "열 여덟", 19: "열 아홉", 20: "스물",
    21: "스물 한", 22: "스물 두", 23: "스물 세", 24: "스물 네", 25: "스물 다섯",
    26: "스물 여섯", 27: "스물 일곱", 28: "스물 여덟", 29: "스물 아홉", 30: "서른",
    31: "서른 한", 32: "서른 두", 33: "서른 세", 34: "서른 네", 35: "서른 다섯",
    36: "서른 여섯", 37: "서른 일곱", 38: "서른 여덟", 39: "서른 아홉", 40: "마흔",
    41: "마흔 한", 42: "마흔 두", 43: "마흔 세", 44: "마흔 네", 45: "마흔 다섯",
    46: "마흔 여섯", 47: "마흔 일곱", 48: "마흔 여덟", 49: "마흔 아홉", 50: "쉰",
    51: "쉰 한", 52: "쉰 두", 53: "쉰 세", 54: "쉰 네", 55: "쉰 다섯",
    56: "쉰 여섯", 57: "쉰 일곱", 58: "쉰 여덟", 59: "쉰 아홉", 60: "예순",
    61: "예순 한", 62: "예순 두", 63: "예순 세", 64: "예순 네", 65: "예순 다섯",
    66: "예순 여섯", 67: "예순 일곱", 68: "예순 여덟", 69: "예순 아홉", 70: "일흔",
    71: "일흔 한", 72: "일흔 두", 73: "일흔 세", 74: "일흔 네", 75: "일흔 다섯",
    76: "일흔 여섯", 77: "일흔 일곱", 78: "일흔 여덟", 79: "일흔 아홉", 80: "여든",
    81: "여든 한", 82: "여든 두", 83: "여든 세", 84: "여든 네", 85: "여든 다섯",
    86: "여든 여섯", 87: "여든 일곱", 88: "여든 여덟", 89: "여든 아홉", 90: "아흔",
    91: "아흔 한", 92: "아흔 두", 93: "아흔 세", 94: "아흔 네", 95: "아흔 다섯",
    96: "아흔 여섯", 97: "아흔 일곱", 98: "아흔 여덟", 99: "아흔 아홉",
}


def _number_to_korean(num: int) -> str:
    """정수 -> 한글 (한자어 수사)"""
    if num == 0:
        return _DIGITS[0]
    if num < 0:
        return "마이너스 " + _number_to_korean(-num)

    parts = []
    for i, unit in enumerate(_UNITS_LARGE):
        if num == 0:
            break
        chunk = num % 10000
        num //= 10000

        if chunk > 0:
            if chunk == 1 and unit:
                parts.append(unit)
            else:
                chunk_str = _convert_chunk(chunk)
                parts.append(chunk_str + " " + unit if unit else chunk_str)

    return " ".join(reversed(parts))


def _convert_chunk(num: int) -> str:
    """천 단위 이하 (0~9999) -> 한글"""
    if num == 0:
        return ""

    res = []
    if num >= 1000:
        t = num // 1000
        res.append("천" if t == 1 else _DIGITS[t] + "천")
        num %= 1000

    if num >= 100:
        h = num // 100
        res.append("백" if h == 1 else _DIGITS[h] + "백")
        num %= 100

    if num >= 10:
        d = num // 10
        res.append("십" if d == 1 else _DIGITS[d] + "십")
        num %= 10

    if num > 0:
        res.append(_DIGITS[num])

    return " ".join(res)


def convert_numbers(text: str) -> str:
    """
    텍스트 내 숫자를 한글로 변환

    Examples:
        "2024년" -> "이천 이십사 년"
        "15:30" -> "열 다섯 시 삼십 분"
    """
    # 천단위 쉼표 제거
    text = re.sub(r'(\d{1,3}(?:,\d{3})+)', lambda m: m.group(1).replace(',', ''), text)

    # 시간 (15:30 -> 열다섯 시 삼십 분)
    def replace_time(m):
        h, minutes = int(m.group(1)), int(m.group(2))
        h_kor = _NATIVE_NUMS.get(h, _number_to_korean(h)) if 1 <= h <= 99 else _number_to_korean(h)
        m_kor = _number_to_korean(minutes) if minutes > 0 else ""
        return f"{h_kor} 시 {m_kor} 분" if minutes > 0 else f"{h_kor} 시"

    text = re.sub(r'(\d{1,2}):(\d{2})\b', replace_time, text)

    # 소수점 (3.14 -> 삼 점 일 사)
    def replace_decimal(m):
        int_part, dec_part = int(m.group(1)), m.group(2)
        unit = m.group(3) or ""
        kor_int = _number_to_korean(int_part)
        kor_dec = " ".join(_DIGITS[int(d)] for d in dec_part)
        result = f"{kor_int} 점 {kor_dec}"
        return f"{result} {unit}" if unit else result

    text = re.sub(r"(\d+)\.(\d+)([" + "".join(_TEXT_UNITS) + "]?)", replace_decimal, text)

    # 구두점 -> 공백
    for p in ['-', ',', ';', ':', '/']:
        text = text.replace(p, ' ')

    # 천 단위 (5천원 -> 오천 원)
    def replace_cheon(m):
        num, text_unit = int(m.group(1)), m.group(2)
        result = f"{_number_to_korean(num)}천"
        return f"{result} {text_unit}" if text_unit else result

    text = re.sub(r"(\d+)천([" + "".join(_TEXT_UNITS) + "]?)", replace_cheon, text)

    # 큰 단위 (3만원, 100억)
    def replace_large(m):
        num, unit, text_unit = int(m.group(1)), m.group(2), m.group(3)
        result = f"{_number_to_korean(num)} {unit}"
        return f"{result} {text_unit}" if text_unit else result

    text = re.sub(r"(\d+)(만|억|조|경)([" + "".join(_TEXT_UNITS) + "]?)", replace_large, text)

    # 일반 숫자
    def replace_num(m):
        num, unit = int(m.group(1)), m.group(2)
        if unit and unit in _NATIVE_UNITS and 1 <= num <= 99:
            kor = _NATIVE_NUMS.get(num, _number_to_korean(num))
        else:
            kor = _number_to_korean(num)
        return f"{kor} {unit}" if unit else kor

    text = re.sub(r"(\d+)([" + "".join(_TEXT_UNITS) + "]?)", replace_num, text)
    return text


# ============================================================
# 알파벳 변환 (Alphabet -> Korean)
# ============================================================

_ALPHABET_PRON = {
    'A': '에이', 'B': '비', 'C': '씨', 'D': '디', 'E': '이',
    'F': '에프', 'G': '지', 'H': '에이치', 'I': '아이', 'J': '제이',
    'K': '케이', 'L': '엘', 'M': '엠', 'N': '엔', 'O': '오',
    'P': '피', 'Q': '큐', 'R': '알', 'S': '에스', 'T': '티',
    'U': '유', 'V': '브이', 'W': '더블유', 'X': '엑스', 'Y': '와이', 'Z': '지',
    '&': '앤',
}

# 특수 약어 (단어화된 두문자어) - 철자읽기 대신 고정 발음
_SPECIAL_ACRONYMS = {}


def load_special_acronyms(path: str) -> None:
    """특수 약어 매핑 파일 로드"""
    from pathlib import Path
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, val = line.split('=', 1)
            _SPECIAL_ACRONYMS[key.strip().upper()] = val.strip()


def convert_alphabet(text: str, special_acronyms: dict = None) -> str:
    """
    영문 약어를 한글 발음으로 변환

    1. 특수 약어 먼저 치환 (COVID -> 코로나)
    2. 나머지는 철자읽기 (KDH -> 케이 디 에이치)

    Examples:
        "COVID 확진자" -> "코로나 확진자"
        "NATO 회의" -> "나토 회의"
        "KDH 프로젝트" -> "케이 디 에이치 프로젝트"
    """
    acronyms = special_acronyms if special_acronyms else _SPECIAL_ACRONYMS

    # 1. 특수 약어 치환 (대소문자 무시)
    if acronyms:
        # 긴 것부터 매칭 (COVID-19가 COVID보다 먼저)
        for key in sorted(acronyms.keys(), key=len, reverse=True):
            pattern = re.compile(re.escape(key), re.IGNORECASE)
            text = pattern.sub(acronyms[key] + ' ', text)

    # 2. 특수 기호 변환
    text = re.sub(r'%p\b', ' 퍼센트 포인트', text)
    text = re.sub(r'%', ' 퍼센트', text)
    text = re.sub(r'\+', ' 플러스', text)

    # 3. 나머지 알파벳 철자읽기
    def replace_acronym(m):
        result_parts = [_ALPHABET_PRON[c.upper()] for c in m.group(0) if c.upper() in _ALPHABET_PRON]
        return " ".join(result_parts) + " "

    return re.sub(r'[A-Z]{2,}|[A-Z](?:[&/\-][A-Z])+|[A-Za-z]', replace_acronym, text)


# ============================================================
# 복합명사 분리 (Compound Noun Splitting)
# ============================================================

def split_compounds(text: str, lexicon: Lexicon, min_length: int = 4) -> str:
    """
    텍스트 내 복합명사를 분리

    Args:
        text: 입력 텍스트
        lexicon: 사전
        min_length: 분리 대상 최소 길이

    Examples:
        "데이터베이스시스템" -> "데이터베이스 시스템"
    """
    # 한글/기타 분리
    pattern = r'([가-힣]+)|([^가-힣]+)'
    result = []

    for match in re.finditer(pattern, text):
        if match.group(1):  # 한글
            token = match.group(1)
            if len(token) >= min_length:
                split_result = _split_compound_token(token, lexicon, min_length)
                result.append(" ".join(split_result))
            else:
                result.append(token)
        else:  # 기타
            result.append(match.group(2))

    return "".join(result)


def _split_compound_token(token: str, lexicon: Lexicon, min_length: int) -> List[str]:
    """단일 토큰 복합명사 분리"""
    # 조사 분리
    stem, josa = split_josa(token)

    if josa and len(stem) >= 2:
        tokens = _do_split(stem, lexicon, min_length)
        return attach_josa(tokens, josa)
    else:
        return _do_split(token, lexicon, min_length)


def _do_split(stem: str, lexicon: Lexicon, min_length: int) -> List[str]:
    """실제 분리 로직"""
    # 분리 대상 아니면 그대로
    if not _should_split(stem, lexicon, min_length):
        return [stem]

    # 후보 생성
    candidates = _generate_candidates(stem, lexicon)
    if not candidates:
        return [stem]

    # 최고 점수 선택
    best = max(candidates, key=lambda c: c[1])
    tokens, score = best

    if len(tokens) == 1 or score <= 0:
        return [stem]

    return tokens


def _should_split(text: str, lexicon: Lexicon, min_length: int) -> bool:
    """분리 여부 판단"""
    if not is_hangul_string(text):
        return False
    if len(text) < min_length or len(text) > 20:
        return False
    if lexicon.is_noun(text) or lexicon.is_legal_term(text) or lexicon.is_nosplit(text):
        return False
    return True


def _generate_candidates(text: str, lexicon: Lexicon) -> List[tuple]:
    """분해 후보 생성 (재귀)"""
    candidates = [([text], 0.0)]  # baseline

    def recurse(remaining: str, tokens: List[str]):
        if not remaining:
            score = _score_candidate(tokens, lexicon)
            candidates.append((tokens, score))
            return

        for i in range(1, len(remaining) + 1):
            left, right = remaining[:i], remaining[i:]
            is_final = len(right) == 0

            if lexicon.is_legal_term(left) or _is_valid_token(left, lexicon, is_final):
                recurse(right, tokens + [left])

    recurse(text, [])
    return candidates


def _is_valid_token(token: str, lexicon: Lexicon, is_final: bool) -> bool:
    """유효한 토큰인지 확인"""
    if len(token) >= 2:
        if lexicon.is_legal_term(token) or lexicon.is_noun(token):
            return True
        # Head noun 패턴 (X+나무)
        for suffix_len in [1, 2]:
            if len(token) > suffix_len:
                suffix, prefix = token[-suffix_len:], token[:-suffix_len]
                if lexicon.is_head_noun(suffix) and lexicon.is_noun(prefix):
                    return True
        return False

    if len(token) == 1:
        return is_final and lexicon.is_end_mono_allowed(token)

    return False


def _score_candidate(tokens: List[str], lexicon: Lexicon) -> float:
    """후보 점수 계산"""
    if not tokens:
        return 0.0

    score = -len(tokens) * 1.0  # 토큰 개수 페널티
    avg_len = sum(len(t) for t in tokens) / len(tokens)
    score += avg_len * 2.0  # 평균 길이 보너스

    # 1음절 페널티
    for i, t in enumerate(tokens):
        if len(t) == 1:
            score -= 0.5 if i == len(tokens) - 1 else 2.0

    # 사전 보너스
    def is_valid_in_dict(t):
        if len(t) >= 2:
            if lexicon.is_noun(t):
                return True
            for suffix_len in [1, 2]:
                if len(t) > suffix_len:
                    suffix, prefix = t[-suffix_len:], t[:-suffix_len]
                    if lexicon.is_head_noun(suffix) and lexicon.is_noun(prefix):
                        return True
            return False
        return lexicon.is_end_mono_allowed(t)

    if all(is_valid_in_dict(t) for t in tokens):
        score += 2.0

    # Legal term 보너스
    for token in tokens:
        if lexicon.is_legal_term(token):
            score += 3.0

    # Head noun 위치 점수
    for i, token in enumerate(tokens):
        if lexicon.is_head_noun(token):
            score += 1.0 if i == len(tokens) - 1 else -3.0

    return score


# ============================================================
# 의존명사 띄어쓰기 (Dependent Noun Spacing)
# ============================================================

_DEPENDENT_NOUNS = {
    '수': has_jongseong_l,
    '리': has_jongseong_l,
    '터': has_jongseong_l,
    '것': lambda c: has_jongseong_n(c) or has_jongseong_l(c) or c == '는',
    '바': lambda c: has_jongseong_n(c) or has_jongseong_l(c) or c == '는',
    '듯': lambda c: has_jongseong_n(c) or has_jongseong_l(c) or c == '는',
    '뿐': lambda c: has_jongseong_n(c) or has_jongseong_l(c),
    '줄': lambda c: has_jongseong_n(c) or has_jongseong_l(c) or c == '는',
    '지': lambda c: has_jongseong_n(c) or has_jongseong_l(c) or c == '는',
    '데': lambda c: has_jongseong_n(c) or has_jongseong_l(c) or c == '는',
}

_PARTICLES = [
    '은', '는', '이', '가', '을', '를', '도', '만', '조차', '마저', '까지',
    '처럼', '같이', '보다', '에', '에서', '로', '으로', '와', '과', '랑',
    '밖에', '뿐이다', '인데', '록',
    '이다', '이라', '이고', '이며', '이니', '이면', '이야', '이지', '인', '일', '임',
    '있다', '있는', '있을', '있으면', '있으니', '있어', '있고', '있지', '있나',
    '없다', '없는', '없을', '없으면', '없으니', '없어', '없고', '없지', '없나',
    '알다', '알았다', '알고', '알면', '아는', '알아',
    '모르다', '몰랐다', '모르고', '모르면', '모르는', '몰라',
    '됐다', '되다', '되면', '되고', '되는', '돼',
    '하다', '한다', '해서', '하고', '하면', '해',
    '싶다', '싶어', '싶은', '싶으면',
    '오래', '얼마', '한참', '꽤', '벌써', '이미', '아직',
]


def apply_spacing(text: str) -> str:
    """
    의존명사 띄어쓰기 + 공백 정규화

    Examples:
        "할수있다" -> "할 수 있다"
        "같은것이" -> "같은 것이"
    """
    # 의존명사 띄어쓰기
    for dep_noun, check_func in _DEPENDENT_NOUNS.items():
        for particle in _PARTICLES:
            pattern = f'([가-힣])({dep_noun}{particle})'
            text = _apply_dep_spacing(text, pattern, check_func)
        pattern = f'([가-힣])({dep_noun})(?=\\s|[.,!?]|$)'
        text = _apply_dep_spacing(text, pattern, check_func)

    # 연속 공백 정리
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _apply_dep_spacing(text: str, pattern: str, check_func) -> str:
    """패턴 매칭 후 조건 충족 시 띄어쓰기 삽입"""
    def replacer(m):
        prev_char, rest = m.group(1), m.group(2)
        if check_func(prev_char):
            return f'{prev_char} {rest}'
        return m.group(0)
    return re.sub(pattern, replacer, text)


# ============================================================
# 통합 정규화 함수
# ============================================================

def normalize(
    text: str,
    lexicon: Lexicon = None,
    *,
    numbers: bool = True,
    alphabet: bool = True,
    compounds: bool = True,
    spacing: bool = True,
) -> str:
    """
    한국어 텍스트 정규화 (TTS 전처리용)

    Args:
        text: 입력 텍스트
        lexicon: 사전 (복합명사 분리 + 특수 약어에 필요)
        numbers: 숫자 변환 활성화
        alphabet: 알파벳 변환 활성화
        compounds: 복합명사 분리 활성화
        spacing: 띄어쓰기 정규화 활성화

    Returns:
        정규화된 텍스트

    Examples:
        >>> normalize("COVID 확진자 2024년", lexicon)
        "코로나 확진자 이천 이십사 년"
    """
    if alphabet:
        acronyms = lexicon.special_acronyms if lexicon else None
        text = convert_alphabet(text, acronyms)

    if numbers:
        text = convert_numbers(text)

    if compounds and lexicon:
        text = split_compounds(text, lexicon)

    if spacing:
        text = apply_spacing(text)

    return text
