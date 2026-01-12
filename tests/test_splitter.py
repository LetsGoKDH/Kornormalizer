# -*- coding: utf-8 -*-
"""Tests for compound noun splitting"""

import pytest
import tempfile
from pathlib import Path
from normalizer import Lexicon, split_compounds


@pytest.fixture
def sample_lexicon():
    """Create a sample lexicon for testing"""
    tmpdir = tempfile.mkdtemp()
    d = Path(tmpdir)

    nouns = ["데이터", "베이스", "시스템", "관리", "프로그램", "개발", "환경"]
    (d / "nouns_base.txt").write_text("\n".join(nouns), encoding="utf-8")
    (d / "end_mono_nouns.txt").write_text("수\n법", encoding="utf-8")
    (d / "nosplit.txt").write_text("", encoding="utf-8")

    return Lexicon.from_dir(d)


def test_split_basic(sample_lexicon):
    """Test basic splitting"""
    result = split_compounds("데이터베이스", sample_lexicon)
    assert "데이터" in result and "베이스" in result

    result = split_compounds("시스템관리", sample_lexicon)
    assert "시스템" in result and "관리" in result


def test_split_nosplit():
    """Test nosplit protection"""
    tmpdir = tempfile.mkdtemp()
    d = Path(tmpdir)

    (d / "nouns_base.txt").write_text("데이터\n베이스", encoding="utf-8")
    (d / "end_mono_nouns.txt").write_text("", encoding="utf-8")
    (d / "nosplit.txt").write_text("데이터베이스", encoding="utf-8")

    lexicon = Lexicon.from_dir(d)
    result = split_compounds("데이터베이스", lexicon)
    assert result == "데이터베이스"  # Protected


def test_split_short_text(sample_lexicon):
    """Test that short text is not split"""
    result = split_compounds("데이터", sample_lexicon)
    assert result == "데이터"  # Too short


def test_split_non_korean(sample_lexicon):
    """Test that non-Korean text is not split"""
    result = split_compounds("database", sample_lexicon)
    assert result == "database"


def test_split_legal_terms():
    """Test legal term protection"""
    tmpdir = tempfile.mkdtemp()
    d = Path(tmpdir)

    (d / "nouns_base.txt").write_text("형사\n사법\n기구", encoding="utf-8")
    (d / "end_mono_nouns.txt").write_text("", encoding="utf-8")
    (d / "nosplit.txt").write_text("", encoding="utf-8")
    (d / "legal_terms_strict.txt").write_text("형사사법\n형사사법기구", encoding="utf-8")

    lexicon = Lexicon.from_dir(d)

    result = split_compounds("형사사법", lexicon)
    assert result == "형사사법", f"Expected '형사사법', got {result}"

    result = split_compounds("형사사법기구", lexicon)
    assert result == "형사사법기구", f"Expected '형사사법기구', got {result}"
