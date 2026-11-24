#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 18 Content Generator (Dual Pipeline: Public + Clinical Expert)
Topic: 겨울 고열·기침, 감기인가 독감인가. RSV·마이코플라스마까지 아이와 어르신 감별법
Keywords: RSV 증상 아이, 마이코플라스마 폐렴 기침, 독감 감기 차이
"""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

DAY_DIR = BASE_DIR / "content" / "2026-11-25-01"
for sub in ("clinical", "instagram", "images_v2", "subtitles", "publish", "video"):
    (DAY_DIR / sub).mkdir(parents=True, exist_ok=True)

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
    title="한랭기 소아·고령 호흡기 감염의 감별: 인플루엔자, RSV 세기관지염, 마이코플라스마 폐렴의 임상 평가와 치료 선택",
)
(DAY_DIR / "clinical" / "clinical_column.html").write_text(clin_html, encoding="utf-8")

dual_html = build_dual_view_html(DAY_DIR)
(DAY_DIR / "dual_view.html").write_text(dual_html, encoding="utf-8")
Path("/workspace/downloads/Day18_콘텐츠_이원화_듀얼뷰어.html").write_text(dual_html, encoding="utf-8")

dual_md = """# 🫁 Day 18 콘텐츠 이원화 허브 (대중용 vs 전문가용)

> **주제**: 겨울 고열·기침, 감기인가 독감인가. RSV·마이코플라스마까지 아이와 어르신 감별법
> **기획 분류**: 의학/건강 (겨울철 피부관리·호흡기질환 7일 기획 4일 차)
> **이원화 구성**:
> 1. [대중용 에디션 (블로그·쇼츠·릴스)](post.md)
> 2. [전문가용 에디션 (임상 심층 칼럼)](clinical/clinical_column.md)
> 3. [인터랙티브 웹 듀얼 뷰어](dual_view.html)

---

## 📊 에디션별 사양 비교표

| 항목 | 📱 대중용 에디션 (General Public) | 🩺 전문가용 에디션 (Clinical / Expert) |
| :--- | :--- | :--- |
| **타깃 독자** | 영유아·초등 자녀를 둔 부모, 65세 이상 어르신과 돌봄 가족, 교사 | 소아청소년과·가정의학과·응급의학과 전문의, 임상간호사, 보건교사 |
| **핵심 메시지** | 시작 방식이 다르면 병도 다르다. 아이는 숨쉬는 모습과 소변 양, 어르신은 밥 먹는 양과 기력으로 급한 정도를 가늠한다. 갈비뼈 아래 함몰과 빠른 호흡은 즉시 응급실 신호다 | 인플루엔자 항바이러스 시점과 고위험군, RSV 세기관지염의 중증도 평가와 근거 기반 보조 요법, 마이코플라스마 마크롤라이드 내성 81.4~89.4퍼센트 상황에서의 48~72시간 반응 재평가와 대체 항생제 전환 |
| **주요 키워드** | RSV 증상 아이, 마이코플라스마 폐렴 기침, 독감 감기 차이 | bronchiolitis, work of breathing, macrolide-resistant Mycoplasma pneumoniae, atypical pneumonia, nirsevimab |
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
