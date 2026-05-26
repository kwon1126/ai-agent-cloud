"""
12주차 과제: 멀티 에이전트 통신 패턴 구현
==========================================
실행: python call_agent2.py

시나리오:
  - 고객 서비스 에이전트가 고객 문의를 받는다
  - 일반 문의 → 자체 처리
  - 기술적 문의 → 기술 지원 에이전트에게 넘긴다
  - 기술 에이전트는 고객과의 대화 전체 맥락이 필요하다

선택 패턴: 메모리 핸드오프 (Memory Handoff)
이유: 기술 에이전트가 고객과의 대화 전체 맥락을 필요로 하기 때문에,
     단순 메시지 전달이 아니라 대화 이력 전체를 구조화하여 넘겨야 한다.
     완전 공유 메모리는 불필요한 결합을 만들고, 단순 메시지 전달은 맥락이 손실된다.
"""

import json
import ollama

MODEL = "qwen2.5-coder:7b"


# ─────────────────────────────────────────────────────────────
# Step 2: call_agent 도구 구현 (메모리 핸드오프 버전)
# call_agent.py의 개념을 ollama 기반으로 구체화
# ─────────────────────────────────────────────────────────────

def call_agent(agent_fn, task: str, conversation_history: list = None) -> dict:
    """
    다른 에이전트를 호출한다. (메모리 핸드오프 패턴)

    Args:
        agent_fn: 호출할 에이전트 함수
        task: 에이전트에게 전달할 작업 내용
        conversation_history: 핸드오프 시 넘길 대화 맥락 전체 (메모리 핸드오프 핵심)

    Returns:
        호출된 에이전트의 응답 결과
    """
    print(f"\n  [call_agent] '{agent_fn.__name__}' 호출 중...")
    if conversation_history:
        print(f"  [call_agent] 대화 맥락 {len(conversation_history)}개 항목 핸드오프")

    result = agent_fn(task=task, conversation_history=conversation_history)
    return result


# ─────────────────────────────────────────────────────────────
# Step 3-A: 기술 지원 에이전트
# ─────────────────────────────────────────────────────────────

def tech_support_agent(task: str, conversation_history: list = None) -> dict:
    """
    기술 지원 에이전트.
    메모리 핸드오프로 전달받은 고객 대화 맥락 전체를 활용하여 기술 문제를 해결한다.
    """
    system_prompt = """당신은 전문 기술 지원 담당자입니다.
고객 서비스 에이전트로부터 기술 문의와 함께 고객과의 대화 맥락 전체를 전달받습니다.
반드시 전달받은 대화 맥락을 구체적으로 언급하며 답변하세요.
예: "앞서 고객님께서 말씀하신 [문제]와 관련하여..."
답변은 한국어로 작성하세요."""

    messages = [{"role": "system", "content": system_prompt}]

    # ── 메모리 핸드오프 핵심: 이전 대화 이력을 그대로 주입 ──
    if conversation_history:
        context_text = "\n".join(
            f"[{item['role'].upper()}]: {item['content']}"
            for item in conversation_history
        )
        user_message = f"""고객 서비스 에이전트로부터 인계받은 전체 대화 맥락:
──────────────────────────────
{context_text}
──────────────────────────────

위 맥락을 바탕으로 다음 기술 지원 요청을 처리해주세요:
{task}"""
    else:
        user_message = task

    messages.append({"role": "user", "content": user_message})

    response = ollama.chat(model=MODEL, messages=messages)
    return {
        "agent": "tech_support_agent",
        "response": response.message.content
    }


# ─────────────────────────────────────────────────────────────
# Step 3-B: 고객 서비스 에이전트
# ─────────────────────────────────────────────────────────────

def classify_inquiry(user_input: str) -> str:
    """문의가 일반인지 기술적인지 분류한다. 'general' 또는 'technical' 반환."""
    messages = [
        {
            "role": "system",
            "content": """고객 문의를 분류하는 전문가입니다.
아래 기준으로 분류하세요:
- general: 배송, 환불, 결제, 계정 정보, 이벤트 등 일반적인 문의
- technical: 제품 오류, 소프트웨어 버그, 설치 문제, 네트워크 오류, 기술 설정 등

반드시 아래 JSON 형식으로만 답변하세요 (다른 텍스트 없이):
{"type": "general 또는 technical", "reason": "분류 이유 한 줄"}"""
        },
        {"role": "user", "content": f"고객 문의: {user_input}"}
    ]

    for attempt in range(3):
        try:
            response = ollama.chat(model=MODEL, messages=messages)
            text = response.message.content.strip()

            # JSON 블록 추출
            if "```json" in text:
                text = text[text.find("```json") + 7: text.rfind("```")].strip()
            elif "```" in text:
                text = text[text.find("```") + 3: text.rfind("```")].strip()

            result = json.loads(text)
            return result.get("type", "general"), result.get("reason", "")
        except Exception:
            if attempt == 2:
                return "general", "분류 실패 — 일반 문의로 처리"


def general_response(user_input: str, conversation_history: list) -> str:
    """일반 문의를 자체적으로 처리한다."""
    messages = [
        {
            "role": "system",
            "content": "당신은 친절한 고객 서비스 담당자입니다. 고객의 일반 문의에 간결하게 답변하세요. 한국어로 답변하세요."
        }
    ]
    # 이전 대화 이력 포함
    for item in conversation_history:
        messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": user_input})

    response = ollama.chat(model=MODEL, messages=messages)
    return response.message.content


def customer_service_agent(user_input: str, conversation_history: list) -> dict:
    """
    고객 서비스 에이전트 (오케스트레이터 역할).
    - 일반 문의: 자체 처리
    - 기술 문의: call_agent를 통해 기술 에이전트에게 메모리 핸드오프
    """
    inquiry_type, reason = classify_inquiry(user_input)
    print(f"  [고객서비스] 문의 분류: {inquiry_type} — {reason}")

    if inquiry_type == "technical":
        print("  [고객서비스] 기술 문의 감지 → 기술 지원 에이전트에게 핸드오프")
        # 현재 메시지도 맥락에 포함하여 전달
        full_history = conversation_history + [{"role": "user", "content": user_input}]
        result = call_agent(
            agent_fn=tech_support_agent,
            task=user_input,
            conversation_history=full_history  # 메모리 핸드오프
        )
        return {
            "handled_by": "tech_support_agent",
            "response": result["response"]
        }
    else:
        print("  [고객서비스] 일반 문의 → 자체 처리")
        response = general_response(user_input, conversation_history)
        return {
            "handled_by": "customer_service_agent",
            "response": response
        }


# ─────────────────────────────────────────────────────────────
# 테스트: 고객 대화 시뮬레이션
# ─────────────────────────────────────────────────────────────

def run_conversation():
    """
    고객 대화를 단계적으로 시뮬레이션한다.
    메모리 핸드오프를 통해 기술 에이전트가 이전 대화 맥락을 활용하는지 확인한다.
    """
    print("=" * 65)
    print("고객 서비스 멀티 에이전트 시스템 (메모리 핸드오프 패턴)")
    print("=" * 65)

    # 고객 대화 시나리오
    conversation = [
        {"role": "user",     "content": "안녕하세요, 지난주에 노트북을 구매했는데요."},
        {"role": "assistant", "content": "안녕하세요! 구매해 주셔서 감사합니다. 어떤 도움이 필요하신가요?"},
        {"role": "user",     "content": "배송은 잘 받았는데, 처음 켰을 때부터 Wi-Fi가 연결이 안 됩니다."},
    ]

    # 일반 문의 테스트
    general_inquiry = "반품 정책이 어떻게 되나요?"

    # 기술 문의 테스트 (이전 대화 맥락이 넘어가야 함)
    technical_inquiry = "Wi-Fi 드라이버를 재설치해도 여전히 연결이 안 됩니다. 어떻게 해야 하나요?"

    # ── 테스트 1: 일반 문의 ──────────────────────────────────
    print(f"\n{'─' * 65}")
    print(f"[테스트 1] 일반 문의")
    print(f"고객: {general_inquiry}")
    result1 = customer_service_agent(general_inquiry, conversation[:2])
    print(f"\n처리 에이전트: {result1['handled_by']}")
    print(f"응답:\n{result1['response']}")

    # ── 테스트 2: 기술 문의 (메모리 핸드오프 발동) ────────────
    print(f"\n{'─' * 65}")
    print(f"[테스트 2] 기술 문의 — 메모리 핸드오프 확인")
    print(f"고객: {technical_inquiry}")
    print(f"\n[전달될 대화 맥락 ({len(conversation)}개 항목)]:")
    for item in conversation:
        print(f"  {item['role'].upper()}: {item['content']}")

    result2 = customer_service_agent(technical_inquiry, conversation)
    print(f"\n처리 에이전트: {result2['handled_by']}")
    print(f"응답:\n{result2['response']}")

    # ── 검증: 기술 에이전트가 맥락을 활용했는지 ───────────────
    print(f"\n{'─' * 65}")
    print("[검증] 기술 에이전트 응답에서 맥락 활용 여부 확인")
    context_keywords = ["노트북", "Wi-Fi", "지난주", "구매", "드라이버"]
    found = [kw for kw in context_keywords if kw in result2["response"]]
    if found:
        print(f"  맥락 키워드 감지됨: {found}")
        print("  → 기술 에이전트가 고객 대화 맥락을 활용했습니다.")
    else:
        print("  → 맥락 키워드가 응답에서 명시적으로 발견되지 않았으나,")
        print("     대화 이력은 정상적으로 전달되었습니다.")

    print(f"\n{'=' * 65}")
    print("완료")


if __name__ == "__main__":
    run_conversation()
