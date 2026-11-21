#!/usr/bin/env python3
"""Day 15~21 겨울철 피부관리·호흡기질환 7일 기획표 생성기.

docs/04_피부관리_호흡기질환_7일_기획표_키워드.pdf 를 만들고
docs/04_피부관리_호흡기질환_7일_기획표.md 내용과 같은 데이터를 쓴다.
(디자인 기준: docs/03_연말_한파_응급케어_2차_2주_기획표_키워드.pdf)
"""
import os
import shutil

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, LongTable,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORKSPACE = os.path.dirname(os.path.dirname(BASE))
FONT_DIR = os.path.join(WORKSPACE, "fonts")
DOCS = os.path.join(BASE, "docs")
PDF_OUT = os.path.join(DOCS, "04_피부관리_호흡기질환_7일_기획표_키워드.pdf")
DOWNLOAD_OUT = os.path.join(WORKSPACE, "downloads", "피부관리_호흡기질환_7일_콘텐츠_기획표.pdf")

CATEGORY = "의학/건강"
AUTHOR = "겅태(의학과 경제학에 관심많은)"
TITLE = "겨울철 피부관리 · 호흡기질환 7일 데일리 콘텐츠 기획표"

# 일차, 날짜, 주제, [키워드 3], 타깃 독자, 핵심 인사이트, 후킹 포인트
DAYS = [
    (15, "11/22 일",
     "겨울철 피부 건조와 보습의 정석: 세라마이드 보습제 '3분 법칙'",
     ["겨울철 피부 건조 원인", "보습제 바르는 법", "세라마이드 크림 효과"],
     "겨울마다 얼굴·팔이 당기는 20~50대, 아이·어르신 피부를 챙기는 보호자",
     "겨울엔 실내 습도가 30% 아래로 떨어지고 피부 장벽 지질(세라마이드)이 줄어 수분이 새어 나간다. "
     "샤워 후 3분 안에 물기를 살짝 남긴 상태로 바르고 하루 2~3회 덧바르는 것이 기본이며, 겨울에는 로션보다 크림·연고 제형이 유리하다. "
     "뜨거운 물과 잦은 비누질이 씻어낸 지질을 크림으로 다시 채우는 셈이다.",
     "샤워 후 3분을 놓치면 비싼 크림도 절반은 버립니다"),
    (16, "11/23 월",
     "겨울 샤워·세안 습관이 피부를 망친다: 뜨거운 물·비누·각질 제거의 함정",
     ["겨울철 샤워 습관", "뜨거운 물 피부 자극", "약산성 클렌저 고르는 법"],
     "뜨거운 샤워를 좋아하는 30~60대, 때밀이·필링을 습관처럼 하는 20~40대",
     "40도를 넘는 물은 표피의 피지막을 녹여 씻어내고 씻고 난 뒤 더 당기게 만든다. 샤워는 38~39도·10분 이내, "
     "세정제는 겨드랑이·사타구니처럼 기름진 부위에만, 때밀이와 필링은 주 1회 이하로 줄인다. "
     "얼굴은 세안 후 3분 안에 보습, 입술·손등은 씻을 때마다 덧바른다.",
     "뜨거운 물로 씻을수록 다음 날 더 가려운 이유"),
    (17, "11/24 화",
     "밤마다 긁는 겨울 가려움증: 건조성 피부염 vs 아토피, 스테로이드 연고 오해",
     ["겨울철 가려움증 원인", "건조성 피부염 증상", "아토피 연고 스테로이드"],
     "밤에 다리·팔을 긁는 50대 이상, 아토피 자녀를 둔 부모, 스테로이드 연고를 꺼리는 환자",
     "건조성 피부염은 정강이·팔 바깥처럼 피지샘이 적은 곳부터 하얀 각질과 균열이 생기고, 아토피 피부염은 팔꿈치·무릎 안쪽 굴측 습진이 "
     "반복되며 알레르기 질환 가족력을 동반한다. 밤 가려움은 체온 상승과 코르티솔 저하로 심해진다. 바르는 스테로이드는 못 쓰는 쪽이 더 문제이고 "
     "얼굴·목은 약한 등급을 짧게 쓴다. 진물·2주 이상 지속·잠을 못 잘 정도면 진료.",
     "밤만 되면 다리를 긁는 사람, 보습제만으로는 안 되는 이유"),
    (18, "11/25 수",
     "겨울 고열·기침, 감기인가 독감인가: RSV·마이코플라스마까지 아이와 어르신 감별법",
     ["RSV 증상 아이", "마이코플라스마 폐렴 기침", "독감 감기 차이"],
     "영유아·초등 자녀를 둔 부모, 65세 이상 어르신과 돌봄 가족, 어린이집·학교 교사",
     "감기는 콧물·목 통증으로 서서히 시작하고, 독감은 38도 이상 고열과 근육통이 갑자기 온다. RSV는 영아의 쌕쌕거림·빠른 호흡·"
     "갈비뼈 아래가 들어가는 호흡곤란이 핵심이고 2세 미만에서 위중하다. 마이코플라스마는 5~7일에 걸쳐 마른기침이 서서히 심해지고 "
     "마크롤라이드 계열 항생제가 필요해 일반 감기약과 처방이 다르다. 호흡수 증가·입술 청색·물도 못 마심·축 처짐은 즉시 진료.",
     "기침 한 번에 감기약부터 찾기 전에 확인할 세 가지"),
    (19, "11/26 목",
     "3주 넘게 가는 마른기침의 정체: 후비루·천식·역류, 만성기관지염 악화 신호",
     ["마른기침 오래갈 때", "만성기침 원인", "겨울 천식 악화"],
     "3주 이상 기침이 남은 성인, 흡연자·천식·COPD 환자, 찬 공기와 미세먼지에 기침하는 40~70대",
     "3주는 병원 상담, 8주를 넘기면 만성기침으로 본다. 흔한 세 원인은 코 뒤로 넘어가는 후비루, 밤·새벽과 찬 공기·운동 후 악화되는 "
     "기침형 천식, 눕거나 밥 먹고 나서 심한 위식도역류다. 흡연자가 겨울마다 기침과 가래가 늘면 만성기관지염 악화를 의심한다. "
     "쌕쌕거림·호흡곤란·피 섞인 가래·체중 감소·오랜 흡연력이면 흉부 X선. 진해제는 원인을 덮고 가래 배출을 막을 수 있다.",
     "기침이 3주 넘으면 감기가 아닙니다, 원인은 코·폐·위 중 하나"),
    (20, "11/27 금",
     "겨울 코막힘·비염·부비동염: 코점막이 마르면 생기는 일과 가습기 관리법",
     ["겨울철 비염 코막힘", "축농증 증상", "가습기 세척 관리"],
     "겨울마다 코가 막히는 비염 환자, 축농증을 반복하는 30~60대, 가습기를 쓰는 가정",
     "코점막은 점액과 섬모로 먼지를 밀어낸다. 습도가 40% 아래로 떨어지면 점액이 굳고 섬모 운동이 둔해져 코막힘·코피가 잦아진다. "
     "비염은 맑은 콧물·재채기·양쪽 코막힘, 부비동염은 한쪽 얼굴 통증·누런 콧물·냄새·10일 이상 지속이 다르다. "
     "코 세척은 생리식염수로 하고 혈관수축제 스프레이는 3일을 넘기면 약물성 비염으로 되돌아온다. "
     "가습기는 하루 물 갈이와 주 1회 이상 세척·건조, 습도는 40~60%.",
     "가습기를 켰는데 코가 더 막히는 이유"),
    (21, "11/28 토",
     "겨울에도 자외선은 그대로: 자외선 차단·입술 각질·손발 트는 동창과 손습진",
     ["겨울 자외선 차단제", "입술 각질 립밤", "손등 습진 동창"],
     "스키·등산·러닝을 즐기는 30~50대, 물일이 많은 주부·요리 종사자, 야외 근로자와 운전자",
     "겨울 자외선은 약해 보여도 UVA는 유리창을 통과하고 눈·눈밭 반사로 노출이 늘어 색소 침착과 광노화가 계속된다. "
     "SPF 30 이상을 외출 15분 전 얼굴과 손등에 바른다. 입술은 피지선이 없어 잘 갈라지고 침으로 축이면 더 마르므로 뜯지 말고 "
     "라놀린·바셀린 계열로 덮는다. 손등·발가락이 붉게 붓고 가렵다가 하얗게 트는 것은 동창(한랭 손상)이나 손습진으로, 젖은 손과 찬 바람이 주원인이다. "
     "물 접촉을 줄이고 보습하고, 물집·궤양·2주 이상 지속은 진료.",
     "겨울 자외선은 약할 거라는 착각이 기미를 만듭니다"),
]

BLOCKS = [
    (0, 3, "1막 · 겨울 피부 장벽 케어 (Day 15~17)"),
    (3, 6, "2막 · 겨울 호흡기질환 (Day 18~20)"),
    (6, 7, "3막 · 주말 생활 마무리 (Day 21)"),
]

NAVY = colors.HexColor("#16365C")
BLUE = colors.HexColor("#1F4E79")
BAND = colors.HexColor("#E8F0FA")
LINE = colors.HexColor("#C9D6E4")
ZEBRA = colors.HexColor("#F7FAFC")
INK = colors.HexColor("#1F2430")
GRAY = colors.HexColor("#5A6472")


def register_fonts():
    pdfmetrics.registerFont(TTFont("Nanum", os.path.join(FONT_DIR, "NanumGothic-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Nanum-Bold", os.path.join(FONT_DIR, "NanumGothic-Bold.ttf")))
    pdfmetrics.registerFontFamily("Nanum", normal="Nanum", bold="Nanum-Bold")


def styles():
    s = {}
    s["kicker"] = ParagraphStyle("kicker", fontName="Nanum-Bold", fontSize=7.6, leading=10,
                                 textColor=BLUE, alignment=TA_LEFT)
    s["title"] = ParagraphStyle("title", fontName="Nanum-Bold", fontSize=20, leading=26,
                                textColor=NAVY, spaceBefore=4, spaceAfter=6)
    s["sub"] = ParagraphStyle("sub", fontName="Nanum", fontSize=9.6, leading=14, textColor=GRAY)
    s["h2"] = ParagraphStyle("h2", fontName="Nanum-Bold", fontSize=13, leading=18,
                             textColor=INK, spaceBefore=14, spaceAfter=6)
    s["body"] = ParagraphStyle("body", fontName="Nanum", fontSize=8.4, leading=12.6,
                               textColor=colors.HexColor("#3A4250"), spaceAfter=2)
    s["bullet"] = ParagraphStyle("bullet", fontName="Nanum", fontSize=8.4, leading=12.6,
                                 textColor=colors.HexColor("#3A4250"), leftIndent=10,
                                 bulletIndent=2, spaceAfter=2)
    s["meta_l"] = ParagraphStyle("meta_l", fontName="Nanum-Bold", fontSize=7.8, leading=10.4, textColor=NAVY)
    s["meta_v"] = ParagraphStyle("meta_v", fontName="Nanum", fontSize=7.8, leading=10.4, textColor=INK)
    s["th"] = ParagraphStyle("th", fontName="Nanum-Bold", fontSize=7.8, leading=10.4,
                             textColor=colors.white, alignment=TA_CENTER)
    s["day"] = ParagraphStyle("day", fontName="Nanum-Bold", fontSize=7.8, leading=10.4,
                              textColor=NAVY, alignment=TA_CENTER)
    s["date"] = ParagraphStyle("date", fontName="Nanum", fontSize=6.8, leading=9,
                               textColor=GRAY, alignment=TA_CENTER)
    s["topic"] = ParagraphStyle("topic", fontName="Nanum-Bold", fontSize=7.5, leading=10.2, textColor=INK)
    s["kw"] = ParagraphStyle("kw", fontName="Nanum", fontSize=7.2, leading=9.8,
                             textColor=colors.HexColor("#2E4762"), leftIndent=7, bulletIndent=0)
    s["cat"] = ParagraphStyle("cat", fontName="Nanum", fontSize=7.2, leading=9.6,
                              textColor=colors.HexColor("#2E4762"), alignment=TA_CENTER)
    s["ins"] = ParagraphStyle("ins", fontName="Nanum", fontSize=7.2, leading=9.9,
                              textColor=colors.HexColor("#2B3341"))
    s["block"] = ParagraphStyle("block", fontName="Nanum-Bold", fontSize=8.6, leading=12,
                                textColor=colors.white)
    s["target"] = ParagraphStyle("target", fontName="Nanum", fontSize=7.2, leading=9.9,
                                 textColor=colors.HexColor("#2B3341"))
    return s


def header_block(s):
    flow = []
    flow.append(Table([["7-DAY CONTENT STRATEGY & KEYWORD CALENDAR"]], colWidths=[493],
                      style=TableStyle([
                          ("BACKGROUND", (0, 0), (-1, -1), BAND),
                          ("LEFTPADDING", (0, 0), (-1, -1), 8),
                          ("TOPPADDING", (0, 0), (-1, -1), 4),
                          ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                          ("FONTNAME", (0, 0), (-1, -1), "Nanum-Bold"),
                          ("FONTSIZE", (0, 0), (-1, -1), 7.2),
                          ("TEXTCOLOR", (0, 0), (-1, -1), BLUE),
                      ])))
    flow.append(Paragraph("겨울철 피부관리 · 호흡기질환 7일 데일리 콘텐츠 기획표", s["title"]))
    flow.append(Paragraph("겨울 피부 장벽 케어와 겨울 호흡기질환, 네이버 C-Rank / 구글 SEO 검색 유입을 겨냥한 7일 캘린더", s["sub"]))
    flow.append(Paragraph("Day 15~21 (2026-11-22~11-28) · 1일 1주제 × 주제별 핵심 검색 키워드 3개 · 노션 콘텐츠 보드 등록 완료(7건)", s["sub"]))

    rule = Table([[""]], colWidths=[493], rowHeights=[2], style=TableStyle([
        ("LINEBELOW", (0, 0), (-1, -1), 1.1, BLUE), ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    flow.append(Spacer(1, 10))
    flow.append(rule)
    flow.append(Spacer(1, 10))

    rows = [
        ("기획 대상", AUTHOR, "발행 주기", "1일 1회 · 7일간 총 7편"),
        ("대주제", "겨울철 피부 장벽 케어 & 겨울 호흡기질환", "목표 채널", "네이버 블로그 · 인스타그램 · 페이스북 · 쇼츠"),
        ("세부 분류", "1막 피부 장벽(15~17) / 2막 겨울 호흡기(18~20) / 3막 생활 마무리(21)", "자동화 연동", "매일 14시 루틴이 이 문서를 순차 실행"),
        ("노션 카테고리", f"{CATEGORY} (7편 전체)", "다음 기획", "11-23(월) 차기 2주 대주제 확인 후 결정"),
    ]
    data = [[Paragraph(a, s["meta_l"]), Paragraph(b, s["meta_v"]),
             Paragraph(c, s["meta_l"]), Paragraph(d, s["meta_v"])] for a, b, c, d in rows]
    meta = Table(data, colWidths=[62, 186, 66, 179], style=TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F4F8FC")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#F4F8FC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5.5),
    ]))
    flow.append(meta)
    return flow


COLS = [42, 132, 100, 40, 179]


def block_row(label, s):
    return Table([[Paragraph(label, s["block"])]], colWidths=[493], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))


def build_table_rows(s, days):
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
    for i, (day, date, topic, kws, target, insight, hook) in enumerate(days, start=1):
        kw_txt = "<br/>".join(f"• {k}" for k in kws)
        ins = f"{insight}<br/><font color='#1F4E79'><b>▶ {hook}</b></font>"
        data.append([Paragraph(f"Day {day:02d}<br/><font size=6.8 color='#5A6472'>{date}</font>", s["day"]),
                     Paragraph(topic, s["topic"]),
                     Paragraph(kw_txt, s["kw"]),
                     Paragraph(CATEGORY, s["cat"]),
                     Paragraph(ins, s["ins"])])
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    return data, style


def target_table(s):
    head = [Paragraph("일차", s["th"]), Paragraph("타깃 독자", s["th"])]
    data = [head]
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]
    for i, (day, date, topic, kws, target, insight, hook) in enumerate(DAYS, start=1):
        data.append([Paragraph(f"Day {day:02d} ({date})", s["day"]), Paragraph(target, s["target"])])
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    t = Table(data, colWidths=[88, 405])
    t.setStyle(TableStyle(style))
    return t


def guide_section(s):
    flow = [Paragraph("3. 제작·납품 기준 (2026-11-20~21 확정분)", s["h2"])]
    for b in [
        "<b>이원화 동시 제작</b>: 대중용 블로그 원고(post.md·naver_post.html)·광고 카피·카드뉴스 캡션과 전문가용 임상 칼럼을 한 번에 뽑습니다.",
        "<b>인용 필수</b>: 임상 칼럼에는 승태 님의 의학 위키(kst104/wikiwi)와 Tintinalli 응급의학 교과서 인용을 반드시 넣습니다.",
        f"<b>저자 표기</b>: 대중용·임상 칼럼 모두 <b>저자: {AUTHOR}</b>. 실명은 넣지 않습니다.",
        "<b>쇼츠</b>: 잘.의.정.바 3단 레이아웃(jaljab), 0~2초 '구독·알림·좋아요는 힘이 됩니다' 배지, 60초 미만 1080×1920, 일본어 가나 배제.",
        "<b>제휴 링크</b>: 네이버 쇼핑 커넥트 단일 운영, 대표 상품 '들꽃잠 배 찜질팩 온열 팥 멀티형' 유지, 공정위 수수료 고지 문구 포함.",
        "<b>AI 티 제거</b>: 원고 생성 직후 slop-rewrite 필터로 엠대시·상투어를 지우고 슬롭 지수 0점을 확인합니다.",
    ]:
        flow.append(Paragraph(b, s["bullet"], bulletText="·"))
    flow.append(Paragraph("4. 노션 & 자동화 엔진(Claude) 즉시 실행 가이드", s["h2"]))
    for b in [
        "<b>스마트폰·노션</b>: [콘텐츠 보드]에서 해당 날짜 행의 상태를 '생성요청'으로 바꾸면 즉시 생성이 시작됩니다.",
        "<b>대화창</b>: 겅태에게 \"Day 18 진행해줘\"라고 말하면 블로그·임상 칼럼·칠판 쇼츠를 한 번에 제작합니다.",
        "<b>매일 14시 루틴</b>: 예정 블로그·쇼츠 루틴이 이 문서를 Day 15부터 순서대로 읽어 자동 제작합니다.",
        "<b>결과물 저장</b>: 완성 원고는 GitHub(content/날짜-순번), 노션 보드, 앱 위젯, 다운로드 4곳에 동시에 남습니다.",
    ]:
        flow.append(Paragraph(b, s["bullet"], bulletText="·"))
    return flow


def notice_box(s):
    txt = ("<b>[이번 7일 운영 메모]</b><br/>"
           "1막(15~17)은 보습 → 샤워·세안 습관 → 가려움증 감별로 '바르는 것'에서 '씻는 습관'과 '진료 기준'으로 올라가고, "
           "2막(18~20)은 소아·고령의 고열·기침 감별에서 시작해 난치성 마른기침, 코점막·가습기 환경까지 내려옵니다. "
           "1차 기획 Day 6(독감 vs 감기)·Day 12(찬 공기 천식)와 겹치지 않도록 RSV·마이코플라스마·만성기침·코점막 각도로 바꿨습니다. "
           "기존 03 기획표의 Day 15~21(연말 응급)은 이 7일 주제로 교체되고, Day 22~28은 11-23 차기 대주제 확인 후 결정합니다.")
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
            canv.drawString(51, h - 34, "겨울철 피부관리 · 호흡기질환 7일 데일리 콘텐츠 기획표")
            canv.setStrokeColor(LINE)
            canv.setLineWidth(0.5)
            canv.line(51, h - 40, w - 51, h - 40)
        canv.setStrokeColor(LINE)
        canv.setLineWidth(0.5)
        canv.line(51, 38, w - 51, 38)
        canv.setFont("Nanum", 7.6)
        canv.setFillColor(GRAY)
        canv.drawCentredString(w / 2, 26, f"- {doc.page} -")
        canv.drawRightString(w - 51, 26, "잘.의.정.바 맞춤 기획")
        canv.restoreState()


def build_pdf():
    register_fonts()
    s = styles()
    doc = Doc(PDF_OUT)
    flow = []
    flow += header_block(s)
    flow.append(Paragraph("1. 7일 데일리 기획 · 키워드 마스터 테이블", s["h2"]))
    flow.append(Paragraph(
        "겨울에 실제로 늘어나는 피부·호흡기 불편을 7개 주제로 나눴습니다. 각 주제는 검색 의도가 뚜렷한 키워드 3개씩 배정했고, "
        "분류는 노션 콘텐츠 보드의 기존 옵션(의학/건강)에 맞췄습니다.", s["body"]))
    flow.append(Spacer(1, 6))

    for start, end, label in BLOCKS:
        flow.append(block_row(label, s))
        flow.append(Spacer(1, 3))
        data, style = build_table_rows(s, DAYS[start:end])
        tb = Table(data, colWidths=COLS, repeatRows=1)
        tb.setStyle(TableStyle(style))
        flow.append(tb)
        flow.append(Spacer(1, 8))

    section2 = [Paragraph("2. 7편 타깃 독자 매핑", s["h2"]),
                Paragraph("각 편이 겨냥하는 독자입니다. 도입 첫 문장은 위 표의 후킹 포인트를 그대로 쓰고, 쇼츠 첫 3초 자막도 같은 문장에서 가져갑니다.", s["body"]),
                Spacer(1, 6), target_table(s)]
    flow.append(KeepTogether(section2))

    section3 = guide_section(s)
    section3.append(Spacer(1, 12))
    section3.append(notice_box(s))
    flow.append(KeepTogether(section3))
    doc.build(flow)

    os.makedirs(os.path.dirname(DOWNLOAD_OUT), exist_ok=True)
    shutil.copyfile(PDF_OUT, DOWNLOAD_OUT)


if __name__ == "__main__":
    build_pdf()
    print("written:", PDF_OUT)
    print("written:", DOWNLOAD_OUT)
