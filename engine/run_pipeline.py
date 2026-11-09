# -*- coding: utf-8 -*-
"""
GitHub × Notion × Claude / ChatGPT 통합 콘텐츠 자동화 엔진
김승태 님을 위한 맞춤형 실행 파이프라인
"""

import os
import sys
import argparse
import datetime
import re
import json

# 상위 경로를 모듈 탐색 경로에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.config import DEFAULT_MODEL_PROVIDER, ANTHROPIC_API_KEY, OPENAI_API_KEY
from engine.claude_engine import generate_blog_with_claude, generate_ads_with_claude
from engine.openai_engine import generate_blog_with_openai, generate_ads_with_openai
from engine.notion_engine import query_pending_items, update_page_status, append_content_to_page

def clean_filename(text: str) -> str:
    """파일명으로 사용 가능한 안전한 문자열로 변환"""
    cleaned = re.sub(r'[\\/*?:"<>|]', '', text)
    cleaned = cleaned.replace(" ", "_").strip()
    return cleaned[:40]

def run_single_generation(topic: str, keyword: str, audience: str = "일반 독자", category: str = "전문 칼럼", provider: str = "claude", page_id: str = None, dry_run: bool = False, hub_id: str = None):
    print(f"\n=======================================================")
    print(f"🚀 콘텐츠 자동 생성 시작")
    print(f"- 주제: {topic}")
    print(f"- 키워드: {keyword}")
    print(f"- 모델 엔진: {provider.upper()}")
    print(f"- 타깃 독자: {audience} | 분류: {category}")
    print(f"=======================================================")

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    slug = clean_filename(topic)

    if dry_run or (provider == "claude" and not ANTHROPIC_API_KEY and not os.getenv("ANTHROPIC_API_KEY")) or (provider == "openai" and not OPENAI_API_KEY and not os.getenv("OPENAI_API_KEY")):
        print(f"[모의 실행(Dry-run) 모드 가동] API 키 미등록 또는 테스트 모드입니다. 표준 샘플 원고와 광고 카피를 생성합니다.")
        blog_content = f"""# {topic} 완전 정복 가이드

## 📌 핵심 요약
- 키워드: {keyword}
- 작성일: {today_str}
- 엔진: {provider.upper()} 최적화 파이프라인

### 1. 왜 지금 {keyword}에 주목해야 하는가?
현대 사회에서 {topic}에 대한 올바른 이해와 실천은 더 이상 선택이 아닌 필수입니다. 많은 분들이 잘못된 정보로 혼란을 겪고 계신데요. 본 칼럼에서는 의학적/실무적 근거를 바탕으로 가장 빠르고 안전한 가이드를 제공합니다.

### 2. 전문가가 알려주는 3단계 실천법
1. **정확한 현재 상태 점검**: 자가 진단 및 데이터 수집
2. **맞춤형 루틴 형성**: 무리하지 않고 지속 가능한 일상 습관 정착
3. **지속적인 모니터링**: 피드백을 통한 단계별 개선

### 3. 자주 묻는 질문 (FAQ)
- **Q. 얼마나 실천해야 변화가 나타나나요?**
  - 개인차가 있지만 통상 2~4주 이내에 유의미한 변화를 체감하실 수 있습니다.

---
#블로그자동화 #{keyword.replace(' ', '')} #전문칼럼 #{provider}엔진
"""
        ad_content = f"""# 다채널 마케팅 광고 소재 ({topic})

### 1. 페이스북/인스타그램 피드 광고 (PAS 공식)
- **Problem**: 아직도 {keyword} 때문에 스트레스받고 계신가요?
- **Agitation**: 방치할수록 손실은 눈덩이처럼 불어납니다. 지금 바로잡지 않으면 늦습니다.
- **Solution**: 상위 1% 전문가가 검증한 3단계 솔루션으로 단 2주 만에 해결하세요!
- **CTA**: 👉 [프로필 링크] 누르고 1초 만에 무료 가이드북 확인하기

### 2. 네이버 파워링크 검색광고 (글자수 엄수)
- [소재 1] 제목: {keyword[:15]} / 설명: 3단계 검증 솔루션 무료 공개 지금 확인하세요
- [소재 2] 제목: {topic[:15]} / 설명: 전문가가 검증한 실전 노하우 지금 바로 확인

### 3. 숏폼 60초 대본
- [0~3초] "설마 아직도 {keyword} 이렇게 하세요? 큰일 납니다!"
- [4~25초] 흔히 하는 치명적인 실수 2가지 짚기
- [26~50초] 당장 오늘부터 실천할 수 있는 초간단 해결책
- [51~60초] "더 자세한 내용은 캡션과 고정 댓글을 확인하세요!"
"""
    else:
        # 실제 AI API 호출
        if provider == "claude":
            print("[1/2] Claude 3.5 Sonnet으로 SEO 블로그 원고 작성 중...")
            blog_content = generate_blog_with_claude(topic, keyword, audience, category)
            print("[2/2] Claude 3.5 Sonnet으로 다채널 광고 카피 10종 생성 중...")
            ad_content = generate_ads_with_claude(topic, keyword, blog_content[:500])
        else:
            print("[1/2] OpenAI GPT-4o로 SEO 블로그 원고 작성 중...")
            blog_content = generate_blog_with_openai(topic, keyword, audience, category)
            print("[2/2] OpenAI GPT-4o로 다채널 광고 카피 10종 생성 중...")
            ad_content = generate_ads_with_openai(topic, keyword, blog_content[:500])

    # 0. slop-rewrite 자동 탈(脫)AI 정밀 교정 패스 실행
    print("🧹 [slop-rewrite] AI 티 제거 및 자연스러운 문체 정밀 교정 패스 실행 중...")
    from engine.slop_engine import apply_slop_rewrite
    blog_content, slop_report = apply_slop_rewrite(blog_content, provider=provider if not dry_run else None)
    print(f"   슬롭 지수: {slop_report['initial_score']} ➔ {slop_report['final_score']} (적용된 교정: {len(slop_report['fixes_applied'])}건)")

    # 1. content/<허브ID>/ 에 저장 (로컬 작업 허브와 같은 구조, Git 커밋 대상)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    content_dir = os.path.join(base_dir, "content")
    os.makedirs(content_dir, exist_ok=True)
    if not hub_id or not os.path.isdir(os.path.join(content_dir, hub_id)):
        n = 1
        while os.path.exists(os.path.join(content_dir, f"{today_str}-{n:02d}")):
            n += 1
        hub_id = hub_id if hub_id and re.fullmatch(r"[\w\-]+", hub_id) else f"{today_str}-{n:02d}"
    item_dir = os.path.join(content_dir, hub_id)
    os.makedirs(item_dir, exist_ok=True)

    post_filepath = os.path.join(item_dir, "post.md")
    ad_filepath = os.path.join(item_dir, "ads.md")
    slop_report_path = os.path.join(item_dir, "slop_report.json")
    with open(post_filepath, "w", encoding="utf-8") as f:
        f.write(blog_content)
    with open(ad_filepath, "w", encoding="utf-8") as f:
        f.write(ad_content)
    with open(slop_report_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(slop_report, ensure_ascii=False, indent=2) + "\n")

    meta_path = os.path.join(item_dir, "meta.json")
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).replace(microsecond=0).isoformat()
    meta.update({"id": hub_id, "title": meta.get("title") or topic, "keyword": keyword, "category": category,
                 "audience": audience, "engine": "Claude" if provider == "claude" else "OpenAI",
                 "status": "검토", "updated": now})
    meta.setdefault("channels", ["블로그", "인스타", "페이스북", "파워링크", "쇼츠"])
    meta.setdefault("created", now)
    if dry_run:
        meta["note"] = "모의 실행 샘플이에요 (실제 원고 아님)"
    if page_id:
        meta["notion_page_id"] = page_id
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")

    print(f"✅ 블로그 원고 저장 완료: {post_filepath}")
    print(f"✅ 광고 카피 저장 완료: {ad_filepath}")

    # 2. 노션 업데이트 (page_id가 존재하는 경우)
    if page_id:
        print(f"[Notion] 페이지 {page_id} 상태 업데이트 및 본문 추가 중...")
        full_text = f"## 📝 {provider.upper()} 자동 생성 원고\n\n{blog_content}\n\n---\n\n## 📢 다채널 광고 카피\n\n{ad_content}"
        append_content_to_page(page_id, full_text)
        update_page_status(page_id, "검토", {"허브ID": {"rich_text": [{"text": {"content": hub_id}}]}})
        print(f"✅ 노션 업데이트 완료!")

    return post_filepath, ad_filepath

def main():
    parser = argparse.ArgumentParser(description="GitHub × Notion × Claude/ChatGPT Content Engine")
    parser.add_argument("--provider", choices=["claude", "openai"], default=DEFAULT_MODEL_PROVIDER, help="AI 엔진 공급자 (기본: claude)")
    parser.add_argument("--topic", type=str, default="", help="포스팅 주제")
    parser.add_argument("--keyword", type=str, default="", help="타깃 검색 키워드")
    parser.add_argument("--audience", type=str, default="일반 독자 / 4050 직장인", help="타깃 독자층")
    parser.add_argument("--category", type=str, default="의학/건강 칼럼", help="카테고리")
    parser.add_argument("--dry-run", action="store_true", help="API 키 없이 로컬 모의 실행")
    args = parser.parse_args()

    # 1. CLI 파라미터가 직접 전달된 경우 즉시 단일 실행
    if args.topic and args.keyword:
        run_single_generation(
            topic=args.topic,
            keyword=args.keyword,
            audience=args.audience,
            category=args.category,
            provider=args.provider,
            dry_run=args.dry_run
        )
        return

    # 2. 노션 연동 모드: 노션 DB에서 '생성요청' 상태인 항목 조회
    print("[Notion] 대기 중인 콘텐츠 아이디어 조회 중...")
    pending_items = query_pending_items()
    if not pending_items:
        print("[Notion] '생성요청' 상태인 항목이 없어요. 할 일이 없으니 종료합니다.")
        return

    for item in pending_items:
        item_id = item["id"]
        props = item.get("properties", {})
        def _text(name):
            rt = props.get(name, {}).get("rich_text", []) or props.get(name, {}).get("title", [])
            return "".join(x.get("plain_text", "") for x in rt).strip()
        def _select(name, default):
            sel = props.get(name, {}).get("select") or {}
            return sel.get("name", default)

        topic = _text("제목") or _text("Name") or "무제"
        keyword = _text("키워드") or _text("타깃 키워드") or topic
        category = _select("카테고리", "칼럼")
        audience = _text("타깃 독자") or "일반 독자"
        provider = _select("엔진", args.provider).lower()
        hub_id = _text("허브ID") or None

        run_single_generation(
            topic=topic,
            keyword=keyword,
            audience=audience,
            category=category,
            provider=provider,
            page_id=item_id,
            dry_run=args.dry_run,
            hub_id=hub_id
        )

if __name__ == "__main__":
    main()
