#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Day 12 탭을 듀얼 뷰어 위젯에 반영한다. 여러 번 실행해도 같은 결과가 나오도록 작성했다."""
import re
from pathlib import Path

content_dir = Path("work/content-automation-engine/content/2026-11-19-01")
pub_html = (content_dir / "naver_post.html").read_text(encoding="utf-8")
clin_html = (content_dir / "clinical" / "clinical_column.html").read_text(encoding="utf-8")

pub_clean = pub_html.replace("`", "\\`").replace("${", "\\${")
clin_clean = clin_html.replace("`", "\\`").replace("${", "\\${")

widget_file = Path("widgets/dual-content-viewer/bundle/index.html")
widget_html = widget_file.read_text(encoding="utf-8")

# 1. Day 선택 버튼 (Day 12 추가, Day 12 활성)
new_btn = '''<div class="day-selector">
        <button class="day-btn" id="dbtn-1" onclick="switchDay(1)">Day 1 (혈압)</button>
        <button class="day-btn" id="dbtn-2" onclick="switchDay(2)">Day 2 (당뇨)</button>
        <button class="day-btn" id="dbtn-3" onclick="switchDay(3)">Day 3 (낙상)</button>
        <button class="day-btn" id="dbtn-4" onclick="switchDay(4)">Day 4 (심근경색)</button>
        <button class="day-btn" id="dbtn-5" onclick="switchDay(5)">Day 5 (저온화상)</button>
        <button class="day-btn" id="dbtn-6" onclick="switchDay(6)">Day 6 (독감감별)</button>
        <button class="day-btn" id="dbtn-7" onclick="switchDay(7)">Day 7 (안구건조)</button>
        <button class="day-btn" id="dbtn-10" onclick="switchDay(10)">Day 10 (음주저체온)</button>
        <button class="day-btn" id="dbtn-11" onclick="switchDay(11)">Day 11 (관절온찜질)</button>
        <button class="day-btn active" id="dbtn-12" onclick="switchDay(12)">Day 12 (찬공기 호흡기)</button>
      </div>'''

widget_html = re.sub(r'<div class="day-selector">.*?</div>', new_btn, widget_html, flags=re.DOTALL, count=1)

# 2. data[12] 추가 또는 갱신
data12 = "      12: {\n        pub: `" + pub_clean + "`,\n        clin: `" + clin_clean + "`\n      }"
anchor = "\n      }\n    };\n\n    let currentDay"
assert anchor in widget_html, "data anchor missing"
start = widget_html.find("\n      12: {")
if start != -1:
    end = widget_html.find(anchor, start)
    assert end != -1, "data12 end anchor missing"
    widget_html = widget_html[:start] + "\n" + data12 + widget_html[end:]
else:
    widget_html = widget_html.replace(
        anchor,
        "\n      },\n" + data12 + "\n    };\n\n    let currentDay",
        1,
    )

# 3. currentDay = 12
widget_html = re.sub(r'let currentDay = \d+;', 'let currentDay = 12;', widget_html)

# 4. switchDay에 b12 처리 (없을 때만 추가)
if "dbtn-12" not in widget_html.split("function switchDay")[-1]:
    old_switch = """      const b11 = document.getElementById('dbtn-11');
      if (b11) b11.className = d === 11 ? 'day-btn active' : 'day-btn';"""
    new_switch = old_switch + """
      const b12 = document.getElementById('dbtn-12');
      if (b12) b12.className = d === 12 ? 'day-btn active' : 'day-btn';"""
    assert old_switch in widget_html
    widget_html = widget_html.replace(old_switch, new_switch, 1)

# 5. 초기 표시 본문을 Day 12으로 교체
p_start = widget_html.find('<div class="body-scroll" id="body-public">')
p_end = widget_html.find('</div>\n    </div>\n\n    <!-- 전문가용 카드 -->', p_start)
assert p_start != -1 and p_end != -1, "public body anchor missing"
widget_html = widget_html[:p_start] + '<div class="body-scroll" id="body-public">' + pub_html + widget_html[p_end:]

c_start = widget_html.find('<div class="body-scroll" id="body-clinical">')
c_end = widget_html.find('</div>\n    </div>\n  </div>\n\n  <script>', c_start)
assert c_start != -1 and c_end != -1, "clinical body anchor missing"
widget_html = widget_html[:c_start] + '<div class="body-scroll" id="body-clinical">' + clin_html + widget_html[c_end:]

widget_file.write_text(widget_html, encoding="utf-8")
print("✅ 위젯 index.html Day 12 반영 완료")
print("   size:", len(widget_html))
print("   dbtn-12:", widget_html.count("dbtn-12"), "| data 12:", "\n      12: {" in widget_html)
