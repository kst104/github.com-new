#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Day 10 탭을 듀얼 뷰어 위젯에 반영한다. 여러 번 실행해도 같은 결과가 나오도록 작성했다."""
import re
from pathlib import Path

content_dir = Path("work/content-automation-engine/content/2026-11-17-01")
pub_html = (content_dir / "naver_post.html").read_text(encoding="utf-8")
clin_html = (content_dir / "clinical" / "clinical_column.html").read_text(encoding="utf-8")

pub_clean = pub_html.replace("`", "\\`").replace("${", "\\${")
clin_clean = clin_html.replace("`", "\\`").replace("${", "\\${")

widget_file = Path("widgets/dual-content-viewer/bundle/index.html")
widget_html = widget_file.read_text(encoding="utf-8")

# 1. Day 선택 버튼 (Day 10 추가, Day 10 활성)
new_btn = '''<div class="day-selector">
        <button class="day-btn" id="dbtn-1" onclick="switchDay(1)">Day 1 (혈압)</button>
        <button class="day-btn" id="dbtn-2" onclick="switchDay(2)">Day 2 (당뇨)</button>
        <button class="day-btn" id="dbtn-3" onclick="switchDay(3)">Day 3 (낙상)</button>
        <button class="day-btn" id="dbtn-4" onclick="switchDay(4)">Day 4 (심근경색)</button>
        <button class="day-btn" id="dbtn-5" onclick="switchDay(5)">Day 5 (저온화상)</button>
        <button class="day-btn" id="dbtn-6" onclick="switchDay(6)">Day 6 (독감감별)</button>
        <button class="day-btn" id="dbtn-7" onclick="switchDay(7)">Day 7 (안구건조)</button>
        <button class="day-btn active" id="dbtn-10" onclick="switchDay(10)">Day 10 (음주저체온)</button>
      </div>'''

widget_html = re.sub(r'<div class="day-selector">.*?</div>', new_btn, widget_html, flags=re.DOTALL, count=1)

# 2. data[10] 추가 또는 갱신
data10 = "      10: {\n        pub: `" + pub_clean + "`,\n        clin: `" + clin_clean + "`\n      }"
start = widget_html.find("\n      10: {")
if start != -1:
    end = widget_html.find("\n      }\n    };\n\n    let currentDay", start)
    assert end != -1, "data10 end anchor missing"
    widget_html = widget_html[:start] + "\n" + data10 + widget_html[end:]
else:
    anchor = "\n      }\n    };\n\n    let currentDay"
    assert anchor in widget_html, "data anchor missing"
    widget_html = widget_html.replace(
        anchor,
        "\n      },\n" + data10 + "\n    };\n\n    let currentDay",
        1,
    )

# 3. currentDay = 10
widget_html = re.sub(r'let currentDay = \d+;', 'let currentDay = 10;', widget_html)

# 4. switchDay에 b10 처리 (없을 때만 추가)
if "dbtn-10" not in widget_html.split("function switchDay")[-1]:
    old_switch = """      const b7 = document.getElementById('dbtn-7');
      if (b7) b7.className = d === 7 ? 'day-btn active' : 'day-btn';"""
    new_switch = old_switch + """
      const b10 = document.getElementById('dbtn-10');
      if (b10) b10.className = d === 10 ? 'day-btn active' : 'day-btn';"""
    assert old_switch in widget_html
    widget_html = widget_html.replace(old_switch, new_switch, 1)

# 5. 초기 표시 본문을 Day 10으로 교체
p_start = widget_html.find('<div class="body-scroll" id="body-public">')
p_end = widget_html.find('</div>\n    </div>\n\n    <!-- 전문가용 카드 -->', p_start)
assert p_start != -1 and p_end != -1, "public body anchor missing"
widget_html = widget_html[:p_start] + '<div class="body-scroll" id="body-public">' + pub_html + widget_html[p_end:]

c_start = widget_html.find('<div class="body-scroll" id="body-clinical">')
c_end = widget_html.find('</div>\n    </div>\n  </div>\n\n  <script>', c_start)
assert c_start != -1 and c_end != -1, "clinical body anchor missing"
widget_html = widget_html[:c_start] + '<div class="body-scroll" id="body-clinical">' + clin_html + widget_html[c_end:]

widget_file.write_text(widget_html, encoding="utf-8")
print("✅ 위젯 index.html Day 10 반영 완료")
print("   size:", len(widget_html))
print("   dbtn-10:", widget_html.count("dbtn-10"), "| data 10:", "\n      10: {" in widget_html)
