# -*- coding: utf-8 -*-
"""
Chalkboard / Blackboard Drawing Medical Shorts Engine
- 칠판 분필 드로잉 및 의학 강의 스타일 비디오 엔진
- 다크 그린 칠판 텍스처, 우드 프레임, 분필 스케치 및 컬러 분필 하이라이트
- Edge-TTS 한국어 음성 (ko-KR-InJoonNeural) 동기화 ("일일구" 정확 발음 적용)
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

def create_chalkboard_scene_frame(
    scene_idx: int,
    badge: str,
    chalk_keyword: str,
    main_text: str,
    sub_text: str,
    chalk_img_path: str,
    out_img: str,
    width: int = 1080,
    height: int = 1920
):
    """칠판 분필 드로잉 스타일 씬 프레임 생성"""
    # 칠판 배경색 (다크 슬레이트 그린)
    img = Image.new("RGBA", (width, height), (22, 38, 30, 255))
    draw = ImageDraw.Draw(img)
    
    font_header = ImageFont.truetype(FONT_BOLD, 42)
    font_badge = ImageFont.truetype(FONT_BOLD, 32)
    font_keyword = ImageFont.truetype(FONT_BOLD, 46)
    font_sub_main = ImageFont.truetype(FONT_BOLD, 52)
    font_sub_sub = ImageFont.truetype(FONT_BOLD, 34)
    font_small = ImageFont.truetype(FONT_BOLD, 26)
    
    # 외곽 우드 프레임 효과 (원목 몰딩 느낌)
    frame_color = (138, 90, 52)
    inner_wood = (101, 62, 33)
    draw.rectangle([(0, 0), (width, height)], outline=frame_color, width=16)
    draw.rectangle([(16, 16), (width - 16, height - 16)], outline=inner_wood, width=8)
    
    # 1. 상단 칠판 헤더 (y: 60 ~ 220)
    # 분필 지우개 자국 및 칠판 질감 데코
    draw.rounded_rectangle([(50, 70), (width - 50, 155)], radius=18, fill=(16, 28, 22, 230), outline=(220, 215, 201), width=2)
    draw.text((width // 2, 112), "🖍️ 닥터 김승태의 응급실 칠판 특강 🖍️", font=font_header, fill=(255, 255, 245), anchor="mm")
    
    if badge:
        # 분필 박스 스타일 배지
        badge_border = (239, 68, 68) if ("경고" in badge or "호출" in badge or "위험" in badge) else (56, 189, 248)
        draw.rounded_rectangle([(120, 180), (width - 120, 245)], radius=14, fill=(16, 28, 22), outline=badge_border, width=3)
        draw.text((width // 2, 212), f"【 {badge} 】", font=font_badge, fill=(254, 240, 138) if badge_border == (239, 68, 68) else (224, 242, 254), anchor="mm")
        
    # 2. 메인 칠판 분필 드로잉 아트 영역 (y: 280 ~ 1240)
    art_x1, art_y1 = 50, 275
    art_x2, art_y2 = width - 50, 1245
    art_w = art_x2 - art_x1
    art_h = art_y2 - art_y1
    
    # 드로잉 외곽 테두리 (화이트 분필 이중선)
    draw.rounded_rectangle([(art_x1 - 6, art_y1 - 6), (art_x2 + 6, art_y2 + 6)], radius=22, fill=(12, 22, 17), outline=(212, 212, 216), width=3)
    
    if os.path.exists(chalk_img_path):
        raw_img = Image.open(chalk_img_path).convert("RGBA")
        img_ratio = raw_img.width / raw_img.height
        target_ratio = art_w / art_h
        
        if img_ratio > target_ratio:
            new_h = art_h
            new_w = int(new_h * img_ratio)
        else:
            new_w = art_w
            new_h = int(new_w / img_ratio)
            
        resized_img = raw_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        crop_x = (new_w - art_w) // 2
        crop_y = (new_h - art_h) // 2
        cropped_img = resized_img.crop((crop_x, crop_y, crop_x + art_w, crop_y + art_h))
        
        mask = Image.new("L", (art_w, art_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (art_w, art_h)], radius=18, fill=255)
        
        img.paste(cropped_img, (art_x1, art_y1), mask)
        
    # 분필 핵심 키워드 태그 (우측 상단 오버레이 - 글자 길이에 맞춰 동적 크기 계산)
    if chalk_keyword:
        bbox = font_keyword.getbbox(chalk_keyword)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        pad_x = 32
        pad_y = 18
        box_w = text_w + pad_x * 2
        box_h = text_h + pad_y * 2
        
        box_right = art_x2 - 30
        box_left = box_right - box_w
        box_top = art_y1 + 30
        box_bottom = box_top + box_h
        
        draw.rounded_rectangle(
            [(box_left, box_top), (box_right, box_bottom)],
            radius=18, fill=(16, 28, 22, 240), outline=(250, 204, 21), width=4
        )
        draw.text(
            ((box_left + box_right) // 2, (box_top + box_bottom) // 2),
            chalk_keyword, font=font_keyword, fill=(253, 224, 71), anchor="mm"
        )
        
    # 3. 하단 칠판 필기 자막 박스 (y: 1275 ~ 1840)
    sub_top = 1275
    sub_bottom = 1845
    draw.rounded_rectangle([(50, sub_top), (width - 50, sub_bottom)], radius=24, fill=(16, 28, 22, 245), outline=(254, 240, 138), width=3)
    
    # 칠판 강의실 노트 표시
    draw.text((80, sub_top + 45), "📝 의사 강의 노트", font=font_small, fill=(148, 163, 184), anchor="lm")
    
    lines = main_text.split("\n")
    y_c = sub_top + 115
    for l in lines:
        draw_text_with_outline(
            draw, (width // 2, y_c), l.strip(),
            font=font_sub_main, fill_color=(254, 240, 138), outline_color=(12, 22, 17), outline_width=4, anchor="mm"
        )
        y_c += 85
        
    y_c += 20
    s_lines = sub_text.split("\n")
    for sl in s_lines:
        draw_text_with_outline(
            draw, (width // 2, y_c), sl.strip(),
            font=font_sub_sub, fill_color=(255, 255, 255), outline_color=(12, 22, 17), outline_width=3, anchor="mm"
        )
        y_c += 60
        
    # 하단 칠판 받침대 및 분필 분진 데코
    draw.rectangle([(50, height - 42), (width - 50, height - 26)], fill=(120, 80, 45))
    draw.rounded_rectangle([(180, height - 40), (240, height - 28)], radius=3, fill=(255, 255, 255)) # 흰 분필
    draw.rounded_rectangle([(260, height - 40), (320, height - 28)], radius=3, fill=(250, 204, 21)) # 노란 분필
    draw.rounded_rectangle([(340, height - 40), (400, height - 28)], radius=3, fill=(239, 68, 68)) # 빨간 분필
    
    img = img.convert("RGB")
    img.save(out_img, quality=95)

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

def render_chalkboard_shorts(scenes: list, output_mp4: str, temp_dir: str = "/tmp/chalk_shorts_build"):
    os.makedirs(temp_dir, exist_ok=True)
    scene_videos = []
    
    print(f"\n[Chalkboard Video Engine] 칠판 분필 드로잉 스타일 쇼츠 렌더링 시작...")
    
    for idx, sc in enumerate(scenes):
        scene_idx = idx + 1
        audio_file = os.path.join(temp_dir, f"audio_{scene_idx}.mp3")
        img_file = os.path.join(temp_dir, f"frame_{scene_idx}.jpg")
        scene_mp4 = os.path.join(temp_dir, f"scene_{scene_idx}.mp4")
        
        asyncio.run(generate_speech(sc["voice"], audio_file))
        duration = get_audio_duration(audio_file)
        
        create_chalkboard_scene_frame(
            scene_idx=scene_idx,
            badge=sc.get("badge", ""),
            chalk_keyword=sc.get("keyword", ""),
            main_text=sc.get("main_text", ""),
            sub_text=sc.get("sub_text", ""),
            chalk_img_path=sc.get("chalk_img", ""),
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
    print(f"\n✅ 칠판 드로잉 쇼츠 완성! -> {output_mp4}")

def build_day4_chalkboard_shorts():
    scenes = [
        {
            "badge": "⚠️ 긴급 경고",
            "keyword": "급체 오인 금지!",
            "chalk_img": "/workspace/assets/chalkboard/day4/scene1_chest_pain.png",
            "main_text": "겨울철 새벽 가슴 통증\n단순 급체로 넘기지 마세요!",
            "sub_text": "찬 공기 노출 즉시 혈관 급수축 심근경색",
            "voice": "겨울철 새벽에 가슴을 쥐어짜는 통증이 찾아오면, 절대 단순 소화불량으로 넘기시면 안 됩니다."
        },
        {
            "badge": "🏥 응급실 현장 진실",
            "keyword": "비전형 30%",
            "chalk_img": "/workspace/assets/chalkboard/day4/scene2_ambulance_ecg.png",
            "main_text": "식은땀과 명치 답답함\n심장의 위험한 SOS 신호!",
            "sub_text": "심근경색 30%는 비전형 증상으로 시작",
            "voice": "실제 응급실 환자의 30%는 가슴 흉통 대신 명치 답답함과 비 오듯 쏟아지는 식은땀으로 시작합니다."
        },
        {
            "badge": "💡 의사의 골든타임",
            "keyword": "120분 사수!",
            "chalk_img": "/workspace/assets/chalkboard/day4/scene3_doctor_heart.png",
            "main_text": "혈관 막히면 2시간!\n스텐트 시술 120분 골든타임",
            "sub_text": "시간 지체 시 심장 근육 영구 괴사",
            "voice": "심장 혈관이 완전히 막히면 2시간 안에 뚫어야 심장 근육의 괴사를 막을 수 있습니다."
        },
        {
            "badge": "🚨 119 즉시 호출",
            "keyword": "자가운전 금기",
            "chalk_img": "/workspace/assets/chalkboard/day4/scene4_call_119.png",
            "main_text": "손 따거나 운전하지 말고\n즉시 119 구급차 부르세요!",
            "sub_text": "구급차 내 심전도 전송 및 심장센터 직행",
            "voice": "소화제 먹거나 직접 운전하지 마시고, 그 즉시 일일구를 불러 심혈관센터로 직행하셔야 합니다."
        },
        {
            "badge": "👨‍👩‍👧 가족 사랑 실천",
            "keyword": "부모님 공유 필수",
            "chalk_img": "/workspace/assets/chalkboard/day4/scene5_warm_family.png",
            "main_text": "소중한 가족의 심장 건강\n빠른 119 신고가 지킵니다",
            "sub_text": "부모님과 지인들께 꼭 공유해 주세요",
            "voice": "소중한 우리 가족의 건강한 심장, 신속한 일일구 신고가 지킵니다. 지금 꼭 공유해 주세요."
        }
    ]
    
    out_file = "/workspace/downloads/Day4_겨울철_심근경색_칠판드로잉_쇼츠.mp4"
    render_chalkboard_shorts(scenes, out_file, temp_dir="/tmp/day4_chalk_shorts_build")
    
    dest_dir = "/workspace/work/content-automation-engine/content/2026-11-11-01/chalkboard"
    os.makedirs(dest_dir, exist_ok=True)
    subprocess.run(["cp", out_file, os.path.join(dest_dir, "chalkboard_shorts_video.mp4")])
    print(f"✅ Day 4 칠판 쇼츠 깃허브 아카이브 완료: chalkboard_shorts_video.mp4")
    return out_file

def build_day5_chalkboard_shorts():
    scenes = [
        {
            "badge": "⚠️ 겨울철 은근한 덫",
            "keyword": "40도 열기의 배신",
            "chalk_img": "/workspace/assets/chalkboard/day5/scene1_electric_mat_sleep.png",
            "main_text": "따뜻한 전기장판 위의 꿀잠\n자고 일어나니 다리에 물집이?",
            "sub_text": "40~50도 은근한 열기가 만드는 저온 화상",
            "voice": "겨울철에 따뜻한 전기장판 틀어놓고 푹 자고 일어났는데, 다리에 누런 물집이 잡혀 놀라신 적 있으신가요?"
        },
        {
            "badge": "🏥 응급실 현장 진실",
            "keyword": "안 아픈 게 더 위험",
            "chalk_img": "/workspace/assets/chalkboard/day5/scene2_skin_burn_anatomy.png",
            "main_text": "통증이 전혀 없는 이유\n신경까지 타버린 3도 화상!",
            "sub_text": "피하지방층 괴사 및 감각 신경 완전 마비",
            "voice": "하나도 안 아프다고 방치하시면 안 됩니다. 감각 신경까지 열기로 타버린 심각한 3도 화상이기 때문입니다."
        },
        {
            "badge": "💡 의사의 온도 법칙",
            "keyword": "44도 6시간 괴사",
            "chalk_img": "/workspace/assets/chalkboard/day5/scene3_doctor_burn_lecture.png",
            "main_text": "44도에서 6시간 노출 시\n피부 단백질이 완전히 변성",
            "sub_text": "당뇨 환자·음주 수면 시 치명적 피부 괴사",
            "voice": "체온보다 조금 높은 44도에서도 6시간 이상 노출되면 피부 단백질이 익어버려 괴사하기 시작합니다."
        },
        {
            "badge": "🚨 절대 금기 민간요법",
            "keyword": "물집·얼음 금지!",
            "chalk_img": "/workspace/assets/chalkboard/day5/scene4_burn_contraindications.png",
            "main_text": "물집 바늘로 터뜨리거나\n얼음·소주 바르면 피부 괴사!",
            "sub_text": "2차 감염과 패혈증 위험, 절대 건드리지 마세요",
            "voice": "물집을 바늘로 터뜨리거나 얼음을 직접 대시면 안 됩니다. 혈관이 수축해 괴사가 더 깊어집니다."
        },
        {
            "badge": "👨‍👩‍👧 올바른 응급처치",
            "keyword": "미온수 15분 쿨링",
            "chalk_img": "/workspace/assets/chalkboard/day5/scene5_proper_burn_firstaid.png",
            "main_text": "15도 미온수로 15분 식히고\n깨끗한 거즈 후 병원 가세요!",
            "sub_text": "우리 가족의 안전한 겨울, 지금 꼭 공유해 주세요",
            "voice": "흐르는 미온수로 15분간 서서히 식힌 뒤 깨끗한 거즈로 보호하고 즉시 병원에 가셔야 합니다. 소중한 가족을 위해 꼭 공유해 주세요."
        }
    ]
    
    out_file = "/workspace/downloads/Day5_겨울철_저온화상_칠판드로잉_쇼츠.mp4"
    render_chalkboard_shorts(scenes, out_file, temp_dir="/tmp/day5_chalk_shorts_build")
    
    dest_dir = "/workspace/work/content-automation-engine/content/2026-11-12-01/chalkboard"
    os.makedirs(dest_dir, exist_ok=True)
    subprocess.run(["cp", out_file, os.path.join(dest_dir, "chalkboard_shorts_video.mp4")])
    print(f"✅ Day 5 칠판 쇼츠 깃허브 아카이브 완료: chalkboard_shorts_video.mp4")
    return out_file

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--day" and sys.argv[2] == "5":
        build_day5_chalkboard_shorts()
    elif len(sys.argv) > 1 and sys.argv[1] == "--day" and sys.argv[2] == "4":
        build_day4_chalkboard_shorts()
    else:
        build_day5_chalkboard_shorts()
