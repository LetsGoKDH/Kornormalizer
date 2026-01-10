# -*- coding: utf-8 -*-
"""Tests for integrated normalizer"""

import pytest
from normalizer import NumberToKorean, AlphabetToKorean, normalize


def test_number_to_korean():
    """Test number conversion"""
    conv = NumberToKorean()
    
    assert "이천 이십사" in conv.convert("2024")
    assert "삼백 오십" in conv.convert("350")
    assert "일구" in conv.convert("19")


def test_alphabet_to_korean():
    """Test alphabet conversion"""
    conv = AlphabetToKorean()
    
    result = conv.convert_acronyms("KDH")
    assert "케이" in result
    assert "디" in result
    assert "에이치" in result
    
    # 소문자는 변환 안 됨
    result = conv.convert_acronyms("hello")
    assert result == "hello"


def test_normalize_without_lexicon():
    """Test normalization without compound splitting"""
    text = "2024년 KDH 프로젝트"
    result = normalize(text, lexicon=None)
    
    # 숫자 변환됨
    assert "이천" in result or "이" in result
    
    # 알파벳 변환됨
    assert "케이" in result


def test_integrated_normalization():
    """Test full normalization pipeline"""
    text = "2024년"
    result = normalize(text)
    
    # 숫자가 한글로 변환되어야 함
    assert "2024" not in result
    assert any(c in result for c in ["이", "영", "사"])
