# -*- coding: utf-8 -*-
import os
import json
import urllib.request
import urllib.error
from engine.config import NOTION_API_KEY, NOTION_DATABASE_ID

NOTION_VERSION = "2022-06-28"

def get_notion_headers():
    api_key = NOTION_API_KEY or os.getenv("NOTION_API_KEY")
    return {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
        "User-Agent": "ContentAutomationEngine/1.0"
    }

def query_pending_items(database_id: str = None):
    """콘텐츠 보드에서 '상태'가 '생성요청'인 행 조회"""
    db_id = database_id or NOTION_DATABASE_ID or os.getenv("NOTION_DATABASE_ID")
    if not db_id:
        print("[Notion] NOTION_DATABASE_ID가 없어 로컬/파라미터 모드로 작동합니다.")
        return []
    
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = {"filter": {"property": "상태", "select": {"equals": "생성요청"}}}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=get_notion_headers(),
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            res_body = response.read().decode("utf-8")
            data = json.loads(res_body)
            return data.get("results", [])
    except urllib.error.HTTPError as e:
        print(f"[Notion] 쿼리 실패 (HTTP {e.code})")
        return []
    except Exception as e:
        print(f"[Notion] 연결 오류: {e}")
        return []

def update_page_status(page_id: str, new_status: str = "검토", extra_props: dict = None):
    """페이지의 진행 상태 업데이트"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    props = {"상태": {"select": {"name": new_status}}}
    if extra_props:
        props.update(extra_props)
    payload = {"properties": props}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=get_notion_headers(),
        method="PATCH"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.status == 200
    except Exception as e:
        print(f"[Notion] 상태 업데이트 실패: {e}")
        return False

def append_content_to_page(page_id: str, markdown_text: str):
    """노션 페이지 하단에 생성된 원고 블록 추가"""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    chunks = [markdown_text[i:i+1800] for i in range(0, len(markdown_text), 1800)]
    children = []
    for chunk in chunks:
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": chunk}
                    }
                ]
            }
        })
    req = urllib.request.Request(
        url,
        data=json.dumps({"children": children}).encode("utf-8"),
        headers=get_notion_headers(),
        method="PATCH"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status == 200
    except Exception as e:
        print(f"[Notion] 본문 블록 추가 실패: {e}")
        return False
