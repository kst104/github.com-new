# -*- coding: utf-8 -*-
"""
Shorts & Reels Video Engine
릴스 및 쇼츠 대본을 읽어 9:16(1080x1920) 고화질 세로형 MP4 비디오를 자동 렌더링합니다.
- Edge-TTS 기반 한국어 음성(ko-KR-InJoonNeural) 생성
- 닥터 겅태 마스코트 캐릭터 및 헤더 브랜딩
- 장면별 핵심 자막 및 텍스트 오버레이 자동 합성
- FFmpeg 무손실 합성
"""

import os
import sys
import asyncio
import subprocess
import json
import argparse
from PIL import Image, ImageDraw, ImageFont

# FFmpeg 경로 확보
FFMPEG_PATH = "/usr/local/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
if not os.path.exists(FFMPEG_PATH):
    FFMPEG_PATH = "ffmpeg"

FONT_BOLD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fonts", "NanumGothic-Bold.ttf"))
if not os.path.exists(FONT_BOLD):
    FONT_BOLD = "/workspace/fonts/NanumGothic-Bold.ttf"

MASCOT_PATH = "/workspace/downloads/doctor_geongtae_neck.png"

async def generate_speech(text: str, output_mp3: str, voice: str = "ko-KR-InJoonNeural", rate: str = "+5%"):
    """Edge-TTS를 이용한 고품질 한국어 음성 합성"""
    import edge_tts
    comm = edge_tts.Communicate(text, voice, rate=rate)
    await comm.save(output_mp3)

def get_audio_duration(audio_path: str) -> float:
    """FFmpeg를 이용한 오디오 재생 시간(초) 측정"""
    cmd = [
        FFMPEG_PATH, "-i", audio_path
    ]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    _, err = p.communicate()
    for line in err.split("\n"):
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
    return 3.0

def create_scene_frame(title: str, main_text: str, sub_text: str, badge: str, out_img: str, width: int = 1080, height: int = 1920):
    """Pillow를 이용한 9:16 세로형 숏폼 장면 프레임 그래픽 생성"""
    # 1. 딥 네이비 그라데이션 배경
    img = Image.new("RGBA", (width, height), (15, 23, 42, 255)) # #0f172a
    draw = ImageDraw.Draw(img)
    
    # 미세한 비네팅/포인트 조명 효과 (상단 원)
    draw.ellipse([(-200, -200), (width + 200, 600)], fill=(30, 58, 138, 255)) # #1e3a8a
    
    # 2. 폰트 로드
    font_header = ImageFont.truetype(FONT_BOLD, 46)
    font_badge = ImageFont.truetype(FONT_BOLD, 40)
    font_main = ImageFont.truetype(FONT_BOLD, 68)
    font_sub = ImageFont.truetype(FONT_BOLD, 48)
    font_footer = ImageFont.truetype(FONT_BOLD, 38)
    
    # 3. 상단 브랜딩 바
    header_text = "닥터 김승태의 1분 응급실 클립"
    draw.rounded_rectangle([(140, 160), (width - 140, 240)], radius=40, fill=(30, 41, 59, 230), outline=(59, 130, 246), width=3)
    draw.text((width // 2, 200), header_text, font=font_header, fill=(255, 255, 255), anchor="mm")
    
    # 4. 뱃지
    if badge:
        draw.rounded_rectangle([(100, 310), (width - 100, 400)], radius=20, fill=(239, 68, 68) if "경고" in badge or "금지" in badge else (37, 99, 235))
        draw.text((width // 2, 355), badge, font=font_badge, fill=(255, 255, 255), anchor="mm")
        
    # 5. 중앙 마스코트 캐릭터 배치 (라운드 액자 카드)
    if os.path.exists(MASCOT_PATH):
        mascot = Image.open(MASCOT_PATH).convert("RGBA")
        mascot.thumbnail((480, 480), Image.Resampling.LANCZOS)
        m_x = (width - mascot.width) // 2
        m_y = 500
        # 깔끔한 네이비/블루 테두리 라운드 박스
        draw.rounded_rectangle(
            [(m_x - 8, m_y - 8), (m_x + mascot.width + 8, m_y + mascot.height + 8)],
            radius=32,
            fill=(0, 0, 0, 255),
            outline=(96, 165, 250), # #60a5fa
            width=4
        )
        img.paste(mascot, (m_x, m_y), mascot)
        
    # 6. 하단 자막 박스 (어두운 반투명 카드)
    box_top = 1150
    box_bottom = 1680
    draw.rounded_rectangle([(80, box_top), (width - 80, box_bottom)], radius=32, fill=(15, 23, 42, 240), outline=(71, 85, 105), width=2)
    
    # 메인 강조 텍스트 (줄바꿈 처리)
    lines = main_text.split("\n")
    y_cursor = box_top + 90
    for line in lines:
        draw.text((width // 2, y_cursor), line.strip(), font=font_main, fill=(250, 204, 21), anchor="mm") # 옐로우 강조
        y_cursor += 95
        
    y_cursor += 30
    sub_lines = sub_text.split("\n")
    for s_line in sub_lines:
        draw.text((width // 2, y_cursor), s_line.strip(), font=font_sub, fill=(241, 245, 249), anchor="mm")
        y_cursor += 75
        
    # 7. 하단 CTA
    draw.text((width // 2, 1780), "소중한 분들께 공유해 주세요 📲", font=font_footer, fill=(148, 163, 184), anchor="mm")
    
    img.convert("RGB").save(out_img, "JPEG", quality=95)

def render_scene_video(img_path: str, audio_path: str, out_mp4: str, duration: float):
    """정지 이미지 + 오디오를 단일 씬 MP4로 렌더링"""
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
        "-t", str(duration + 0.3), # 오디오 끝부분 여유 0.3초
        "-shortest",
        out_mp4
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def render_full_shorts(scenes: list, output_mp4: str, temp_dir: str = "/tmp/shorts_build"):
    """모든 씬을 순차 합성하여 최종 릴스/쇼츠 MP4 생성"""
    os.makedirs(temp_dir, exist_ok=True)
    scene_videos = []
    
    print(f"\n[Video Engine] 총 {len(scenes)}개 장면 비디오 렌더링 시작...")
    
    for idx, sc in enumerate(scenes):
        scene_idx = idx + 1
        audio_file = os.path.join(temp_dir, f"audio_{scene_idx}.mp3")
        img_file = os.path.join(temp_dir, f"frame_{scene_idx}.jpg")
        scene_mp4 = os.path.join(temp_dir, f"scene_{scene_idx}.mp4")
        
        # 1. 음성 합성
        asyncio.run(generate_speech(sc["voice"], audio_file))
        duration = get_audio_duration(audio_file)
        
        # 2. 그래픽 프레임 생성
        create_scene_frame(
            title=sc.get("title", ""),
            main_text=sc.get("main_text", ""),
            sub_text=sc.get("sub_text", ""),
            badge=sc.get("badge", ""),
            out_img=img_file
        )
        
        # 3. 씬 비디오 렌더링
        render_scene_video(img_file, audio_file, scene_mp4, duration)
        scene_videos.append(scene_mp4)
        print(f"  - 씬 {scene_idx}/{len(scenes)} 렌더링 완료 ({duration:.1f}초): {sc.get('badge')}")
        
    # 4. 파일 합치기 (Concat)
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
    print(f"\n✅ 최종 릴스/쇼츠 완성! -> {output_mp4}")
    return output_mp4

def build_day1_sample():
    """Day 1: 겨울철 혈압 급상승 주의보 실전 릴스 생성"""
    scenes = [
        {
            "badge": "⚠️ 긴급 주의보",
            "main_text": "겨울철 아침에\n벌떡 일어나지 마세요!",
            "sub_text": "순간적으로 혈압이 15mmHg 치솟습니다",
            "voice": "겨울철 아침, 알람 울렸다고 이불 밖으로 벌떡 일어나시는 분들, 정말 위험합니다."
        },
        {
            "badge": "🏥 응급실 현장 리포트",
            "main_text": "오전 6시 ~ 9시\n심뇌혈관 환자 급증",
            "sub_text": "밤새 끈적해진 혈액 + 찬 공기 노출",
            "voice": "응급실에 있으면 매년 겨울 기온이 뚝 떨어질 때마다 아침 6시에서 9시 사이에 실려 오시는 분들을 너무 많이 봅니다."
        },
        {
            "badge": "💡 의사의 3분 처방",
            "main_text": "내일부터 딱 3분!\n기상 공식을 지키세요",
            "sub_text": "1. 손발 털기  2. 걸터앉기  3. 겉옷 입기",
            "voice": "내일부터 딱 3분만 지켜보세요. 누운 채로 기지개 켜고 손발 1분 털기, 침대에 걸터앉아 1분 호흡하기, 그리고 겉옷 입고 방 밖으로 나가기."
        },
        {
            "badge": "❌ 절대 금지",
            "main_text": "겨울철 새벽 조깅은\n보약이 아니라 독입니다",
            "sub_text": "운동은 반드시 해 뜬 낮이나 실내에서!",
            "voice": "그리고 새벽 야외 조깅은 겨울철엔 보약이 아니라 독입니다. 운동은 해 뜨고 낮에 하세요."
        },
        {
            "badge": "📲 가족 공유 필수",
            "main_text": "소중한 부모님께\n지금 바로 공유하세요!",
            "sub_text": "3분 습관 하나가 소중한 생명을 지킵니다",
            "voice": "이 3분 습관 하나가 소중한 생명을 지킵니다. 부모님께 지금 꼭 공유해 주세요."
        }
    ]
    
    out_file = "/workspace/downloads/겨울철_혈압_주의보_쇼츠_릴스.mp4"
    render_full_shorts(scenes, out_file)
    
    # 깃허브 폴더에도 복사
    dest_dir = "/workspace/work/content-automation-engine/content/2026-11-09-05/instagram"
    if os.path.exists(dest_dir):
        subprocess.run(["cp", out_file, os.path.join(dest_dir, "reel_video.mp4")])
        print(f"✅ 깃허브 content 폴더 복사 완료: {dest_dir}/reel_video.mp4")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shorts & Reels Video Engine")
    parser.add_argument("--sample", action="store_true", help="Day 1 샘플 쇼츠 생성")
    args = parser.parse_args()
    
    if args.sample or len(sys.argv) == 1:
        build_day1_sample()
