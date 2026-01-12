# -*- coding: utf-8 -*-
"""Tests for Lexicon"""

import pytest
import tempfile
from pathlib import Path
from normalizer import Lexicon


def test_lexicon_load():
    """Test lexicon loading"""
    with tempfile.TemporaryDirectory() as tmpdir:
        d = Path(tmpdir)
        (d / "nouns_base.txt").write_text("데이터\n베이스\n", encoding="utf-8")
        (d / "end_mono_nouns.txt").write_text("수\n", encoding="utf-8")
        (d / "nosplit.txt").write_text("", encoding="utf-8")

        lexicon = Lexicon.from_dir(d)
        assert lexicon.is_noun("데이터")
        assert not lexicon.is_noun("없음")
