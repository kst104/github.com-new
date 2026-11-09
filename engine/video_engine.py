# -*- coding: utf-8 -*-
"""
Shorts & Reels Video Engine v2
- 레이아웃: 캐릭터 좌측 배치(설명자/호스트 역할) + 우측 메인 상황별 일러스트 그래픽 카드 + 하단 고대비 자막 바
- Edge-TTS 한국어 음성 (ko-KR-InJoonNeural)
- 1080x1920 9:16 인스타그램 릴스 & 유튜브 쇼츠 표준 규격
"""

import os
import sys
import asyncio
import subprocess
import json
import argparse
from PIL import Image, ImageDraw, ImageFont

FFMPEG_PATH = "/usr/local/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
if not os.path.exists(FFMPEG_PATH):
    FFMPEG_PATH = "ffmpeg"

FONT_BOLD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts", "NanumGothic-Bold.ttf"))
if not os.path.exists(FONT_BOLD):
    FONT_BOLD = "/workspace/fonts/NanumGothic-Bold.ttf"

CHAR_DIR = "/workspace/assets/character/geongtae"

async def generate_speech(text: str, output_mp3: str, voice: str = "ko-KR-InJoonNeural", rate: str = "+5%"):
    import edge_tts
    comm = edge_tts.Communicate(text, voice, rate=rate)
    await comm.save(output_mp3)

def get_audio_duration(audio_path: str) -> float:
    cmd = [FFMPEG_PATH, "-i", audio_path]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    _, err = p.communicate()
    for line in err.split("\n"):
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 3.0

def draw_situation_card(draw, scene_idx: int, x1: int, y1: int, x2: int, y2: int, font_title, font_body, font_highlight, font_small):
    """우측 메인 영역에 상황별 의학 그래픽/일러스트 카드 렌더링"""
    # 카드 배경
    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=28, fill=(30, 41, 59, 250), outline=(59, 130, 246), width=3)
    card_w = x2 - x1
    center_x = (x1 + x2) // 2
    
    if scene_idx == 1:
        # [씬 1: 기상 시 혈압 급상승 상황 카드]
        draw.rounded_rectangle([(x1 + 30, y1 + 30), (x2 - 30, y1 + 100)], radius=16, fill=(220, 38, 38))
        draw.text((center_x, y1 + 65), "한파 속 기상 위험", font=font_title, fill=(255, 255, 255), anchor="mm")
        
        # 기온차 비교
        draw.text((center_x, y1 + 145), "따뜻한 이불 속 (30°C)", font=font_body, fill=(203, 213, 225), anchor="mm")
        draw.text((center_x, y1 + 195), "⬇️  차가운 방 공기 노출 (18°C)  ⬇️", font=font_small, fill=(248, 113, 113), anchor="mm")
        
        # 혈압 게이지 박스
        draw.rounded_rectangle([(x1 + 30, y1 + 235), (x2 - 30, y1 + 455)], radius=20, fill=(15, 23, 42, 240), outline=(239, 68, 68), width=3)
        draw.text((center_x, y1 + 280), "혈관 순간 수축 반응", font=font_small, fill=(148, 163, 184), anchor="mm")
        draw.text((center_x, y1 + 345), "혈압 15mmHg ↑", font=font_highlight, fill=(250, 204, 21), anchor="mm")
        draw.text((center_x, y1 + 410), "뇌졸중 · 심근경색 급증", font=font_body, fill=(239, 68, 68), anchor="mm")
        
        # 하단 핵심 수칙 박스
        draw.rounded_rectangle([(x1 + 30, y1 + 485), (x2 - 30, y2 - 30)], radius=20, fill=(30, 58, 138), outline=(96, 165, 250), width=2)
        draw.text((center_x, y1 + 540), "⚠️ 아침 기상 핵심 수칙", font=font_body, fill=(250, 204, 21), anchor="mm")
        draw.text((center_x, y1 + 600), "• 알람 울려도 '벌떡' 일어나기 금지", font=font_small, fill=(241, 245, 249), anchor="mm")
        draw.text((center_x, y1 + 655), "• 몸이 적응할 3분의 여유 주기", font=font_small, fill=(226, 232, 240), anchor="mm")
        draw.text((center_x, y1 + 710), "• 겉옷 착용 후 거실로 이동", font=font_small, fill=(148, 163, 184), anchor="mm")

    elif scene_idx == 2:
        # [씬 2: 마의 3시간 응급실 통계]
        draw.rounded_rectangle([(x1 + 30, y1 + 30), (x2 - 30, y1 + 100)], radius=16, fill=(185, 28, 28))
        draw.text((center_x, y1 + 65), "응급실 골든타임 리포트", font=font_title, fill=(255, 255, 255), anchor="mm")
        
        # 마의 3시간 시계 카드
        draw.rounded_rectangle([(x1 + 30, y1 + 130), (x2 - 30, y1 + 340)], radius=20, fill=(15, 23, 42, 240), outline=(220, 38, 38), width=3)
        draw.text((center_x, y1 + 180), "하루 중 가장 위험한 시간대", font=font_small, fill=(148, 163, 184), anchor="mm")
        draw.text((center_x, y1 + 245), "오전 06:00 ~ 09:00", font=font_highlight, fill=(250, 204, 21), anchor="mm")
        draw.text((center_x, y1 + 300), "심뇌혈관 발생률 2.5배 급증", font=font_body, fill=(248, 113, 113), anchor="mm")
        
        # 원인 박스
        draw.rounded_rectangle([(x1 + 30, y1 + 370), (x2 - 30, y2 - 30)], radius=20, fill=(51, 65, 85), outline=(148, 163, 184), width=2)
        draw.text((center_x, y1 + 420), "응급실 의사가 밝히는 원인:", font=font_body, fill=(255, 255, 255), anchor="mm")
        draw.text((center_x, y1 + 490), "1. 수면 중 수분 손실 ➔ 혈액 점도 상승", font=font_small, fill=(226, 232, 240), anchor="mm")
        draw.text((center_x, y1 + 560), "2. 기상 직후 교감신경 흥분", font=font_small, fill=(226, 232, 240), anchor="mm")
        draw.text((center_x, y1 + 630), "3. 영하권 찬 방 공기의 혈관 충격", font=font_small, fill=(248, 113, 113), anchor="mm")
        draw.text((center_x, y1 + 710), "➔ 골든타임 3시간 내 병원 필수", font=font_small, fill=(250, 204, 21), anchor="mm")

    elif scene_idx == 3:
        # [씬 3: 의사의 3분 기상 처방전 3단계 카드 (충분한 간격 배치)]
        draw.rounded_rectangle([(x1 + 30, y1 + 30), (x2 - 30, y1 + 100)], radius=16, fill=(37, 99, 235))
        draw.text((center_x, y1 + 65), "의사의 [3분 기상 공식]", font=font_title, fill=(255, 255, 255), anchor="mm")
        
        # 1단계 (y: 130 ~ 310)
        draw.rounded_rectangle([(x1 + 30, y1 + 130), (x2 - 30, y1 + 310)], radius=18, fill=(15, 23, 42, 240), outline=(34, 197, 94), width=3)
        draw.rounded_rectangle([(x1 + 50, y1 + 155), (x1 + 140, y1 + 205)], radius=10, fill=(34, 197, 94))
        draw.text((x1 + 95, y1 + 180), "1분", font=font_small, fill=(255, 255, 255), anchor="mm")
        draw.text((x1 + 160, y1 + 180), "이불 속 손발 털기", font=font_body, fill=(255, 255, 255), anchor="lm")
        draw.text((center_x, y1 + 255), "누운 채로 기지개 & 발목 10회 돌리기", font=font_small, fill=(148, 163, 184), anchor="mm")
        
        # 2단계 (y: 340 ~ 520)
        draw.rounded_rectangle([(x1 + 30, y1 + 340), (x2 - 30, y1 + 520)], radius=18, fill=(15, 23, 42, 240), outline=(234, 179, 8), width=3)
        draw.rounded_rectangle([(x1 + 50, y1 + 365), (x1 + 140, y1 + 415)], radius=10, fill=(234, 179, 8))
        draw.text((x1 + 95, y1 + 390), "1분", font=font_small, fill=(15, 23, 42), anchor="mm")
        draw.text((x1 + 160, y1 + 390), "침대 모서리 걸터앉기", font=font_body, fill=(255, 255, 255), anchor="lm")
        draw.text((center_x, y1 + 465), "기립성 혈류 적응 & 천천히 심호흡", font=font_small, fill=(148, 163, 184), anchor="mm")
        
        # 3단계 (y: 550 ~ 730)
        draw.rounded_rectangle([(x1 + 30, y1 + 550), (x2 - 30, y1 + 730)], radius=18, fill=(15, 23, 42, 240), outline=(59, 130, 246), width=3)
        draw.rounded_rectangle([(x1 + 50, y1 + 575), (x1 + 140, y1 + 625)], radius=10, fill=(59, 130, 246))
        draw.text((x1 + 95, y1 + 600), "1분", font=font_small, fill=(255, 255, 255), anchor="mm")
        draw.text((x1 + 160, y1 + 600), "겉옷 입고 방 밖으로", font=font_body, fill=(255, 255, 255), anchor="lm")
        draw.text((center_x, y1 + 675), "가디건 착용 & 따뜻한 미온수 한 잔", font=font_small, fill=(148, 163, 184), anchor="mm")

    elif scene_idx == 4:
        # [씬 4: 새벽 조깅 금지 경고]
        draw.rounded_rectangle([(x1 + 30, y1 + 30), (x2 - 30, y1 + 100)], radius=16, fill=(220, 38, 38))
        draw.text((center_x, y1 + 65), "겨울철 운동 주의보", font=font_title, fill=(255, 255, 255), anchor="mm")
        
        # 금지 박스
        draw.rounded_rectangle([(x1 + 30, y1 + 130), (x2 - 30, y1 + 380)], radius=20, fill=(15, 23, 42, 240), outline=(239, 68, 68), width=3)
        draw.text((center_x, y1 + 190), "❌ 새벽 야외 조깅 금지", font=font_title, fill=(239, 68, 68), anchor="mm")
        draw.text((center_x, y1 + 255), "영하권 찬 공기 직접 흡입 시", font=font_body, fill=(250, 204, 21), anchor="mm")
        draw.text((center_x, y1 + 315), "기관지 & 관상동맥 급경련 유발!", font=font_body, fill=(248, 113, 113), anchor="mm")
        
        # 대안 박스
        draw.rounded_rectangle([(x1 + 30, y1 + 410), (x2 - 30, y2 - 30)], radius=20, fill=(22, 101, 52), outline=(34, 197, 94), width=2)
        draw.text((center_x, y1 + 465), "✅ 올바른 겨울 운동법:", font=font_body, fill=(255, 255, 255), anchor="mm")
        draw.text((center_x, y1 + 535), "1. 해가 충분히 뜬 오전 11시 이후", font=font_small, fill=(220, 252, 231), anchor="mm")
        draw.text((center_x, y1 + 605), "2. 실내 스트레칭 및 맨몸 운동", font=font_small, fill=(220, 252, 231), anchor="mm")
        draw.text((center_x, y1 + 675), "3. 모자·장갑·넥워머 완전 무장", font=font_small, fill=(250, 204, 21), anchor="mm")

    elif scene_idx == 5:
        # [씬 5: 가족 공유 & 실천 독려]
        draw.rounded_rectangle([(x1 + 30, y1 + 30), (x2 - 30, y1 + 100)], radius=16, fill=(147, 51, 234)) # 퍼플
        draw.text((center_x, y1 + 65), "가족 건강 선물하기", font=font_title, fill=(255, 255, 255), anchor="mm")
        
        draw.rounded_rectangle([(x1 + 30, y1 + 130), (x2 - 30, y1 + 320)], radius=20, fill=(15, 23, 42, 240), outline=(168, 85, 247), width=2)
        draw.text((center_x, y1 + 185), "💌 소중한 부모님께 공유", font=font_title, fill=(244, 114, 182), anchor="mm")
        draw.text((center_x, y1 + 245), "3분 습관이 생명을 지킵니다", font=font_body, fill=(250, 204, 21), anchor="mm")
        draw.text((center_x, y1 + 285), "내일 아침 기상부터 함께 실천해요", font=font_small, fill=(226, 232, 240), anchor="mm")
        
        draw.rounded_rectangle([(x1 + 30, y1 + 350), (x2 - 30, y2 - 30)], radius=20, fill=(30, 58, 138))
        draw.text((center_x, y1 + 410), "닥터 김승태 & 겅태의", font=font_body, fill=(203, 213, 225), anchor="mm")
        draw.text((center_x, y1 + 460), "응급실 1분 건강 클립", font=font_title, fill=(255, 255, 255), anchor="mm")

def create_scene_frame_v2(scene_idx: int, badge: str, main_text: str, sub_text: str, char_path: str, out_img: str, width: int = 1080, height: int = 1920):
    """
    신규 레이아웃:
    - 상단 헤더 & 배지
    - 중단 좌측: 겅태 캐릭터 (호스트/설명자)
    - 중단 우측: 상황별 의학 그래픽 카드
    - 하단: 고시인성 풀와이드 자막 바
    """
    img = Image.new("RGBA", (width, height), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)
    
    # 배경 그라데이션 조명
    draw.ellipse([(-100, -100), (width + 100, 500)], fill=(30, 58, 138, 255))
    
    # 폰트 로드
    font_header = ImageFont.truetype(FONT_BOLD, 42)
    font_badge = ImageFont.truetype(FONT_BOLD, 36)
    font_card_title = ImageFont.truetype(FONT_BOLD, 38)
    font_card_body = ImageFont.truetype(FONT_BOLD, 32)
    font_card_hl = ImageFont.truetype(FONT_BOLD, 46)
    font_card_small = ImageFont.truetype(FONT_BOLD, 26)
    font_sub_main = ImageFont.truetype(FONT_BOLD, 54)
    font_sub_sub = ImageFont.truetype(FONT_BOLD, 38)
    
    # 1. 상단 브랜딩 바
    header_text = "닥터 김승태의 1분 응급실 클립"
    draw.rounded_rectangle([(160, 100), (width - 160, 175)], radius=36, fill=(30, 41, 59, 230), outline=(59, 130, 246), width=2)
    draw.text((width // 2, 137), header_text, font=font_header, fill=(255, 255, 255), anchor="mm")
    
    # 2. 씬 배지
    if badge:
        draw.rounded_rectangle([(120, 205), (width - 120, 275)], radius=18, fill=(220, 38, 38) if "경고" in badge or "금지" in badge or "주의" in badge else (37, 99, 235))
        draw.text((width // 2, 240), badge, font=font_badge, fill=(255, 255, 255), anchor="mm")
        
    # 3. 중단 좌측: 겅태 캐릭터 (호스트 역할, x: 50~450, y: 400~1180)
    char_box_x = 50
    char_box_y = 340
    char_w = 400
    char_h = 820
    
    # 캐릭터 액자 카드
    draw.rounded_rectangle([(char_box_x, char_box_y), (char_box_x + char_w, char_box_y + char_h)], radius=24, fill=(15, 23, 42, 200), outline=(71, 85, 105), width=2)
    draw.text((char_box_x + char_w // 2, char_box_y + 40), "메디컬 호스트 겅태", font=font_card_small, fill=(148, 163, 184), anchor="mm")
    
    # 캐릭터 이미지 합성
    if os.path.exists(char_path):
        mascot = Image.open(char_path).convert("RGBA")
        mascot.thumbnail((360, 520), Image.Resampling.LANCZOS)
        m_x = char_box_x + (char_w - mascot.width) // 2
        m_y = char_box_y + 100
        img.paste(mascot, (m_x, m_y), mascot)
        
    draw.rounded_rectangle([(char_box_x + 30, char_box_y + char_h - 110), (char_box_x + char_w - 30, char_box_y + char_h - 40)], radius=16, fill=(30, 58, 138))
    draw.text((char_box_x + char_w // 2, char_box_y + char_h - 75), "응급의학과 비서", font=font_card_small, fill=(255, 255, 255), anchor="mm")
    
    # 4. 중단 우측: 상황별 의학 그래픽 카드 (x: 480~1030, y: 340~1160)
    draw_situation_card(
        draw, scene_idx,
        x1=480, y1=char_box_y, x2=1030, y2=char_box_y + char_h,
        font_title=font_card_title, font_body=font_card_body, font_highlight=font_card_hl, font_small=font_card_small
    )
    
    # 5. 하단 고시인성 자막 바 (y: 1220 ~ 1780)
    sub_top = 1220
    sub_bottom = 1780
    draw.rounded_rectangle([(60, sub_top), (width - 60, sub_bottom)], radius=32, fill=(15, 23, 42, 240), outline=(96, 165, 250), width=3)
    
    lines = main_text.split("\n")
    y_c = sub_top + 90
    for l in lines:
        draw.text((width // 2, y_c), l.strip(), font=font_sub_main, fill=(250, 204, 21), anchor="mm") # 옐로우 강조
        y_c += 85
        
    y_c += 20
    s_lines = sub_text.split("\n")
    for sl in s_lines:
        draw.text((width // 2, y_c), sl.strip(), font=font_sub_sub, fill=(241, 245, 249), anchor="mm")
        y_c += 65
        
    draw.text((width // 2, sub_bottom - 45), "소중한 분들께 공유해 주세요 📲", font=font_card_small, fill=(148, 163, 184), anchor="mm")
    
    img.convert("RGB").save(out_img, "JPEG", quality=95)

def render_scene_video_v2(img_path: str, audio_path: str, out_mp4: str, duration: float):
    cmd = [
        FFMPEG_PATH, "-y",
        "-loop", "1",
        "-i", img_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-t", str(duration + 0.3),
        "-shortest",
        out_mp4
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def render_full_shorts_v2(scenes: list, output_mp4: str, temp_dir: str = "/tmp/shorts_build_v2"):
    os.makedirs(temp_dir, exist_ok=True)
    scene_videos = []
    
    print(f"\n[Video Engine v2] 좌측 호스트 + 우측 상황 카드 레이아웃 렌더링 시작...")
    
    for idx, sc in enumerate(scenes):
        scene_idx = idx + 1
        audio_file = os.path.join(temp_dir, f"audio_{scene_idx}.mp3")
        img_file = os.path.join(temp_dir, f"frame_{scene_idx}.jpg")
        scene_mp4 = os.path.join(temp_dir, f"scene_{scene_idx}.mp4")
        
        asyncio.run(generate_speech(sc["voice"], audio_file))
        duration = get_audio_duration(audio_file)
        
        create_scene_frame_v2(
            scene_idx=scene_idx,
            badge=sc.get("badge", ""),
            main_text=sc.get("main_text", ""),
            sub_text=sc.get("sub_text", ""),
            char_path=sc.get("character"),
            out_img=img_file
        )
        
        render_scene_video_v2(img_file, audio_file, scene_mp4, duration)
        scene_videos.append(scene_mp4)
        print(f"  - 씬 {scene_idx}/{len(scenes)} 완료 ({duration:.1f}초): {sc.get('badge')}")
        
    concat_txt = os.path.join(temp_dir, "concat.txt")
    with open(concat_txt, "w") as f:
        for v in scene_videos:
            f.write(f"file '{v}'\n")
            
    concat_cmd = [
        FFMPEG_PATH, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",
        output_mp4
    ]
    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"\n✅ 최종 개편 릴스/쇼츠 완성! -> {output_mp4}")
    return output_mp4

def build_v2_sample(style: str = "both", day: int = 1):
    """
    쇼츠 스타일 선택 지원:
    - standard: 기존 겅태 3D 마스코트 + 우측 상황 카드
    - anime: 90년대 일본 레트로 셀 애니메이션 만화 스타일
    - both: 일반과 애니 버전 2개 모두 생성 (기본 권장)
    """
    outputs = {}
    
    if day == 1:
        if style in ("standard", "both"):
            scenes_standard = [
                {
                    "badge": "⚠️ 긴급 주의보",
                    "character": f"{CHAR_DIR}/01_doctor_front.png" if os.path.exists(f"{CHAR_DIR}/01_doctor_front.png") else f"{CHAR_DIR}/doctor_front.png",
                    "main_text": "겨울철 아침에\n벌떡 일어나지 마세요!",
                    "sub_text": "순간적으로 혈압이 15mmHg 치솟습니다",
                    "voice": "겨울철 아침, 알람 울렸다고 이불 밖으로 벌떡 일어나시는 분들, 정말 위험합니다."
                },
                {
                    "badge": "🏥 응급실 현장 리포트",
                    "character": f"{CHAR_DIR}/06_sweat_worry.png" if os.path.exists(f"{CHAR_DIR}/06_sweat_worry.png") else f"{CHAR_DIR}/expr_worried.png",
                    "main_text": "오전 6시 ~ 9시\n심뇌혈관 환자 급증",
                    "sub_text": "밤새 끈적해진 혈액 + 찬 공기 노출",
                    "voice": "응급실에 있으면 매년 겨울 기온이 뚝 떨어질 때마다 아침 6시에서 9시 사이에 실려 오시는 분들을 너무 많이 봅니다."
                },
                {
                    "badge": "💡 의사의 3분 처방",
                    "character": f"{CHAR_DIR}/02_doctor_point.png" if os.path.exists(f"{CHAR_DIR}/02_doctor_point.png") else f"{CHAR_DIR}/pose_point.png",
                    "main_text": "내일부터 딱 3분!\n기상 공식을 지키세요",
                    "sub_text": "1. 손발 털기  2. 걸터앉기  3. 겉옷 입기",
                    "voice": "내일부터 딱 3분만 지켜보세요. 누운 채로 기지개 켜고 손발 1분 털기, 침대에 걸터앉아 1분 호흡하기, 그리고 겉옷 입고 방 밖으로 나가기."
                },
                {
                    "badge": "❌ 절대 금지",
                    "character": f"{CHAR_DIR}/07_doctor_surprise.png" if os.path.exists(f"{CHAR_DIR}/07_doctor_surprise.png") else f"{CHAR_DIR}/expr_surprise.png",
                    "main_text": "겨울철 새벽 조깅은\n보약이 아니라 독입니다",
                    "sub_text": "운동은 반드시 해 뜬 낮이나 실내에서!",
                    "voice": "그리고 새벽 야외 조깅은 겨울철엔 보약이 아니라 독입니다. 운동은 해 뜨고 낮에 하세요."
                },
                {
                    "badge": "📲 가족 공유 필수",
                    "character": f"{CHAR_DIR}/04_cheer_jump.png" if os.path.exists(f"{CHAR_DIR}/04_cheer_jump.png") else f"{CHAR_DIR}/pose_cheer.png",
                    "main_text": "소중한 부모님께\n지금 바로 공유하세요!",
                    "sub_text": "3분 습관 하나가 소중한 생명을 지킵니다",
                    "voice": "이 3분 습관 하나가 소중한 생명을 지킵니다. 부모님께 지금 꼭 공유해 주세요."
                }
            ]
            out_std = "/workspace/downloads/Day1_겨울철_혈압_주의보_겅태_쇼츠_데모_v2.mp4"
            render_full_shorts_v2(scenes_standard, out_std)
            outputs["standard"] = out_std
            
            # 깃허브 content 폴더 동기화
            dest_dir = "/workspace/work/content-automation-engine/content/2026-11-09-05/instagram"
            if os.path.exists(dest_dir):
                subprocess.run(["cp", out_std, os.path.join(dest_dir, "standard_reel_video.mp4")])
                subprocess.run(["cp", out_std, os.path.join(dest_dir, "reel_video.mp4")])
                
        if style in ("anime", "both"):
            try:
                from engine.anime_video_engine import build_day1_anime_shorts
                build_day1_anime_shorts()
                outputs["anime"] = "/workspace/downloads/Day1_겨울철_혈압_주의보_90s애니_쇼츠.mp4"
            except Exception as e:
                print(f"⚠️ 애니 쇼츠 렌더 오류: {e}")
                
    elif day == 2:
        if style in ("standard", "both"):
            try:
                subprocess.run(["python3", "render_day2_video.py"], check=True)
                outputs["standard"] = "/workspace/downloads/Day2_겨울철_당뇨_인슐린_발관리_겅태_쇼츠.mp4"
            except Exception as e:
                print(f"⚠️ Day 2 일반 쇼츠 렌더 오류: {e}")
                
        if style in ("anime", "both"):
            try:
                from engine.anime_video_engine import build_day2_anime_shorts
                outputs["anime"] = build_day2_anime_shorts()
            except Exception as e:
                print(f"⚠️ Day 2 애니 쇼츠 렌더 오류: {e}")
                
    return outputs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shorts & Reels Video Engine")
    parser.add_argument("--style", choices=["standard", "anime", "both"], default="both", help="쇼츠 비주얼 스타일 선택 (기본: both)")
    parser.add_argument("--day", type=int, default=1, choices=[1, 2], help="제작할 Day 번호 (기본: 1)")
    args = parser.parse_args()
    build_v2_sample(style=args.style, day=args.day)
