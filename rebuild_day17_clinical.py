#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Day 17 임상 칼럼 표 정정(2026-11-24 2차 검수) 후 HTML 산출물 재생성.

- clinical/clinical_column.md → clinical_column.html (위젯·듀얼뷰어용)
- clinical_column_naver.html (네이버 붙여넣기용) + publish/clin2.html 사본
- dual_view.html 및 downloads/Day17_콘텐츠_이원화_듀얼뷰어.html
대중용(naver_post.html)은 손대지 않는다.
"""
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.clinical_engine import markdown_to_clinical_html  # noqa: E402
from engine.dual_pipeline import build_dual_view_html  # noqa: E402
import publish_prep_day17  # noqa: E402

DAY_DIR = BASE_DIR / "content" / "2026-11-24-01"
CLIN_MD = DAY_DIR / "clinical" / "clinical_column.md"

md = CLIN_MD.read_text(encoding="utf-8")

clin_html = markdown_to_clinical_html(
    md,
    title="한랭기 소양과 만성 습진의 감별: 건조성 습진과 아토피 피부염의 병태생리, 국소 스테로이드 근거 기반 처방",
)
(DAY_DIR / "clinical" / "clinical_column.html").write_text(clin_html, encoding="utf-8")

naver_html = publish_prep_day17.build_clinical()
(DAY_DIR / "clinical" / "clinical_column_naver.html").write_text(naver_html, encoding="utf-8")
(DAY_DIR / "publish" / "clin2.html").write_text(naver_html, encoding="utf-8")

dual_html = build_dual_view_html(DAY_DIR)
(DAY_DIR / "dual_view.html").write_text(dual_html, encoding="utf-8")
Path("/workspace/downloads/Day17_콘텐츠_이원화_듀얼뷰어.html").write_text(dual_html, encoding="utf-8")

for name, html in (("clinical_column.html", clin_html), ("clinical_column_naver.html", naver_html),
                   ("dual_view.html", dual_html)):
    print(f"[{name}] chars={len(html)} tables={html.count('<table')} 데소나이드={html.count('데소나이드')} "
          f"데소니드={html.count('데소니드')} 모메타손연고={html.count('모메타손 푸로에이트 0.1% 연고')} "
          f"모메타손크림={html.count('모메타손 푸로에이트 0.1% 크림')} 저자={'겅태(의학과 경제학에 관심많은)' in html}")
