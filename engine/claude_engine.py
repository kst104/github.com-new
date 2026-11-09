# -*- coding: utf-8 -*-
import os
import json
import urllib.request
import urllib.error
from engine.config import ANTHROPIC_API_KEY, CLAUDE_MODEL

def call_claude(system_prompt: str, user_prompt: str, model: str = None) -> str:
    """Anthropic Claude API 호출 (Claude 3.5 Sonnet 최적화, 표준 라이브러리 urllib 기반)"""
    api_key = ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다. .env 파일이나 GitHub Secrets를 확인하세요.")
    
    target_model = model or CLAUDE_MODEL
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
        "User-Agent": "ContentAutomationEngine/1.0"
    }
    payload = {
        "model": target_model,
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            res_body = response.read().decode("utf-8")
            data = json.loads(res_body)
            content_blocks = data.get("content", [])
            result_text = "".join([block.get("text", "") for block in content_blocks if block.get("type") == "text"])
            return result_text
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8") if e.fp else str(e)
        raise RuntimeError(f"Claude API 호출 실패 (HTTP {e.code}): {err_msg}")
    except Exception as e:
        raise RuntimeError(f"Claude API 호출 중 오류 발생: {e}")

def generate_blog_with_claude(topic: str, keyword: str, audience: str = "일반 독자", category: str = "칼럼") -> str:
    """Claude 3.5 Sonnet을 이용한 SEO 블로그 포스팅 원고 생성"""
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "claude_blog_prompt.md")
    system_prompt = "당신은 대한민국 최고의 SEO 블로그 에디터입니다."
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

    user_prompt = f"""
[요청 정보]
- 글 주제: {topic}
- 타깃 키워드: {keyword}
- 타깃 독자: {audience}
- 글 카테고리: {category}

위 요청 정보를 바탕으로 네이버 C-Rank 및 구글 SEO 최적화 전문 블로그 원고를 XML 구조(<blog_post>)에 맞추어 작성해 주세요.
모바일 가독성을 고려하여 단락 구분을 명확히 하고, 바로 복사하여 블로그에 포스팅할 수 있는 완결된 형태로 작성해 주세요.
"""
    raw_blog = call_claude(system_prompt, user_prompt)
    try:
        from engine.slop_engine import apply_slop_rewrite
        cleaned_blog, _ = apply_slop_rewrite(raw_blog, provider="claude")
        return cleaned_blog
    except Exception:
        return raw_blog

def generate_ads_with_claude(topic: str, keyword: str, blog_summary: str = "") -> str:
    """Claude 3.5 Sonnet을 이용한 다채널 마케팅 광고 카피 생성"""
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "claude_ad_prompt.md")
    system_prompt = "당신은 대한민국 최고의 퍼포먼스 마케터이자 다이렉트 리스폰스 카피라이터입니다."
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

    user_prompt = f"""
[요청 정보]
- 콘텐츠 주제: {topic}
- 타깃 키워드: {keyword}
- 블로그 핵심 요약: {blog_summary}

위 정보를 바탕으로 페이스북/인스타 피드 카피(PAS), 카드뉴스 구성(AIDA), 스토리텔링 카피(BAB), 네이버 파워링크 검색광고(제목 15자/설명 45자 엄수 5세트), 숏폼 60초 대본을 XML 구조(<marketing_assets>)에 맞추어 작성해 주세요.
"""
    return call_claude(system_prompt, user_prompt)
