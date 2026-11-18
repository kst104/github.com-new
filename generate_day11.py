#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 11 Content Generator (Dual Pipeline: Public + Clinical Expert)
Topic: 무릎 관절염·오십견 환자를 위한 초겨울 관절 보온과 온찜질 스트레칭
Keywords: 겨울철 무릎 관절염, 오십견 스트레칭, 관절 통증 온찜질
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DAY_DIR = BASE_DIR / "content" / "2026-11-18-01"
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
    title="겨울철 관절 증상의 병태생리와 물리적 인자 치료의 근거, 퇴행성 슬관절염과 유착성 관절낭염의 단계별 재활 전략",
)
(DAY_DIR / "clinical" / "clinical_column.html").write_text(clin_html, encoding="utf-8")

dual_html = build_dual_view_html(DAY_DIR)
(DAY_DIR / "dual_view.html").write_text(dual_html, encoding="utf-8")
Path("/workspace/downloads/Day11_콘텐츠_이원화_듀얼뷰어.html").write_text(dual_html, encoding="utf-8")

dual_md = """# 🩺 Day 11 콘텐츠 이원화 허브 (대중용 vs 전문가용)

> **주제**: 무릎 관절염·오십견 환자를 위한 초겨울 관절 보온과 온찜질 스트레칭
> **기획 분류**: 재활/운동 (겨울철 건강관리 14일 기획 11일 차)
> **이원화 구성**:
> 1. [대중용 에디션 (블로그·쇼츠·릴스)](post.md)
> 2. [전문가용 에디션 (임상 심층 칼럼)](clinical/clinical_column.md)
> 3. [인터랙티브 웹 듀얼 뷰어](dual_view.html)

---

## 📊 에디션별 사양 비교표

| 항목 | 📱 대중용 에디션 (General Public) | 🩺 전문가용 에디션 (Clinical / Expert) |
| :--- | :--- | :--- |
| **타깃 독자** | 50~70대 무릎 관절염 환자와 가족, 어깨가 굳은 40~60대, 당뇨 동반 만성질환자 | 재활의학과·정형외과·가정의학과 전문의, 전공의, 의대생, 물리치료사 |
| **핵심 메시지** | 뻣뻣하면 데우고 붓고 뜨거우면 식힌다, 45도 15분, 온찜질 뒤 스트레칭, 통증기에는 펴지 않는다 | 활액 유변학과 기상 요인 근거의 한계, ACR·OARSI 권고 등급, 코크란 온열 근거, 유착성 관절낭염 병기별 치료 |
| **주요 키워드** | 겨울철 무릎 관절염, 오십견 스트레칭, 관절 통증 온찜질 | Synovial fluid rheology, Thermotherapy evidence, Adhesive capsulitis staging, Intra-articular corticosteroid |
| **권장 채널** | 네이버 블로그, 인스타그램, 유튜브 쇼츠 | 학술 위키(`kst104/wikiwi`), 병원 의학 칼럼 |
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
