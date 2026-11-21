#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 14 Content Generator (Dual Pipeline: Public + Clinical Expert)
Topic: 체온을 1도 올리는 겨울철 온열 영양 식단과 면역 강화 푸드
Keywords: 겨울철 면역력 음식, 온열 식품 식단, 생강차 대추차 효능
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DAY_DIR = BASE_DIR / "content" / "2026-11-21-01"
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
    title="한랭 계절 영양 관리의 생리학적 근거: 식사성 발열효과, 미량영양소 보충의 임상 근거 수준, 그리고 만성질환자에서의 식이 조정",
)
(DAY_DIR / "clinical" / "clinical_column.html").write_text(clin_html, encoding="utf-8")

dual_html = build_dual_view_html(DAY_DIR)
(DAY_DIR / "dual_view.html").write_text(dual_html, encoding="utf-8")
Path("/workspace/downloads/Day14_콘텐츠_이원화_듀얼뷰어.html").write_text(dual_html, encoding="utf-8")

dual_md = """# 🍲 Day 14 콘텐츠 이원화 허브 (대중용 vs 전문가용)

> **주제**: 체온을 1도 올리는 겨울철 온열 영양 식단과 면역 강화 푸드
> **기획 분류**: 영양/식단 (겨울철 건강관리 14일 기획 14일 차)
> **이원화 구성**:
> 1. [대중용 에디션 (블로그·쇼츠·릴스)](post.md)
> 2. [전문가용 에디션 (임상 심층 칼럼)](clinical/clinical_column.md)
> 3. [인터랙티브 웹 듀얼 뷰어](dual_view.html)

---

## 📊 에디션별 사양 비교표

| 항목 | 📱 대중용 에디션 (General Public) | 🩺 전문가용 에디션 (Clinical / Expert) |
| :--- | :--- | :--- |
| **타깃 독자** | 겨울마다 감기를 달고 사는 50~70대, 당뇨·고혈압·신장질환으로 식이 조절 중인 분, 부모님 식사를 걱정하는 자녀 | 가정의학과·내분비내과·신장내과·순환기내과 전문의, 임상영양사, 응급의학과 전공의 |
| **핵심 메시지** | 체온을 올리는 음식은 없다. 열은 몸이 만든다. 단백질을 매 끼 20그램, 겨울에는 비타민D, 국물은 건더기 위주, 대추차는 잔 수와 당류부터 | 식사성 발열효과의 영양소별 계수, 비타민D IPD 메타분석의 결핍군 집중 효과, 아연 로젠지의 용량·기간 한정, 만성질환별 나트륨·칼륨·유리당 상한과 약물 상호작용 |
| **주요 키워드** | 겨울철 면역력 음식, 온열 식품 식단, 생강차 대추차 효능 | Diet-induced thermogenesis, 25-hydroxyvitamin D, Zinc lozenge, Protein intake per meal, Cold-related thermoregulation |
| **권장 채널** | 네이버 블로그, 인스타그램, 유튜브 쇼츠 | 병원 의학 칼럼, 학술 리뷰, 영양 상담 교육자료 |
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
