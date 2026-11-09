# -*- coding: utf-8 -*-
"""
네이버 스마트에디터 ONE 호환 HTML 변환기
마크다운 서식을 네이버 블로그 에디터에 그대로 복사·붙여넣기할 수 있는 고품질 인라인 스타일 HTML로 변환합니다.
"""

import re
import html

def markdown_to_naver_html(md_text: str) -> str:
    lines = md_text.split("\n")
    html_lines = []
    
    in_blockquote = False
    in_list = False
    
    for line in lines:
        line_stripped = line.strip()
        
        # 빈 줄
        if not line_stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if in_blockquote:
                html_lines.append("</div>")
                in_blockquote = False
            html_lines.append("<p style='line-height: 1.8; margin-bottom: 15px;'>&nbsp;</p>")
            continue
            
        # 구분선
        if line_stripped in ("---", "***", "___"):
            html_lines.append("<hr style='border: 0; height: 1px; background: #e2e8f0; margin: 30px 0;' />")
            continue
            
        # H1
        if line_stripped.startswith("# "):
            title_text = line_stripped[2:].strip()
            html_lines.append(f"<h1 style='font-size: 26px; font-weight: bold; color: #111827; line-height: 1.4; margin-top: 30px; margin-bottom: 15px;'>{title_text}</h1>")
            continue
            
        # H2
        if line_stripped.startswith("## "):
            h2_text = line_stripped[3:].strip()
            html_lines.append(f"<h2 style='font-size: 20px; font-weight: bold; color: #1e3a8a; border-left: 4px solid #3b82f6; padding-left: 12px; margin-top: 35px; margin-bottom: 15px;'>{h2_text}</h2>")
            continue
            
        # H3
        if line_stripped.startswith("### "):
            h3_text = line_stripped[4:].strip()
            html_lines.append(f"<h3 style='font-size: 17px; font-weight: bold; color: #1f2937; margin-top: 25px; margin-bottom: 10px;'>{h3_text}</h3>")
            continue
            
        # 인용구 (Blockquote)
        if line_stripped.startswith("> "):
            quote_text = line_stripped[2:].strip()
            if not in_blockquote:
                html_lines.append("<div style='background: #f8fafc; border-left: 4px solid #64748b; padding: 14px 18px; margin: 20px 0; border-radius: 4px; color: #334155; font-size: 15px; line-height: 1.7;'>")
                in_blockquote = True
            # 볼드 처리
            quote_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', quote_text)
            html_lines.append(f"<p style='margin: 0;'>{quote_text}</p>")
            continue
        else:
            if in_blockquote:
                html_lines.append("</div>")
                in_blockquote = False
                
        # 리스트 아이템
        if line_stripped.startswith("- ") or line_stripped.startswith("* "):
            item_text = line_stripped[2:].strip()
            if not in_list:
                html_lines.append("<ul style='padding-left: 20px; margin: 15px 0; line-height: 1.8;'>")
                in_list = True
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', item_text)
            html_lines.append(f"<li style='margin-bottom: 8px; font-size: 16px; color: #374151;'>{item_text}</li>")
            continue
        elif re.match(r'^\d+\.\s', line_stripped):
            # 숫자 리스트
            item_text = re.sub(r'^\d+\.\s', '', line_stripped).strip()
            item_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', item_text)
            html_lines.append(f"<p style='margin-left: 10px; margin-bottom: 8px; font-size: 16px; color: #374151; line-height: 1.7;'>• {item_text}</p>")
            continue
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
                
        # 일반 본문 문단
        p_text = line_stripped
        p_text = re.sub(r'\*\*(.*?)\*\*', r'<b style="color: #0f172a;">\1</b>', p_text)
        p_text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="color: #2563eb; text-decoration: underline;" target="_blank">\1</a>', p_text)
        html_lines.append(f"<p style='font-size: 16px; line-height: 1.8; color: #334155; margin-bottom: 12px;'>{p_text}</p>")
        
    if in_list:
        html_lines.append("</ul>")
    if in_blockquote:
        html_lines.append("</div>")
        
    body_html = "\n".join(html_lines)
    
    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>네이버 블로그 복사용 포스팅</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; max-width: 720px; margin: 40px auto; padding: 20px; background: #ffffff;">
<div id="naver-post-container">
{body_html}
</div>
</body>
</html>
"""
    return full_html
