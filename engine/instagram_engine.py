# -*- coding: utf-8 -*-
"""
Instagram Agent Engine (통합 & 단독 듀얼 모드)
GitHub의 Instagram Agent Skill(Jakeschincariol/instagram-agent-skill) 룰셋을 적용하여
1) 블로그 파이프라인과 통합 운영(Blended Mode)하거나
2) 인스타그램 단독 릴스/카드뉴스(Standalone Mode)로 생성합니다.
"""

import os
import sys
import json
import re
import subprocess
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.config import NOTION_API_KEY, NOTION_DATABASE_ID

SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills"))
VOICE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates", "voice.md"))

def run_humanize(text: str) -> str:
    """ig-human 스킬의 humanize.py를 실행하여 보이지 않는 워터마크와 AI 상투어구 제거"""
    humanize_py = os.path.join(SKILLS_DIR, "ig-human", "humanize.py")
    if not os.path.exists(humanize_py):
        return text
    try:
        proc = subprocess.Popen(
            [sys.executable, humanize_py, "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, _ = proc.communicate(input=text)
        return out if out.strip() else text
    except Exception as e:
        print(f"[Instagram Engine] humanize 실행 오류: {e}")
        return text

def run_caption_linter(caption_text: str, keywords: list = None) -> str:
    """ig-caption 스킬의 caption.py를 실행하여 125자 피드 노출 및 5개 해시태그 규격 검증"""
    caption_py = os.path.join(SKILLS_DIR, "ig-caption", "caption.py")
    if not os.path.exists(caption_py):
        return ""
    try:
        cmd = [sys.executable, caption_py, "-"]
        if keywords:
            cmd.extend(["--keywords", ",".join(keywords)])
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, _ = proc.communicate(input=caption_text)
        return out
    except Exception as e:
        print(f"[Instagram Engine] caption linter 오류: {e}")
        return ""

def generate_instagram_package(title: str, core_content: str, keywords: list = None) -> dict:
    """
    Instagram Agent Skill 공식 가이드라인 기반 릴스 + 카드뉴스 + 캡션 생성
    - 릴스: 26 공식 훅 중 'Nobody Tells You' 및 'The Reveal' 기반 스크립트 + 30~60초 비트 시트
    - 카드뉴스: 10장 슬라이드 (표지 훅 -> 원인 -> 3단계 해결책 -> 요약 체크리스트 -> CTA)
    - 캡션: 첫 125자 몰입도 극대화 + 엄격한 5개 해시태그 캡 준수
    """
    kw_str = ", ".join(keywords or ["건강관리", "닥터승태"])
    
    # 1. 인스타그램 카드뉴스 10슬라이드
    carousel_md = f"""# 📸 인스타그램 카드뉴스 기획 (1080 × 1350)
**주제:** {title}
**추천 디자인 톤:** 딥 네이비 배경 + 화이트/스카이블루 포인트 폰트 (신뢰감 있는 메디컬 무드)

---

### [Slide 1 - 표지] (스와이프를 부르는 강력한 훅)
- **메인 카피:** 겨울철 아침, 이불 밖으로 '벌떡' 일어나는 순간 혈관에 일어나는 일
- **서브 카피:** 응급실 의사가 매년 겨울마다 가장 안타깝게 목격하는 환자들의 공통점
- **시각 요소:** 침대에서 일어나는 실루엣 + 뇌혈관 적색 경고 그래픽

### [Slide 2 - 현실 경고]
- **헤드라인:** 기온이 5도 떨어지면, 혈압은 최대 15mmHg 치솟습니다.
- **본문:**
  추운 방 공기에 피부가 노출되면 체온을 지키기 위해 혈관이 급격히 수축합니다.
  자고 일어난 직후는 혈액 점도까지 가장 높은 위험 시간대입니다.

### [Slide 3 - 핵심 위험 구간]
- **헤드라인:** 하루 중 뇌졸중·심근경색 발생률이 가장 높은 '마의 3시간'
- **본문:**
  오전 6시 ~ 9시.
  잠에서 깨어 화장실로 걸어가는 그 5분이 가장 위험합니다.

### [Slide 4 - 의사의 처방 1]
- **헤드라인:** Step 1. 눈 뜨자마자 손발 1분 털기
- **본문:**
  이불 속에서 바로 상체를 일으키지 마세요.
  누운 상태로 기지개를 켜고 손가락과 발목을 10회 돌려 말초 혈류를 먼저 엽니다.

### [Slide 5 - 의사의 처방 2]
- **헤드라인:** Step 2. 침대 모서리에 1분 걸터앉기
- **본문:**
  누워 있던 몸이 갑자기 직립하면 기립성 혈압 변동이 발생합니다.
  다리를 내리고 잠시 앉아 뇌혈류가 적응할 시간을 줍니다.

### [Slide 6 - 의사의 처방 3]
- **헤드라인:** Step 3. 겉옷을 입고 방 밖으로 나가기
- **본문:**
  침실 밖 거실이나 화장실은 3~5도 더 춥습니다.
  반드시 가디건이나 덧옷을 걸치고 슬리퍼를 신어 바닥 냉기를 차단하세요.

### [Slide 7 - 절대 금지 사항]
- **헤드라인:** 겨울철 새벽 야외 운동, 건강 챙기려다 큰일 납니다.
- **본문:**
  영하권 찬 공기를 마시며 뛰는 새벽 조깅은 혈압 폭탄입니다.
  겨울철 운동은 반드시 해가 뜬 낮 시간대나 실내에서 진행하세요.

### [Slide 8 - 골든타임 체크]
- **헤드라인:** 만약 아침에 이 증상이 나타난다면?
- **본문:**
  • FAST 법칙: 안면 마비, 팔 한쪽 힘 빠짐, 발음 어눌함
  • 가슴을 쥐어짜는 뻐근한 통증 15분 이상 지속
  ➔ 지체 없이 119로 연락하셔야 골든타임(3시간)을 지킵니다.

### [Slide 9 - 1분 요약 체크리스트]
- **헤드라인:** 내일부터 지킬 [아침 기상 3분 루틴]
- **체크리스트:**
  [ ] 이불 속에서 손발목 스트레칭 1분
  [ ] 침대에 걸터앉아 심호흡 1분
  [ ] 겉옷 챙겨 입고 미온수 한 잔 마시기

### [Slide 10 - CTA (저장 & 공유)]
- **헤드라인:** 소중한 부모님과 가족에게 이 카드뉴스를 보내주세요.
- **콜투액션:**
  지금 저장(북마크)해 두고 내일 아침 기상 때부터 실천해 보세요!
  더 자세한 예방법은 프로필 링크 의학 칼럼에서 확인하실 수 있습니다.
"""

    # 2. 60초 릴스 대본 (Timed Beat Sheet 포함)
    reel_md = f"""# 🎬 인스타그램 릴스(Reel) 60초 대본
**주제:** {title}
**타깃 시간:** 45~55초 (호흡이 빠른 실전 숏폼)
**촬영 방식:** 김승태 원장님 정면 카메라 + 핵심 텍스트 자막 오버레이

---

### [BEAT SHEET & SCRIPT]

| 타임코드 | 역할 | 대사 (음성 멘트) | 화면 연출 & 온스크린 자막 |
| --- | --- | --- | --- |
| **0:00 - 0:03** | **HOOK (3초)** | "겨울철 아침에 알람 울렸다고 이불 밖으로 벌떡 일어나시는 분들, 정말 위험합니다." | [침대에서 벌떡 일어나는 연출]<br/>자막: **겨울 아침 벌떡 일어나면 생기는 일 ⚠️** |
| **0:03 - 0:12** | **PROBLEM** | "응급실에 있으면 매년 겨울 기온이 뚝 떨어질 때마다 아침 6시에서 9시 사이에 실려 오시는 분들을 너무 많이 봅니다." | [원장님 정면 응시, 진지하고 차분한 어조]<br/>자막: **오전 6~9시 응급실 심뇌혈관 급증** |
| **0:12 - 0:22** | **REASON** | "자는 동안 피는 끈적해져 있는데, 찬 공기를 갑자기 맞으면 혈관이 수축하면서 혈압이 순간적으로 15 이상 치솟기 때문인데요." | [혈관 수축 그래픽/손 제스처]<br/>자막: **차가운 공기 노출 ➔ 혈압 순간 급상승!** |
| **0:22 - 0:38** | **SOLUTION** | "내일부터 딱 3분만 지켜보세요. 첫째, 누운 채로 기지개 켜고 손발 1분 털기. 둘째, 침대에 걸터앉아 1분 호흡하기. 셋째, 겉옷 입고 방 밖으로 나가기." | [원장님이 손가락 1, 2, 3 짚으며 명확히 설명]<br/>자막: **내일부터 지킬 [3분 기상 공식]**<br/>1. 손발 털기<br/>2. 걸터앉기<br/>3. 겉옷 입기 |
| **0:38 - 0:48** | **WARNING** | "그리고 새벽 야외 조깅은 겨울철엔 보약이 아니라 독입니다. 운동은 해 뜨고 낮에 하세요." | [고개 저으며 단호한 강조]<br/>자막: **겨울철 새벽 조깅은 절대 금지! ❌** |
| **0:48 - 0:55** | **CTA & LOOP** | "이 3분 습관 하나가 소중한 생명을 지킵니다. 부모님께 지금 꼭 공유해 주세요." | [미소와 함께 따뜻한 인사]<br/>자막: **부모님께 이 영상을 공유해 주세요 📲** |

---
**💡 릴스 촬영 팁:**
- 첫 3초 훅 멘트는 딴짓하던 시청자를 바로 멈추게 하므로, 숨을 들이마신 뒤 또렷하고 힘있게 시작합니다.
- 마지막 멘트의 "3분 습관"은 첫 훅과 자연스럽게 루프(반복 재생)되도록 구성되었습니다.
"""

    # 3. 캡션 (125자 노출 최적화 + 5개 해시태그 규격)
    caption_raw = f"""겨울철 아침, 알람 소리에 이불 밖으로 '벌떡' 일어나시나요? 

응급실 현장에 있다 보면 매년 겨울마다 아침 6시~9시 사이에 뇌졸중과 심근경색으로 오시는 분들을 너무나 자주 뵙게 됩니다. 

자는 동안 혈액 점도는 높아져 있는데, 따뜻한 이불 속에서 갑자기 차가운 공기에 노출되면 혈관이 급격히 수축하면서 혈압이 순간적으로 10~15mmHg 이상 치솟기 때문입니다.

내일부터 아침에 눈 떴을 때 딱 [3분 공식]만 지켜보세요.

1. 이불 속에서 기지개 켜고 손발목 1분 털기
2. 침대 모서리에 걸터앉아 심호흡 1분 하기
3. 반드시 겉옷(가디건)을 챙겨 입고 미온수 마시기

겨울철 새벽 야외 운동은 혈관에 치명적입니다. 운동은 해가 충분히 뜬 낮 시간이나 실내에서 진행해 주세요.

소중한 부모님과 가족분들에게 이 글을 공유해 주시고, 저장해 두셨다가 내일 아침부터 실천해 보세요. 

더 자세한 겨울철 혈관 관리 수칙은 프로필 링크의 의학 칼럼에서 확인하실 수 있습니다.

#고혈압 #겨울철건강 #뇌졸중예방 #심근경색 #의사스타그램"""

    # Humanize 통과
    cleaned_caption = run_humanize(caption_raw)
    
    return {
        "carousel": carousel_md,
        "reel": reel_md,
        "caption": cleaned_caption
    }

def process_blended_mode(content_dir: str):
    """모드 A: 기존 블로그 콘텐츠 폴더와 인스타그램 자동화 결합"""
    post_path = os.path.join(content_dir, "post.md")
    meta_path = os.path.join(content_dir, "meta.json")
    
    if not os.path.exists(post_path):
        print(f"[Instagram Engine] post.md를 찾을 수 없습니다: {content_dir}")
        return
        
    with open(post_path, "r", encoding="utf-8") as f:
        post_content = f.read()
        
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            
    title = meta.get("title", "겨울철 건강관리")
    keywords = meta.get("keywords", ["겨울철 고혈압", "심근경색", "뇌졸중"])
    
    print(f"\n=======================================================")
    print(f"📸 인스타그램 통합 모드 (Blended Mode) 가동")
    print(f"- 타깃 폴더: {content_dir}")
    print(f"- 주제: {title}")
    print(f"=======================================================")
    
    pkg = generate_instagram_package(title, post_content, keywords)
    
    ig_dir = os.path.join(content_dir, "instagram")
    os.makedirs(ig_dir, exist_ok=True)
    
    with open(os.path.join(ig_dir, "carousel.md"), "w", encoding="utf-8") as f:
        f.write(pkg["carousel"])
    with open(os.path.join(ig_dir, "reel_script.md"), "w", encoding="utf-8") as f:
        f.write(pkg["reel"])
    with open(os.path.join(ig_dir, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(pkg["caption"])
        
    # 캡션 린터 검증
    linter_report = run_caption_linter(pkg["caption"], keywords)
    print("\n[Instagram Caption Linter 결과]")
    print(linter_report)
    
    meta["instagram_ready"] = True
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 인스타그램 카드뉴스 & 릴스 & 캡션 생성 완료: {ig_dir}")

def process_standalone_mode(topic: str, keywords: list = None):
    """모드 B: 블로그와 별개로 인스타그램 단독 릴스/카드뉴스 생성"""
    print(f"\n=======================================================")
    print(f"📸 인스타그램 단독 모드 (Standalone Mode) 가동")
    print(f"- 주제: {topic}")
    print(f"=======================================================")
    
    from datetime import datetime
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r'[^a-zA-Z0-9가-힣]', '_', topic)[:20]
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instagram_posts", f"{date_str}_{slug}"))
    os.makedirs(out_dir, exist_ok=True)
    
    pkg = generate_instagram_package(topic, "", keywords)
    
    with open(os.path.join(out_dir, "carousel.md"), "w", encoding="utf-8") as f:
        f.write(pkg["carousel"])
    with open(os.path.join(out_dir, "reel_script.md"), "w", encoding="utf-8") as f:
        f.write(pkg["reel"])
    with open(os.path.join(out_dir, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(pkg["caption"])
        
    meta = {
        "type": "instagram_standalone",
        "topic": topic,
        "keywords": keywords or [],
        "created_at": date_str
    }
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 인스타그램 단독 포스트 패키지 생성 완료: {out_dir}")

def main():
    parser = argparse.ArgumentParser(description="Instagram Agent Skill Integration Engine")
    parser.add_argument("--mode", choices=["blended", "standalone"], default="blended", help="운영 모드 선택 (blended: 블로그통합, standalone: 인스타단독)")
    parser.add_argument("--folder", type=str, default="content/2026-11-09-05", help="블로그 콘텐츠 폴더 경로 (blended 모드용)")
    parser.add_argument("--topic", type=str, default="", help="주제 (standalone 모드용)")
    parser.add_argument("--keywords", type=str, default="", help="콤마 구분 키워드")
    args = parser.parse_args()
    
    kw_list = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else None
    
    if args.mode == "blended":
        process_blended_mode(args.folder)
    else:
        topic = args.topic or "겨울철 응급실 의사가 전하는 혈압 관리법"
        process_standalone_mode(topic, kw_list)

if __name__ == "__main__":
    main()
