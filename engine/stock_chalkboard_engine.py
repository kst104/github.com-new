# -*- coding: utf-8 -*-
"""
Stock / Market Chalkboard Shorts Engine
- 칠판 분필 드로잉 시장 인사이트 특강 스타일 (응급실 특강 엔진의 주식·시장 버전)
- 다크 그린 칠판 + 우드 프레임 + 분필 수치 카드(지수·등락률·수급·투기지수·감마)
- 겅태 캐릭터 감정 매핑 인서트 (공식 3D 에셋 15종, 흰 배경 키아웃)
- 하단 투자 면책 고지 상시 노출, 1080x1920 25fps 유튜브 쇼츠 규격
- 음성: Edge-TTS ko-KR-InJoonNeural (차분한 남성 톤)
"""

import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FFMPEG_PATH = "/usr/local/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
if not os.path.exists(FFMPEG_PATH):
    FFMPEG_PATH = "ffmpeg"

BASE_DIR = Path(__file__).resolve().parent
FONT_BOLD = os.path.abspath(os.path.join(BASE_DIR, "..", "fonts", "NanumGothic-Bold.ttf"))
if not os.path.exists(FONT_BOLD):
    FONT_BOLD = "/workspace/fonts/NanumGothic-Bold.ttf"

CHAR_DIR = Path("/workspace/work/content-automation-engine/assets/character/geongtae")

DISCLAIMER = "본 영상은 투자 권유가 아닌 시장 기록 및 정보 정리입니다."

# 칠판 팔레트
BOARD = (22, 38, 30)
BOARD_DARK = (14, 26, 20)
CHALK_WHITE = (255, 255, 245)
CHALK_YELLOW = (253, 224, 71)
CHALK_BLUE = (125, 190, 250)   # 하락
CHALK_RED = (248, 130, 120)    # 상승
CHALK_GRAY = (196, 204, 196)

COLOR_MAP = {
    "down": CHALK_BLUE,
    "up": CHALK_RED,
    "neutral": CHALK_YELLOW,
}


def generate_speech(text: str, output_mp3: str, voice: str = "ko-KR-InJoonNeural", rate: str = "+5%"):
    import asyncio
    import edge_tts

    async def _run():
        comm = edge_tts.Communicate(text, voice, rate=rate)
        await comm.save(output_mp3)

    asyncio.run(_run())


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


def _text_with_outline(draw, pos, text, font, fill, outline=(12, 22, 17), width=4, anchor="mm"):
    x, y = pos
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx or dy:
                draw.text((x + dx, y + dy), text, font=font, fill=outline, anchor=anchor)
    draw.text((x, y), text, font=font, fill=fill, anchor=anchor)


def _fit_font(text: str, size: int, max_w: int):
    """텍스트가 카드 폭을 넘으면 폰트 크기를 줄인다."""
    while size > 18:
        f = ImageFont.truetype(FONT_BOLD, size)
        bbox = f.getbbox(text)
        if bbox[2] - bbox[0] <= max_w:
            return f
        size -= 2
    return ImageFont.truetype(FONT_BOLD, size)


def load_geongtae(name: str, size: int):
    """겅태 공식 3D 에셋 로드 + 흰 배경 키아웃 (칠판 위 인서트용)."""
    path = CHAR_DIR / f"{name}.png"
    if not path.exists():
        return None
    img = Image.open(path).convert("RGBA")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            m = min(r, g, b)
            if m >= 226:
                px[x, y] = (r, g, b, 0)
            elif m >= 190:
                # 가장자리 페더링 (흰 배경 잔여 제거)
                alpha = int((226 - m) / 36 * 255)
                px[x, y] = (r, g, b, min(a, alpha))
    # 흰 테두리 프린지 제거: 알파 1px 침식
    from PIL import ImageFilter
    alpha = img.getchannel("A").filter(ImageFilter.MinFilter(3))
    img.putalpha(alpha)
    ratio = size / max(w, h)
    return img.resize((max(1, int(w * ratio)), max(1, int(h * ratio))), Image.Resampling.LANCZOS)


def create_stock_scene_frame(
    *,
    scene_idx: int,
    header_title: str,
    header_meta: str,
    badge: str,
    keyword: str,
    main_text: str,
    sub_text: str,
    stats: list,
    chalk_img_path: str,
    character_img: str,
    character_label: str = "",
    out_img: str,
    width: int = 1080,
    height: int = 1920,
):
    img = Image.new("RGBA", (width, height), BOARD + (255,))
    draw = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(FONT_BOLD, 44)
    f_meta = ImageFont.truetype(FONT_BOLD, 28)
    f_badge = ImageFont.truetype(FONT_BOLD, 30)
    f_keyword = ImageFont.truetype(FONT_BOLD, 42)
    f_main = ImageFont.truetype(FONT_BOLD, 56)
    f_sub = ImageFont.truetype(FONT_BOLD, 34)
    f_small = ImageFont.truetype(FONT_BOLD, 25)
    f_note = ImageFont.truetype(FONT_BOLD, 24)

    # 우드 프레임
    draw.rectangle([(0, 0), (width, height)], outline=(138, 90, 52), width=16)
    draw.rectangle([(16, 16), (width - 16, height - 16)], outline=(96, 60, 32), width=8)

    # 1) 헤더 (y 54 ~ 148)
    draw.rounded_rectangle([(50, 54), (width - 50, 148)], radius=16, fill=BOARD_DARK, outline=CHALK_GRAY, width=2)
    draw.text((76, 101), header_title, font=f_title, fill=CHALK_WHITE, anchor="lm")
    if header_meta:
        draw.text((width - 76, 101), header_meta, font=f_meta, fill=CHALK_GRAY, anchor="rm")

    # 2) 배지 (y 158 ~ 224)
    if badge:
        danger = any(k in badge for k in ("경고", "위험", "급락", "이탈", "충돌"))
        color = (239, 100, 100) if danger else (86, 190, 240)
        draw.rounded_rectangle([(110, 158), (width - 110, 224)], radius=14, fill=BOARD_DARK, outline=color, width=3)
        draw.text((width // 2, 191), f"【 {badge} 】", font=f_badge, fill=CHALK_YELLOW if danger else (224, 242, 254), anchor="mm")

    # 3) 분필 드로잉 아트 (y 240 ~ 900)
    ax1, ay1, ax2, ay2 = 50, 240, width - 50, 900
    aw, ah = ax2 - ax1, ay2 - ay1
    draw.rounded_rectangle([(ax1 - 5, ay1 - 5), (ax2 + 5, ay2 + 5)], radius=20, fill=(12, 22, 17),
                           outline=(210, 210, 214), width=3)
    if chalk_img_path and os.path.exists(chalk_img_path):
        raw = Image.open(chalk_img_path).convert("RGBA")
        ratio = raw.width / raw.height
        target = aw / ah
        if ratio > target:
            new_h, new_w = ah, int(ah * ratio)
        else:
            new_w, new_h = aw, int(aw / ratio)
        resized = raw.resize((new_w, new_h), Image.Resampling.LANCZOS)
        cx, cy = (new_w - aw) // 2, (new_h - ah) // 2
        cropped = resized.crop((cx, cy, cx + aw, cy + ah))
        mask = Image.new("L", (aw, ah), 0)
        ImageDraw.Draw(mask).rounded_rectangle([(0, 0), (aw, ah)], radius=16, fill=255)
        img.paste(cropped, (ax1, ay1), mask)

    # 겅태 캐릭터 인서트 (아트 좌하단, 분필 원 위에 서 있는 진행자)
    if character_img:
        ch = load_geongtae(character_img, 205)
        if ch is not None:
            cx0 = ax1 + 34
            cy0 = ay2 - ch.height - 18
            ring_r = 92
            ring_c = (cx0 + ch.width // 2, ay2 - 30)
            draw.ellipse(
                [(ring_c[0] - ring_r, ring_c[1] - 26), (ring_c[0] + ring_r, ring_c[1] + 26)],
                outline=(226, 226, 218), width=4,
            )
            img.paste(ch, (cx0, cy0), ch)
            if character_label:
                draw.text((cx0 + ch.width // 2, ay2 - 58), character_label, font=f_note,
                          fill=CHALK_YELLOW, anchor="mm")

    # 분필 키워드 태그 (우측 상단, 동적 폭)
    if keyword:
        bbox = f_keyword.getbbox(keyword)
        bw = bbox[2] - bbox[0] + 64
        bh = bbox[3] - bbox[1] + 36
        bx2, by1 = ax2 - 28, ay1 + 26
        bx1, by2 = bx2 - bw, by1 + bh
        draw.rounded_rectangle([(bx1, by1), (bx2, by2)], radius=16, fill=(16, 28, 22), outline=(250, 204, 21), width=4)
        draw.text(((bx1 + bx2) // 2, (by1 + by2) // 2), keyword, font=f_keyword, fill=CHALK_YELLOW, anchor="mm")

    # 4) 수치 카드 밴드 (y 902 ~ 1074)
    if stats:
        n = len(stats)
        gap = 22
        cw = (width - 100 - gap * (n - 1)) // n
        y1, y2 = 918, 1090
        for i, st in enumerate(stats):
            x1 = 50 + i * (cw + gap)
            x2 = x1 + cw
            draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=16, fill=BOARD_DARK, outline=(186, 192, 186), width=2)
            color = COLOR_MAP.get(st.get("color", "neutral"), CHALK_YELLOW)
            f_lab = _fit_font(st["label"], 26, cw - 24)
            f_val = _fit_font(st["value"], 44, cw - 20)
            f_del = _fit_font(st.get("delta", ""), 25, cw - 24)
            draw.text(((x1 + x2) // 2, y1 + 36), st["label"], font=f_lab, fill=CHALK_GRAY, anchor="mm")
            draw.text(((x1 + x2) // 2, y1 + 90), st["value"], font=f_val, fill=color, anchor="mm")
            if st.get("delta"):
                draw.text(((x1 + x2) // 2, y1 + 142), st["delta"], font=f_del, fill=color, anchor="mm")

    # 5) 강의 노트 텍스트 박스 (y 1108 ~ 1616, 본문은 세로 중앙 정렬)
    t1, t2 = 1108, 1616
    draw.rounded_rectangle([(50, t1), (width - 50, t2)], radius=22, fill=BOARD_DARK, outline=CHALK_YELLOW, width=3)
    draw.text((84, t1 + 44), "시장 기록 노트", font=f_small, fill=(150, 165, 152), anchor="lm")
    main_lines = [l.strip() for l in main_text.split("\n") if l.strip()]
    sub_lines = [l.strip() for l in sub_text.split("\n") if l.strip()]
    block_h = len(main_lines) * 82 + (16 + len(sub_lines) * 56 if sub_lines else 0)
    area_top, area_bottom = t1 + 92, t2 - 34
    y = area_top + max(0, (area_bottom - area_top - block_h) // 2) + 40
    for line in main_lines:
        _text_with_outline(draw, (width // 2, y), line, f_main, CHALK_YELLOW, width=4)
        y += 82
    if sub_lines:
        y += 16
    for line in sub_lines:
        _text_with_outline(draw, (width // 2, y), line, f_sub, CHALK_WHITE, width=3)
        y += 56

    # 6) 투자 면책 고지 밴드 (y 1638 ~ 1712)
    draw.rounded_rectangle([(50, 1638), (width - 50, 1712)], radius=14, fill=(10, 18, 14), outline=(120, 130, 120), width=2)
    draw.text((width // 2, 1675), DISCLAIMER, font=f_note, fill=(196, 200, 190), anchor="mm")

    # 7) 칠판 받침대 · 분필 데코
    draw.rectangle([(50, height - 40), (width - 50, height - 24)], fill=(120, 80, 45))
    for x, c in ((180, CHALK_WHITE), (262, CHALK_RED), (344, CHALK_YELLOW), (426, CHALK_BLUE)):
        draw.rounded_rectangle([(x, height - 38), (x + 62, height - 26)], radius=3, fill=c)
    draw.text((84, height - 96), "매일 장마감 시장 기록", font=f_note, fill=(140, 150, 140), anchor="lm")
    draw.text((width - 84, height - 96), "김승태", font=f_note, fill=(150, 160, 150), anchor="rm")

    img.convert("RGB").save(out_img, quality=95)


def render_scene_video(img_path: str, audio_path: str, out_mp4: str, duration: float, fps: int = 25):
    cmd = [
        FFMPEG_PATH, "-y",
        "-loop", "1", "-framerate", str(fps), "-i", img_path,
        "-i", audio_path,
        "-c:v", "libx264", "-tune", "stillimage", "-r", str(fps),
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
        "-pix_fmt", "yuv420p",
        "-t", f"{duration + 0.35:.2f}",
        "-shortest", out_mp4,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def render_stock_shorts(scenes: list, output_mp4: str, header_title: str, header_meta: str,
                        temp_dir: str = "/tmp/stock_chalk_build", fps: int = 25):
    os.makedirs(temp_dir, exist_ok=True)
    parts = []
    print(f"\n[Stock Chalkboard Engine] 시장 칠판 특강 쇼츠 렌더링 시작 ({len(scenes)}씬)")
    for idx, sc in enumerate(scenes, 1):
        audio = os.path.join(temp_dir, f"audio_{idx}.mp3")
        frame = os.path.join(temp_dir, f"frame_{idx}.jpg")
        part = os.path.join(temp_dir, f"scene_{idx}.mp4")
        generate_speech(sc["voice"], audio)
        dur = get_audio_duration(audio)
        create_stock_scene_frame(
            scene_idx=idx,
            header_title=header_title,
            header_meta=header_meta,
            badge=sc.get("badge", ""),
            keyword=sc.get("keyword", ""),
            main_text=sc.get("main_text", ""),
            sub_text=sc.get("sub_text", ""),
            stats=sc.get("stats", []),
            chalk_img_path=sc.get("chalk_img", ""),
            character_img=sc.get("character", ""),
            character_label=sc.get("character_label", ""),
            out_img=frame,
            width=1080,
            height=1920,
        )
        render_scene_video(frame, audio, part, dur, fps=fps)
        parts.append(part)
        print(f"  - 씬 {idx}/{len(scenes)} ({dur:.1f}초, {sc.get('badge')}, 겅태:{sc.get('character','')})")

    concat = os.path.join(temp_dir, "concat.txt")
    with open(concat, "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    raw = os.path.join(temp_dir, "concat_raw.mp4")
    subprocess.run([FFMPEG_PATH, "-y", "-f", "concat", "-safe", "0", "-i", concat,
                    "-c", "copy", raw],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    # 최종 CFR 25fps · yuv420p 통일 패스 (프레임레이트·픽셀포맷 규격 보장)
    subprocess.run([FFMPEG_PATH, "-y", "-i", raw,
                    "-r", str(fps), "-fps_mode", "cfr",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-colorspace", "bt709",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                    "-movflags", "+faststart", output_mp4],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    total = sum(get_audio_duration(os.path.join(temp_dir, f"audio_{i}.mp3")) + 0.35
                for i in range(1, len(scenes) + 1))
    print(f"✅ 완성 -> {output_mp4} (약 {total:.1f}초)")
    return total
