# -*- coding: utf-8 -*-
"""Tests for Korean text normalizer"""

import pytest
from normalizer import normalize, convert_numbers, convert_alphabet


def test_convert_numbers():
    """Test number conversion"""
    assert "이천 이십사" in convert_numbers("2024")
    assert "삼백 오십" in convert_numbers("350")


def test_convert_alphabet():
    """Test alphabet conversion"""
    result = convert_alphabet("KDH")
    assert "케이" in result
    assert "디" in result
    assert "에이치" in result


def test_normalize_without_lexicon():
    """Test normalization without compound splitting"""
    text = "2024년 KDH 프로젝트"
    result = normalize(text, lexicon=None)

    assert "이천" in result or "이" in result
    assert "케이" in result


def test_normalize_basic():
    """Test basic normalization"""
    text = "2024년"
    result = normalize(text)

    assert "2024" not in result
    assert any(c in result for c in ["이", "영", "사"])
