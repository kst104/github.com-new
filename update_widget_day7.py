#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from pathlib import Path

content_dir = Path("work/content-automation-engine/content/2026-11-14-01")
pub_html = (content_dir / "naver_post.html").read_text(encoding="utf-8")
clin_html = (content_dir / "clinical" / "clinical_column.html").read_text(encoding="utf-8")

# Escape backticks in html
pub_clean = pub_html.replace("`", "\\`").replace("${", "\\${")
clin_clean = clin_html.replace("`", "\\`").replace("${", "\\${")

widget_file = Path("widgets/dual-content-viewer/bundle/index.html")
widget_html = widget_file.read_text(encoding="utf-8")

# 1. Update day-selector buttons
new_btn = '''<div class="day-selector">
        <button class="day-btn" id="dbtn-1" onclick="switchDay(1)">Day 1 (혈압)</button>
        <button class="day-btn" id="dbtn-2" onclick="switchDay(2)">Day 2 (당뇨)</button>
        <button class="day-btn" id="dbtn-3" onclick="switchDay(3)">Day 3 (낙상)</button>
        <button class="day-btn" id="dbtn-4" onclick="switchDay(4)">Day 4 (심근경색)</button>
        <button class="day-btn" id="dbtn-5" onclick="switchDay(5)">Day 5 (저온화상)</button>
        <button class="day-btn" id="dbtn-6" onclick="switchDay(6)">Day 6 (독감감별)</button>
        <button class="day-btn active" id="dbtn-7" onclick="switchDay(7)">Day 7 (안구건조)</button>
      </div>'''

widget_html = re.sub(
    r'<div class="day-selector">.*?</div>',
    new_btn,
    widget_html,
    flags=re.DOTALL
)

# 2. Add data[7]
target_str = "\n    };\n\n    let currentDay"
if target_str in widget_html:
    widget_html = widget_html.replace(target_str, f",\n      7: {{\n        pub: `{pub_clean}`,\n        clin: `{clin_clean}`\n      }}\n    }};\n\n    let currentDay")
else:
    idx = widget_html.find("let currentDay")
    last_brace = widget_html.rfind("};", 0, idx)
    widget_html = widget_html[:last_brace] + f",\n      7: {{\n        pub: `{pub_clean}`,\n        clin: `{clin_clean}`\n      }}\n    }};" + widget_html[last_brace+2:]

# 3. Update currentDay = 7
widget_html = re.sub(r'let currentDay = \d+;', 'let currentDay = 7;', widget_html)

# 4. Update switchDay(d)
old_switch = '''      const b6 = document.getElementById('dbtn-6');
      if (b6) b6.className = d === 6 ? 'day-btn active' : 'day-btn';'''

new_switch = '''      const b6 = document.getElementById('dbtn-6');
      if (b6) b6.className = d === 6 ? 'day-btn active' : 'day-btn';
      const b7 = document.getElementById('dbtn-7');
      if (b7) b7.className = d === 7 ? 'day-btn active' : 'day-btn';'''

if old_switch in widget_html:
    widget_html = widget_html.replace(old_switch, new_switch)

# 5. Update initial body-public and body-clinical
p_start = widget_html.find('<div class="body-scroll" id="body-public">')
p_end = widget_html.find('</div>\n    </div>\n\n    <!-- 전문가용 카드 -->', p_start)
if p_start != -1 and p_end != -1:
    widget_html = widget_html[:p_start] + f'<div class="body-scroll" id="body-public">{pub_html}' + widget_html[p_end:]

c_start = widget_html.find('<div class="body-scroll" id="body-clinical">')
c_end = widget_html.find('</div>\n    </div>\n  </div>\n\n  <script>', c_start)
if c_start != -1 and c_end != -1:
    widget_html = widget_html[:c_start] + f'<div class="body-scroll" id="body-clinical">{clin_html}' + widget_html[c_end:]

widget_file.write_text(widget_html, encoding="utf-8")
print("✅ Widget index.html updated successfully with Day 7!")
