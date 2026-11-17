# -*- coding: utf-8 -*-
"""
마크다운 표(| ... |)를 HTML <table>로 변환하는 공용 헬퍼.
네이버 스마트에디터용(인라인 스타일), 임상 칼럼용(클래스), 듀얼 뷰어용(기본) 렌더러를 제공한다.
"""

import re

SEP_RE = re.compile(r'^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?$')


def _split_row(line: str):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def replace_markdown_tables(text: str, render):
    """표 블록을 render(headers, rows) 결과로 치환한다. (변환 텍스트, 표 개수) 반환."""
    lines = text.split("\n")
    out = []
    i = 0
    count = 0
    while i < len(lines):
        cur = lines[i].strip()
        if cur.startswith("|") and i + 1 < len(lines) and SEP_RE.match(lines[i + 1].strip()):
            headers = _split_row(cur)
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(_split_row(lines[j].strip()))
                j += 1
            out.append(render(headers, rows))
            count += 1
            i = j
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out), count


def _naver_inline(text: str) -> str:
    text = re.sub(r'\*\*(.*?)\*\*', r'<b style="color: #0f172a;">\1</b>', text)
    text = re.sub(
        r'\[(.*?)\]\((.*?)\)',
        r'<a href="\2" style="color: #2563eb; text-decoration: underline;" target="_blank">\1</a>',
        text,
    )
    return text


def naver_table(headers, rows) -> str:
    th_style = ("border: 1px solid #cbd5e1; background: #eff6ff; padding: 10px 12px; "
                "font-weight: bold; color: #1e3a8a; font-size: 15px; text-align: left;")
    td_style = ("border: 1px solid #e2e8f0; padding: 10px 12px; color: #334155; "
                "font-size: 15px; line-height: 1.6; vertical-align: top;")
    html = ["<table style='border-collapse: collapse; width: 100%; margin: 18px 0;'>", "<thead><tr>"]
    for h in headers:
        html.append(f"<th style='{th_style}'>{_naver_inline(h)}</th>")
    html.append("</tr></thead><tbody>")
    for r in rows:
        html.append("<tr>")
        for c in r:
            html.append(f"<td style='{td_style}'>{_naver_inline(c)}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")
    return "".join(html)


def clinical_table(headers, rows) -> str:
    html = ["<table class=\"journal-table\">", "<thead><tr>"]
    for h in headers:
        html.append(f"<th>{h}</th>")
    html.append("</tr></thead><tbody>")
    for r in rows:
        html.append("<tr>")
        for c in r:
            html.append(f"<td>{c}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")
    return "".join(html)


def simple_table(headers, rows) -> str:
    style = "border-collapse: collapse; width: 100%; margin: 14px 0; font-size: 14px;"
    cell = "border: 1px solid #cbd5e1; padding: 8px 10px; vertical-align: top;"
    head = "border: 1px solid #cbd5e1; padding: 8px 10px; background: #eef2ff; font-weight: 700;"
    html = [f"<table style='{style}'><thead><tr>"]
    for h in headers:
        html.append(f"<th style='{head}'>{h}</th>")
    html.append("</tr></thead><tbody>")
    for r in rows:
        html.append("<tr>")
        for c in r:
            html.append(f"<td style='{cell}'>{c}</td>")
        html.append("</tr>")
    html.append("</tbody></table>")
    return "".join(html)
