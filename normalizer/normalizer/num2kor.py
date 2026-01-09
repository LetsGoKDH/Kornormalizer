# -*- coding: utf-8 -*-
"""숫자를 한국어로 바꿔주는 모듈"""

import re


class NumberToKorean:
    # 0~9 한글 표현 (한자어 수사)
    DIGITS = ["영", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]

    # 0~99 고유어 수사 (Native Korean numerals) - 띄어쓰기 포함
    NATIVE_NUMS = {
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
        96: "아흔 여섯", 97: "아흔 일곱", 98: "아흔 여덟", 99: "아흔 아홉"
    }

    # 고유어 수사를 사용하는 단위 (1~99 범위에서만)
    NATIVE_UNITS = ["개", "명", "살", "시"]

    UNITS_SMALL = ["", "십", "백", "천"]
    UNITS_LARGE = ["", "만", "억", "조", "경"]

    # 숫자 뒤에 붙는 단위들 (띄어쓰기 넣어야 함)
    TEXT_UNITS = ["년", "월", "일", "시", "분", "초", "원", "명", "개", "권", "장", "살", "세", "조", "항", "호", "점"]

    def convert(self, text: str) -> str:
        """텍스트에서 숫자 찾아서 한글로 바꿈"""

        # 1,234 같은 천단위 쉼표 먼저 제거
        text = re.sub(r'(\d{1,3}(?:,\d{3})+)', lambda m: m.group(1).replace(',', ''), text)

        # 시간 표현 (15:30 -> 열다섯 시 삼십 분)
        def replace_time(match):
            h = int(match.group(1))
            m = int(match.group(2))

            # 시(hour)는 고유어 수사 사용 (1~23)
            if 1 <= h <= 99:
                h_kor = self.NATIVE_NUMS.get(h, self._number_to_korean(h))
            else:
                h_kor = self._number_to_korean(h)

            # 분(minute)은 한자어 수사 사용
            m_kor = self._number_to_korean(m) if m > 0 else ""

            if m > 0:
                return h_kor + " 시 " + m_kor + " 분"
            return h_kor + " 시"

        text = re.sub(r'(\d{1,2}):(\d{2})\b', replace_time, text)

        # 소수점 (35.43 -> 삼십 오 점 사 삼) - 구두점 제거 전에 처리
        def replace_decimal(m):
            int_part = int(m.group(1))
            dec_part = m.group(2)
            unit = m.group(3) if m.group(3) else ""
            kor_int = self._number_to_korean(int_part)
            kor_dec = " ".join(self.DIGITS[int(d)] for d in dec_part)
            result = kor_int + " 점 " + kor_dec
            if unit:
                result += " " + unit
            return result

        text = re.sub(r"(\d+)\.(\d+)([" + "".join(self.TEXT_UNITS) + "]?)", replace_decimal, text)

        # 구두점 띄어쓰기로 (&는 제외, 알파벳 변환에서 처리)
        for p in ['-', ',', ';', ':', '/']:
            text = text.replace(p, ' ')

        # 큰 단위 (3만원, 100억 같은 거)
        def replace_large(m):
            num = int(m.group(1))
            unit = m.group(2)
            text_unit = m.group(3)

            result = self._number_to_korean(num) + " " + unit
            if text_unit:
                result += " " + text_unit
            return result

        text = re.sub(r"(\d+)(만|억|조|경)([" + "".join(self.TEXT_UNITS) + "]?)",
                     replace_large, text)

        # 나머지 일반 숫자들
        def replace_num(m):
            num = int(m.group(1))
            unit = m.group(2)

            # 고유어 수사 사용 여부 판단
            if unit and unit in self.NATIVE_UNITS and 1 <= num <= 99:
                kor = self.NATIVE_NUMS.get(num, self._number_to_korean(num))
            else:
                kor = self._number_to_korean(num)

            return kor + " " + unit if unit else kor

        text = re.sub(r"(\d+)([" + "".join(self.TEXT_UNITS) + "]?)",
                     replace_num, text)
        return text
    
    def _number_to_korean(self, num: int) -> str:
        """정수 -> 한글"""
        if num == 0:
            return self.DIGITS[0]
        if num < 0:
            return "마이너스 " + self._number_to_korean(-num)

        # 만/억/조/경 단위로 쪼갬
        parts = []
        for i, unit in enumerate(self.UNITS_LARGE):
            if num == 0:
                break

            chunk = num % 10000
            num //= 10000

            if chunk > 0:
                # 1만, 1억은 "일"을 생략 (그냥 만, 억)
                if chunk == 1 and unit:
                    parts.append(unit)
                else:
                    chunk_str = self._convert_chunk(chunk)
                    if unit:
                        parts.append(chunk_str + " " + unit)
                    else:
                        parts.append(chunk_str)

        return " ".join(reversed(parts))
    
    def _convert_chunk(self, num: int) -> str:
        """천 단위 이하 (0~9999)를 한글로"""
        if num == 0:
            return ""

        res = []

        # 천백십일 순서대로
        if num >= 1000:
            t = num // 1000
            res.append("천" if t == 1 else self.DIGITS[t] + "천")
            num %= 1000

        if num >= 100:
            h = num // 100
            res.append("백" if h == 1 else self.DIGITS[h] + "백")
            num %= 100

        if num >= 10:
            d = num // 10
            res.append("십" if d == 1 else self.DIGITS[d] + "십")
            num %= 10

        if num > 0:
            res.append(self.DIGITS[num])

        return " ".join(res)


# 년도 읽기용 간단 버전
def number_to_korean_simple(num: int) -> str:
    """각 자리 숫자 그대로 읽기 (2024 -> 이 영 이 사)"""
    digits = ["영", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
    return " ".join(digits[int(d)] for d in str(num))
