#!/usr/bin/env python3
"""
Dual Content Pipeline Runner
Simultaneously generates:
1. Public Edition (Blog, Reels, Shorts, Ad copies, Instagram assets)
2. Professional Edition (Clinical In-Depth Column referencing Dr. K's Wiki)
And builds a responsive Side-by-Side Dual Viewer.
"""

import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from engine.clinical_engine import generate_day1_clinical_column, markdown_to_clinical_html


def build_dual_view_html(content_dir: Path):
    """Builds an interactive side-by-side / toggle dual viewer HTML."""
    post_md = (content_dir / "post.md").read_text(encoding="utf-8") if (content_dir / "post.md").exists() else ""
    clinical_md = (content_dir / "clinical" / "clinical_column.md").read_text(encoding="utf-8") if (content_dir / "clinical" / "clinical_column.md").exists() else ""
    
    # Quick HTML conversion for previewing
    def simple_render(text):
        lines = []
        in_p = False
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                if in_p:
                    lines.append("</p>")
                    in_p = False
                continue
            if line.startswith("# "):
                lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("## "):
                lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("### "):
                lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith("- "):
                lines.append(f"<li>{line[2:]}</li>")
            elif line.startswith("> "):
                lines.append(f"<blockquote>{line[2:]}</blockquote>")
            elif line.startswith("|"):
                lines.append(f"<code>{line}</code><br>")
            else:
                if not in_p:
                    lines.append("<p>")
                    in_p = True
                lines.append(line + "<br>")
        if in_p:
            lines.append("</p>")
        return "\n".join(lines)

    public_html = simple_render(post_md)
    clinical_html = simple_render(clinical_md)

    dual_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>닥터 K 콘텐츠 이원화 듀얼 뷰어 (대중용 vs 전문가용)</title>
  <style>
    :root {{
      --primary: #2563eb;
      --clinical: #0f766e;
      --bg: #f1f5f9;
      --card-bg: #ffffff;
      --text: #0f172a;
      --border: #cbd5e1;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Nanum Gothic", sans-serif;
      margin: 0;
      padding: 0;
      background: var(--bg);
      color: var(--text);
    }}
    header {{
      background: #0f172a;
      color: white;
      padding: 16px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }}
    header h1 {{
      font-size: 18px;
      margin: 0;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .toggle-bar {{
      display: flex;
      gap: 8px;
    }}
    .tab-btn {{
      background: #1e293b;
      border: 1px solid #334155;
      color: #94a3b8;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .tab-btn.active {{
      background: var(--primary);
      color: white;
      border-color: var(--primary);
    }}
    .tab-btn.clinical-active {{
      background: var(--clinical);
      color: white;
      border-color: var(--clinical);
    }}
    .main-wrapper {{
      display: flex;
      max-width: 1600px;
      margin: 20px auto;
      gap: 20px;
      padding: 0 20px;
    }}
    .column {{
      flex: 1;
      background: var(--card-bg);
      border-radius: 12px;
      padding: 30px;
      border: 1px solid var(--border);
      box-shadow: 0 4px 15px rgba(0,0,0,0.05);
      min-width: 0;
    }}
    .column-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 2px solid #e2e8f0;
      padding-bottom: 14px;
      margin-bottom: 20px;
    }}
    .column-header.public {{ border-bottom-color: var(--primary); }}
    .column-header.clinical {{ border-bottom-color: var(--clinical); }}
    .col-title {{
      font-size: 20px;
      font-weight: 800;
      margin: 0;
    }}
    .col-title.public {{ color: var(--primary); }}
    .col-title.clinical {{ color: var(--clinical); }}
    .badge {{
      font-size: 12px;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 12px;
    }}
    .badge-public {{ background: #eff6ff; color: #1d4ed8; }}
    .badge-clinical {{ background: #f0fdf4; color: #15803d; }}
    .content-body {{
      font-size: 15px;
      line-height: 1.8;
      word-break: break-all;
    }}
    .content-body h1 {{ font-size: 22px; color: #1e293b; margin-top: 24px; }}
    .content-body h2 {{ font-size: 18px; color: #334155; margin-top: 20px; }}
    .content-body h3 {{ font-size: 16px; color: #475569; margin-top: 16px; }}
    .content-body blockquote {{
      background: #f8fafc;
      border-left: 4px solid var(--primary);
      padding: 10px 16px;
      margin: 16px 0;
      font-size: 13px;
    }}
    .clinical .content-body blockquote {{
      border-left-color: var(--clinical);
    }}
    @media (max-width: 1024px) {{
      .main-wrapper {{ flex-direction: column; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>🩺 닥터 K 임상·대중 이원화 콘텐츠 허브 (Day 1)</h1>
    <div class="toggle-bar">
      <button class="tab-btn active" onclick="setView('both')">나란히 비교 (Dual)</button>
      <button class="tab-btn" onclick="setView('public')">대중용만 보기</button>
      <button class="tab-btn" onclick="setView('clinical')">전문가용만 보기</button>
    </div>
  </header>

  <div class="main-wrapper" id="wrapper">
    <!-- 대중용 칼럼 & 쇼츠 영역 -->
    <section class="column public" id="col-public">
      <div class="column-header public">
        <h2 class="col-title public">📱 대중용 에디션 (General Public)</h2>
        <span class="badge badge-public">블로그 · 릴스 · 쇼츠 · 광고 10종</span>
      </div>
      <div class="content-body">
        <div style="background: #f0f9ff; border: 1px solid #bae6fd; padding: 14px; border-radius: 8px; margin-bottom: 20px;">
          <strong>🎬 제작 완료 숏폼 영상</strong>: <a href="Day1_겨울철_혈압_주의보_겅태_쇼츠_데모_v2.mp4" target="_blank">Day 1 겅태 쇼츠 데모 v2 (MP4) 재생</a><br>
          <strong>📋 핵심 타깃</strong>: 4050 직장인, 고혈압 환자 및 가족 보호자<br>
          <strong>💡 강조 포인트</strong>: 3분 기상 공식, 생활 속 금기 사항, 쉬운 비유
        </div>
        {public_html}
      </div>
    </section>

    <!-- 전문가용 임상 심층 칼럼 영역 -->
    <section class="column clinical" id="col-clinical">
      <div class="column-header clinical">
        <h2 class="col-title clinical">🩺 전문가용 에디션 (Clinical In-Depth)</h2>
        <span class="badge badge-clinical">Dr. K's Wiki · Tintinalli · 응급 프로토콜</span>
      </div>
      <div class="content-body">
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 14px; border-radius: 8px; margin-bottom: 20px;">
          <strong>🏛️ 연동 지식베이스</strong>: <code>kst104/wikiwi</code> (닥터 K 의학 위키, ACS & 대동맥 박리 프로토콜)<br>
          <strong>📋 핵심 타깃</strong>: 의사, 응급실 의료진, 임상 연구자, 의학 전문 독자<br>
          <strong>🔬 강조 포인트</strong>: SVR & 카테콜아민 분비 기전, DAPT 로딩, Nicardipine/Labetalol 감압 프로토콜
        </div>
        {clinical_html}
      </div>
    </section>
  </div>

  <script>
    function setView(mode) {{
      const p = document.getElementById('col-public');
      const c = document.getElementById('col-clinical');
      const btns = document.querySelectorAll('.tab-btn');
      btns.forEach(b => b.classList.remove('active', 'clinical-active'));

      if (mode === 'both') {{
        p.style.display = 'block';
        c.style.display = 'block';
        btns[0].classList.add('active');
      }} else if (mode === 'public') {{
        p.style.display = 'block';
        c.style.display = 'none';
        btns[1].classList.add('active');
      }} else if (mode === 'clinical') {{
        p.style.display = 'none';
        c.style.display = 'block';
        btns[2].classList.add('clinical-active');
      }}
    }}
  </script>
</body>
</html>
"""
    return dual_html


def run_dual_pipeline():
    content_dir = BASE_DIR / "content" / "2026-11-09-05"
    print("[Dual Pipeline] Running dual simultaneous generation for Day 1...")
    
    # 1. Ensure clinical column exists
    from engine.clinical_engine import generate_day1_clinical_column, markdown_to_clinical_html
    clin_dir = content_dir / "clinical"
    clin_dir.mkdir(parents=True, exist_ok=True)
    clin_md = generate_day1_clinical_column()
    (clin_dir / "clinical_column.md").write_text(clin_md, encoding="utf-8")
    (clin_dir / "clinical_column.html").write_text(markdown_to_clinical_html(clin_md), encoding="utf-8")
    
    # 2. Build Dual View HTML
    dual_html = build_dual_view_html(content_dir)
    (content_dir / "dual_view.html").write_text(dual_html, encoding="utf-8")
    
    # Copy to downloads for user chat attachment
    downloads_path = Path("/workspace/downloads/Day1_콘텐츠_이원화_듀얼뷰어.html")
    downloads_path.write_text(dual_html, encoding="utf-8")
    
    # 3. Create DUAL_VIEW.md summary in content dir
    dual_md = f"""# 🩺 Day 1 콘텐츠 이원화 허브 (대중용 vs 전문가용)

> **주제**: 겨울철 한파와 혈압 급상승 주의보: 아침 기상 시 뇌졸중·심근경색 예방법
> **이원화 구성**:
> 1. [대중용 에디션 (블로그·쇼츠·릴스)](post.md)
> 2. [전문가용 에디션 (임상 심층 칼럼)](clinical/clinical_column.md)
> 3. [인터랙티브 웹 듀얼 뷰어](dual_view.html)

---

## 📊 에디션별 사양 비교표

| 항목 | 📱 대중용 에디션 (General Public) | 🩺 전문가용 에디션 (Clinical / Expert) |
| :--- | :--- | :--- |
| **타깃 독자** | 4050 직장인, 고혈압 환자, 가족 보호자 | 의료진, 임상 연구자, 고관여 심혈관 환자 |
| **분량 및 형식** | 약 2,000자 / 친절한 구어체 및 생활 비유 | 약 4,200자 (8,300자) / 학술 저널 리뷰 포맷 |
| **참조 지식원** | 일상 응급실 경험담, 생활 수칙 | **Dr. K's Wiki (`kst104/wikiwi`)**, Tintinalli, AHA/ESC |
| **핵심 내용** | 이불 속 3분 기상 공식, 새벽 조깅 금지 | SVR & 카테콜아민 기전, DAPT 로딩, Nicardipine 감압 |
| **동반 제작 에셋** | 네이버 HTML, 인스타 카드뉴스, 쇼츠 영상 v2, 광고 10종 | 고밀도 의학 학술 HTML, 진단 플로우차트, 참고문헌 |
"""
    (content_dir / "DUAL_VIEW.md").write_text(dual_md, encoding="utf-8")
    print(f"✅ Dual view HTML built: {downloads_path}")


if __name__ == "__main__":
    run_dual_pipeline()
