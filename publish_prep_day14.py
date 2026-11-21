#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Day 14 발행용 본문 HTML 생성.
- 블로그 제목 필드와 중복되는 H1 제거
- 작성자용 헤더(카테고리·키워드·독자·GitHub) 제거, 저자 한 줄만 유지
- 제목 옵션·메타 디스크립션·태그 섹션 제거(발행 화면에서 따로 입력)
"""
import re, sys
from pathlib import Path
sys.path.insert(0, '.')
from publisher.naver_formatter import markdown_to_naver_html

day = Path('content/2026-11-21-01')
md = (day / 'post.md').read_text(encoding='utf-8')

# 헤더 전체(제목 줄 ~ 첫 구분선 이후) 잘라내고 저자 한 줄로 대체
i = md.find('## 💡 현장 리포트')
body_start = md.rfind('\n---\n', 0, i)
md = '> **저자**: 겅태(의학과 경제학에 관심많은)\n\n---\n\n' + md[i:]

# 제목 옵션·메타 디스크립션 섹션 제거(이미 위에서 잘림) 및 태그 섹션 제거
i = md.find('## 🏷️ 태그')
if i != -1:
    j = md.find('*이 글은 의학적 정보')
    md = md[:i].rstrip('\n-\n ') + '\n\n' + md[j:]

html = markdown_to_naver_html(md)
(day / 'naver_post_publish.html').write_text(html, encoding='utf-8')
print('ok', len(html), '| tables', html.count('<table'), '| h1', html.count('<h1'), '| 저자', '겅태' in html)
print(repr(md[:120]))
