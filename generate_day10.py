#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 10 Content Generator (Dual Pipeline: Public + Clinical Expert)
Topic: 겨울철 음주 후 귀가 시 저체온증의 치명적 위험 (응급실 단골 사고)
Keywords: 겨울철 음주 저체온증, 저체온증 증상 체온, 동상 응급처치
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DAY_DIR = BASE_DIR / "content" / "2026-11-17-01"
DAY_DIR.mkdir(parents=True, exist_ok=True)
(DAY_DIR / "clinical").mkdir(parents=True, exist_ok=True)
(DAY_DIR / "instagram").mkdir(parents=True, exist_ok=True)
(DAY_DIR / "chalkboard").mkdir(parents=True, exist_ok=True)

POST_MD = (DAY_DIR / "post.md")
CLIN_MD = (DAY_DIR / "clinical" / "clinical_column.md")
ADS_MD = (DAY_DIR / "ads.md")
INSTA_MD = (DAY_DIR / "instagram" / "card_news_caption.md")

# 생성 본문은 같은 폴더의 원고 파일을 원본으로 삼는다.
# (원고는 generate_day10_content.py 로 작성, 이 스크립트는 변환·검증·배포를 담당)

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
    title="알코올 노출과 저체온증의 병태생리, 심부체온 단계별 심전도 변화, 재가온 전략과 동상 급속 재가온 프로토콜",
)
(DAY_DIR / "clinical" / "clinical_column.html").write_text(clin_html, encoding="utf-8")

dual_html = build_dual_view_html(DAY_DIR)
(DAY_DIR / "dual_view.html").write_text(dual_html, encoding="utf-8")
Path("/workspace/downloads/Day10_콘텐츠_이원화_듀얼뷰어.html").write_text(dual_html, encoding="utf-8")

dual_md = """# 🩺 Day 10 콘텐츠 이원화 허브 (대중용 vs 전문가용)

> **주제**: 겨울철 음주 후 귀가 시 저체온증의 치명적 위험과 동상 응급처치
> **이원화 구성**:
> 1. [대중용 에디션 (블로그·쇼츠·릴스)](post.md)
> 2. [전문가용 에디션 (임상 심층 칼럼)](clinical/clinical_column.md)
> 3. [인터랙티브 웹 듀얼 뷰어](dual_view.html)

---

## 📊 에디션별 사양 비교표

| 항목 | 📱 대중용 에디션 (General Public) | 🩺 전문가용 에디션 (Clinical / Expert) |
| :--- | :--- | :--- |
| **타깃 독자** | 연말 술자리가 잦은 직장인, 야간 귀가자와 가족 | 응급의학과·가정의학과 전문의, 전공의, 의대생 |
| **핵심 메시지** | 술은 몸을 덥히지 않는다, 단계별 체온 신호, 동상은 문지르지 않는다, 의식 흐림은 일일구 | 알코올성 혈관확장과 떨림 억제, Swiss staging, Osborn J파, afterdrop과 재가온 쇼크, ECMO 적응 |
| **주요 키워드** | 겨울철 음주 저체온증, 저체온증 증상 체온, 동상 응급처치 | Cutaneous vasodilation, Shivering thermogenesis, Osborn wave, Active internal rewarming, Frostbite rapid rewarming |
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
