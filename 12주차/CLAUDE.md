# 12주차 실습 — 멀티 에이전트 통신 패턴

## 주제

멀티 에이전트 시스템에서 통신 패턴(메시지 전달 / 메모리 핸드오프 / 완전 공유 메모리)을 이해하고, 고객 서비스 시나리오에 적합한 패턴을 선택하여 구현한다.

## 파일 구성

| 파일 | 설명 |
|------|------|
| `call_agent.py` | call_agent 도구 원형 (register_tool 기반 개념 코드) |
| `call_agent2.py` | 실습 구현 — ollama 기반 멀티 에이전트 고객 서비스 시스템 |
| `서술형.md` | 서술형 과제 답안 (문제 1, 2) |

## 실행 방법

```powershell
# 1. 별도 터미널에서 Ollama 서버 시작 (유지 필요)
ollama serve

# 2. 모델 확인 (최초 1회)
ollama pull qwen2.5-coder:7b

# 3. 실습 실행
python call_agent2.py
```

## 시나리오 구조

```
고객 문의
   │
   ▼
customer_service_agent (오케스트레이터)
   │
   ├── 일반 문의 → 자체 처리 (general_response)
   │
   └── 기술 문의 → call_agent() 호출
                      │
                      └── tech_support_agent
                          (대화 맥락 전체 수신 후 처리)
```

## 선택 패턴: 메모리 핸드오프 (Memory Handoff)

- **이유**: 기술 에이전트가 고객과의 대화 전체 맥락을 필요로 하기 때문
- **메시지 전달**은 현재 메시지만 넘겨 맥락 손실 발생
- **완전 공유 메모리**는 에이전트 간 불필요한 결합 생성
- 핸드오프 시 `conversation_history` 리스트 전체를 `call_agent`에 전달

## 핵심 구현 포인트

### call_agent (메모리 핸드오프 버전)
```python
def call_agent(agent_fn, task, conversation_history=None):
    result = agent_fn(task=task, conversation_history=conversation_history)
    return result
```

### 기술 에이전트 — 맥락 주입
```python
context_text = "\n".join(
    f"[{item['role'].upper()}]: {item['content']}"
    for item in conversation_history
)
# context_text를 프롬프트에 포함하여 LLM에 전달
```

## 서술형 과제 요약

### 문제 1: 시스템 지시사항 오염
- 단일 에이전트의 한계: 역할 충돌, 지시사항 희석
- 오염 문제: 오케스트레이터 지시가 서브에이전트의 시스템 프롬프트를 덮어씀
- 해결: 시스템 프롬프트를 불변 영역으로 보호, 오케스트레이터 입력은 user 메시지로만 수신

### 문제 2: 메모리 핸드오프 패턴
- 적합: 단계가 명확한 순차 파이프라인 (수집→분석→보고서)
- 부적합: 빈번한 양방향 참조가 필요한 실시간 협업 시스템
