#!/usr/bin/env python3
"""2차 2주(Day 15~28) 기획표 생성기.

docs/03_연말_한파_응급케어_2차_2주_기획표_키워드.pdf 와
docs/03_연말_한파_응급케어_2차_2주_기획표.md 를 같은 데이터에서 만든다.
(디자인 기준: docs/02_겨울철_건강관리_2주_기획표_키워드.pdf)
"""
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, LongTable,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT_DIR = "/workspace/fonts"
DOCS = os.path.join(BASE, "docs")
PDF_OUT = os.path.join(DOCS, "03_연말_한파_응급케어_2차_2주_기획표_키워드.pdf")
MD_OUT = os.path.join(DOCS, "03_연말_한파_응급케어_2차_2주_기획표.md")

CATEGORY = "의학/건강"

META = [
    ("기획 대상", "김승태 님 (응급의학과 의사 / 전문 칼럼니스트)", "발행 주기", "1일 1회 · 2주간 총 14편"),
    ("대주제", "연말 모임 & 한파 대비 응급실 실전 케어", "목표 채널", "네이버 블로그 · 인스타그램 · 페이스북"),
    ("세부 분류", "3주차 연말 모임·응급실 실전 / 4주차 한파·생활응급 심화", "자동화 연동", "Notion 콘텐츠 보드 & Claude 연동 완비"),
    ("노션 카테고리", "의학/건강 (14편 전체)", "다음 기획", "Day 29~42(3차) · 2주 후 대주제 확정 후"),
]

# day, 주제, [키워드 3], 타깃 독자, 핵심 인사이트, 후킹 포인트
DAYS = [
    (15, "송년회 음주와 숙취·급성 알코올성 위염 (응급실 링거·수액 기준)",
     ["알코올성 위염 증상", "숙취 링거 효과", "숙취 두통 원인"],
     "연말 송년회가 잦은 30~50대 직장인, 숙취에 링거를 찾는 20~40대",
     "숙취는 탈수·아세트알데히드·위점막 손상의 합. 구토로 물도 못 넘길 때만 수액이 답이고, 해장술과 진한 커피는 위산을 더 자극한다.",
     "술 깨려고 응급실 링거 맞으러 가는 사람들, 정말 효과 있을까?"),
    (16, "연말 과식·기름진 안주 후 급성 복통: 맹장염·담낭염·급성 췌장염 구별법",
     ["오른쪽 윗배 통증 원인", "담낭염 초기 증상", "급성 췌장염 통증 위치"],
     "40~60대, 기름진 회식이 잦은 직장인, 담석·고지혈증·음주 습관 보유자",
     "우상복부 통증이 등으로 뻗고 기름진 음식 뒤 심하면 담낭염, 명치에서 띠처럼 조이면 췌장염, 배꼽에서 우하복부로 옮겨가면 맹장염. 6시간 지속·발열·황달은 응급.",
     "소화제로 안 낫는 명치 통증, 췌장일 수 있습니다"),
    (17, "겨울철 생선가시·떡·고기 기도 폐쇄 (하임리히법 & 응급실 내원 기준)",
     ["하임리히법 방법", "목에 가시 걸렸을 때", "기도 폐쇄 응급처치"],
     "가족과 함께 식사하는 전 연령, 어르신·아이가 있는 가정",
     "말과 기침이 나오면 기도는 완전히 막히지 않았다. 말도 기침도 안 나오면 즉시 하임리히법. 가시는 밥 뭉치로 밀면 식도 점막이 찢어진다.",
     "가시 걸렸을 때 밥 덩어리로 밀어내면 생기는 일"),
    (18, "연말 수면 부족·피로 누적과 돌발성 어지럼증 (이석증 vs 뇌졸중 구별법)",
     ["이석증 증상", "어지럼증 뇌졸중 구별", "돌발성 어지럼증 원인"],
     "40~70대, 수면 부족이 누적된 직장인, 고혈압·당뇨 동반자",
     "이석증은 자세 변화에 수 초~1분 회전성 어지럼. 복시·발음 장애·한쪽 마비·걷기 불가가 붙으면 뇌졸중이고, 5분에 사라져도 골든타임은 4.5시간.",
     "어지럽다 5분 만에 괜찮아졌다? 그게 위험 신호일 수 있습니다"),
    (19, "겨울철 일산화탄소 중독과 밀폐 공간 난방기구 안전 수칙 (캠핑·차박·보일러)",
     ["일산화탄소 중독 증상", "차박 난방 사고", "보일러 일산화탄소 점검"],
     "캠핑·차박을 즐기는 30~50대, 노후 보일러를 쓰는 가구, 1인 가구",
     "무색무취에 혈색소 결합력이 산소의 200배. 두통·구역을 감기로 오인하다 의식이 흐려지면 못 빠져나온다. 실내 연소기구는 창문 열고, 의심되면 119.",
     "차박 중 찾아온 두통, 감기가 아니라 중독입니다"),
    (20, "한파 속 혈당 스파이크와 연말 모임 당뇨인 외식·음주 생존법",
     ["당뇨 연말 외식 메뉴", "혈당 스파이크 원인", "당뇨 술 마실 때 주의"],
     "40~60대 당뇨 환자와 가족, 당뇨 전단계·공복혈당 장애",
     "추위엔 교감신경 항진으로 인슐린 반응이 흔들리고, 술은 몇 시간 뒤 혈당을 떨어뜨린다. 채소·단백질 먼저, 공복 음주 금지, 새벽 혈당 확인.",
     "당뇨인이 술 마신 다음날 새벽이 더 위험한 이유"),
    (21, "겨울철 눈길·빙판길 발목 염좌 vs 골절: RICE 응급처치와 X-ray 기준",
     ["발목 염좌 응급처치", "발목 골절 구별법", "RICE 요법 방법"],
     "눈길 출퇴근 직장인, 60대 이상 보행자, 겨울 등산·러닝 인구",
     "복사뼈 주변 네 곳 압통과 네 걸음 가능 여부가 X-ray 기준. 48시간은 보호·냉찜질 15~20분·압박·거상이고, 급성기 온찜질과 마사지는 독.",
     "삐었다고 그냥 두면 발목이 영구히 약해집니다"),
    (22, "겨울철 안면마비(구안와사) 전조증상과 골든타임 (벨마비 vs 뇌경색)",
     ["구안와사 초기 증상", "벨마비 뇌졸중 차이", "안면마비 골든타임"],
     "40~70대, 한파에 노출되는 야외 근로자, 고혈압·당뇨 환자",
     "이마에 주름이 잡히면 말초성 벨마비, 이마는 움직이고 입가만 처지면 뇌졸중. 벨마비는 72시간 내 스테로이드가 회복률을 좌우한다.",
     "입이 돌아갔을 때 '이마 주름' 하나로 병이 갈립니다"),
    (23, "콧물·코막힘·부비동염(축농증)과 코피 응급 지혈의 정석",
     ["축농증 증상 치료", "코피 지혈 방법", "코막힘 부비동염"],
     "겨울철 건조한 실내에서 지내는 성인, 아이·어르신이 있는 가정",
     "코피는 앞으로 숙여 콧방울 5~10분 압박. 뒤로 젖히면 피가 인두로 넘어가 기도·구토 위험이 생긴다. 10분 넘게 멈추지 않으면 응급실.",
     "코피에 고개를 뒤로 젖히면 위험한 이유"),
    (24, "겨울철 소아 고열·열성경련 대처법 (해열제 교차복용과 응급실 신호)",
     ["열성경련 대처법", "소아 해열제 교차복용", "아기 고열 응급실 기준"],
     "영유아·초등 저학년 부모, 조부모 양육자",
     "열성경련은 5분 내 멈추면 대부분 무해. 옆으로 눕히고 입에 아무것도 넣지 않는다. 5분 초과·24시간 내 반복·한쪽 떨림·의식 지연은 119.",
     "39도 열보다 위험한 건 아이의 상태입니다"),
    (25, "겨울철 심야 가슴 통증: 역류성 식도염 vs 협심증·대동맥박리 구별법",
     ["밤에 가슴 답답한 이유", "협심증 초기 증상", "역류성 식도염 가슴 통증"],
     "50대 이상, 야식·음주 습관이 있는 직장인, 고혈압·이상지질혈증 환자",
     "협심증은 5~15분 조이는 통증과 팔·턱 방사통, 박리는 찢어지듯 등으로 번진다. 20분 넘게 지속되거나 식은땀·호흡곤란이 붙으면 즉시 119.",
     "밤에 가슴이 답답할 때 '체한 것 같다'고 넘기면 안 되는 이유"),
    (26, "수족냉증과 레이노 현상: 단순 손발 시림 vs 혈관·자가면역 질환 신호",
     ["수족냉증 원인", "레이노 증후군 증상", "손발이 시린 질환"],
     "20~50대 여성, 흡연자, 류마티스 질환 가족력이 있는 30~60대",
     "추위에 손가락이 흰색→청색→홍색으로 변하는 삼단계가 레이노. 한쪽만 심하거나 손끝 궤양·피부 경화가 있으면 자가면역 검사가 필요하다.",
     "손끝이 하얗게 변했다가 파래진다면, 추위 탓만은 아닙니다"),
    (27, "겨울철 실내 환기 부족과 두통·만성피로 개선 루틴 (수면·조도·수분)",
     ["겨울철 환기 시간", "실내 두통 원인", "환기 부족 만성피로"],
     "재택·실내 근무 직장인, 밀폐 난방으로 지내는 1인 가구와 어르신",
     "닫힌 방은 이산화탄소가 1,000ppm을 넘기 쉽고 이 농도에서 두통·집중력 저하가 온다. 하루 세 번 10분 맞통풍, 습도 40~60%, 아침 햇빛 10분.",
     "환기 안 한 방에서 자면 다음 날 두통이 오는 이유"),
    (28, "한파 대비 가정용 상비약·응급키트 10가지 총정리 (응급의학과 의사가 직접 고른 리스트)",
     ["가정 상비약 리스트", "응급키트 구성", "겨울철 필수 상비약"],
     "모든 가구, 특히 1인 가구와 노부모를 모시는 가정",
     "해열진통제·전해질·체온계·압박붕대·소독제·찜질팩·담요·상처연고·복약 목록·응급연락 카드. 반기마다 유효기간 확인, 남은 항생제는 보관하지 않는다.",
     "응급실 의사가 우리 집에 꼭 두는 10가지"),
]

WEEK_TITLES = {
    15: "3주차 · 연말 모임 & 응급실 실전 케어 (Day 15~21)",
    22: "4주차 · 한파 & 생활응급 심화 (Day 22~28)",
}

NAVY = colors.HexColor("#16365C")
BLUE = colors.HexColor("#1F4E79")
BAND = colors.HexColor("#E8F0FA")
LINE = colors.HexColor("#C9D6E4")
ZEBRA = colors.HexColor("#F7FAFC")
INK = colors.HexColor("#1F2430")
GRAY = colors.HexColor("#5A6472")
LIGHT_BLUE = colors.HexColor("#DCE8F7")


def register_fonts():
    pdfmetrics.registerFont(TTFont("Nanum", os.path.join(FONT_DIR, "NanumGothic-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Nanum-Bold", os.path.join(FONT_DIR, "NanumGothic-Bold.ttf")))
    pdfmetrics.registerFontFamily("Nanum", normal="Nanum", bold="Nanum-Bold")


def styles():
    s = {}
    s["kicker"] = ParagraphStyle("kicker", fontName="Nanum-Bold", fontSize=7.6, leading=10,
                                 textColor=BLUE, alignment=TA_LEFT)
    s["title"] = ParagraphStyle("title", fontName="Nanum-Bold", fontSize=21, leading=27,
                                textColor=NAVY, spaceBefore=4, spaceAfter=6)
    s["sub"] = ParagraphStyle("sub", fontName="Nanum", fontSize=10, leading=15, textColor=GRAY)
    s["h2"] = ParagraphStyle("h2", fontName="Nanum-Bold", fontSize=14, leading=19,
                             textColor=INK, spaceBefore=16, spaceAfter=6)
    s["body"] = ParagraphStyle("body", fontName="Nanum", fontSize=8.4, leading=12.5,
                               textColor=colors.HexColor("#3A4250"), spaceAfter=2)
    s["bullet"] = ParagraphStyle("bullet", fontName="Nanum", fontSize=8.4, leading=12.5,
                                 textColor=colors.HexColor("#3A4250"), leftIndent=10,
                                 bulletIndent=2, spaceAfter=2)
    s["meta_l"] = ParagraphStyle("meta_l", fontName="Nanum-Bold", fontSize=7.8, leading=10.4, textColor=NAVY)
    s["meta_v"] = ParagraphStyle("meta_v", fontName="Nanum", fontSize=7.8, leading=10.4, textColor=INK)
    s["th"] = ParagraphStyle("th", fontName="Nanum-Bold", fontSize=7.8, leading=10.4,
                             textColor=colors.white, alignment=TA_CENTER)
    s["day"] = ParagraphStyle("day", fontName="Nanum-Bold", fontSize=7.8, leading=10.4,
                              textColor=NAVY, alignment=TA_CENTER)
    s["topic"] = ParagraphStyle("topic", fontName="Nanum-Bold", fontSize=7.5, leading=10.2, textColor=INK)
    s["kw"] = ParagraphStyle("kw", fontName="Nanum", fontSize=7.2, leading=9.8,
                             textColor=colors.HexColor("#2E4762"), leftIndent=7, bulletIndent=0)
    s["cat"] = ParagraphStyle("cat", fontName="Nanum", fontSize=7.2, leading=9.6,
                              textColor=colors.HexColor("#2E4762"), alignment=TA_CENTER)
    s["ins"] = ParagraphStyle("ins", fontName="Nanum", fontSize=7.2, leading=9.9,
                              textColor=colors.HexColor("#2B3341"))
    s["week"] = ParagraphStyle("week", fontName="Nanum-Bold", fontSize=8.6, leading=12,
                               textColor=colors.white)
    s["target"] = ParagraphStyle("target", fontName="Nanum", fontSize=7.2, leading=9.9,
                                 textColor=colors.HexColor("#2B3341"))
    return s


def header_block(s):
    flow = []
    flow.append(Table([["2ND CYCLE CONTENT STRATEGY & KEYWORD CALENDAR"]],
                      colWidths=[493], style=TableStyle([
                          ("BACKGROUND", (0, 0), (-1, -1), BAND),
                          ("LEFTPADDING", (0, 0), (-1, -1), 8),
                          ("TOPPADDING", (0, 0), (-1, -1), 4),
                          ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                          ("FONTNAME", (0, 0), (-1, -1), "Nanum-Bold"),
                          ("FONTSIZE", (0, 0), (-1, -1), 7.2),
                          ("TEXTCOLOR", (0, 0), (-1, -1), BLUE),
                      ])))
    flow.append(Paragraph("연말·한파 응급케어 14일(2주) 데일리 콘텐츠 기획표", s["title"]))
    flow.append(Paragraph("응급실 실전 케어와 네이버 C-Rank / 구글 SEO 검색 유입을 겨냥한 2차 2주 캘린더", s["sub"]))
    flow.append(Paragraph("Day 15~28 · 1일 1주제 × 주제별 핵심 검색 키워드 3개 · 노션 콘텐츠 보드 등록 완료(14건)", s["sub"]))

    rule = Table([[""]], colWidths=[493], rowHeights=[2], style=TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 1.1, BLUE), ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    flow.append(Spacer(1, 10))
    flow.append(rule)
    flow.append(Spacer(1, 10))

    rows = []
    for l1, v1, l2, v2 in META:
        rows.append([Paragraph(l1, s["meta_l"]), Paragraph(v1, s["meta_v"]),
                     Paragraph(l2, s["meta_l"]), Paragraph(v2, s["meta_v"])])
    meta = Table(rows, colWidths=[62, 186, 66, 179], style=TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F4F8FC")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F4F8FC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5.5),
    ]))
    flow.append(meta)
    return flow


COLS = [38, 136, 104, 44, 171]


def week_row(no, s):
    return Table([[Paragraph(WEEK_TITLES[no], s["week"])]], colWidths=[493],
                 style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), BLUE),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 7),
                                   ("TOPPADDING", (0, 0), (-1, -1), 4),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))


def target_table(s):
    """타깃 독자를 7행×2단으로 나눈 좌우 배치 표(페이지 여백 최소화)."""
    left, right = DAYS[:7], DAYS[7:]
    head = [Paragraph("일차", s["th"]), Paragraph("타깃 독자", s["th"]),
            Paragraph("일차", s["th"]), Paragraph("타깃 독자", s["th"])]
    data = [head]
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LINEAFTER", (1, 0), (1, -1), 1.1, colors.white),
    ]
    for i in range(7):
        row = [Paragraph(f"Day {left[i][0]:02d}", s["day"]), Paragraph(left[i][3], s["target"]),
               Paragraph(f"Day {right[i][0]:02d}", s["day"]), Paragraph(right[i][3], s["target"])]
        data.append(row)
        if i % 2 == 1:
            style.append(("BACKGROUND", (0, i + 1), (-1, i + 1), ZEBRA))
    t = Table(data, colWidths=[38, 208, 38, 209])
    t.setStyle(TableStyle(style))
    return t


def guide_section(s):
    flow = [Paragraph("3. 노션 & 자동화 엔진(Claude) 즉시 실행 가이드", s["h2"])]
    flow.append(Paragraph(
        "이번 14편은 노션 콘텐츠 보드에 <b>아이디어</b> 상태로 14건 모두 등록되어 있습니다. "
        "행 하나를 <b>생성요청</b>으로 바꾸면 엔진이 해당 주제와 키워드로 블로그·광고·카드뉴스·칠판 쇼츠를 한 번에 뽑습니다.", s["body"]))
    for b in [
        "<b>방법 1 (스마트폰·노션)</b>: 노션의 콘텐츠 보드에서 원하는 날짜 행의 상태를 [생성요청]으로 바꾸면 즉시 원고 생성이 시작됩니다.",
        "<b>방법 2 (대화창)</b>: 비서 겅태에게 \"Day 15 진행해줘\"라고 말하면 1초 만에 착수해 10분 뒤 블로그·임상·쇼츠까지 완료 보고를 받습니다.",
        "<b>방법 3 (Claude.ai 직접 작성)</b>: Claude 앱에 접속해 이 기획표의 주제·키워드·인사이트를 붙여 넣으면 같은 톤의 원고가 나옵니다.",
        "<b>결과물 저장</b>: 완성 원고는 GitHub 저장소(content/날짜-순번), 노션 보드, 앱 위젯, 다운로드 4곳에 동시에 남습니다.",
    ]:
        flow.append(Paragraph(b, s["bullet"], bulletText="·"))
    flow.append(Spacer(1, 9))
    flow.append(notion_summary(s))
    return flow


def notion_summary(s):
    rows = [
        ["등록 건수", "14건 (Day 15~28)", "상태", "아이디어"],
        ["카테고리", CATEGORY, "엔진", "Claude"],
        ["채널", "블로그 · 인스타 · 페이스북 · 파워링크 · 쇼츠", "등록 위치", "노션 콘텐츠 보드"],
    ]
    data = [[Paragraph(a, s["meta_l"]), Paragraph(b, s["meta_v"]),
             Paragraph(c, s["meta_l"]), Paragraph(d, s["meta_v"])] for a, b, c, d in rows]
    t = Table(data, colWidths=[56, 192, 52, 193], style=TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F4F8FC")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F4F8FC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def quality_section(s):
    flow = [Paragraph("4. 2차 시리즈 납품 기준 (기존 파이프라인 그대로)", s["h2"])]
    for b in [
        "<b>이원화 동시 제작</b>: 대중용 블로그·카드뉴스·릴스 대본과 전문가용 임상 칼럼을 한 번에 뽑아 나란히 확인합니다.",
        "<b>AI 티 제거</b>: 원고 생성 직후 슬롭 필터를 돌려 엠대시·상투어를 지우고 슬롭 지수 0점을 확인합니다.",
        "<b>쇼츠</b>: 칠판 분필 드로잉 기본, 1080×1920 세로형. 자막에 숫자·영문 오독이 없도록 음절 표기를 점검합니다.",
        "<b>네이버 발행</b>: 스마트에디터용 HTML을 함께 만들어 표가 실제 표로 붙는지 검수한 뒤 5초 복사·발행으로 마무리합니다.",
        "<b>4곳 동기화</b>: GitHub(content/날짜-순번), 노션 보드(상태 갱신), 앱 위젯, 다운로드 폴더에 같은 날 결과를 남깁니다.",
    ]:
        flow.append(Paragraph(b, s["bullet"], bulletText="·"))
    return flow


def notice_box(s):
    txt = ("<b>[2차 시리즈 운영 메모]</b><br/>"
           "3주차(15~21)는 송년회 술자리·과식·실내 난방처럼 연말에 반복되는 상황을, 4주차(22~28)는 안면마비·코피·소아 고열·심야 흉통처럼 "
           "‘이 정도면 병원에 가야 하나’를 스스로 판단하기 어려운 생활응급으로 묶었습니다. 모든 편은 응급실에서 실제로 마주치는 장면으로 시작해 "
           "집에서 할 수 있는 처치와 병원에 가야 하는 신호를 나눠 주는 구조를 유지합니다.")
    t = Table([[Paragraph(txt, ParagraphStyle("box", fontName="Nanum", fontSize=8.2, leading=12.6,
                                              textColor=colors.HexColor("#22303F")))]],
              colWidths=[493], style=TableStyle([
                  ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EDF3FB")),
                  ("BOX", (0, 0), (-1, -1), 0.9, colors.HexColor("#4A79B5")),
                  ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                  ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
              ]))
    return t


class Doc(BaseDocTemplate):
    def __init__(self, path, **kw):
        BaseDocTemplate.__init__(self, path, pagesize=A4,
                                 leftMargin=51, rightMargin=51, topMargin=48, bottomMargin=44, **kw)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f")
        self.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=self.decorate)])

    def decorate(self, canv, doc):
        canv.saveState()
        w, h = A4
        if doc.page > 1:
            canv.setFont("Nanum", 7.6)
            canv.setFillColor(GRAY)
            canv.drawString(51, h - 34, "연말·한파 응급케어 14일 데일리 콘텐츠 기획표")
            canv.setStrokeColor(LINE)
            canv.setLineWidth(0.5)
            canv.line(51, h - 40, w - 51, h - 40)
        canv.setStrokeColor(LINE)
        canv.setLineWidth(0.5)
        canv.line(51, 38, w - 51, 38)
        canv.setFont("Nanum", 7.6)
        canv.setFillColor(GRAY)
        canv.drawCentredString(w / 2, 26, f"- {doc.page} -")
        canv.drawRightString(w - 51, 26, "김승태 님 맞춤 기획")
        canv.restoreState()


def build_pdf():
    register_fonts()
    s = styles()
    doc = Doc(PDF_OUT)
    flow = []
    flow += header_block(s)
    flow.append(Paragraph("1. 연말·한파 응급케어 14일 데일리 기획 & 키워드 마스터 테이블", s["h2"]))
    flow.append(Paragraph(
        "응급실에서 반복해서 마주치는 연말·한파 상황을 14개 주제로 나눴습니다. 각 주제는 검색 의도가 뚜렷한 키워드 3개씩 "
        "배정했고, 분류는 노션 콘텐츠 보드의 기존 옵션(의학/건강)에 맞췄습니다.", s["body"]))
    flow.append(Spacer(1, 6))
    flow.append(week_row(15, s))
    flow.append(Spacer(1, 3))

    t15 = build_table_rows(s, DAYS[:7], 0)
    flow_t15 = Table(t15[0], colWidths=COLS, repeatRows=1)
    flow_t15.setStyle(TableStyle(t15[1]))
    flow.append(flow_t15)

    flow.append(Spacer(1, 10))
    flow.append(week_row(22, s))
    flow.append(Spacer(1, 3))
    t22 = build_table_rows(s, DAYS[7:], 7)
    tb = LongTable(t22[0], colWidths=COLS, repeatRows=1)
    tb.setStyle(TableStyle(t22[1]))
    flow.append(tb)

    section2 = [Paragraph("2. 14편 타깃 독자 매핑", s["h2"]),
                Paragraph("각 편이 겨냥하는 독자입니다. 도입 첫 문장은 위 표의 후킹 포인트를 그대로 쓰고, 쇼츠 첫 3초 자막도 같은 문장에서 가져갑니다.", s["body"]),
                Spacer(1, 6), target_table(s)]
    flow.append(KeepTogether(section2))

    section3 = guide_section(s)
    section3 += quality_section(s)
    section3.append(Spacer(1, 12))
    section3.append(notice_box(s))
    flow.append(KeepTogether(section3))
    doc.build(flow)


def build_table_rows(s, days, offset):
    head = [Paragraph(t, s["th"]) for t in
            ["일차", "포스팅 주제(제목)", "검색 키워드(3개)", "분류", "핵심 의학 인사이트 & 후킹 포인트"]]
    data = [head]
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("VALIGN", (1, 1), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for i, (day, topic, kws, target, insight, hook) in enumerate(days, start=1):
        kw_txt = "<br/>".join(f"• {k}" for k in kws)
        ins = f"{insight}<br/><font color='#1F4E79'><b>▶ {hook}</b></font>"
        data.append([Paragraph(f"Day {day:02d}", s["day"]),
                     Paragraph(topic, s["topic"]),
                     Paragraph(kw_txt, s["kw"]),
                     Paragraph(CATEGORY, s["cat"]),
                     Paragraph(ins, s["ins"])])
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    return data, style


def build_md():
    L = []
    L.append("# 연말·한파 응급케어 2차 2주(Day 15~28) 데일리 콘텐츠 기획표")
    L.append("")
    L.append("응급실 실전 케어와 네이버 C-Rank / 구글 SEO 검색 유입을 겨냥한 2차 2주 캘린더. "
             "1일 1주제 × 주제별 핵심 검색 키워드 3개, 노션 [📋 콘텐츠 보드]에 14건 아이디어 상태로 등록 완료.")
    L.append("")
    L.append("| 구분 | 내용 |")
    L.append("| --- | --- |")
    for k, v in [
        ("기획 대상", "김승태 님 (응급의학과 의사 / 전문 칼럼니스트)"),
        ("대주제", "연말 모임 & 한파 대비 응급실 실전 케어"),
        ("발행 주기", "1일 1회, 2주간 총 14편 (Day 15~28)"),
        ("세부 분류", "3주차 연말 모임·응급실 실전 / 4주차 한파·생활응급 심화"),
        ("노션 카테고리", f"{CATEGORY} (14편 전체)"),
        ("채널", "블로그, 인스타, 페이스북, 파워링크, 쇼츠"),
        ("엔진", "Claude"),
        ("상태", "아이디어"),
        ("PDF", "docs/03_연말_한파_응급케어_2차_2주_기획표_키워드.pdf"),
    ]:
        L.append(f"| {k} | {v} |")
    L.append("")
    L.append("## 1. 14일 데일리 기획 · 키워드 마스터 테이블")
    L.append("")
    L.append("| 일차 | 포스팅 주제(제목) | 검색 키워드(3개) | 분류 | 타깃 독자 | 핵심 의학 인사이트 | 후킹 포인트 |")
    L.append("| --- | --- | --- | --- | --- | --- | --- |")
    for day, topic, kws, target, insight, hook in DAYS:
        L.append(f"| Day {day:02d} | {topic} | {', '.join(kws)} | {CATEGORY} | {target} | {insight} | {hook} |")
    L.append("")
    L.append("## 2. 주차별 설계 의도")
    L.append("")
    L.append("- **3주차 (Day 15~21) 연말 모임 & 응급실 실전 케어**: 송년회 술자리, 기름진 안주, 생선가시·떡, 수면 부족, 밀폐 난방, 외식·음주, 빙판길. "
             "연말에 실제로 반복되는 상황을 시간 순서대로 배치했다.")
    L.append("- **4주차 (Day 22~28) 한파 & 생활응급 심화**: 안면마비, 코피·부비동염, 소아 고열·열성경련, 심야 흉통, 수족냉증·레이노, 환기 부족, 상비약·응급키트. "
             "‘이 정도면 병원에 가야 하나’를 스스로 판단하기 어려운 주제를 모았다.")
    L.append("- 모든 편은 응급실에서 마주치는 장면으로 시작해 **집에서 할 수 있는 처치**와 **병원에 가야 하는 신호**를 나눠 주는 구조를 유지한다.")
    L.append("- 키워드는 네이버 자동완성·연관검색어 기준으로 검색 의도가 분명한 3개씩 배정했고, 분류는 노션 보드 기존 옵션(`의학/건강`)에 맞췄다.")
    L.append("")
    L.append("## 3. 노션 & 자동화 엔진(Claude) 즉시 실행 가이드")
    L.append("")
    L.append("1. **스마트폰·노션**: [📋 콘텐츠 보드]에서 해당 날짜 행의 상태를 `생성요청`으로 변경하면 즉시 생성이 시작된다.")
    L.append("2. **대화창**: 겅태에게 \"Day 15 진행해줘\"라고 말하면 블로그·임상 칼럼·칠판 쇼츠를 한 번에 제작한다.")
    L.append("3. **Claude.ai 직접 작성**: Claude 프로젝트에 접속해 주제·키워드·인사이트를 붙여 넣으면 같은 톤의 원고가 나온다.")
    L.append("4. **결과물 저장**: 완성 원고는 GitHub(`content/날짜-순번`), 노션 보드, 앱 위젯, 다운로드 4곳에 동시에 남는다.")
    L.append("")
    with open(MD_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    build_pdf()
    build_md()
    print("written:", PDF_OUT)
    print("written:", MD_OUT)
