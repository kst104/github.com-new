#!/usr/bin/env python3
"""Day 21(2026-11-28) 네이버 블로그 발행용 HTML 2편 생성.

- 입력: content/2026-11-28-01/post.md, clinical/clinical_column.md
- 출력: content/2026-11-28-01/publish/pub.html, clin.html
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DAY = ROOT / "content" / "2026-11-28-01"
RAW = "https://raw.githubusercontent.com/kst104/github.com-new/main/content/2026-11-28-01/images_v2/"

P_STYLE = "font-size: 16px; line-height: 1.8; color: #334155; margin-bottom: 12px;"
H2_STYLE = ("font-size: 20px; font-weight: bold; color: #1e3a8a; border-left: 4px solid #3b82f6; "
            "padding-left: 12px; margin-top: 35px; margin-bottom: 15px;")
H3_STYLE = "font-size: 17px; font-weight: bold; color: #1f2937; margin-top: 24px; margin-bottom: 10px;"
TD_STYLE = "border: 1px solid #cbd5e1; padding: 8px 10px; font-size: 14px; line-height: 1.6; color: #334155;"
TH_STYLE = "border: 1px solid #cbd5e1; padding: 8px 10px; font-size: 14px; background: #f1f5f9; font-weight: bold; color: #1e293b;"


def inline(txt: str) -> str:
    txt = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", txt)
    txt = re.sub(r"`(.+?)`", r"<code>\1</code>", txt)
    return txt


def convert(md: str) -> str:
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        if ln.startswith("# "):
            i += 1
            continue
        if ln.startswith("## "):
            out.append(f"<h2 style='{H2_STYLE}'>{inline(ln[3:].strip())}</h2>")
            i += 1
            continue
        if ln.startswith("### "):
            out.append(f"<h3 style='{H3_STYLE}'>{inline(ln[4:].strip())}</h3>")
            i += 1
            continue
        m = re.match(r"\[\[IMG:(.+?)\|(.+?)\]\]", ln.strip())
        if m:
            name, cap = m.group(1), m.group(2)
            out.append(
                "<p style='text-align:center; margin:22px 0 6px 0;'>"
                f"<img src='{RAW}{name}' alt='{cap}' style='width:100%; max-width:760px; border-radius:8px;' /></p>"
            )
            out.append(f"<p style='text-align:center; font-size:13px; color:#64748b; margin:0 0 18px 0;'>{cap}</p>")
            i += 1
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            body = rows[1:] if len(rows) > 1 and set(rows[1][0]) <= set("-: ") else rows
            head = rows[0]
            html = ["<table style='border-collapse: collapse; width: 100%; margin: 16px 0 20px 0;'>"]
            html.append("<tr>" + "".join(f"<th style='{TH_STYLE}'>{inline(c)}</th>" for c in head) + "</tr>")
            for r in body:
                html.append("<tr>" + "".join(f"<td style='{TD_STYLE}'>{inline(c)}</td>" for c in r) + "</tr>")
            html.append("</table>")
            out.append("".join(html))
            continue
        if ln.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:].strip())
                i += 1
            html = ["<ul style='margin: 8px 0 16px 0; padding-left: 22px;'>"]
            html += [f"<li style='margin-bottom: 8px; font-size: 16px; color: #374151;'>{inline(t)}</li>" for t in items]
            html.append("</ul>")
            out.append("".join(html))
            continue
        if re.match(r"^\d+\. ", ln):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i]).strip())
                i += 1
            html = ["<ul style='margin: 8px 0 16px 0; padding-left: 22px;'>"]
            html += [f"<li style='margin-bottom: 8px; font-size: 16px; color: #374151;'>{inline(t)}</li>" for t in items]
            html.append("</ul>")
            out.append("".join(html))
            continue
        out.append(f"<p style='{P_STYLE}'>{inline(ln.strip())}</p>")
        i += 1
    return "\n".join(out)


def page(title: str, body_html: str, prompt: str, product_lead: str, meta: list[str] | None = None) -> str:
    meta_lines = "".join(f"<p style='margin: 0;'>{m}</p>" for m in (meta or []))
    author = (
        "<div style='background: #f8fafc; border-left: 4px solid #64748b; padding: 14px 18px; margin: 20px 0; "
        "border-radius: 4px; color: #334155; font-size: 15px; line-height: 1.7;'>"
        "<p style='margin: 0;'><b>저자</b>: 겅태(의학과 경제학에 관심많은)</p>" + meta_lines + "</div>"
    )
    prompt_box = (
        "<p style='line-height: 1.8; margin-bottom: 15px;'>&nbsp;</p>"
        "<p style=\"font-size:30px; font-weight:bold; margin:18px 0 14px 0;\">💡 오늘의 프롬프트</p>"
        "<table style='border-collapse:collapse;width:100%;border:2px solid #ff0010;'><tr>"
        f"<td style='border:2px solid #ff0010;padding:14px 16px;font-size:16px;line-height:1.7;'>{prompt}</td>"
        "</tr></table>"
        "<h2 style='font-size:20px;font-weight:bold;margin-top:34px;'>▍함께 보면 좋은 제품</h2>"
        f"<p style='font-size:16px; line-height:1.8;'>{product_lead}</p>"
        "<p style='font-size:16px; line-height:1.8;'>• 상품명: 이니스프리 그린티 씨드 히알루론산 보습 속건조 수분크림 80ml</p>"
        "<p style='font-size:16px; line-height:1.8;'>• 가격: 24,700원 (정가 38,000원)</p>"
        "<p style='font-size:16px; line-height:1.8;'>• 특징: 그린티 씨드 오일과 히알루론산을 담은 보습 크림입니다. 세안이나 손 씻기 뒤 피부가 "
        "촉촉할 때 얇게 펴 바릅니다. 새 제품은 팔 안쪽에 먼저 발라 보고 자극이 없을 때 사용하십시오. 갈라져 벌어진 부위나 진물이 "
        "나는 부위에는 바르지 말고 진료를 먼저 받으십시오.</p>"
        "<p style='font-size:16px;'><a href='https://naver.me/5nhmDgab' target='_blank' style='color:#2563eb;text-decoration:underline;'>"
        "네이버에서 이니스프리 그린티 씨드 히알루론산 수분크림 보기</a></p>"
        "<p style='font-size:16px;'><a href='https://cshop.naver.com/geongtae_shop' target='_blank' style='color:#2563eb;text-decoration:underline;'>"
        "크리에이터샵: 겅태 크리에이터샵</a></p>"
        "<p style='font-size:16px; line-height:1.8;'>이 포스팅은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다.</p>"
    )
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{title}</title></head>"
        "<body style=\"max-width: 760px; margin: 30px auto; padding: 10px; font-family: 'Apple SD Gothic Neo','Malgun Gothic',sans-serif;\">"
        "<div id='naver-post-container'>"
        + author + body_html + prompt_box +
        "</div></body></html>"
    )


def main() -> None:
    pub_title = "겨울 자외선은 약하다는 착각, 기미와 손등 트임은 이렇게 시작됩니다"
    clin_title = "한랭기 광노출과 말초 피부 손상: 자외선 방어, 구순 건조, 동창과 손습진의 감별"

    pub_md = (DAY / "post.md").read_text(encoding="utf-8")
    clin_md = (DAY / "clinical" / "clinical_column.md").read_text(encoding="utf-8")
    keep = []
    for ln in clin_md.split("\n"):
        if ln.startswith(("저자:", "발행처:", "기획 분류:")):
            continue
        keep.append(ln)
    clin_md = "\n".join(keep)
    clin_meta = [
        "<b>발행처</b>: 닥터 K 임상 의학 리뷰 (Doctor K Clinical Review Series)",
        "<b>기획 분류</b>: 의학/건강 (겨울철 피부관리·호흡기질환 7일 기획 7일 차)",
        ("<b>참고 문헌</b>: Tintinalli's Emergency Medicine: A Comprehensive Study Guide (9th ed.), "
         "Chapter 208 Cold Injuries; Chapter 209 Hypothermia; AAD 갈라진 입술 관리; DermNet Chilblains; "
         "Mayo Clinic Chilblains; NHS Contact dermatitis·Hand eczema; 질병관리청 국가건강정보포털 일광화상; "
         "기상청 생활기상지수; 식품의약품안전처 자외선차단제 안내; 국내 위키 kst104/wikiwi"),
    ]

    pub_body = convert(pub_md)
    clin_body = convert(clin_md)

    # 임상 칼럼 말미 면책 문구는 본문의 마지막 문단으로 이미 포함된다.
    pub_html = page(
        pub_title, pub_body,
        "이번 주 야외 활동 전에 얼굴과 손등에 바를 자외선 차단제와 립밤을, 챙길 물건 목록으로 정리해 볼까요?",
        "겨울에는 손 씻는 일이 늘고 난방으로 실내가 건조해져 얼굴과 손등이 트기 쉽습니다. 씻은 뒤 물기가 남아 있을 때 "
        "얇게 펴 바르기 좋은 보습 크림입니다.",
    )
    clin_html = page(
        clin_title, clin_body,
        "한랭 노출 뒤 생긴 손발 피부 병변을 동창·손습진·동상으로 나눠 감별하는 체크리스트를 표로 만들어 줘.",
        "한랭기 진료에서는 손 위생과 습윤 작업이 겹칩니다. 손 씻기 뒤 장벽 회복을 돕는 보습제를 함께 안내할 수 있습니다.",
        meta=clin_meta,
    )

    out = DAY / "publish"
    out.mkdir(exist_ok=True)
    (out / "pub.html").write_text(pub_html, encoding="utf-8")
    (out / "clin.html").write_text(clin_html, encoding="utf-8")
    for name in ("pub.html", "clin.html"):
        text = (out / name).read_text(encoding="utf-8")
        plain = re.sub(r"<[^>]+>", "", text)
        print(name, len(text), "chars |", "## 잔존:", plain.count("##"), "| ** 잔존:", plain.count("**"),
              "| 표:", text.count("<table"), "| 이미지:", text.count("<img"))


if __name__ == "__main__":
    main()
