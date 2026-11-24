#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11/24 7회차 네이버 블로그 발행용 HTML 생성 (A 시황 / B 수급)"""
import re
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/work/content-automation-engine")
from publisher.naver_formatter import markdown_to_naver_html  # noqa: E402

OUT = Path("/workspace/work/content-automation-engine/content/naver-1124")
OUT.mkdir(parents=True, exist_ok=True)

A_SRC = Path("/workspace/work/stock-analysis/content/2026-11-24/01_market_daily_insight.md")
B_SRC = Path("/workspace/work/stock-future/content/2026-11-24/02_foreign_flow_analysis.md")

INTRO = ("지금 투자는 AI와의 전쟁입니다. AI를 이해하는 능력이 투자 성패를 가릅니다. "
         "이 채널을 통해 주식선물, 지수선물, 코덱스 레버리지·인버스 등의 방향 투자로 시대의 흐름에 편승하세요.")
NOTICE = ("📢 [안내] '올.주.선.이'는 유튜브 구독자 또는 블로그 이웃 1,000명까지는 평생 무료로 서비스를 이어가며, "
          "그 이상 신규 가입자부터는 유료 전환을 검토하고 있습니다.")
PRODUCT_LINES = [
    ("h", "▍함께 보면 좋은 제품"),
    ("p", "매일 시장 기록을 올리는 채널입니다. 함께 소개하는 제품의 판매 수수료는 기록을 이어가는 데 보탬이 됩니다."),
    ("p", "• 상품명: 이니스프리 그린티 씨드 히알루론산 보습 속건조 수분크림 80ml"),
    ("p", "• 가격: 24,700원 (정가 38,000원)"),
    ("p", "• 특징: 그린티 씨드 오일과 히알루론산을 담은 보습 크림입니다. 세안이나 목욕 뒤 피부가 촉촉할 때 얼굴과 목에 얇게 펴 바릅니다. 새 제품은 팔 안쪽에 먼저 발라 보고 자극이 없을 때 사용하십시오."),
    ("a", ("네이버에서 이니스프리 그린티 씨드 히알루론산 수분크림 보기", "https://naver.me/5nhmDgab")),
    ("a", ("크리에이터샵: 겅태 크리에이터샵", "https://cshop.naver.com/geongtae_shop")),
    ("p", "이 포스팅은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다."),
    ("p", "본 글은 투자 권유가 아닌 개인적인 시장 기록 및 정보 정리 목적입니다."),
]

PROMPT_A = "오늘 코스피 마감 수치와 외국인·기관·개인 수급을 표로 정리하고, 이 반등이 이틀 이어질지 판단할 지표 세 가지를 체크리스트로 만들어 줘."
PROMPT_B = "외국인 선물 누적과 미결제·베이시스·옵션 수치를 시간대별 표로 만들고, 장 막판에 포지션 성격이 매도로 바뀐 구간을 표시해 줘."

DIRECTION_HTML = """<h2 style="font-size:20px;font-weight:bold;">오늘의 방향 / 내일의 예상</h2>
<table style="border-collapse:collapse;width:100%;margin:14px 0;">
<tr><th style="border:1px solid #ddd;background:#f5f5f5;padding:10px;">구분</th><th style="border:1px solid #ddd;background:#f5f5f5;padding:10px;">판단</th></tr>
<tr><td style="border:1px solid #ddd;padding:10px;">오늘의 방향</td><td style="border:1px solid #ddd;padding:10px;">▲ 강위, 강한 상방</td></tr>
<tr><td style="border:1px solid #ddd;padding:10px;">내일의 예상</td><td style="border:1px solid #ddd;padding:10px;">▲ 강위, 강한 상방</td></tr>
<tr><td style="border:1px solid #ddd;padding:10px;">방향성 적중률</td><td style="border:1px solid #ddd;padding:10px;">11/23~ 100.0% (1/1)</td></tr>
</table>"""


def inner_html(md: str) -> str:
    full = markdown_to_naver_html(md)
    m = re.search(r'<div id="naver-post-container">(.*)</div>\s*</body>', full, re.S)
    return (m.group(1) if m else full).strip()


def body_of(path: Path) -> str:
    md = path.read_text(encoding="utf-8")
    i = md.index("**본문**") + len("**본문**")
    j = md.index("## 쇼츠·릴스 대본")
    body = md[i:j]
    body = re.sub(r"^(\s*-{3,}\s*)+", "", body)
    return body.strip()


def wrap(inner: str) -> str:
    return ("<!DOCTYPE html>\n<html><head><meta charset='utf-8'><title>naver</title></head>\n"
            "<body style=\"max-width: 760px; margin: 30px auto; padding: 10px; font-family: 'Apple SD Gothic Neo','Malgun Gothic',sans-serif;\">\n"
            "<div id='naver-post-container'>\n" + inner + "\n</div></body></html>\n")


def build(path: Path, prompt: str, with_direction: bool) -> str:
    parts = [
        "<p style='font-size:15px;color:#555;margin-bottom:14px;'>저자: 겅태(의학과 경제학에 관심많은)</p>",
        f"<blockquote style='border-left:4px solid #8a8a8a; padding:12px 16px; margin:18px 0; color:#333; font-size:15px; line-height:1.7;'><p style='margin:0;'>{INTRO}</p></blockquote>",
        f"<p style='font-size:15px; line-height:1.8; margin:16px 0;'>{NOTICE}</p>",
        "<hr style='border:0;height:1px;background:#dddddd;margin:26px 0;' />",
        inner_html(body_of(path)),
    ]
    if with_direction:
        parts.append(DIRECTION_HTML)
    parts.append("<hr style='border:0;height:1px;background:#dddddd;margin:30px 0;' />")
    parts.append("<p style=\"font-size:30px; font-weight:bold; margin:18px 0 14px 0;\">💡 오늘의 프롬프트</p>")
    parts.append("<table style='border-collapse:collapse;width:100%;border:2px solid #ff0010;'>"
                 f"<tr><td style='border:2px solid #ff0010;padding:14px 16px;font-size:16px;line-height:1.7;'>{prompt}</td></tr>"
                 "</table>")
    for kind, value in PRODUCT_LINES:
        if kind == "h":
            parts.append(f"<h2 style='font-size:20px;font-weight:bold;margin-top:34px;'>{value}</h2>")
        elif kind == "a":
            text, url = value
            parts.append(f"<p style='font-size:16px;'><a href='{url}' target='_blank' style='color:#2563eb;text-decoration:underline;'>{text}</a></p>")
        else:
            parts.append(f"<p style='font-size:16px; line-height:1.8;'>{value}</p>")
    parts.append("<p style='font-size:16px; font-weight:bold; margin-top:22px;'>이 글은 오후 4시까지의 수급으로 분석했습니다.</p>")
    return wrap("\n".join(parts))


if __name__ == "__main__":
    a = build(A_SRC, PROMPT_A, with_direction=True)
    b = build(B_SRC, PROMPT_B, with_direction=False)
    (OUT / "a.html").write_text(a, encoding="utf-8")
    (OUT / "b.html").write_text(b, encoding="utf-8")
    for name, h in (("A", a), ("B", b)):
        print(f"[{name}] html chars={len(h)} tables={h.count('<table')} red={h.count('#ff0010')} "
              f"blockquote={h.count('<blockquote')} naver.me={h.count('naver.me/5nhmDgab')} "
              f"cshop={h.count('cshop.naver.com/geongtae_shop')} 김승태={'김승태' in h} 💡={h.count('💡')} 📢={h.count('📢')}")
