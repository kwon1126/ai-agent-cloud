# 11주차 실습 — AI 에이전틱 설계

## 프로젝트 개요

Ollama 로컬 LLM(`qwen2.5-coder:7b`)을 사용한 인보이스 처리 에이전트 실습.

## 파일 구성

| 파일 | 설명 |
|------|------|
| `01_invoice_agent.py` | 인보이스 데이터 추출 에이전트 |
| `02_invoice_agent_with_experts.py` | 전문가 페르소나 + 구매 규칙 준수 에이전트 |
| `purchasing_rules.txt` | 구매 규칙 문서 (Document-as-Implementation) |

## 실행 방법

`uv`가 없는 경우 `python`으로 직접 실행:

```powershell
# 의존성 설치 (최초 1회)
pip install ollama

# Ollama 서버 시작 (별도 터미널에서 실행 후 유지)
ollama serve

# 모델 다운로드 (최초 1회, 약 4~5GB)
ollama pull qwen2.5-coder:7b

# 실습 1 실행
python 01_invoice_agent.py

# 실습 2 실행
python 02_invoice_agent_with_experts.py
```

## 구현 내용

### 실습 1: `01_invoice_agent.py`

**Step 1 — `prompt_llm_for_json()` 함수**
- `ollama.chat(model=MODEL, messages=[system, user])` 호출
- `response.message.content`로 텍스트 추출

**Step 2 — `extract_invoice_data()` 함수의 JSON 스키마**
- `required`: `invoice_number`, `date`, `total_amount`
- `properties`: 인보이스 번호, 발행일(YYYY-MM-DD), 공급업체(이름/주소), 총금액, 통화, 품목목록(품목명/수량/단가/소계)

### 실습 2: `02_invoice_agent_with_experts.py`

**Step 1 — `classify_expense()` 페르소나 프롬프트**
- 페르소나 패턴: "기업 재무 지출 분류 전문가로서 행동하라"
- 공급업체명, 총금액, 품목목록, 카테고리 목록(`EXPENSE_CATEGORIES`) 포함

**Step 2 — `check_compliance()` 프롬프트**
- 페르소나 패턴: "구매 규칙 준수 전문가로서 행동하라"
- Document-as-Implementation: `<purchasing_rules>` 태그 안에 `purchasing_rules.txt` 내용 삽입
- 인보이스 전체 정보(번호/공급업체/금액/날짜/품목) 포함

## 핵심 패턴

- **페르소나 패턴**: LLM에게 전문가 역할을 부여하여 응답 품질 향상
- **Document-as-Implementation**: 코드 수정 없이 텍스트 파일만 바꿔도 에이전트 동작이 달라짐
- **JSON 스키마 강제**: system 메시지로 출력 형식을 고정, 파싱 실패 시 최대 3회 재시도
