"""
실습 2: 전문가 페르소나가 붙은 인보이스 에이전트
=====================================================
실행: uv run python student/02_invoice_agent_with_experts.py

심화 과제:
  - purchasing_rules.txt 내용을 바꿔보고 동작이 달라지는지 확인하세요
"""

import os
import json
import ollama

MODEL = "qwen2.5-coder:7b"

# ─────────────────────────────────────────────────────────────
# 실습 1 완성 코드 (수정하지 마세요)
# ─────────────────────────────────────────────────────────────

def prompt_llm_for_json(schema: dict, prompt: str) -> dict:
    system_message = f"""당신은 JSON 데이터 추출 전문가입니다.
반드시 아래 JSON 스키마를 따르는 유효한 JSON을 출력해야 합니다.
출력은 ```json 코드블록으로 감싸세요.
다른 설명 없이 JSON만 출력하세요.

스키마:
{json.dumps(schema, ensure_ascii=False, indent=2)}"""

    for attempt in range(3):
        try:
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ]
            )
            text = response.message.content

            if "```json" in text:
                start = text.find("```json") + 7
                end = text.rfind("```")
                text = text[start:end].strip()
            elif "```" in text:
                start = text.find("```") + 3
                end = text.rfind("```")
                text = text[start:end].strip()

            return json.loads(text)

        except Exception as e:
            if attempt == 2:
                raise RuntimeError(f"JSON 추출 실패: {e}")

    return {}


def extract_invoice_data(document_text: str) -> dict:
    invoice_schema = {
        "type": "object",
        "required": ["invoice_number", "date", "total_amount"],
        "properties": {
            "invoice_number": {"type": "string"},
            "date": {"type": "string"},
            "vendor": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                }
            },
            "total_amount": {"type": "number"},
            "currency": {"type": "string"},
            "line_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "total": {"type": "number"},
                    }
                }
            }
        }
    }
    prompt = f"""아래 인보이스 문서에서 핵심 정보를 추출하세요.
금액은 숫자만, 날짜는 YYYY-MM-DD 형식으로.

<invoice>
{document_text}
</invoice>"""
    return prompt_llm_for_json(invoice_schema, prompt)


invoice_storage: dict[str, dict] = {}

def store_invoice(invoice_data: dict) -> dict:
    invoice_number = invoice_data.get("invoice_number")
    if not invoice_number:
        raise ValueError("인보이스 번호가 없습니다")
    invoice_storage[invoice_number] = invoice_data
    return {"status": "success", "invoice_number": invoice_number}


# ─────────────────────────────────────────────────────────────
# Step 1: 지출 분류 전문가 (페르소나 패턴)
# ─────────────────────────────────────────────────────────────

EXPENSE_CATEGORIES = ["사무용품", "IT/소프트웨어", "교육/훈련", "출장/교통", "시설/유지보수", "마케팅/홍보", "기타"]

def classify_expense(invoice_data: dict) -> dict:
    schema = {
        "type": "object",
        "required": ["category", "confidence", "reason"],
        "properties": {
            "category": {"type": "string", "enum": EXPENSE_CATEGORIES},
            "confidence": {"type": "string", "enum": ["높음", "중간", "낮음"]},
            "reason": {"type": "string"},
        }
    }

    items_desc = "\n".join(
        f"  - {item.get('description', '')}"
        for item in invoice_data.get("line_items", [])
    )

    # TODO: 페르소나 패턴을 사용해서 prompt를 작성하세요
    # 힌트: "기업 재무 지출 분류 전문가로서 행동하라" 로 시작하세요
    # 힌트: 인보이스 정보 (vendor, total_amount, line_items)를 포함하세요
    # 힌트: 카테고리 목록(EXPENSE_CATEGORIES)을 알려주세요
    prompt = ""  # TODO: 여기를 채우세요

    return prompt_llm_for_json(schema, prompt)


# ─────────────────────────────────────────────────────────────
# Step 2: 구매 규칙 전문가 (Document-as-Implementation)
# ─────────────────────────────────────────────────────────────

def load_purchasing_rules() -> str:
    rules_path = os.path.join(os.path.dirname(__file__), "purchasing_rules.txt")
    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "구매 규칙 파일을 찾을 수 없습니다. 모든 인보이스를 준수로 처리합니다."


def check_compliance(invoice_data: dict) -> dict:
    purchasing_rules = load_purchasing_rules()

    schema = {
        "type": "object",
        "required": ["is_compliant", "issues", "recommendation"],
        "properties": {
            "is_compliant": {"type": "boolean"},
            "issues": {"type": "array", "items": {"type": "string"}},
            "recommendation": {"type": "string"},
        }
    }

    # TODO: 페르소나 패턴 + Document-as-Implementation 으로 prompt를 작성하세요
    # 힌트: "구매 규칙 준수 전문가로서 행동하라" 로 시작하세요
    # 힌트: purchasing_rules를 <purchasing_rules> 태그 안에 넣으세요
    # 힌트: 인보이스 정보를 함께 넣으세요
    prompt = ""  # TODO: 여기를 채우세요

    return prompt_llm_for_json(schema, prompt)


# ─────────────────────────────────────────────────────────────
# Step 3: purchasing_rules.txt 작성
# ─────────────────────────────────────────────────────────────
# TODO: student/ 폴더 안에 purchasing_rules.txt 파일을 직접 만들어보세요
# 규칙 예시: 금액 한도, 승인 기준, 금지 항목 등 3~5개면 충분합니다


# ─────────────────────────────────────────────────────────────
# 실행 코드 (완성되어 있습니다)
# ─────────────────────────────────────────────────────────────

SAMPLE_INVOICES = [
    """
    INVOICE
    Invoice Number: INV-2024-0042
    Date: 2024-05-10
    From: 한국오피스서플라이 주식회사
    Items:
    - A4 복사용지 (500매 x 10박스)   120,000원
    - 볼펜 세트 (12개입)               42,500원
    - 화이트보드 마커 세트              45,000원
    TOTAL: 228,250원
    """,
    """
    청구서
    청구서번호: 2024-KR-0087
    발행일: 2024년 5월 12일
    공급자: 테크솔루션즈 코리아
    1. 클라우드 서버 호스팅 (1개월) .... 450,000원
    2. 보안 솔루션 라이선스 (연간) ..... 1,200,000원
    3. 기술 지원 서비스 (10시간) ....... 300,000원
    청구금액: 2,145,000원
    """,
]


def process_invoice_full(invoice_text: str) -> None:
    print("[1] 데이터 추출 중...")
    invoice_data = extract_invoice_data(invoice_text)
    store_invoice(invoice_data)
    print(f"    → {invoice_data.get('invoice_number')} | {invoice_data.get('vendor', {}).get('name', '?')} | {invoice_data.get('total_amount', 0):,}원")

    print("[2] 지출 분류 중... (전문가 페르소나)")
    classification = classify_expense(invoice_data)
    print(f"    → {classification.get('category')} (신뢰도: {classification.get('confidence')})")
    print(f"    → 근거: {classification.get('reason')}")

    print("[3] 구매 규칙 준수 확인 중... (Document-as-Implementation)")
    compliance = check_compliance(invoice_data)
    status = "✓ 준수" if compliance.get("is_compliant") else "✗ 위반/주의"
    print(f"    → {status}")
    for issue in compliance.get("issues", []):
        print(f"       - {issue}")
    print(f"    → 권고: {compliance.get('recommendation')}")


def main():
    print(f"전문가 페르소나 인보이스 에이전트 (모델: {MODEL})\n")

    for i, invoice in enumerate(SAMPLE_INVOICES, 1):
        print(f"\n{'=' * 60}")
        print(f"인보이스 {i}/{len(SAMPLE_INVOICES)} 처리")
        process_invoice_full(invoice)

    print(f"\n{'=' * 60}")
    print(f"처리 완료! 저장된 인보이스 수: {len(invoice_storage)}")
    print("\n[심화 과제] purchasing_rules.txt 내용을 바꾼 뒤 다시 실행해보세요.")


if __name__ == "__main__":
    main()
