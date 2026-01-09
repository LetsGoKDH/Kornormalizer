# -*- coding: utf-8 -*-
"""Tests for CompoundNounSplitter"""

import pytest
from pathlib import Path
from normalizer import Lexicon, CompoundNounSplitter


@pytest.fixture
def sample_lexicon():
    """Create a sample lexicon for testing"""
    import tempfile
    tmpdir = tempfile.mkdtemp()
    d = Path(tmpdir)
    
    nouns = ["데이터", "베이스", "시스템", "관리", "프로그램", "개발", "환경"]
    (d / "nouns.txt").write_text("
".join(nouns), encoding="utf-8")
    
    mono = ["수", "법"]
    (d / "mono_whitelist.txt").write_text("
".join(mono), encoding="utf-8")
    
    (d / "affixes.txt").write_text("", encoding="utf-8")
    (d / "nosplit.txt").write_text("", encoding="utf-8")
    
    return Lexicon.from_dir(d)


def test_splitter_basic(sample_lexicon):
    """Test basic splitting"""
    splitter = CompoundNounSplitter(sample_lexicon)
    
    result = splitter.split("데이터베이스")
    assert result == ["데이터", "베이스"]
    
    result = splitter.split("시스템관리")
    assert result == ["시스템", "관리"]


def test_splitter_nosplit(sample_lexicon):
    """Test nosplit protection"""
    import tempfile
    tmpdir = tempfile.mkdtemp()
    d = Path(tmpdir)
    
    (d / "nouns.txt").write_text("데이터
베이스", encoding="utf-8")
    (d / "mono_whitelist.txt").write_text("", encoding="utf-8")
    (d / "affixes.txt").write_text("", encoding="utf-8")
    (d / "nosplit.txt").write_text("데이터베이스", encoding="utf-8")
    
    lexicon = Lexicon.from_dir(d)
    splitter = CompoundNounSplitter(lexicon)
    
    result = splitter.split("데이터베이스")
    assert result == ["데이터베이스"]  # Protected by nosplit


def test_splitter_short_text(sample_lexicon):
    """Test that short text is not split"""
    splitter = CompoundNounSplitter(sample_lexicon, min_length=4)
    
    result = splitter.split("데이터")
    assert result == ["데이터"]  # Too short


def test_splitter_non_korean(sample_lexicon):
    """Test that non-Korean text is not split"""
    splitter = CompoundNounSplitter(sample_lexicon)

    result = splitter.split("database")
    assert result == ["database"]

    result = splitter.split("데이터123")
    assert result == ["데이터123"]


def test_splitter_legal_terms():
    """Test legal term protection"""
    import tempfile
    tmpdir = tempfile.mkdtemp()
    d = Path(tmpdir)

    # Create minimal lexicon with legal terms
    (d / "nouns_base.txt").write_text("형사\n사법\n기구", encoding="utf-8")
    (d / "end_mono_nouns.txt").write_text("", encoding="utf-8")
    (d / "nosplit.txt").write_text("", encoding="utf-8")
    (d / "legal_terms_strict.txt").write_text("형사사법\n형사사법기구", encoding="utf-8")

    lexicon = Lexicon.from_dir(d)
    splitter = CompoundNounSplitter(lexicon, min_length=4)

    # Should NOT split legal terms
    result = splitter.split("형사사법")
    assert result == ["형사사법"], f"Expected ['형사사법'], got {result}"

    result = splitter.split("형사사법기구")
    assert result == ["형사사법기구"], f"Expected ['형사사법기구'], got {result}"
