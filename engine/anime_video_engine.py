# -*- coding: utf-8 -*-
"""
90s Retro Japanese Anime & Manga Style Video Engine
- 90년대 일본 레트로 셀 애니메이션 및 만화 비주얼
- VHS REC 타임코드, CRT 스캔라인, 만화 효과음(SFX) 배지, 옐로우 볼드 자막
- Edge-TTS 한국어 음성 (ko-KR-InJoonNeural) 동기화
- 1080x1920 9:16 인스타그램 릴스 & 유튜브 쇼츠 표준 규격
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FFMPEG_PATH = "/usr/local/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
if not os.path.exists(FFMPEG_PATH):
    FFMPEG_PATH = "ffmpeg"

FONT_BOLD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts", "NanumGothic-Bold.ttf"))
if not os.path.exists(FONT_BOLD):
    FONT_BOLD = "/workspace/fonts/NanumGothic-Bold.ttf"

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

def draw_text_with_outline(draw, pos, text, font, fill_color, outline_color, outline_width=3, anchor="mm"):
    x, y = pos
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color, anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill_color, anchor=anchor)

def create_anime_scene_frame(
    scene_idx: int,
    badge: str,
    sfx_text: str,
    main_text: str,
    sub_text: str,
    anime_img_path: str,
    out_img: str,
    width: int = 1080,
    height: int = 1920
):
    """90년대 일본 레트로 셀 애니메이션 스타일 씬 프레임 생성"""
    img = Image.new("RGBA", (width, height), (10, 15, 29, 255))
    draw = ImageDraw.Draw(img)
    
    font_vhs = ImageFont.truetype(FONT_BOLD, 30)
    font_header = ImageFont.truetype(FONT_BOLD, 38)
    font_badge = ImageFont.truetype(FONT_BOLD, 32)
    font_sfx = ImageFont.truetype(FONT_BOLD, 54)
    font_sub_main = ImageFont.truetype(FONT_BOLD, 50)
    font_sub_sub = ImageFont.truetype(FONT_BOLD, 34)
    font_small = ImageFont.truetype(FONT_BOLD, 26)
    
    # 1. 상단 레트로 VHS TV 오버레이 (y: 60 ~ 220)
    draw.ellipse([(80, 80), (106, 106)], fill=(239, 68, 68))
    draw.text((120, 93), "REC  SP 0:00:24", font=font_vhs, fill=(241, 245, 249), anchor="lm")
    draw.text((width - 80, 93), "1995.11.09 HI-FI", font=font_vhs, fill=(148, 163, 184), anchor="rm")
    
    draw.rounded_rectangle([(60, 130), (width - 60, 205)], radius=18, fill=(30, 41, 59, 230), outline=(245, 158, 11), width=2)
    draw.text((width // 2, 167), "⚡ 닥터 김승태의 90s 레트로 응급실 만화 ⚡", font=font_header, fill=(255, 255, 255), anchor="mm")
    
    if badge:
        draw.rounded_rectangle([(100, 225), (width - 100, 285)], radius=14, fill=(220, 38, 38) if ("경고" in badge or "금지" in badge or "위험" in badge) else (14, 116, 144))
        draw.text((width // 2, 255), badge, font=font_badge, fill=(255, 255, 255), anchor="mm")
        
    # 2. 메인 애니메이션 셀 아트 프레임 (y: 310 ~ 1240)
    frame_x1, frame_y1 = 60, 310
    frame_x2, frame_y2 = width - 60, 1240
    frame_w = frame_x2 - frame_x1
    frame_h = frame_y2 - frame_y1
    
    draw.rounded_rectangle([(frame_x1 - 10, frame_y1 - 10), (frame_x2 + 10, frame_y2 + 10)], radius=32, fill=(2, 6, 23), outline=(71, 85, 105), width=3)
    
    if os.path.exists(anime_img_path):
        anime_raw = Image.open(anime_img_path).convert("RGBA")
        img_ratio = anime_raw.width / anime_raw.height
        target_ratio = frame_w / frame_h
        
        if img_ratio > target_ratio:
            new_h = frame_h
            new_w = int(new_h * img_ratio)
        else:
            new_w = frame_w
            new_h = int(new_w / img_ratio)
            
        anime_resized = anime_raw.resize((new_w, new_h), Image.Resampling.LANCZOS)
        crop_x = (new_w - frame_w) // 2
        crop_y = (new_h - frame_h) // 2
        anime_cropped = anime_resized.crop((crop_x, crop_y, crop_x + frame_w, crop_y + frame_h))
        
        mask = Image.new("L", (frame_w, frame_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (frame_w, frame_h)], radius=24, fill=255)
        
        img.paste(anime_cropped, (frame_x1, frame_y1), mask)
        
        # CRT 스캔라인 레이어
        scanline_overlay = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
        scan_draw = ImageDraw.Draw(scanline_overlay)
        for y_scan in range(0, frame_h, 6):
            scan_draw.line([(0, y_scan), (frame_w, y_scan)], fill=(0, 0, 0, 45), width=1)
        img.paste(scanline_overlay, (frame_x1, frame_y1), scanline_overlay)
        
    if sfx_text:
        sfx_box_x = frame_x2 - 240
        sfx_box_y = frame_y1 + 40
        draw.rounded_rectangle([(sfx_box_x, sfx_box_y), (sfx_box_x + 210, sfx_box_y + 90)], radius=20, fill=(250, 204, 21), outline=(220, 38, 38), width=4)
        draw.text((sfx_box_x + 105, sfx_box_y + 45), sfx_text, font=font_sfx, fill=(220, 38, 38), anchor="mm")
        
    # 3. 하단 레트로 만화 자막 박스 (y: 1270 ~ 1820)
    sub_top = 1270
    sub_bottom = 1820
    draw.rounded_rectangle([(60, sub_top), (width - 60, sub_bottom)], radius=28, fill=(15, 23, 42, 245), outline=(234, 179, 8), width=3)
    
    lines = main_text.split("\n")
    y_c = sub_top + 100
    for l in lines:
        draw_text_with_outline(
            draw, (width // 2, y_c), l.strip(),
            font=font_sub_main, fill_color=(254, 240, 138), outline_color=(0, 0, 0), outline_width=4, anchor="mm"
        )
        y_c += 85
        
    y_c += 15
    s_lines = sub_text.split("\n")
    for sl in s_lines:
        draw_text_with_outline(
            draw, (width // 2, y_c), sl.strip(),
            font=font_sub_sub, fill_color=(255, 255, 255), outline_color=(15, 23, 42), outline_width=3, anchor="mm"
        )
        y_c += 60
        
    draw.text((width // 2, sub_bottom - 45), "닥터 김승태 × 90s RETRO MANGA ANIME 📺", font=font_small, fill=(148, 163, 184), anchor="mm")
    
    os.makedirs(os.path.dirname(out_img), exist_ok=True)
    img.convert("RGB").save(out_img, "JPEG", quality=95)

def render_scene_video(img_path: str, audio_path: str, out_mp4: str, duration: float):
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

def render_anime_shorts(scenes: list, output_mp4: str, temp_dir: str = "/tmp/anime_shorts_build"):
    os.makedirs(temp_dir, exist_ok=True)
    scene_videos = []
    
    print(f"\n[Anime Video Engine] 90s 일본 레트로 만화 스타일 쇼츠 렌더링 시작...")
    
    for idx, sc in enumerate(scenes):
        scene_idx = idx + 1
        audio_file = os.path.join(temp_dir, f"audio_{scene_idx}.mp3")
        img_file = os.path.join(temp_dir, f"frame_{scene_idx}.jpg")
        scene_mp4 = os.path.join(temp_dir, f"scene_{scene_idx}.mp4")
        
        asyncio.run(generate_speech(sc["voice"], audio_file))
        duration = get_audio_duration(audio_file)
        
        create_anime_scene_frame(
            scene_idx=scene_idx,
            badge=sc.get("badge", ""),
            sfx_text=sc.get("sfx", ""),
            main_text=sc.get("main_text", ""),
            sub_text=sc.get("sub_text", ""),
            anime_img_path=sc.get("anime_img", ""),
            out_img=img_file
        )
        
        render_scene_video(img_file, audio_file, scene_mp4, duration)
        scene_videos.append(scene_mp4)
        print(f"  - 씬 {scene_idx}/{len(scenes)} 렌더 완료 ({duration:.1f}초): {sc.get('badge')}")
        
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
    print(f"\n✅ 90s 레트로 애니 쇼츠 완성! -> {output_mp4}")
    return output_mp4

def build_day1_anime_shorts():
    scenes = [
        {
            "badge": "⚠️ 긴급 주의보",
            "sfx": "쿵!!",
            "anime_img": "/workspace/assets/anime/day1/scene1_wakeup.png",
            "main_text": "겨울철 아침에\n벌떡 일어나지 마세요!",
            "sub_text": "순간적으로 혈압이 15mmHg 치솟습니다",
            "voice": "겨울철 아침, 알람 울렸다고 이불 밖으로 벌떡 일어나시는 분들, 정말 위험합니다."
        },
        {
            "badge": "🏥 응급실 현장 리포트",
            "sfx": "위잉!!",
            "anime_img": "/workspace/assets/anime/day1/scene2_er.png",
            "main_text": "오전 6시 ~ 9시\n심뇌혈관 환자 급증",
            "sub_text": "밤새 끈적해진 혈액 + 찬 공기 노출",
            "voice": "응급실에 있으면 매년 겨울 기온이 뚝 떨어질 때마다 아침 6시에서 9시 사이에 실려 오시는 분들을 너무 많이 봅니다."
        },
        {
            "badge": "💡 의사의 3분 처방",
            "sfx": "반짝✨",
            "anime_img": "/workspace/assets/anime/day1/scene3_doctor.png",
            "main_text": "내일부터 딱 3분!\n기상 공식을 지키세요",
            "sub_text": "1. 손발 털기  2. 걸터앉기  3. 겉옷 입기",
            "voice": "내일부터 딱 3분만 지켜보세요. 누운 채로 기지개 켜고 손발 1분 털기, 침대에 걸터앉아 1분 호흡하기, 그리고 겉옷 입고 방 밖으로 나가기."
        },
        {
            "badge": "❌ 절대 금지",
            "sfx": "콰앙!!",
            "anime_img": "/workspace/assets/anime/day1/scene4_jogging.png",
            "main_text": "겨울철 새벽 조깅은\n보약이 아니라 독입니다",
            "sub_text": "운동은 반드시 해 뜬 낮이나 실내에서!",
            "voice": "그리고 새벽 야외 조깅은 겨울철엔 보약이 아니라 독입니다. 운동은 해 뜨고 낮에 하세요."
        },
        {
            "badge": "📲 가족 공유 필수",
            "sfx": "훈훈~",
            "anime_img": "/workspace/assets/anime/day1/scene5_family.png",
            "main_text": "소중한 부모님께\n지금 바로 공유하세요!",
            "sub_text": "3분 습관 하나가 소중한 생명을 지킵니다",
            "voice": "이 3분 습관 하나가 소중한 생명을 지킵니다. 부모님께 지금 꼭 공유해 주세요."
        }
    ]
    
    out_file = "/workspace/downloads/Day1_겨울철_혈압_주의보_90s애니_쇼츠.mp4"
    render_anime_shorts(scenes, out_file)
    
    # 저장소 동기화
    dest_dir = "/workspace/work/content-automation-engine/content/2026-11-09-05/instagram"
    if os.path.exists(dest_dir):
        subprocess.run(["cp", out_file, os.path.join(dest_dir, "anime_reel_video.mp4")])
        print(f"✅ 애니 쇼츠 깃허브 아카이브 완료: anime_reel_video.mp4")
    return out_file

def build_day2_anime_shorts():
    scenes = [
        {
            "badge": "⚠️ 긴급 경고",
            "sfx": "화들짝!!",
            "anime_img": "/workspace/assets/anime/day2/scene1_heatpad.png",
            "main_text": "전기장판에 발 대고\n절대 주무시지 마세요!",
            "sub_text": "신경 마비로 3도 저온 화상 위험",
            "voice": "당뇨 환자분들, 겨울철에 전기장판이나 핫팩 발에 대고 주무시면 발을 잃을 수 있습니다."
        },
        {
            "badge": "❄️ 한파 인슐린 쇼크",
            "sfx": "위잉!!",
            "anime_img": "/workspace/assets/anime/day2/scene2_insulin_shock.png",
            "main_text": "추위에 모세혈관 수축!\n오후 급성 저혈당 쇼크",
            "sub_text": "인슐린 흡수 지연 후 한꺼번에 방출",
            "voice": "게다가 날씨가 추우면 피부 모세혈관이 수축해서, 아침에 맞은 인슐린이 흡수가 안 되다가 오후에 한꺼번에 퍼져 급성 저혈당 쇼크가 옵니다."
        },
        {
            "badge": "💡 의사의 3대 처방",
            "sfx": "반짝✨",
            "anime_img": "/workspace/assets/anime/day2/scene3_doctor_mirror.png",
            "main_text": "매일 저녁 손거울로\n발바닥 상처 확인!",
            "sub_text": "1. 맨살 접촉 금지  2. 손거울 점검  3. 인슐린 실온 보관",
            "voice": "딱 3가지만 기억하세요! 첫째, 전기장판 맨살 접촉 금지. 둘째, 매일 저녁 손거울로 발바닥 상처 확인. 셋째, 인슐린 펜은 절대 얼리지 말고 실온 안주머니 보관!"
        },
        {
            "badge": "🚨 응급실 직행 신호",
            "sfx": "콰앙!!",
            "anime_img": "/workspace/assets/anime/day2/scene4_warning_foot.png",
            "main_text": "작은 물집·피멍 생기면\n집에서 절대 짜지 마세요!",
            "sub_text": "세균 감염·괴사 위험, 즉시 병원으로 달려가야",
            "voice": "발에 작은 물집이나 피멍이 보이면 집에서 짜지 마시고 그 즉시 병원으로 달려오셔야 합니다."
        },
        {
            "badge": "📲 부모님 필수 공유",
            "sfx": "훈훈~",
            "anime_img": "/workspace/assets/anime/day2/scene5_family_socks.png",
            "main_text": "소중한 부모님의\n평생 걸음을 지켜주세요!",
            "sub_text": "오늘 저녁 부모님 발 한번 꼭 살펴봐 드리세요",
            "voice": "매일 저녁 발을 살피는 작은 습관이 평생 보행을 지킵니다. 부모님께 지금 꼭 공유해 주세요."
        }
    ]
    
    out_file = "/workspace/downloads/Day2_겨울철_당뇨_인슐린_발관리_90s애니_쇼츠.mp4"
    render_anime_shorts(scenes, out_file, temp_dir="/tmp/day2_anime_shorts_build")
    
    # 저장소 동기화
    dest_dir = "/workspace/work/content-automation-engine/content/2026-11-09-06/instagram"
    if os.path.exists(dest_dir):
        subprocess.run(["cp", out_file, os.path.join(dest_dir, "anime_reel_video.mp4")])
        print(f"✅ Day 2 애니 쇼츠 깃허브 아카이브 완료: anime_reel_video.mp4")
    return out_file

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="90s Retro Anime Video Engine")
    parser.add_argument("--day", type=int, default=1, choices=[1, 2], help="제작할 Day 번호 (기본: 1)")
    args = parser.parse_args()
    
    if args.day == 1:
        build_day1_anime_shorts()
    elif args.day == 2:
        build_day2_anime_shorts()

