#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Day 17 네이버 블로그 발행용 HTML 생성 (대중용 + 임상 칼럼).

- 블로그 제목 필드와 중복되는 H1, 작성자용 머리말, 제목 옵션·메타 디스크립션·태그 섹션 제거
- `💡 오늘의 프롬프트`를 본문 끝난 직후, 제품 소개 바로 위에 빨간 1x1 표로 삽입 (#ff0010)
- 제휴: 이니스프리 수분크림 80ml + 크리에이터샵 + 공정위 고지
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/work/content-automation-engine")
from publisher.naver_formatter import markdown_to_naver_html  # noqa: E402

DAY = Path("/workspace/work/content-automation-engine/content/2026-11-24-01")
SRC_PUBLIC = DAY / "post.md"
SRC_CLINICAL = DAY / "clinical" / "clinical_column.md"

PROMPT_PUBLIC = "밤에 긁는 부위를 하나씩 적고, 그 부위에 맞는 보습제와 연고 사용 순서를 표로 만들어 줘."
PROMPT_CLINICAL = "야간 소양 환자의 문진 항목을 표로 정리하고, 건조성 습진과 아토피 피부염을 구분하는 감별 체크리스트를 만들어 줘."

PROMPT_HTML = (
    "<hr style='border:0;height:1px;background:#dddddd;margin:30px 0;' />\n"
    "<p style=\"font-size:30px; font-weight:bold; margin:18px 0 14px 0;\">💡 오늘의 프롬프트</p>\n"
    "<table style='border-collapse:collapse;width:100%;border:2px solid #ff0010;'>"
    "<tr><td style='border:2px solid #ff0010;padding:14px 16px;font-size:16px;line-height:1.7;'>{prompt}</td></tr>"
    "</table>\n"
)

PRODUCT_HTML = """<h2 style='font-size:20px;font-weight:bold;margin-top:34px;'>▍함께 보면 좋은 제품</h2>
<p style='font-size:16px; line-height:1.8;'>겨울에는 보습제를 넉넉히 바르는 것이 기본입니다. 씻고 나서 피부가 아직 촉촉할 때 얼굴과 목, 손등에 얇게 펴 바르기 좋은 제품을 소개합니다.</p>
<p style='font-size:16px; line-height:1.8;'>• 상품명: 이니스프리 그린티 씨드 히알루론산 보습 속건조 수분크림 80ml</p>
<p style='font-size:16px; line-height:1.8;'>• 가격: 24,700원 (정가 38,000원)</p>
<p style='font-size:16px; line-height:1.8;'>• 특징: 그린티 씨드 오일과 히알루론산을 담은 보습 크림입니다. 세안이나 목욕 뒤 피부가 촉촉할 때 얇게 펴 바릅니다. 새 제품은 팔 안쪽에 먼저 발라 보고 자극이 없을 때 사용하십시오. 갈라져 벌어진 부위나 진물이 나는 부위에는 바르지 말고 진료를 먼저 받으십시오.</p>
<p style='font-size:16px;'><a href='https://naver.me/5nhmDgab' target='_blank' style='color:#2563eb;text-decoration:underline;'>네이버에서 이니스프리 그린티 씨드 히알루론산 수분크림 보기</a></p>
<p style='font-size:16px;'><a href='https://cshop.naver.com/geongtae_shop' target='_blank' style='color:#2563eb;text-decoration:underline;'>크리에이터샵: 겅태 크리에이터샵</a></p>
<p style='font-size:16px; line-height:1.8;'>이 포스팅은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다.</p>
"""


def inner_html(md: str) -> str:
    full = markdown_to_naver_html(md)
    return full.strip()


def wrap(inner: str) -> str:
    return ("<!DOCTYPE html>\n<html><head><meta charset='utf-8'><title>naver</title></head>\n"
            "<body style=\"max-width: 760px; margin: 30px auto; padding: 10px; "
            "font-family: 'Apple SD Gothic Neo','Malgun Gothic',sans-serif;\">\n"
            "<div id='naver-post-container'>\n" + inner + "\n</div></body></html>\n")


def build_public() -> str:
    md = SRC_PUBLIC.read_text(encoding="utf-8")
    i = md.index("## 💡 현장 리포트")
    md_body = "> **저자**: 겅태(의학과 경제학에 관심많은)\n\n---\n\n" + md[i:]
    # 태그·면책 섹션 정리: 제품 소개 이후는 HTML로 직접 붙인다
    j = md_body.index("## 🛍️ 함께 보면 좋은 제품")
    md_body = md_body[:j].rstrip()

    inner = inner_html(md_body)
    parts = [inner, PROMPT_HTML.format(prompt=PROMPT_PUBLIC), PRODUCT_HTML,
             "<p style='font-size:15px; line-height:1.8; color:#555;'>*이 글은 의학적 정보 제공을 목적으로 하며, 개인의 진단과 치료를 대신하지 않습니다. 진물이나 발열, 번지는 붉음이 있거나 밤에 잠을 못 잘 정도로 가렵고 2주 이상 낫지 않으면 의료기관을 방문하십시오.*</p>"]
    return wrap("\n".join(parts))


def build_clinical() -> str:
    md = SRC_CLINICAL.read_text(encoding="utf-8")
    # H1과 긴 머리말(저자·발행처·참고문헌 등)은 발행 화면에서 쓰지 않고, 저자 한 줄만 남긴다
    i = md.index("## 1. 개요 및 문제 설정")
    header = md[:i]
    # 참고문헌 원문은 부록에 별도로 유지되므로 머리말의 긴 목록은 생략하지 않고 그대로 둔다
    md_body = header + md[i:]
    md_body = re.sub(r"^# .+\n", "", md_body, count=1)
    # 부록의 제품 안내는 본문에서 제거하고 HTML로 붙인다
    j = md_body.index("## 부록: 보습 처방과 제휴 안내")
    appendix = md_body[j:]
    md_body = md_body[:j].rstrip()

    inner = inner_html(md_body)
    appendix_md = appendix.replace("## 부록: 보습 처방과 제휴 안내",
                                   "## 부록: 보습 처방")
    # 제휴 줄은 appendix_md 안에 있으므로 잘라낸 뒤 PRODUCT_HTML로 대체
    cut = appendix_md.index("- 제휴 상품:")
    appendix_md = appendix_md[:cut].rstrip()
    appendix_html = inner_html(appendix_md)

    parts = [inner, appendix_html, PROMPT_HTML.format(prompt=PROMPT_CLINICAL), PRODUCT_HTML,
             "<p style='font-size:15px; line-height:1.8; color:#555;'>*이 글은 의료인을 대상으로 한 임상 정보 정리이며, 개별 환자의 진단과 처방을 대신하지 않습니다. 실제 처방은 환자의 나이, 병변 부위와 면적, 동반 질환을 고려해 결정해야 합니다.*</p>"]
    return wrap("\n".join(parts))


if __name__ == "__main__":
    pub = build_public()
    clin = build_clinical()
    (DAY / "naver_post_publish.html").write_text(pub, encoding="utf-8")
    (DAY / "clinical" / "clinical_column_naver.html").write_text(clin, encoding="utf-8")
    for name, h in (("대중용", pub), ("임상", clin)):
        print(f"[{name}] chars={len(h)} tables={h.count('<table')} red={h.count('#ff0010')} "
              f"prompt={'오늘의 프롬프트' in h} naver.me={h.count('naver.me/5nhmDgab')} "
              f"cshop={h.count('cshop.naver.com/geongtae_shop')} 김승태={'김승태' in h} "
              f"h1={h.count('<h1')}")
