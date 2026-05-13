# 10주차 실습 — AI 에이전틱 설계 (학생용)

## 사전 준비

**1. Ollama 설치 및 모델 다운로드**
```bash
# Ollama 설치: https://ollama.com
ollama pull qwen2.5-coder:7b
```

**2. 의존성 설치**
```bash
uv sync
```

---

## 실습 1: 인보이스 처리 에이전트

```bash
uv run python 01_invoice_agent.py
```

`01_invoice_agent.py` 파일을 열고 `# TODO` 부분을 채우세요.

| 단계 | 구현할 내용 |
|------|------------|
| Step 1 | `ollama.chat()` 호출 + 응답에서 텍스트 꺼내기 |
| Step 2 | 인보이스 JSON 스키마 직접 설계 |

---

## 실습 2: 전문가 페르소나 에이전트

```bash
uv run python 02_invoice_agent_with_experts.py
```

`02_invoice_agent_with_experts.py` 파일을 열고 `# TODO` 부분을 채우세요.

| 단계 | 구현할 내용 |
|------|------------|
| Step 1 | 지출 분류 전문가 페르소나 프롬프트 작성 |
| Step 2 | 구매 규칙 전문가 프롬프트 작성 |
| Step 3 | `purchasing_rules.txt` 내용 수정 후 동작 변화 확인 |

---

## 심화 과제

`purchasing_rules.txt`의 금액 한도나 규칙을 바꾼 뒤 실습 2를 다시 실행해보세요.
코드를 전혀 수정하지 않아도 에이전트 동작이 달라지는지 확인해보세요.
