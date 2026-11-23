#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 17 Content Generator (Dual Pipeline: Public + Clinical Expert)
Topic: 밤마다 긁는 겨울 가려움증, 건조성 피부염 vs 아토피, 스테로이드 연고 오해
Keywords: 겨울철 가려움증 원인, 건조성 피부염 증상, 아토피 연고 스테로이드
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DAY_DIR = BASE_DIR / "content" / "2026-11-24-01"
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
    title="한랭기 소양과 만성 습진의 감별: 건조성 습진과 아토피 피부염의 병태생리, 국소 스테로이드 근거 기반 처방",
)
(DAY_DIR / "clinical" / "clinical_column.html").write_text(clin_html, encoding="utf-8")

dual_html = build_dual_view_html(DAY_DIR)
(DAY_DIR / "dual_view.html").write_text(dual_html, encoding="utf-8")
Path("/workspace/downloads/Day17_콘텐츠_이원화_듀얼뷰어.html").write_text(dual_html, encoding="utf-8")

dual_md = """# 🌙 Day 17 콘텐츠 이원화 허브 (대중용 vs 전문가용)

> **주제**: 밤마다 긁는 겨울 가려움증, 건조성 피부염 vs 아토피, 스테로이드 연고 오해
> **기획 분류**: 의학/건강 (겨울철 피부관리·호흡기질환 7일 기획 3일 차)
> **이원화 구성**:
> 1. [대중용 에디션 (블로그·쇼츠·릴스)](post.md)
> 2. [전문가용 에디션 (임상 심층 칼럼)](clinical/clinical_column.md)
> 3. [인터랙티브 웹 듀얼 뷰어](dual_view.html)

---

## 📊 에디션별 사양 비교표

| 항목 | 📱 대중용 에디션 (General Public) | 🩺 전문가용 에디션 (Clinical / Expert) |
| :--- | :--- | :--- |
| **타깃 독자** | 밤에 다리·팔을 긁는 50대 이상, 아토피 자녀를 둔 부모, 스테로이드 연고를 꺼리는 분 | 피부과·가정의학과·응급의학과 전문의, 임상간호사, 보건교사 |
| **핵심 메시지** | 밤 가려움은 생체 리듬과 환경의 함수다. 정강이가 갈라지면 건조성 피부염, 팔꿈치·무릎 안쪽이 반복되면 아토피다. 연고는 등급·부위·기간을 지키면 쓸 수 있고, 진물과 열감은 진료 신호다 | 야간 소양의 병태생리, 건조성 습진과 아토피의 감별, 국소 스테로이드 등급·용량(FTU)·유지 요법의 근거, 스테로이드 공포증 대응, 헤르페스 습진과 홍피증의 응급 평가 |
| **주요 키워드** | 겨울철 가려움증 원인, 건조성 피부염 증상, 아토피 연고 스테로이드 | nocturnal pruritus, asteatotic eczema, atopic dermatitis, topical corticosteroid phobia, proactive therapy |
| **권장 채널** | 네이버 블로그, 인스타그램, 유튜브 쇼츠 | 병원 의학 칼럼, 학술 리뷰, 환자 교육자료 |
"""
(DAY_DIR / "DUAL_VIEW.md").write_text(dual_md, encoding="utf-8")

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
        print("   -", f.get("type"), f.get("quote", "")[:60], f.get("description"))

(DAY_DIR / "slop_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print("post chars:", len(post_md), "clinical chars:", len(clinical_md))
print("tables public:", naver_html.count("<table"), "| tables clinical:", clin_html.count("<table"))
