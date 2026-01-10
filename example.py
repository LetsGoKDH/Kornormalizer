#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Korean Text Normalizer 사용 예제
"""

from pathlib import Path
from normalizer import normalize, Lexicon


def main():
    # 1. 사전 로드
    lexicon_dir = Path(__file__).parent / "lexicon"

    print("사전 로드 중...")
    lexicon = Lexicon.from_dir(lexicon_dir)
    print(f"  명사: {len(lexicon.nouns):,}개")
    print(f"  법률용어: {len(lexicon.legal_terms):,}개")

    # 2. 테스트
    test_cases = [
        "2024년 R&D 예산 350만원",
        "C++ 코드는 3.0 버전에서만 동작한다.",
        "데이터베이스시스템 구축이 지연됐다.",
        "형사사법기구 개편안이 논의됐다.",
        "자작나무숲이 아름답다.",
    ]

    print("\n정규화 결과:")
    for text in test_cases:
        result = normalize(text, lexicon=lexicon)
        print(f"  {text}")
        print(f"  → {result}")
        print()


if __name__ == "__main__":
    main()
