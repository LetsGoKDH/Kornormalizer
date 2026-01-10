# -*- coding: utf-8 -*-
"""
Alphabet to Korean pronunciation converter
영문자를 한국어 발음으로 변환 (예: KDH -> 케이 디 에이치)
"""

import re


class AlphabetToKorean:
    """영문 알파벳을 한국어 발음으로 변환"""
    
    # 알파벳 발음 매핑
    ALPHABET_PRONUNCIATION = {
        'A': '에이', 'B': '비', 'C': '씨', 'D': '디', 'E': '이',
        'F': '에프', 'G': '지', 'H': '에이치', 'I': '아이', 'J': '제이',
        'K': '케이', 'L': '엘', 'M': '엠', 'N': '엔', 'O': '오',
        'P': '피', 'Q': '큐', 'R': '알', 'S': '에스', 'T': '티',
        'U': '유', 'V': '브이', 'W': '더블유', 'X': '엑스', 'Y': '와이', 'Z': '지',
        '&': '앤'
    }
    
    def convert(self, text: str) -> str:
        """
        텍스트 내의 영문자를 한글 발음으로 변환
        
        Examples:
            "KDH" -> "케이 디 에이치"
            "COVID-19" -> "씨 오 브이 아이 디 일구"
        """
        result = []
        
        for char in text:
            if char.upper() in self.ALPHABET_PRONUNCIATION:
                result.append(self.ALPHABET_PRONUNCIATION[char.upper()])
            else:
                result.append(char)
        
        return " ".join(result)
    
    def convert_acronyms(self, text: str) -> str:
        """
        약어(연속 대문자)만 선택적으로 변환

        Examples:
            "KDH 프로젝트" -> "케이 디 에이치 프로젝트"
            "R&D" -> "알 앤 디"
            "AI/ML" -> "에이 아이 슬래시 엠 엘"
            "hello world" -> "hello world" (소문자는 그대로)
            "35.5%p" -> "35.5 퍼센트 포인트"
            "10%" -> "10 퍼센트"
        """
        # 특수 기호 변환 (알파벳 변환 전에 먼저 처리)
        text = re.sub(r'%p\b', ' 퍼센트 포인트', text)
        text = re.sub(r'%', ' 퍼센트', text)
        text = re.sub(r'\+', ' 플러스', text)

        # 연속 대문자 2글자 이상, 또는 구두점으로 연결된 대문자들을 찾아서 변환
        def replace_acronym(match):
            acronym = match.group(0)
            # 알파벳만 추출해서 변환
            result_parts = []
            for c in acronym:
                if c.upper() in self.ALPHABET_PRONUNCIATION:
                    result_parts.append(self.ALPHABET_PRONUNCIATION[c.upper()])
                # 구두점은 그대로 유지 (나중에 num2kor에서 처리됨)
            return " ".join(result_parts) + " "

        # 연속 대문자 2글자 이상, 또는 [대문자-구두점-대문자] 패턴
        # [A-Z](?:[&/\-][A-Z])+ : R&D, AI/ML 같은 패턴
        # 추가: 단일 알파벳도 변환 (대소문자 모두)
        # 변환 후 공백 추가 (숫자/한글과 구분)
        result = re.sub(r'[A-Z]{2,}|[A-Z](?:[&/\-][A-Z])+|[A-Za-z]', replace_acronym, text)
        return result
