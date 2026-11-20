#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 13 Content Generator (Dual Pipeline: Public + Clinical Expert)
Topic: 겨울철 안전한 운동 가이드 (실내 맨몸 홈트 vs 야외 걷기 안전 수칙)
Keywords: 겨울철 실내 운동, 한파 야외 걷기, 심혈관 운동 주의점
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DAY_DIR = BASE_DIR / "content" / "2026-11-20-01"
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
    title="한랭 환경 운동의 심혈관 부하와 운동 시간대의 생리학적 근거, 동적 준비운동 및 실내 저항운동·야외 보행의 위험 계층화",
)
(DAY_DIR / "clinical" / "clinical_column.html").write_text(clin_html, encoding="utf-8")

dual_html = build_dual_view_html(DAY_DIR)
(DAY_DIR / "dual_view.html").write_text(dual_html, encoding="utf-8")
Path("/workspace/downloads/Day13_콘텐츠_이원화_듀얼뷰어.html").write_text(dual_html, encoding="utf-8")

dual_md = """# 🏃 Day 13 콘텐츠 이원화 허브 (대중용 vs 전문가용)

> **주제**: 겨울철 안전한 운동 가이드: 실내 맨몸 홈트 vs 야외 걷기 안전 수칙
> **기획 분류**: 운동/피트니스 (겨울철 건강관리 14일 기획 13일 차)
> **이원화 구성**:
> 1. [대중용 에디션 (블로그·쇼츠·릴스)](post.md)
> 2. [전문가용 에디션 (임상 심층 칼럼)](clinical/clinical_column.md)
> 3. [인터랙티브 웹 듀얼 뷰어](dual_view.html)

---

## 📊 에디션별 사양 비교표

| 항목 | 📱 대중용 에디션 (General Public) | 🩺 전문가용 에디션 (Clinical / Expert) |
| :--- | :--- | :--- |
| **타깃 독자** | 겨울에도 걷기와 홈트를 이어 가려는 50~70대, 혈압약·심장약을 먹는 만성질환자, 새벽 운동 습관이 있는 직장인, 부모님 운동을 걱정하는 자녀 | 순환기·가정의학과·응급의학과 전문의, 전공의, 운동처방사, 심장재활 담당 간호사 |
| **핵심 메시지** | 겨울 아침을 피해 오후 두 시에서 네 시에 운동하고, 실내에서는 의자 하나로 20분, 야외에서는 보폭 절반과 양손 주머니 밖, 가슴 통증 5분이면 119 | 한랭 노출의 교감신경·혈역학·유변학적 부하, 아침 혈압 상승과 계절 변동, 동적 준비운동과 베타차단제 복용자의 강도 지표, 낙상 후 Ottawa 기준과 저체온·동상 처치 |
| **주요 키워드** | 겨울철 실내 운동, 한파 야외 걷기, 심혈관 운동 주의점 | Cold-induced cardiac strain, Rate pressure product, Morning blood pressure surge, Dynamic warm-up, Exercise-related acute cardiovascular events |
| **권장 채널** | 네이버 블로그, 인스타그램, 유튜브 쇼츠 | 병원 의학 칼럼, 학술 리뷰, 심장재활 교육자료 |
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
