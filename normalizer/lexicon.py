# -*- coding: utf-8 -*-
"""Lexicon loader for Korean noun dictionary"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set, Dict


def _load_set(path: Path) -> Set[str]:
    """Load word set from file, ignoring comments"""
    if not path.exists():
        return set()
    items: Set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        t = line.strip()
        if not t or t.startswith("#"):
            continue
        items.add(t)
    return items


def _load_dict(path: Path) -> Dict[str, str]:
    """Load key=value mapping from file"""
    if not path.exists():
        return {}
    items: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            items[key.strip().upper()] = val.strip()
    return items


@dataclass(frozen=True)
class Lexicon:
    """
    한국어 명사 사전

    Attributes:
        nouns: 2음절 이상 명사 집합
        end_mono_nouns: 끝 1음절 허용 명사 (숲, 강, 산 등)
        nosplit: 분해 금지 목록
        legal_terms: 법률 용어 (분해 금지, 선택적)
        head_nouns: Head noun 목록 (나무, 꽃, 숲 등 - 끝 위치 선호)
        special_acronyms: 특수 약어 매핑 (COVID=코로나 등)
    """

    nouns: Set[str]
    end_mono_nouns: Set[str]
    nosplit: Set[str]
    legal_terms: Set[str] = None
    head_nouns: Set[str] = None
    special_acronyms: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dir(cls, lexicon_dir: str | Path) -> "Lexicon":
        """
        디렉토리에서 사전 파일 로드

        Args:
            lexicon_dir: 사전 파일이 있는 디렉토리 경로

        Returns:
            Lexicon 인스턴스

        파일 구성:
            - nouns_base.txt: 2음절 이상 명사
            - end_mono_nouns.txt: 끝 1음절 허용 명사
            - nosplit.txt: 분해 금지 목록 (선택)
            - legal_terms_strict.txt: 법률 용어 (선택)
            - special_acronyms.txt: 특수 약어 매핑 (선택)
        """
        d = Path(lexicon_dir)
        return cls(
            nouns=_load_set(d / "nouns_base.txt"),
            end_mono_nouns=_load_set(d / "end_mono_nouns.txt"),
            nosplit=_load_set(d / "nosplit.txt") if (d / "nosplit.txt").exists() else set(),
            legal_terms=_load_set(d / "legal_terms_strict.txt") if (d / "legal_terms_strict.txt").exists() else set(),
            head_nouns=_load_set(d / "head_nouns.txt") if (d / "head_nouns.txt").exists() else set(),
            special_acronyms=_load_dict(d / "special_acronyms.txt"),
        )

    def is_noun(self, s: str) -> bool:
        """2음절 이상 명사 여부 확인"""
        return s in self.nouns

    def is_end_mono_allowed(self, s: str) -> bool:
        """끝 1음절 허용 여부 확인"""
        return s in self.end_mono_nouns

    def is_nosplit(self, s: str) -> bool:
        """분해 금지 여부 확인"""
        return s in self.nosplit

    def is_legal_term(self, s: str) -> bool:
        """법률 용어 여부 확인"""
        return self.legal_terms and s in self.legal_terms

    def is_head_noun(self, s: str) -> bool:
        """Head noun 여부 확인 (나무, 꽃, 숲 등)"""
        return self.head_nouns and s in self.head_nouns
