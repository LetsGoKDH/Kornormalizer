# -*- coding: utf-8 -*-
import pytest
from pathlib import Path
from normalizer import Lexicon

def test_lexicon_load():
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        d = Path(tmpdir)
        (d / "nouns.txt").write_text("데이터
베이스
", encoding="utf-8")
        (d / "mono_whitelist.txt").write_text("수
", encoding="utf-8")
        (d / "affixes.txt").write_text("", encoding="utf-8")
        (d / "nosplit.txt").write_text("", encoding="utf-8")
        
        lexicon = Lexicon.from_dir(d)
        assert lexicon.is_noun("데이터")
        assert not lexicon.is_noun("없음")
