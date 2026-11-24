#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""듀얼 뷰어 위젯에 회차를 추가·갱신한다(JSON 데이터 방식).

2026-11-24 위젯 수정 이후 `widgets/dual-content-viewer/bundle/index.html` 의
데이터는 템플릿 리터럴이 아니라 `<script type="application/json" id="day-data">`
안의 JSON 이다. 이 스크립트는 그 JSON 을 직접 다루므로 백틱·따옴표 이스케이프
문제가 생기지 않는다. 여러 번 실행해도 같은 결과가 나온다.

사용 예:
    python3 update_widget_json.py --day 18 \
        --content-dir work/content-automation-engine/content/2026-11-25-01 \
        --label "동상"
    python3 update_widget_json.py --day 18 --no-activate
    python3 update_widget_json.py --check          # 검증만
"""
import argparse
import json
import re
import sys
from pathlib import Path

WIDGET = Path("widgets/dual-content-viewer/bundle/index.html")
JSON_RE = re.compile(r'(<script type="application/json" id="day-data">)(.*?)(</script>)', re.S)
BTN_RE = re.compile(r'<button class="day-btn( active)?" id="dbtn-(\d+)" data-day="(\d+)" onclick="switchDay\((\d+)\)">Day (\d+) \(([^)]*)\)</button>')


def load(widget_path):
    html = widget_path.read_text(encoding="utf-8")
    m = JSON_RE.search(html)
    if not m:
        raise SystemExit("day-data JSON 블록을 찾지 못했습니다. 위젯 구조를 먼저 확인하세요.")
    return html, m, json.loads(m.group(2))


def dump(data):
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    if "</script" in payload.lower():
        raise SystemExit("페이로드에 </script 문자열이 남아 있습니다.")
    return payload


def labels_from_buttons(html):
    labels = {}
    for m in BTN_RE.finditer(html):
        labels[int(m.group(2))] = m.group(6)
    return labels


def build_buttons(labels, active_day):
    lines = ['      <div class="day-selector">']
    for d in sorted(labels):
        active = " active" if d == active_day else ""
        lines.append(
            f'        <button class="day-btn{active}" id="dbtn-{d}" data-day="{d}" '
            f'onclick="switchDay({d})">Day {d} ({labels[d]})</button>'
        )
    lines.append("      </div>")
    return "\n".join(lines)


def replace_buttons(html, labels, active_day):
    start = html.index('<div class="day-selector">')
    sel_open = html.rindex("\n", 0, start) + 1          # 줄 시작
    sel_close = html.index("\n      </div>", start) + len("\n      </div>")
    return html[:sel_open] + build_buttons(labels, active_day) + html[sel_close:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", type=int, help="추가·갱신할 회차 번호")
    ap.add_argument("--content-dir", help="naver_post.html 과 clinical/clinical_column.html 이 있는 폴더")
    ap.add_argument("--label", default=None, help="탭에 표시할 짧은 이름 (예: 동상)")
    ap.add_argument("--pub", help="대중용 HTML 파일 경로 (--content-dir 대신)")
    ap.add_argument("--clin", help="임상 칼럼 HTML 파일 경로 (--content-dir 대신)")
    ap.add_argument("--no-activate", action="store_true", help="기본 활성 회차를 바꾸지 않는다")
    ap.add_argument("--check", action="store_true", help="검증만 하고 쓰지 않는다")
    ap.add_argument("--widget", default=str(WIDGET))
    args = ap.parse_args()

    widget_path = Path(args.widget)
    html, m, data = load(widget_path)
    labels = labels_from_buttons(html)

    if args.check:
        days = sorted(int(k) for k in data)
        ok = days == list(range(1, max(days) + 1))
        print(f"회차: {days}")
        print(f"버튼 수: {len(labels)}  데이터 수: {len(data)}")
        print(f"연속 여부: {'OK' if ok else '불연속'}")
        print("JSON: OK")
        return 0 if ok else 1

    if args.day is None:
        raise SystemExit("--day 가 필요합니다.")

    if args.content_dir:
        base = Path(args.content_dir)
        pub_path = base / "naver_post.html"
        clin_path = base / "clinical" / "clinical_column.html"
    else:
        pub_path, clin_path = Path(args.pub or ""), Path(args.clin or "")

    if not pub_path.is_file() or not clin_path.is_file():
        raise SystemExit(f"원고 파일이 없습니다: {pub_path} / {clin_path}")

    data[str(args.day)] = {
        "pub": pub_path.read_text(encoding="utf-8"),
        "clin": clin_path.read_text(encoding="utf-8"),
    }
    labels[args.day] = args.label or labels.get(args.day, f"Day {args.day}")

    active_day = args.day
    if args.no_activate:
        prev = [int(x.group(2)) for x in BTN_RE.finditer(html) if x.group(1)]
        active_day = prev[0] if prev else max(labels)

    new_html = replace_buttons(html, labels, active_day)
    new_html = JSON_RE.sub(lambda mm: mm.group(1) + dump(data) + mm.group(3), new_html, count=1)

    # 쓰기 전에 다시 읽어 검증
    tmp = widget_path.with_suffix(".tmp")
    tmp.write_text(new_html, encoding="utf-8")
    _, _, check = load(tmp)
    assert str(args.day) in check and check[str(args.day)]["pub"] == data[str(args.day)]["pub"]
    tmp.replace(widget_path)

    print(f"Day {args.day} 반영 완료 → {widget_path}")
    print(f"  회차: {sorted(int(k) for k in check)}")
    print(f"  기본 활성: Day {active_day}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
