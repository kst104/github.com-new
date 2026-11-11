#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from pathlib import Path

content_dir = Path("work/content-automation-engine/content/2026-11-12-01")
pub_html = (content_dir / "naver_post.html").read_text(encoding="utf-8")
clin_html = (content_dir / "clinical" / "clinical_column.html").read_text(encoding="utf-8")

# Escape backticks in html
pub_clean = pub_html.replace("`", "\\`").replace("${", "\\${")
clin_clean = clin_html.replace("`", "\\`").replace("${", "\\${")

widget_file = Path("widgets/dual-content-viewer/bundle/index.html")
widget_html = widget_file.read_text(encoding="utf-8")

# 1. Update day-selector buttons
old_btn = '''<div class="day-selector">
        <button class="day-btn" id="dbtn-1" onclick="switchDay(1)">Day 1 (혈압)</button>
        <button class="day-btn active" id="dbtn-2" onclick="switchDay(2)">Day 2 (당뇨)</button>
      </div>'''

new_btn = '''<div class="day-selector">
        <button class="day-btn" id="dbtn-1" onclick="switchDay(1)">Day 1 (혈압)</button>
        <button class="day-btn" id="dbtn-2" onclick="switchDay(2)">Day 2 (당뇨)</button>
        <button class="day-btn" id="dbtn-3" onclick="switchDay(3)">Day 3 (낙상)</button>
        <button class="day-btn" id="dbtn-4" onclick="switchDay(4)">Day 4 (심근경색)</button>
        <button class="day-btn active" id="dbtn-5" onclick="switchDay(5)">Day 5 (저온화상)</button>
      </div>'''

if old_btn in widget_html:
    widget_html = widget_html.replace(old_btn, new_btn)
else:
    # Pattern replace if dbtn-3,4 were already there
    widget_html = re.sub(
        r'<div class="day-selector">.*?</div>',
        new_btn,
        widget_html,
        flags=re.DOTALL
    )

# 2. Add data[5] using string find/replace instead of re.sub to avoid escape issues
target_str = "\n    };\n\n    let currentDay"
if target_str in widget_html:
    widget_html = widget_html.replace(target_str, f",\n      5: {{\n        pub: `{pub_clean}`,\n        clin: `{clin_clean}`\n      }}\n    }};\n\n    let currentDay")
else:
    # fallback find
    idx = widget_html.find("let currentDay")
    last_brace = widget_html.rfind("};", 0, idx)
    widget_html = widget_html[:last_brace] + f",\n      5: {{\n        pub: `{pub_clean}`,\n        clin: `{clin_clean}`\n      }}\n    }};" + widget_html[last_brace+2:]

# 3. Update currentDay = 5
widget_html = re.sub(r'let currentDay = \d+;', 'let currentDay = 5;', widget_html)

# 4. Update switchDay(d)
old_switch = '''    function switchDay(d) {
      currentDay = d;
      document.getElementById('dbtn-1').className = d === 1 ? 'day-btn active' : 'day-btn';
      document.getElementById('dbtn-2').className = d === 2 ? 'day-btn active' : 'day-btn';
      const b3 = document.getElementById('dbtn-3');
      if (b3) b3.className = d === 3 ? 'day-btn active' : 'day-btn';
      const b4 = document.getElementById('dbtn-4');
      if (b4) b4.className = d === 4 ? 'day-btn active' : 'day-btn';'''

new_switch = '''    function switchDay(d) {
      currentDay = d;
      document.getElementById('dbtn-1').className = d === 1 ? 'day-btn active' : 'day-btn';
      document.getElementById('dbtn-2').className = d === 2 ? 'day-btn active' : 'day-btn';
      const b3 = document.getElementById('dbtn-3');
      if (b3) b3.className = d === 3 ? 'day-btn active' : 'day-btn';
      const b4 = document.getElementById('dbtn-4');
      if (b4) b4.className = d === 4 ? 'day-btn active' : 'day-btn';
      const b5 = document.getElementById('dbtn-5');
      if (b5) b5.className = d === 5 ? 'day-btn active' : 'day-btn';'''

widget_html = widget_html.replace(old_switch, new_switch)

# 5. Update initial body-public and body-clinical
p_start = widget_html.find('<div class="card-body" id="body-public">')
p_end = widget_html.find('</div>\n    </div>\n\n    <!-- 전문가용 카드 -->', p_start)
if p_start != -1 and p_end != -1:
    widget_html = widget_html[:p_start] + f'<div class="card-body" id="body-public">{pub_html}' + widget_html[p_end:]

c_start = widget_html.find('<div class="card-body" id="body-clinical">')
c_end = widget_html.find('</div>\n    </div>\n  </div>\n\n  <script>', c_start)
if c_start != -1 and c_end != -1:
    widget_html = widget_html[:c_start] + f'<div class="card-body" id="body-clinical">{clin_html}' + widget_html[c_end:]

widget_file.write_text(widget_html, encoding="utf-8")
print("✅ Widget index.html updated successfully with Day 5!")
