# Korean Text Normalizer

음성 전사 텍스트를 위한 한국어 정규화 모듈

## 주요 기능

### 숫자 → 한글
```
2024년           → 이천 이십 사 년
1,234명          → 천 이백 삼십 사 명
15:30            → 십 오 시 삼십 분
350만원          → 삼백 오십 만 원
3.14점           → 삼 점 일 사 점
0.5%p            → 영 점 오 퍼센트 포인트
```

### 알파벳 → 한글 발음
```
KDH              → 케이 디 에이치
R&D              → 알 앤 디
C++              → 씨 플러스 플러스
API-v2.0         → 에이 피 아이 브이 이 점 영
```

### 복합명사 분리
```
데이터베이스시스템  → 데이터베이스 시스템
자작나무숲         → 자작나무 숲
형사사법기구       → 형사사법 기구  (법률용어 "형사사법" 보호)
```

## 설치

```bash
pip install -e .
```

## 사용법

### 기본 사용

```python
from normalizer import normalize, Lexicon

# 숫자/알파벳만 변환 (사전 없이)
text = "2024년 R&D 예산 350만원"
result = normalize(text)
print(result)
# → "이천 이십 사 년 알 앤 디 예산 삼백 오십 만 원"

# 복합명사 분리까지 (사전 필요)
lexicon = Lexicon.from_dir("lexicon")
text = "데이터베이스시스템 구축"
result = normalize(text, lexicon=lexicon)
print(result)
# → "데이터베이스 시스템 구축"
```

### 개별 모듈 사용

```python
from normalizer import NumberToKorean, AlphabetToKorean, CompoundNounSplitter, Lexicon

# 숫자만
num = NumberToKorean()
print(num.convert("350만원"))  # → "삼백 오십 만 원"

# 알파벳만
alpha = AlphabetToKorean()
print(alpha.convert_acronyms("C++"))  # → "씨 플러스 플러스"

# 복합명사만
lexicon = Lexicon.from_dir("lexicon")
splitter = CompoundNounSplitter(lexicon)
print(splitter.split("데이터베이스시스템"))  # → ["데이터베이스", "시스템"]
```

## 사전 파일

`lexicon/` 디렉토리에 포함된 사전 파일들:

| 파일 | 항목 수 | 설명 |
|------|---------|------|
| `nouns_base.txt` | 26,219 | 2음절 이상 명사 |
| `end_mono_nouns.txt` | 121 | 끝 1음절 허용 명사 (숲, 강, 산 등) |
| `head_nouns.txt` | 15 | 핵심 명사 (나무, 베이스 등) |
| `legal_terms_strict.txt` | 108,115 | 법률 용어 (3자 이상) |
| `legal_terms_len2.txt` | 7,212 | 법률 용어 (2자) |
| `nosplit.txt` | - | 분해 금지 목록 |

## 데이터 출처

### 명사 사전 (nouns_base.txt, end_mono_nouns.txt)

- **출처**: 국립국어원 한국어기초사전
- **다운로드**: https://krdict.korean.go.kr/
- **라이선스**: 공공누리 제1유형 (출처표시)
- **가공 방법**:
  - JSON 형식의 전체 사전 데이터에서 품사가 "명사"인 항목 추출
  - 2음절 이상 순한글 명사만 필터링
  - 끝 1음절 명사(숲, 강 등)는 별도 분리

### 법률 용어 사전 (legal_terms_strict.txt, legal_terms_len2.txt)

- **출처**: 법제처 국가법령정보센터 법령용어
- **다운로드**: https://www.law.go.kr/
- **라이선스**: 공공저작물 자유이용허락
- **가공 방법**:
  - CSV 형식의 법령용어 데이터에서 용어명 추출
  - 3자 이상 / 2자 용어 분리
  - 순한글 용어만 필터링

## 정규화 파이프라인

```
입력 → 알파벳 변환 → 숫자 변환 → 복합명사 분리 → 띄어쓰기 정규화 → 출력
```

## 테스트

```bash
pytest tests/ -v
```

## 라이선스

- **코드**: MIT License
- **사전 데이터**:
  - 국립국어원 한국어기초사전 (공공누리 제1유형)
  - 법제처 법령용어 (공공저작물 자유이용허락)
