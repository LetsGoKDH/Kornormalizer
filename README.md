# Korean Text Normalizer

TTS(음성 합성)를 위한 한국어 텍스트 정규화 라이브러리

## 주요 기능

### 숫자 -> 한글
```
2024년           -> 이천 이십 사 년
1,234명          -> 천 이백 삼십 사 명
15:30            -> 열 다섯 시 삼십 분
350만원          -> 삼백 오십 만 원
3.14             -> 삼 점 일 사
```

### 알파벳 -> 한글 발음
```
KDH              -> 케이 디 에이치
R&D              -> 알 앤 디
C++              -> 씨 플러스 플러스
```

### 복합명사 분리
```
데이터베이스시스템  -> 데이터베이스 시스템
자작나무숲         -> 자작나무 숲
형사사법기구       -> 형사사법 기구  (법률용어 보호)
```

### 의존명사 띄어쓰기
```
할수있다          -> 할 수 있다
같은것이          -> 같은 것이
있는데            -> 있는 데
```

## 설치

```bash
pip install -e .
```

## 사용법

### 기본 사용

```python
from normalizer import normalize, Lexicon

# 사전 로드
lexicon = Lexicon.from_dir("lexicon")

# 정규화
text = "2024년 R&D 예산 350만원"
result = normalize(text, lexicon)
# -> "이천 이십 사 년 알 앤 디 예산 삼백 오십 만 원"
```

### 개별 함수 사용

```python
from normalizer import convert_numbers, convert_alphabet, split_compounds, apply_spacing

# 숫자만 변환
convert_numbers("350만원")
# -> "삼백 오십 만 원"

# 알파벳만 변환
convert_alphabet("C++")
# -> "씨 플러스 플러스"

# 복합명사 분리 (사전 필요)
split_compounds("데이터베이스시스템", lexicon)
# -> "데이터베이스 시스템"

# 의존명사 띄어쓰기
apply_spacing("할수있다")
# -> "할 수 있다"
```

### 옵션 선택

```python
# 특정 기능만 활성화
normalize(text, lexicon, numbers=True, alphabet=False, compounds=True, spacing=True)
```

## 정규화 파이프라인

```
입력 -> 알파벳 변환 -> 숫자 변환 -> 복합명사 분리 -> 의존명사 띄어쓰기 -> 출력
```

## 파일 구조

```
normalizer/
├── __init__.py      # 공개 API
├── lexicon.py       # 사전 로더
├── hangul.py        # 한글 유틸리티
└── transforms.py    # 변환 함수들
```

## 사전 데이터

| 파일 | 항목 수 | 설명 |
|------|---------|------|
| `nouns_base.txt` | 26,219 | 2음절 이상 명사 |
| `end_mono_nouns.txt` | 121 | 끝 1음절 허용 명사 |
| `head_nouns.txt` | 15 | 핵심 명사 (나무, 베이스 등) |
| `legal_terms_strict.txt` | 108,115 | 법률 용어 |
| `nosplit.txt` | - | 분해 금지 목록 |

## 데이터 출처

- **명사 사전**: 국립국어원 한국어기초사전 (공공누리 제1유형)
- **법률 용어**: 법제처 국가법령정보센터 (공공저작물 자유이용허락)

## 테스트

```bash
pytest tests/ -v
```

## 라이선스

MIT License
