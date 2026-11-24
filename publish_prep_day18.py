#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Day 18 네이버 블로그 발행용 HTML 생성 (대중용 + 임상 칼럼).

- 블로그 제목 필드와 중복되는 H1·제목 옵션·메타·태그 섹션은 제거
- `💡 오늘의 프롬프트`를 본문 끝난 직후, 제품 소개 바로 위에 빨간 1x1 표(#ff0010)로 삽입
- 제휴: 이니스프리 수분크림 80ml + 크리에이터샵 + 공정위 고지
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/work/content-automation-engine")
from publisher.naver_formatter import markdown_to_naver_html  # noqa: E402

DAY = Path("/workspace/work/content-automation-engine/content/2026-11-25-01")
SRC_PUBLIC = DAY / "post.md"
SRC_CLINICAL = DAY / "clinical" / "clinical_column.md"

PROMPT_PUBLIC = "아이 기침과 열을 진료받을 때, 언제부터 어떻게 시작했는지와 숨쉬는 모습을 어떻게 정리해 가면 좋을까요?"
PROMPT_CLINICAL = "인플루엔자·RSV·마이코플라스마 폐렴을 나이와 시작 양상으로 구분하는 감별 체크리스트를 표로 만들어 줘."

PROMPT_HTML = (
    "<hr style='border:0;height:1px;background:#dddddd;margin:30px 0;' />\n"
    "<p style=\"font-size:30px; font-weight:bold; margin:18px 0 14px 0;\">💡 오늘의 프롬프트</p>\n"
    "<table style='border-collapse:collapse;width:100%;border:2px solid #ff0010;'>"
    "<tr><td style='border:2px solid #ff0010;padding:14px 16px;font-size:16px;line-height:1.7;'>{prompt}</td></tr>"
    "</table>\n"
)

PRODUCT_HTML = """<h2 style='font-size:20px;font-weight:bold;margin-top:34px;'>▍함께 보면 좋은 제품</h2>
<p style='font-size:16px; line-height:1.8;'>겨울에는 손 씻는 횟수가 늘고 실내가 건조해져 손등과 얼굴이 트기 쉽습니다. 아이를 돌보기 전후로 손을 씻고, 물기가 남아 있을 때 얇게 펴 바르기 좋은 제품을 소개합니다.</p>
<p style='font-size:16px; line-height:1.8;'>• 상품명: 이니스프리 그린티 씨드 히알루론산 보습 속건조 수분크림 80ml</p>
<p style='font-size:16px; line-height:1.8;'>• 가격: 24,700원 (정가 38,000원)</p>
<p style='font-size:16px; line-height:1.8;'>• 특징: 그린티 씨드 오일과 히알루론산을 담은 보습 크림입니다. 세안이나 손 씻기 뒤 피부가 촉촉할 때 얇게 펴 바릅니다. 새 제품은 팔 안쪽에 먼저 발라 보고 자극이 없을 때 사용하십시오. 갈라져 벌어진 부위나 진물이 나는 부위에는 바르지 말고 진료를 먼저 받으십시오.</p>
<p style='font-size:16px;'><a href='https://naver.me/5nhmDgab' target='_blank' style='color:#2563eb;text-decoration:underline;'>네이버에서 이니스프리 그린티 씨드 히알루론산 수분크림 보기</a></p>
<p style='font-size:16px;'><a href='https://cshop.naver.com/geongtae_shop' target='_blank' style='color:#2563eb;text-decoration:underline;'>크리에이터샵: 겅태 크리에이터샵</a></p>
<p style='font-size:16px; line-height:1.8;'>이 포스팅은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다.</p>
"""


def inner_html(md: str) -> str:
    return markdown_to_naver_html(md).strip()


def wrap(inner: str) -> str:
    return ("<!DOCTYPE html>\n<html><head><meta charset='utf-8'><title>naver</title></head>\n"
            "<body style=\"max-width: 760px; margin: 30px auto; padding: 10px; "
            "font-family: 'Apple SD Gothic Neo','Malgun Gothic',sans-serif;\">\n"
            "<div id='naver-post-container'>\n" + inner + "\n</div></body></html>\n")


def build_public() -> str:
    md = SRC_PUBLIC.read_text(encoding="utf-8")
    i = md.index("## 💡 현장 리포트")
    md_body = "> **저자**: 겅태(의학과 경제학에 관심많은)\n\n---\n\n" + md[i:]
    j = md_body.index("## 💡 오늘의 프롬프트")
    md_body = re.sub(r"(\s*-{3,}\s*)+$", "", md_body[:j]).rstrip()

    inner = inner_html(md_body)
    parts = [inner, PROMPT_HTML.format(prompt=PROMPT_PUBLIC), PRODUCT_HTML,
             "<p style='font-size:15px; line-height:1.8; color:#555;'>*이 글은 의학적 정보 제공을 목적으로 하며, 개인의 진단과 치료를 대신하지 않습니다. 숨이 차거나 물을 못 마시는 경우, 3개월 미만 아이가 열이 나는 경우에는 지체 없이 의료기관을 방문하십시오.*</p>"]
    return wrap("\n".join(parts))


def build_clinical() -> str:
    md = SRC_CLINICAL.read_text(encoding="utf-8")
    i = md.index("## 1. 개요 및 문제 설정")
    header = md[:i]
    md_body = header + md[i:]
    md_body = re.sub(r"^# .+\n", "", md_body, count=1)
    j = md_body.index("## 부록: 보습 처방과 제휴 안내")
    appendix = md_body[j:]
    md_body = re.sub(r"(\s*-{3,}\s*)+$", "", md_body[:j]).rstrip()

    inner = inner_html(md_body)
    appendix_md = appendix.replace("## 부록: 보습 처방과 제휴 안내", "## 부록: 보습 처방")
    cut = appendix_md.index("- 제휴 상품:")
    appendix_md = appendix_md[:cut].rstrip()
    appendix_html = inner_html(appendix_md)

    parts = [inner, appendix_html, PROMPT_HTML.format(prompt=PROMPT_CLINICAL), PRODUCT_HTML,
             "<p style='font-size:15px; line-height:1.8; color:#555;'>*이 글은 의료인을 대상으로 한 임상 정보 정리이며, 개별 환자의 진단과 처방을 대신하지 않습니다. 항생제 선택과 변경은 환자의 나이, 중증도, 검사 결과를 고려해 결정해야 합니다.*</p>"]
    return wrap("\n".join(parts))


if __name__ == "__main__":
    pub = build_public()
    clin = build_clinical()
    (DAY / "naver_post_publish.html").write_text(pub, encoding="utf-8")
    (DAY / "clinical" / "clinical_column_naver.html").write_text(clin, encoding="utf-8")
    (DAY / "publish").mkdir(exist_ok=True)
    (DAY / "publish" / "pub.html").write_text(pub, encoding="utf-8")
    (DAY / "publish" / "clin.html").write_text(clin, encoding="utf-8")
    for name, h in (("대중용", pub), ("임상", clin)):
        print(f"[{name}] chars={len(h)} tables={h.count('<table')} red={h.count('#ff0010')} "
              f"prompt={'오늘의 프롬프트' in h} naver.me={h.count('naver.me/5nhmDgab')} "
              f"cshop={h.count('cshop.naver.com/geongtae_shop')} 김승태={'김승태' in h} h1={h.count('<h1')}")
