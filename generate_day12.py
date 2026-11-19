#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 12 Content Generator (Dual Pipeline: Public + Clinical Expert)
Topic: 만성 호흡기 질환자(천식·COPD)의 찬 공기 기관지 수축 방어법
Keywords: 찬 공기 천식 기침, 겨울철 호흡기 관리, 방한 마스크 효과
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DAY_DIR = BASE_DIR / "content" / "2026-11-19-01"
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
    title="한랭 건조 공기 유발 기관지수축의 병태생리와 천식·COPD의 겨울철 악화 예방, 마스크의 가온·가습 효과에 대한 근거 검토",
)
(DAY_DIR / "clinical" / "clinical_column.html").write_text(clin_html, encoding="utf-8")

dual_html = build_dual_view_html(DAY_DIR)
(DAY_DIR / "dual_view.html").write_text(dual_html, encoding="utf-8")
Path("/workspace/downloads/Day12_콘텐츠_이원화_듀얼뷰어.html").write_text(dual_html, encoding="utf-8")

dual_md = """# 🫁 Day 12 콘텐츠 이원화 허브 (대중용 vs 전문가용)

> **주제**: 만성 호흡기 질환자(천식·COPD)의 찬 공기 기관지 수축 방어법
> **기획 분류**: 의학/호흡기 (겨울철 건강관리 14일 기획 12일 차)
> **이원화 구성**:
> 1. [대중용 에디션 (블로그·쇼츠·릴스)](post.md)
> 2. [전문가용 에디션 (임상 심층 칼럼)](clinical/clinical_column.md)
> 3. [인터랙티브 웹 듀얼 뷰어](dual_view.html)

---

## 📊 에디션별 사양 비교표

| 항목 | 📱 대중용 에디션 (General Public) | 🩺 전문가용 에디션 (Clinical / Expert) |
| :--- | :--- | :--- |
| **타깃 독자** | 천식·COPD로 흡입기를 쓰는 40~80대와 가족, 겨울 아침 운동을 하는 50대 이상, 만성기침이 있는 흡연자 | 호흡기내과·가정의학과·응급의학과 전문의, 전공의, 의대생, 호흡기 전문 간호사 |
| **핵심 메시지** | 찬 공기를 그대로 마시지 않게 하고, 기도를 건조하게 두지 않으며, 감염을 막는다. 외출 전 15분과 첫 10분, 그리고 119 신호 | 냉각·건조 자극의 이중 기전, 운동 유발 기관지수축의 시간 경과와 진단, GINA·GOLD 기반 약물 전략, COPD 급성 악화 기준과 산소 목표 |
| **주요 키워드** | 찬 공기 천식 기침, 겨울철 호흡기 관리, 방한 마스크 효과 | Cold-induced bronchoconstriction, Exercise-induced bronchoconstriction, COPD exacerbation, Mask humidification |
| **권장 채널** | 네이버 블로그, 인스타그램, 유튜브 쇼츠 | 병원 의학 칼럼, 학술 리뷰 |
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
