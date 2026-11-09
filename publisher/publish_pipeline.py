# -*- coding: utf-8 -*-
"""
콘텐츠 자동 발행 & 로딩 파이프라인 (Multi-Channel Publishing Pipeline)
노션에서 '상태'가 '발행요청'인 콘텐츠를 감지하여 타깃 채널에 맞게 자동 발행/로딩을 수행합니다.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import urllib.error
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.config import NOTION_API_KEY, NOTION_DATABASE_ID
from publisher.naver_formatter import markdown_to_naver_html

def query_publish_pending_items():
    """노션에서 상태가 '발행요청'인 항목 조회"""
    api_key = NOTION_API_KEY or os.getenv("NOTION_API_KEY")
    db_id = NOTION_DATABASE_ID or os.getenv("NOTION_DATABASE_ID")
    if not api_key or not db_id:
        print("[Publisher] NOTION 키 또는 DB ID가 없어 로컬 파일 모드로 실행합니다.")
        return []
        
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    payload = {
        "filter": {
            "or": [
                {"property": "상태", "select": {"equals": "발행요청"}},
                {"property": "진행 상태", "status": {"equals": "발행요청"}}
            ]
        }
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=20) as res:
            return json.loads(res.read().decode("utf-8")).get("results", [])
    except Exception as e:
        print(f"[Publisher] 노션 쿼리 오류: {e}")
        return []

def publish_to_tistory(title: str, content_html: str, tags: list = None) -> str:
    """티스토리 Open API를 통한 100% 완전 자동 발행"""
    access_token = os.getenv("TISTORY_ACCESS_TOKEN", "")
    blog_name = os.getenv("TISTORY_BLOG_NAME", "")
    
    if not access_token or not blog_name:
        print("[Tistory] TISTORY_ACCESS_TOKEN 또는 TISTORY_BLOG_NAME 미설정 (모의 실행)")
        return f"https://{blog_name or 'myblog'}.tistory.com/demo-preview"
        
    url = "https://www.tistory.com/apis/post/write"
    params = {
        "access_token": access_token,
        "output": "json",
        "blogName": blog_name,
        "title": title,
        "content": content_html,
        "visibility": 3, # 3: 발행, 0: 비공개
        "tag": ",".join(tags or [])
    }
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            post_url = res_data.get("tistory", {}).get("url", "")
            print(f"✅ 티스토리 자동 발행 완료: {post_url}")
            return post_url
    except Exception as e:
        print(f"[Tistory] 발행 실패: {e}")
        return ""

def publish_to_naver_blog_prep(content_dir: str, title: str, post_md: str) -> str:
    """
    네이버 블로그: 스마트에디터 ONE 최적화 서식 변환 및 1초 복사용 HTML 패키징
    (네이버의 봇 탐지·저품질 제재를 방지하기 위해 스마트에디터 완벽 서식 HTML 파일 생성)
    """
    html_content = markdown_to_naver_html(post_md)
    output_path = os.path.join(content_dir, "naver_post.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ 네이버 블로그 스마트 서식 HTML 생성 완료: {output_path}")
    print(f"👉 브라우저에서 {output_path}를 열고 [Ctrl+A ➔ Ctrl+C] 후 네이버 블로그에 [Ctrl+V] 하시면 글자 서식·박스·강조가 100% 유지됩니다.")
    return output_path

def update_notion_published(page_id: str, publish_url: str = ""):
    """노션 페이지 상태를 '발행완료'로 변경하고 발행 URL 기록"""
    api_key = NOTION_API_KEY or os.getenv("NOTION_API_KEY")
    if not api_key:
        return False
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    props = {
        "상태": {"select": {"name": "발행완료"}}
    }
    if publish_url:
        props["발행 URL"] = {"url": publish_url}
        
    try:
        req = urllib.request.Request(url, data=json.dumps({"properties": props}).encode("utf-8"), headers=headers, method="PATCH")
        with urllib.request.urlopen(req, timeout=20) as res:
            return res.status == 200
    except Exception as e:
        print(f"[Publisher] 노션 상태 업데이트 실패: {e}")
        return False

def process_content_folder(folder_path: str):
    """지정된 content/<id>/ 폴더의 발행 처리"""
    meta_path = os.path.join(folder_path, "meta.json")
    post_path = os.path.join(folder_path, "post.md")
    
    if not os.path.exists(post_path):
        print(f"[Publisher] post.md가 존재하지 않습니다: {folder_path}")
        return
        
    with open(post_path, "r", encoding="utf-8") as f:
        post_md = f.read()
        
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            
    title = meta.get("title", "발행 원고")
    channels = meta.get("channels", ["블로그"])
    
    print(f"\n=======================================================")
    print(f"🚀 자동 발행 파이프라인 구동: {title}")
    print(f"- 대상 폴더: {folder_path}")
    print(f"- 타깃 채널: {', '.join(channels)}")
    print(f"=======================================================")
    
    # 1. 네이버 블로그 서식 파일 생성 (필수 기본 제공)
    naver_html = publish_to_naver_blog_prep(folder_path, title, post_md)
    
    # 2. 티스토리 연동이 활성화된 경우 자동 포스팅
    published_url = ""
    if os.getenv("TISTORY_ACCESS_TOKEN"):
        published_url = publish_to_tistory(title, markdown_to_naver_html(post_md))
        
    # 3. meta.json 갱신
    meta["status"] = "발행완료"
    if published_url:
        meta["published_url"] = published_url
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        
    # 4. 노션 페이지 동기화
    notion_page_id = meta.get("notion_page_id")
    if notion_page_id:
        update_notion_published(notion_page_id, published_url)
        print(f"✅ 노션 상태 '발행완료' 동기화 완료!")

def main():
    parser = argparse.ArgumentParser(description="Multi-Channel Content Publishing Pipeline")
    parser.add_argument("--folder", type=str, default="", help="발행할 content 폴더 경로 (예: content/2026-11-09-05)")
    args = parser.parse_args()
    
    if args.folder:
        process_content_folder(args.folder)
        return
        
    # 노션에서 '발행요청' 상태 항목 탐색
    print("[Publisher] 노션에서 '발행요청' 상태 항목 조회 중...")
    items = query_publish_pending_items()
    if not items:
        print("[Publisher] 발행 대기 중인 항목이 없습니다.")
        return
        
    for item in items:
        props = item.get("properties", {})
        hub_id = props.get("허브ID", {}).get("rich_text", [{}])[0].get("plain_text", "")
        if hub_id:
            folder = os.path.join(os.path.dirname(__file__), "..", "content", hub_id)
            if os.path.exists(folder):
                process_content_folder(folder)

if __name__ == "__main__":
    main()
