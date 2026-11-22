#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 15 Content Generator (Dual Pipeline: Public + Clinical Expert)
Topic: 겨울철 피부 건조와 보습의 정석, 세라마이드 보습제 3분 법칙
Keywords: 겨울철 피부 건조 원인, 보습제 바르는 법, 세라마이드 크림 효과
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DAY_DIR = BASE_DIR / "content" / "2026-11-22-01"
DAY_DIR.mkdir(parents=True, exist_ok=True)
(DAY_DIR / "clinical").mkdir(parents=True, exist_ok=True)
(DAY_DIR / "instagram").mkdir(parents=True, exist_ok=True)
(DAY_DIR / "chalkboard").mkdir(parents=True, exist_ok=True)

POST_MD = DAY_DIR / "post.md"
CLIN_MD = DAY_DIR / "clinical" / "clinical_column.md"
ADS_MD = DAY_DIR / "ads.md"
INSTA_MD = DAY_DIR / "instagram" / "card_news_caption.md"

from publisher.naver_formatter import markdown_to_naver_html as generate_smarteditor_html
from engine.clinical_engine import markdown_to_clinical_html
from engine.dual_pipeline import build_dual_view_html
from engine.slop_engine import scan_text_for_slop

post_md = POST_MD.read_text(encoding="utf-8")
clinical_md = CLIN_MD.read_text(encoding="utf-8")
ads_md = ADS_MD.read_text(encoding="utf-8")
insta_md = INSTA_MD.read_text(encoding="utf-8")

naver_html = generate_smarteditor_html(post_md)
(DAY_DIR / "naver_post.html").write_text(naver_html, encoding="utf-8")

clin_html = markdown_to_clinical_html(
    clinical_md,
    title="한랭기 피부 장벽 손상의 병태생리와 보습 요법의 임상 근거: 각질층 지질 조성, 경피수분손실, 그리고 세라마이드 보충의 근거 수준",
)
(DAY_DIR / "clinical" / "clinical_column.html").write_text(clin_html, encoding="utf-8")

dual_html = build_dual_view_html(DAY_DIR)
(DAY_DIR / "dual_view.html").write_text(dual_html, encoding="utf-8")
Path("/workspace/downloads/Day15_콘텐츠_이원화_듀얼뷰어.html").write_text(dual_html, encoding="utf-8")

dual_md = """# 🧴 Day 15 콘텐츠 이원화 허브 (대중용 vs 전문가용)

> **주제**: 겨울철 피부 건조와 보습의 정석, 세라마이드 보습제 3분 법칙
> **기획 분류**: 의학/건강 (겨울철 피부관리·호흡기질환 7일 기획 1일 차)
> **이원화 구성**:
> 1. [대중용 에디션 (블로그·쇼츠·릴스)](post.md)
> 2. [전문가용 에디션 (임상 심층 칼럼)](clinical/clinical_column.md)
> 3. [인터랙티브 웹 듀얼 뷰어](dual_view.html)

---

## 📊 에디션별 사양 비교표

| 항목 | 📱 대중용 에디션 (General Public) | 🩺 전문가용 에디션 (Clinical / Expert) |
| :--- | :--- | :--- |
| **타깃 독자** | 겨울마다 얼굴·팔이 당기는 20~50대, 아이·어르신 피부를 챙기는 보호자 | 피부과·가정의학과·소아청소년과 전문의, 알레르기 전문의, 임상간호사 |
| **핵심 메시지** | 겨울 피부에 부족한 건 물이 아니라 기름이다. 샤워 후 물기를 남기고 3분 안에 20그램, 하루 두 번. 세라마이드 크림은 효과가 있지만 광고만큼은 아니고, 아토피 예방 근거는 없다 | 각질층 세포간 지질 조성과 표면 산도의 생리, 경피수분손실의 해석, 3분 법칙 근거 수준(즉시 도포와 지연 도포의 무차이), 코크란 리뷰의 근거 등급, BEEP·PreventADALL의 예방 효과 반증 |
| **주요 키워드** | 겨울철 피부 건조 원인, 보습제 바르는 법, 세라마이드 크림 효과 | Stratum corneum lipid lamellae, transepidermal water loss, ceramide-dominant emollient, filaggrin, soak and smear |
| **권장 채널** | 네이버 블로그, 인스타그램, 유튜브 쇼츠 | 병원 의학 칼럼, 학술 리뷰, 환자 교육자료 |
"""
(DAY_DIR / "DUAL_VIEW.md").write_text(dual_md, encoding="utf-8")

# 슬롭 검사: 대중용·임상·광고·인스타 전 원고
targets = {
    "post.md": post_md,
    "clinical/clinical_column.md": clinical_md,
    "ads.md": ads_md,
    "instagram/card_news_caption.md": insta_md,
}
report = {}
for name, text in targets.items():
    res = scan_text_for_slop(text)
    report[name] = res
    print(f"slop [{name}] score={res['slop_score']} findings={res['finding_count']}")
    for f in res["findings"]:
        print("   -", f.get("type"), f.get("quote", ""), f.get("description"))

(DAY_DIR / "slop_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print("post chars:", len(post_md), "clinical chars:", len(clinical_md))
print("tables public:", naver_html.count("<table"), "| tables clinical:", clin_html.count("<table"))
