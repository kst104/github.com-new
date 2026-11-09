# -*- coding: utf-8 -*-
import os
import json
import urllib.request
import urllib.error
from engine.config import OPENAI_API_KEY, OPENAI_MODEL

def call_openai(system_prompt: str, user_prompt: str, model: str = None) -> str:
    """OpenAI API 호출 (GPT-4o / GPT-4o-mini, 표준 라이브러리 urllib 기반)"""
    api_key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일이나 GitHub Secrets를 확인하세요.")
    
    target_model = model or OPENAI_MODEL
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "ContentAutomationEngine/1.0"
    }
    payload = {
        "model": target_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            res_body = response.read().decode("utf-8")
            data = json.loads(res_body)
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8") if e.fp else str(e)
        raise RuntimeError(f"OpenAI API 호출 실패 (HTTP {e.code}): {err_msg}")
    except Exception as e:
        raise RuntimeError(f"OpenAI API 호출 중 오류 발생: {e}")

def generate_blog_with_openai(topic: str, keyword: str, audience: str = "일반 독자", category: str = "칼럼") -> str:
    """OpenAI GPT-4o를 이용한 SEO 블로그 포스팅 원고 생성"""
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "openai_blog_prompt.md")
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

위 요청 정보를 바탕으로 네이버 C-Rank 및 구글 SEO 최적화 전문 블로그 원고를 작성해 주세요.
제목 3개, 메타 디스크립션, 서론(훅), 본문(H2, H3), 결론 요약 및 해시태그를 포함하세요.
"""
    return call_openai(system_prompt, user_prompt)

def generate_ads_with_openai(topic: str, keyword: str, blog_summary: str = "") -> str:
    """OpenAI GPT-4o를 이용한 다채널 마케팅 광고 카피 생성"""
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "openai_ad_prompt.md")
    system_prompt = "당신은 대한민국 최고의 퍼포먼스 마케터이자 다이렉트 리스폰스 카피라이터입니다."
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

    user_prompt = f"""
[요청 정보]
- 콘텐츠 주제: {topic}
- 타깃 키워드: {keyword}
- 블로그 핵심 요약: {blog_summary}

위 정보를 바탕으로 PAS 광고 카피, AIDA 카드뉴스 구성안, BAB 카피, 네이버 파워링크 검색광고(제목 15자/설명 45자 엄수 5세트), 숏폼 60초 대본을 작성해 주세요.
"""
    return call_openai(system_prompt, user_prompt)
