#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11/27 8회차 올.주.선.이 네이버 블로그 발행용 HTML 생성 (A 시황 / B 수급)

- 본문: work/stock-*/content/2026-11-27/*.md 의 **본문** 블록
- 캡처 3장: GitHub raw (커밋 SHA 고정) → 스마트에디터가 붙여넣기 때 가져간다
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, "/workspace/work/content-automation-engine")
from publisher.naver_formatter import markdown_to_naver_html  # noqa: E402

OUT = Path("/workspace/work/content-automation-engine/content/naver-1127")
OUT.mkdir(parents=True, exist_ok=True)

IMG_SHA = sys.argv[1] if len(sys.argv) > 1 else "2e804bc"
RAW = f"https://raw.githubusercontent.com/kst104/github.com-new/{IMG_SHA}/content/naver-1127"

A_SRC = Path("/workspace/work/stock-analysis/content/2026-11-27/01_market_daily_insight.md")
B_SRC = Path("/workspace/work/stock-future/content/2026-11-27/02_foreign_flow_analysis.md")

CAPTIONS = {
    "capture-1": "8901 반도체 수급 대전제·규칙 요약 (2026.11.27 15:19 화면)",
    "capture-2": "8901 반도체 누적 수급·추세선과 코스피200 선물 (2026.11.27 15:19 화면)",
    "capture-3": "18901 가격대별 GEX 곡선·GEX×VEX 매트릭스와 8766 외국인 선물·옵션 포지션 (2026.11.27 15:45~15:49 화면)",
}

INTRO = ("지금 투자는 AI와의 전쟁입니다. AI를 이해하는 능력이 투자 성패를 가릅니다. "
         "이 채널을 통해 주식선물, 지수선물, 코덱스 레버리지·인버스 등의 방향 투자로 시대의 흐름에 편승하세요.")
NOTICE = ("📢 [안내] '올.주.선.이'는 유튜브 구독자 또는 블로그 이웃 1,000명까지는 평생 무료로 서비스를 이어가며, "
          "그 이상 신규 가입자부터는 유료 전환을 검토하고 있습니다.")


def inner_html(md: str) -> str:
    full = markdown_to_naver_html(md)
    m = re.search(r'<div id="naver-post-container">(.*)</div>\s*</body>', full, re.S)
    return (m.group(1) if m else full).strip()


def img_block(key: str) -> str:
    cap = CAPTIONS.get(key, "")
    return ("<p style='text-align:center; margin:20px 0 6px 0;'>"
            f"<img src='{RAW}/{key}.png' alt='{cap}' style='max-width:100%; height:auto;' /></p>"
            "<p style='text-align:center; font-size:13px; color:#666666; margin:0 0 20px 0;'>"
            f"{cap}</p>")


def split_and_convert(body_md: str) -> str:
    parts = re.split(r"\[\[IMG:(capture-\d)\]\]", body_md)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out.append(img_block(part.strip()))
        else:
            if part.strip():
                out.append(inner_html(part))
    return "\n".join(out)


def body_and_prompt(path: Path):
    md = path.read_text(encoding="utf-8")
    i = md.index("**본문**") + len("**본문**")
    j = md.index("**오늘의 프롬프트 (본문 말미 고정)**")
    body = md[i:j]
    rest = md[j + len("**오늘의 프롬프트 (본문 말미 고정)**"):]
    rest = rest.split("---")[0]
    prompt = " ".join(line.strip() for line in rest.strip().split("\n") if line.strip())
    return body.strip(), prompt


def wrap(inner: str) -> str:
    return ("<!DOCTYPE html>\n<html><head><meta charset='utf-8'><title>naver</title></head>\n"
            "<body style=\"max-width: 760px; margin: 30px auto; padding: 10px; "
            "font-family: 'Apple SD Gothic Neo','Malgun Gothic',sans-serif;\">\n"
            "<div id='naver-post-container'>\n" + inner + "\n</div></body></html>\n")


def build(path: Path) -> str:
    body_md, prompt = body_and_prompt(path)
    parts = [
        "<p style='font-size:15px;color:#555;margin-bottom:14px;'>저자: 겅태(의학과 경제학에 관심많은)</p>",
        ("<blockquote style='border-left:4px solid #8a8a8a; padding:12px 16px; margin:18px 0; color:#333; "
         "font-size:15px; line-height:1.7;'><p style='margin:0;'>" + INTRO + "</p></blockquote>"),
        f"<p style='font-size:15px; line-height:1.8; margin:16px 0;'>{NOTICE}</p>",
        "<hr style='border:0;height:1px;background:#dddddd;margin:26px 0;' />",
        split_and_convert(body_md),
        "<hr style='border:0;height:1px;background:#dddddd;margin:30px 0;' />",
        "<p style=\"font-size:30px; font-weight:bold; margin:18px 0 14px 0;\">💡 오늘의 프롬프트</p>",
        ("<table style='border-collapse:collapse;width:100%;border:2px solid #ff0010;'>"
         "<tr><td style='border:2px solid #ff0010;padding:14px 16px;font-size:16px;line-height:1.7;'>"
         + prompt + "</td></tr></table>"),
        "<h2 style='font-size:20px;font-weight:bold;margin-top:34px;'>▍겅태의 크리에이터샵</h2>",
        "<p style='font-size:16px; line-height:1.8;'>매일 시장 기록을 올리는 채널입니다. 시장·건강 관련 추천 제품은 아래 크리에이터샵에 모아 두었습니다.</p>",
        "<p style='font-size:16px;'><a href='https://cshop.naver.com/geongtae_shop' target='_blank' style='color:#2563eb;text-decoration:underline;'>크리에이터샵: 겅태 크리에이터샵</a></p>",
        "<p style='font-size:16px; line-height:1.8;'>이 포스팅은 네이버 크리에이터샵 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다.</p>",
        "<p style='font-size:16px; line-height:1.8;'>본 글은 투자 권유가 아닌 개인적인 시장 기록 및 정보 정리 목적입니다.</p>",
        "<p style='font-size:16px; font-weight:bold; margin-top:22px;'>이 글은 오후 4시까지의 수급으로 분석했습니다.</p>",
    ]
    return wrap("\n".join(parts))


if __name__ == "__main__":
    a = build(A_SRC)
    b = build(B_SRC)
    (OUT / "a.html").write_text(a, encoding="utf-8")
    (OUT / "b.html").write_text(b, encoding="utf-8")
    for name, h in (("A", a), ("B", b)):
        print(f"[{name}] chars={len(h)} tables={h.count('<table')} red={h.count('#ff0010')} "
              f"blockquote={h.count('<blockquote')} img={h.count('<img')} cshop={h.count('cshop.naver.com/geongtae_shop')} "
              f"4시={'오후 4시까지의 수급으로 분석했습니다' in h} 김승태={'김승태' in h} 💡={h.count('💡')} 📢={h.count('📢')}")
