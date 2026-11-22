#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 16 Content Generator (Dual Pipeline: Public + Clinical Expert)
Topic: 겨울 샤워·세안 습관이 피부를 망친다, 뜨거운 물·비누·각질 제거의 함정
Keywords: 겨울철 샤워 습관, 뜨거운 물 피부 자극, 약산성 클렌저 고르는 법
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DAY_DIR = BASE_DIR / "content" / "2026-11-23-01"
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
    title="한랭기 세정 습관과 표피 장벽: 계면활성제·표면산도·물리적 각질제거의 병태생리와 근거 기반 세정 처방",
)
(DAY_DIR / "clinical" / "clinical_column.html").write_text(clin_html, encoding="utf-8")

dual_html = build_dual_view_html(DAY_DIR)
(DAY_DIR / "dual_view.html").write_text(dual_html, encoding="utf-8")
Path("/workspace/downloads/Day16_콘텐츠_이원화_듀얼뷰어.html").write_text(dual_html, encoding="utf-8")

dual_md = """# 🚿 Day 16 콘텐츠 이원화 허브 (대중용 vs 전문가용)

> **주제**: 겨울 샤워·세안 습관이 피부를 망친다, 뜨거운 물·비누·각질 제거의 함정
> **기획 분류**: 의학/건강 (겨울철 피부관리·호흡기질환 7일 기획 2일 차)
> **이원화 구성**:
> 1. [대중용 에디션 (블로그·쇼츠·릴스)](post.md)
> 2. [전문가용 에디션 (임상 심층 칼럼)](clinical/clinical_column.md)
> 3. [인터랙티브 웹 듀얼 뷰어](dual_view.html)

---

## 📊 에디션별 사양 비교표

| 항목 | 📱 대중용 에디션 (General Public) | 🩺 전문가용 에디션 (Clinical / Expert) |
| :--- | :--- | :--- |
| **타깃 독자** | 뜨거운 샤워를 좋아하는 30~60대, 때밀이·필링을 습관처럼 하는 20~40대 | 피부과·가정의학과·응급의학과 전문의, 임상간호사, 산업보건 담당자 |
| **핵심 메시지** | 42도 물과 알칼리성 비누, 때밀이가 한 번의 목욕에 겹치면 장벽이 무너진다. 38~39도에서 10분, 세정제는 겨드랑이와 사타구니에만, 때밀이는 주 1회 이하, 물기가 남았을 때 보습제 | 계면활성제의 단백 변성과 지질 용해, 표면 산도 상승에 의한 지질 가공 효소 저해, 물리적 각질 제거 후 장벽 회복 동역학, 건조성 습진·손습진·연조직 감염의 감별 |
| **주요 키워드** | 겨울철 샤워 습관, 뜨거운 물 피부 자극, 약산성 클렌저 고르는 법 | Surfactant-induced protein denaturation, skin surface pH, stratum corneum lipid lamellae, irritant contact dermatitis, asteatotic eczema |
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
