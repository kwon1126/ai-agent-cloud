from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import os

# macOS 한글 폰트 등록
font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
pdfmetrics.registerFont(TTFont("AppleGothic", font_path))

output_path = os.path.join(os.path.dirname(__file__), "company_policy.pdf")
c = canvas.Canvas(output_path, pagesize=A4)
width, height = A4

c.setFont("AppleGothic", 20)
c.drawCentredString(width / 2, height - 3 * cm, "ABC 주식회사 사내 정책서")

c.setFont("AppleGothic", 10)
c.drawCentredString(width / 2, height - 4 * cm, "2026년 1월 개정")

sections = [
    ("제1조 근무시간", [
        "1. 정규 근무시간은 오전 9시부터 오후 6시까지이다.",
        "2. 점심시간은 오후 12시부터 1시까지이다.",
        "3. 유연근무제를 적용하며, 코어타임은 오전 10시~오후 4시이다.",
    ]),
    ("제2조 연차휴가", [
        "1. 입사 1년 미만: 매월 1일의 유급휴가가 발생한다.",
        "2. 입사 1년 이상: 연간 15일의 유급휴가가 부여된다.",
        "3. 3년 이상 근속 시 매 2년마다 1일의 추가 휴가가 부여된다.",
        "4. 연차휴가는 당해 연도 내 사용을 원칙으로 한다.",
    ]),
    ("제3조 재택근무", [
        "1. 주 2회까지 재택근무가 가능하다.",
        "2. 재택근무 시 전날까지 팀장에게 사전 승인을 받아야 한다.",
        "3. 재택근무 중에도 코어타임(오전 10시~오후 4시)에는 연락 가능해야 한다.",
    ]),
    ("제4조 경비 처리", [
        "1. 업무 관련 경비는 법인카드 사용을 원칙으로 한다.",
        "2. 식대 지원: 야근 시(오후 9시 이후) 1인당 15,000원 한도.",
        "3. 교통비: 야근 택시비는 오후 10시 이후 귀가 시 실비 지급.",
        "4. 도서 구입비: 분기당 50,000원 한도 내 지원.",
        "5. 모든 경비는 영수증 첨부 후 7일 이내 정산해야 한다.",
    ]),
    ("제5조 보안", [
        "1. 사내 자료의 외부 반출은 보안팀 승인 후 가능하다.",
        "2. 개인 USB 사용은 금지한다.",
        "3. 퇴근 시 PC 화면 잠금(Win+L)을 필수로 실행한다.",
        "4. 고객 개인정보는 암호화하여 저장해야 한다.",
    ]),
]

y = height - 5.5 * cm

for title, items in sections:
    if y < 4 * cm:
        c.showPage()
        y = height - 3 * cm

    c.setFont("AppleGothic", 14)
    c.drawString(2 * cm, y, title)
    y -= 0.8 * cm

    c.setFont("AppleGothic", 11)
    for item in items:
        if y < 3 * cm:
            c.showPage()
            y = height - 3 * cm
        c.drawString(2.5 * cm, y, item)
        y -= 0.6 * cm

    y -= 0.5 * cm

c.save()
print(f"PDF 생성 완료: {output_path}")
