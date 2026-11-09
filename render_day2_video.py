#!/usr/bin/env python3
"""
Renders Day 2 Shorts Video (Left Host Geongtae + Right Situation Cards)
"""

import os
import sys
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.video_engine import (
    CHAR_DIR, FFMPEG_PATH, FONT_BOLD,
    generate_speech, get_audio_duration, render_scene_video_v2
)
FONT_PATH = FONT_BOLD

DAY2_SCENES = [
    {
        "idx": 1,
        "badge": "⚠️ 긴급 경고",
        "audio_text": "당뇨 환자분들, 겨울철에 전기장판이나 핫팩 발에 대고 주무시면 발을 잃을 수 있습니다!",
        "main_sub": "겨울철 당뇨 환자!\n전기장판에 발 대지 마세요!",
        "sub_desc": "살이 3도로 익어가도 통증을 전혀 못 느낍니다",
        "char": f"{CHAR_DIR}/01_doctor_front.png",
        "card_title": "당뇨발 저온 화상 위험",
        "card_lines": [
            ("온열기구 접촉 (42~45°C)", "#ef4444"),
            ("말초신경 마비로 통증 無", "#f59e0b"),
            ("조용한 심부 진피 괴사 발생", "#dc2626")
        ]
    },
    {
        "idx": 2,
        "badge": "🏥 응급실 리포트",
        "audio_text": "당뇨병으로 발끝 신경이 둔해지면 살이 타들어가는데도 전혀 아프지 않아 괴사로 실려 오십니다.",
        "main_sub": "응급실 당뇨발 환자의 50%\n원인은 '전기장판 저온 화상'",
        "sub_desc": "통각 소실로 2~3시간 동안 방치되어 심부 괴사 진행",
        "char": f"{CHAR_DIR}/06_sweat_worry.png",
        "card_title": "응급실 족부 궤양 통계",
        "card_lines": [
            ("겨울철 당뇨발 응급 내원 급증", "#3b82f6"),
            ("Wagner Grade 2~3 중증 진행", "#ef4444"),
            ("초기 미세 상처 방치 시 절단 위험", "#b91c1c")
        ]
    },
    {
        "idx": 3,
        "badge": "💡 의사의 3대 처방",
        "audio_text": "첫째, 전기장판 맨살 접촉 금지! 둘째, 매일 저녁 거울 발바닥 점검! 셋째, 인슐린은 실온 안주머니 보관!",
        "main_sub": "겨울철 당뇨발 3대 안전 수칙\n매일 저녁 거울을 보세요!",
        "sub_desc": "1. 간접 온열 2. 매일 거울 점검 3. 인슐린 실온 보관",
        "char": f"{CHAR_DIR}/02_doctor_point.png",
        "card_title": "의사의 3대 당뇨 처방전",
        "card_lines": [
            ("1. 두꺼운 패드 깔고 간접 난방", "#10b981"),
            ("2. 매일 저녁 손거울 발바닥 확인", "#f59e0b"),
            ("3. 인슐린 펜 실온(15~25℃) 보관", "#3b82f6")
        ]
    },
    {
        "idx": 4,
        "badge": "❄️ 인슐린 흡수 지연",
        "audio_text": "추운 날씨엔 피하 모세혈관이 수축해 인슐린 흡수가 지연되다 오후에 한꺼번에 퍼져 급성 저혈당이 옵니다.",
        "main_sub": "한파 속 혈당 롤러코스터!\n식후 고혈당 ➔ 오후 저혈당 쇼크",
        "sub_desc": "피하 모세혈관 수축으로 인슐린 혈류 흡수 지연",
        "char": f"{CHAR_DIR}/07_doctor_surprise.png",
        "card_title": "피하 혈류 수축 메커니즘",
        "card_lines": [
            ("기온 급락 시 피부 모세혈관 수축", "#3b82f6"),
            ("주사된 인슐린 피하 체류 지연", "#ef4444"),
            ("실내 재확장 시 급성 저혈당 급습", "#dc2626")
        ]
    },
    {
        "idx": 5,
        "badge": "📲 가족 공유 필수",
        "audio_text": "매일 저녁 발을 살피는 1분의 습관이 평생 보행을 지킵니다. 주변 당뇨 환자분들께 지금 꼭 공유해 주세요!",
        "main_sub": "매일 저녁 거울로 발바닥 확인!\n작은 습관이 평생 보행을 지킵니다",
        "sub_desc": "당뇨가 있는 부모님과 소중한 분들께 꼭 전해 주세요",
        "char": f"{CHAR_DIR}/04_doctor_cheer.png",
        "card_title": "당뇨 가족 필수 공유",
        "card_lines": [
            ("실내에서도 밝은색 면양말 착용", "#10b981"),
            ("발가락 사이는 보습제 바르지 말 것", "#3b82f6"),
            ("물집 발견 시 즉시 병원 내원", "#ef4444")
        ]
    }
]


def draw_day2_card(draw, scene, x1, y1, x2, y2, font_title, font_body, font_small):
    # Base card
    draw.rounded_rectangle([x1, y1, x2, y2], radius=24, fill=(24, 34, 53), outline=(51, 65, 85), width=2)
    center_x = (x1 + x2) // 2

    # Title pill
    draw.rounded_rectangle([x1 + 20, y1 + 24, x2 - 20, y1 + 96], radius=16, fill=(37, 99, 235))
    draw.text((center_x, y1 + 60), scene["card_title"], font=font_title, fill=(255, 255, 255), anchor="mm")

    # Item rows
    lines = scene["card_lines"]
    box_height = 120
    gap = 20
    start_y = y1 + 120

    for i, (text, color_hex) in enumerate(lines):
        by1 = start_y + i * (box_height + gap)
        by2 = by1 + box_height
        
        # Parse hex color
        h = color_hex.lstrip("#")
        rgb = tuple(int(h[j:j+2], 16) for j in (0, 2, 4))

        draw.rounded_rectangle([x1 + 20, by1, x2 - 20, by2], radius=16, fill=(15, 23, 42), outline=rgb, width=2)
        # Indicator tag
        draw.rounded_rectangle([x1 + 36, by1 + 20, x1 + 80, by2 - 20], radius=8, fill=rgb)
        draw.text((x1 + 58, (by1 + by2) // 2), f"0{i+1}", font=font_small, fill=(255, 255, 255), anchor="mm")
        
        draw.text((x1 + 100, (by1 + by2) // 2), text, font=font_body, fill=(255, 255, 255), anchor="lm")


def create_day2_frame(scene, out_img, width=1080, height=1920):
    img = Image.new("RGBA", (width, height), (10, 15, 30, 255))
    draw = ImageDraw.Draw(img)

    f_brand = ImageFont.truetype(FONT_PATH, 42)
    f_badge = ImageFont.truetype(FONT_PATH, 38)
    f_title = ImageFont.truetype(FONT_PATH, 34)
    f_body = ImageFont.truetype(FONT_PATH, 25)
    f_small = ImageFont.truetype(FONT_PATH, 22)
    f_sub_main = ImageFont.truetype(FONT_PATH, 48)
    f_sub_desc = ImageFont.truetype(FONT_PATH, 32)
    f_host = ImageFont.truetype(FONT_PATH, 28)

    # 1. Top Branding Bar
    draw.rounded_rectangle([160, 100, width - 160, 180], radius=40, fill=(30, 41, 59), outline=(71, 85, 105), width=2)
    draw.text((width // 2, 140), "닥터 김승태의 1분 응급실 클립", font=f_brand, fill=(255, 255, 255), anchor="mm")

    # 2. Badge
    draw.rounded_rectangle([120, 210, width - 120, 270], radius=16, fill=(37, 99, 235))
    draw.text((width // 2, 240), scene["badge"], font=f_badge, fill=(255, 255, 255), anchor="mm")

    # 3. Middle Left: Medical Host Geongtae Card
    lx1, ly1, lx2, ly2 = 50, 350, 450, 1160
    draw.rounded_rectangle([lx1, ly1, lx2, ly2], radius=24, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
    draw.text(((lx1 + lx2) // 2, ly1 + 45), "메디컬 호스트 겅태", font=f_host, fill=(148, 163, 184), anchor="mm")

    char_p = scene["char"]
    if os.path.exists(char_p):
        c_img = Image.open(char_p).convert("RGBA")
        c_w, c_h = c_img.size
        target_w = 340
        target_h = int(c_h * (target_w / c_w))
        if target_h > 460:
            target_h = 460
            target_w = int(c_w * (target_h / c_h))
        c_resized = c_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        cx = lx1 + (lx2 - lx1 - target_w) // 2
        cy = ly1 + 130 + (480 - target_h) // 2
        img.paste(c_resized, (cx, cy), c_resized)

    # Host role pill
    draw.rounded_rectangle([lx1 + 30, ly2 - 110, lx2 - 30, ly2 - 40], radius=14, fill=(30, 64, 175))
    draw.text(((lx1 + lx2) // 2, ly2 - 75), "응급의학과 비서", font=f_title, fill=(255, 255, 255), anchor="mm")

    # 4. Middle Right: Situation Card
    rx1, ry1, rx2, ry2 = 480, 350, width - 50, 1160
    draw_day2_card(draw, scene, rx1, ry1, rx2, ry2, f_title, f_body, f_small)

    # 5. Bottom Subtitle Card
    bx1, by1, bx2, by2 = 60, 1220, width - 60, 1780
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=28, fill=(15, 23, 42), outline=(37, 99, 235), width=2)

    sub_lines = scene["main_sub"].split("\n")
    if len(sub_lines) == 1:
        draw.text((width // 2, by1 + 130), sub_lines[0], font=f_sub_main, fill=(250, 204, 21), anchor="mm")
    else:
        draw.text((width // 2, by1 + 95), sub_lines[0], font=f_sub_main, fill=(250, 204, 21), anchor="mm")
        draw.text((width // 2, by1 + 165), sub_lines[1], font=f_sub_main, fill=(255, 255, 255), anchor="mm")

    draw.text((width // 2, by1 + 260), scene["sub_desc"], font=f_sub_desc, fill=(241, 245, 249), anchor="mm")
    draw.text((width // 2, by2 - 40), "소중한 분들께 공유해 주세요", font=f_small, fill=(148, 163, 184), anchor="mm")

    img.convert("RGB").save(out_img, "JPEG", quality=95)


async def main():
    temp_dir = "/tmp/day2_shorts_build"
    os.makedirs(temp_dir, exist_ok=True)
    out_mp4 = "/workspace/downloads/Day2_겨울철_당뇨_인슐린_발관리_겅태_쇼츠.mp4"

    scene_videos = []
    print("[Day 2 Video] Rendering scenes...")
    for s in DAY2_SCENES:
        idx = s["idx"]
        img_p = f"{temp_dir}/frame_{idx}.jpg"
        aud_p = f"{temp_dir}/speech_{idx}.mp3"
        vid_p = f"{temp_dir}/scene_{idx}.mp4"

        create_day2_frame(s, img_p)
        await generate_speech(s["audio_text"], aud_p)
        dur = get_audio_duration(aud_p) + 0.6

        render_scene_video_v2(img_p, aud_p, vid_p, dur)
        scene_videos.append(vid_p)
        print(f"  - 씬 {idx}/5 완료 ({dur:.1f}초): {s['badge']}")

    # Concat
    list_p = f"{temp_dir}/concat.txt"
    with open(list_p, "w", encoding="utf-8") as f:
        for vp in scene_videos:
            f.write(f"file '{vp}'\n")

    cmd = [
        FFMPEG_PATH, "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_p,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k",
        out_mp4
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"✅ Day 2 완성 비디오: {out_mp4}")

    # Copy to content repo
    repo_mp4 = BASE_DIR / "content" / "2026-11-09-06" / "instagram" / "reel_video.mp4"
    import shutil
    shutil.copyfile(out_mp4, repo_mp4)

    # Extract sample frames for chat display
    subprocess.run([FFMPEG_PATH, "-y", "-ss", "00:00:03", "-i", out_mp4, "-vframes", "1", "-q:v", "2", "/workspace/downloads/day2_scene1_warning.jpg"], check=True)
    subprocess.run([FFMPEG_PATH, "-y", "-ss", "00:00:20", "-i", out_mp4, "-vframes", "1", "-q:v", "2", "/workspace/downloads/day2_scene3_prescription.jpg"], check=True)
    subprocess.run([FFMPEG_PATH, "-y", "-ss", "00:00:30", "-i", out_mp4, "-vframes", "1", "-q:v", "2", "/workspace/downloads/day2_scene4_insulin.jpg"], check=True)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
