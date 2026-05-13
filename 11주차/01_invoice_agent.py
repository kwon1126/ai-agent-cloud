"""
실습 1: 인보이스 처리 에이전트
=====================================
실행: uv run python student/01_invoice_agent.py
"""

import json
import ollama

MODEL = "qwen2.5-coder:7b"

SAMPLE_INVOICES = [
    """
    INVOICE
    Invoice Number: INV-2024-0042
    Date: 2024-05-10
    From: 한국오피스서플라이 주식회사
    Bill To: 강남대학교
    Items:
    - A4 복사용지 (500매 x 10박스)   단가: 12,000원   수량: 10   합계: 120,000원
    - 볼펜 세트 (12개입)              단가: 8,500원    수량: 5    합계: 42,500원
    - 화이트보드 마커 세트             단가: 15,000원   수량: 3    합계: 45,000원
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


# ─────────────────────────────────────────────────────────────
# Step 1: LLM을 호출해서 JSON을 받아오는 함수
# ─────────────────────────────────────────────────────────────

def prompt_llm_for_json(schema: dict, prompt: str) -> dict:
    """LLM에게 schema에 맞는 JSON을 생성하게 한다. 최대 3번 재시도."""

    system_message = f"""당신은 JSON 데이터 추출 전문가입니다.
반드시 아래 JSON 스키마를 따르는 유효한 JSON을 출력해야 합니다.
출력은 ```json 코드블록으로 감싸세요.
다른 설명 없이 JSON만 출력하세요.

스키마:
{json.dumps(schema, ensure_ascii=False, indent=2)}"""

    for attempt in range(3):
        try:
            # TODO: ollama.chat()을 호출해서 LLM 응답을 받으세요
            # 힌트: model=MODEL, messages에 system_message와 prompt를 넣어야 합니다
            response = None  # TODO: 여기를 채우세요
            text = ""        # TODO: response에서 텍스트를 꺼내세요

            # 마크다운 코드블록 제거 (이 부분은 완성되어 있습니다)
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
            print(f"  [재시도 {attempt + 1}/3] 오류: {e}")
            if attempt == 2:
                raise RuntimeError(f"JSON 추출 실패: {e}")

    return {}


# ─────────────────────────────────────────────────────────────
# Step 2: 인보이스에서 데이터를 추출하는 함수
# ─────────────────────────────────────────────────────────────

def extract_invoice_data(document_text: str) -> dict:
    """인보이스 텍스트에서 표준화된 데이터를 추출한다."""

    # TODO: 인보이스에서 어떤 정보를 뽑아야 할지 스키마를 직접 설계하세요
    # 힌트: 인보이스 번호, 날짜, 금액은 필수입니다
    invoice_schema = {
        "type": "object",
        "required": [],  # TODO: 필수 필드를 넣으세요
        "properties": {
            # TODO: 필요한 필드를 추가하세요
            # 예시:
            # "invoice_number": {"type": "string", "description": "인보이스 번호"},
        }
    }

    prompt = f"""아래 인보이스 문서에서 핵심 정보를 추출하세요.
금액은 숫자만 추출하고 통화 기호나 단위는 제외하세요.
날짜는 YYYY-MM-DD 형식으로 변환하세요.

<invoice>
{document_text}
</invoice>"""

    return prompt_llm_for_json(invoice_schema, prompt)


# ─────────────────────────────────────────────────────────────
# Step 3: 인보이스를 저장하는 함수 (완성되어 있습니다)
# ─────────────────────────────────────────────────────────────

invoice_storage: dict[str, dict] = {}

def store_invoice(invoice_data: dict) -> dict:
    invoice_number = invoice_data.get("invoice_number")
    if not invoice_number:
        raise ValueError("인보이스 번호가 없습니다")
    invoice_storage[invoice_number] = invoice_data
    return {
        "status": "success",
        "message": f"인보이스 {invoice_number} 저장 완료",
        "invoice_number": invoice_number,
    }


# ─────────────────────────────────────────────────────────────
# 실행 코드 (완성되어 있습니다)
# ─────────────────────────────────────────────────────────────

def main():
    print(f"인보이스 처리 에이전트 시작 (모델: {MODEL})\n")

    for i, invoice in enumerate(SAMPLE_INVOICES, 1):
        print(f"\n{'=' * 60}")
        print(f"인보이스 {i}/{len(SAMPLE_INVOICES)} 처리 중...")

        print("[1] 데이터 추출 중...")
        extracted = extract_invoice_data(invoice)
        print(json.dumps(extracted, ensure_ascii=False, indent=2))

        print("[2] 저장 중...")
        result = store_invoice(extracted)
        print(result["message"])

    print(f"\n{'=' * 60}")
    print("저장된 인보이스 목록:")
    for inv_num, data in invoice_storage.items():
        total = data.get("total_amount", "?")
        vendor = data.get("vendor", {}).get("name", "?")
        date = data.get("date", "?")
        print(f"  [{inv_num}] {date} | {vendor} | {total}")


if __name__ == "__main__":
    main()
