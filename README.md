# Korean Text Normalizer

TTS(음성 합성)를 위한 한국어 텍스트 정규화 라이브러리

## 주요 기능

| 기능 | 입력 | 출력 |
|------|------|------|
| 숫자 변환 | `2024년` | `이천 이십 사 년` |
| 알파벳 변환 | `R&D` | `알 앤 디` |
| 복합명사 분리 | `데이터베이스시스템` | `데이터베이스 시스템` |
| 의존명사 띄어쓰기 | `할수있다` | `할 수 있다` |

## 요구사항

- Python 3.8 이상
- 외부 의존성 없음 (순수 Python)

## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/LetsGoKDH/Kornormalizer.git
cd Kornormalizer
```

### 2. 패키지 설치

```bash
# 개발 모드 설치 (권장)
pip install -e .

# 또는 일반 설치
pip install .
```

### 3. 설치 확인

```bash
python example.py
```

## 빠른 시작

```python
from pathlib import Path
from normalizer import normalize, Lexicon

# 사전 로드
lexicon = Lexicon.from_dir(Path("lexicon"))

# 정규화
text = "2024년 R&D 예산 350만원"
result = normalize(text, lexicon)
print(result)
# -> "이천 이십 사 년 알 앤 디 예산 삼백 오십 만 원"
```

## 사용법

### 전체 정규화

```python
from normalizer import normalize, Lexicon

lexicon = Lexicon.from_dir("lexicon")

# 기본 사용
normalize("데이터베이스시스템 구축", lexicon)
# -> "데이터베이스 시스템 구축"

# 옵션 선택
normalize(text, lexicon,
    numbers=True,     # 숫자 변환
    alphabet=True,    # 알파벳 변환
    compounds=True,   # 복합명사 분리
    spacing=True      # 의존명사 띄어쓰기
)
```

### 개별 함수 사용

```python
from normalizer import convert_numbers, convert_alphabet, split_compounds, apply_spacing

# 숫자만
convert_numbers("350만원")           # -> "삼백 오십 만 원"
convert_numbers("15:30")             # -> "열 다섯 시 삼십 분"

# 알파벳만
convert_alphabet("C++")              # -> "씨 플러스 플러스"
convert_alphabet("R&D")              # -> "알 앤 디"

# 복합명사 분리 (사전 필요)
split_compounds("자작나무숲", lexicon)  # -> "자작나무 숲"

# 의존명사 띄어쓰기
apply_spacing("할수있다")            # -> "할 수 있다"
apply_spacing("같은것이")            # -> "같은 것이"
```

## 프로젝트 구조

```
Kornormalizer/
├── normalizer/          # 메인 패키지
│   ├── __init__.py      # 공개 API
│   ├── transforms.py    # 변환 함수들
│   ├── lexicon.py       # 사전 로더
│   └── hangul.py        # 한글 유틸리티
├── lexicon/             # 사전 파일들
│   ├── nouns_base.txt
│   ├── end_mono_nouns.txt
│   ├── head_nouns.txt
│   ├── legal_terms_strict.txt
│   └── nosplit.txt
├── tests/               # 테스트
├── example.py           # 사용 예제
├── setup.py
└── README.md
```

## 사전 데이터

| 파일 | 항목 수 | 설명 |
|------|---------|------|
| `nouns_base.txt` | 26,219 | 2음절 이상 명사 |
| `end_mono_nouns.txt` | 121 | 끝 1음절 허용 명사 (숲, 강 등) |
| `head_nouns.txt` | 15 | 핵심 명사 (나무, 베이스 등) |
| `legal_terms_strict.txt` | 108,115 | 법률 용어 (분해 금지) |
| `nosplit.txt` | - | 분해 금지 목록 |

## 데이터 출처

- **명사 사전**: [국립국어원 한국어기초사전](https://krdict.korean.go.kr/) (공공누리 제1유형)
- **법률 용어**: [법제처 국가법령정보센터](https://www.law.go.kr/) (공공저작물 자유이용허락)

## 테스트

```bash
# pytest 설치
pip install pytest

# 테스트 실행
pytest tests/ -v
```

## 정규화 파이프라인

```
입력 텍스트
    ↓
알파벳 변환 (KDH -> 케이 디 에이치)
    ↓
숫자 변환 (2024 -> 이천 이십 사)
    ↓
복합명사 분리 (데이터베이스시스템 -> 데이터베이스 시스템)
    ↓
의존명사 띄어쓰기 (할수있다 -> 할 수 있다)
    ↓
출력 텍스트
```

## 라이선스

MIT License
