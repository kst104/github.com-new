# -*- coding: utf-8 -*-
"""
Chalkboard / Blackboard Drawing Medical Shorts Engine
- 칠판 분필 드로잉 및 의학 강의 스타일 비디오 엔진
- 다크 그린 칠판 텍스처, 우드 프레임, 분필 스케치 및 컬러 분필 하이라이트
- Edge-TTS 한국어 음성 (ko-KR-InJoonNeural) 동기화 ("일일구" 정확 발음 적용)
- 1080x1920 9:16 인스타그램 릴스 & 유튜브 쇼츠 표준 규격

레이아웃 모드 (2026-11-20 승태 님 확정)
- ``jaljab`` (기본값): 잘.의.정.바 3단 레이아웃 — 상단 흰색 헤더 / 중단 칠판 영상 / 하단 여백
  (시안: downloads/Day13_잘의정바_1장시안_v2.png)
  + 영상 첫 2초(0.0~2.0s)에만 '구독·알림·좋아요는 힘이 됩니다' 배지 오버레이
- ``chalkboard``: 기존 전면 칠판 프레임(우드 프레임·배지·강의 노트 박스) — 과거 회차 재현용
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

# ---------------------------------------------------------------------------
# 잘.의.정.바 3단 레이아웃 규격 (1080x1920)
# ---------------------------------------------------------------------------
LAYOUT_JALJAB = "jaljab"          # 잘.의.정.바 3단 레이아웃 (신규 기본값)
LAYOUT_CLASSIC = "chalkboard"     # 기존 전면 칠판 프레임
DEFAULT_SHORTS_LAYOUT = LAYOUT_JALJAB

JALJAB_TITLE = "잘못된 의료 정보 바로잡기"
JALJAB_BRAND = "잘.의.정.바"
JALJAB_FOOTER = "잘.의.정.바 · 자세한 칼럼은 프로필 링크"
JALJAB_POINT = (238, 108, 22)     # #EE6C1E 주황 포인트
JALJAB_TEXT = (20, 20, 20)
JALJAB_FOOTER_GRAY = (105, 105, 105)

# 3단 경계 (px, 상단 포함·하단 미포함)
JALJAB_TOP_BAND = (0, 540)        # 상단 1/3 — 흰 배경 타이틀
JALJAB_VIDEO_BAND = (540, 1400)   # 중단 — 칠판 영상 1080x860
JALJAB_FOOTER_Y = 1422            # 하단 안내문 시작 y

# 중단 영역 한 줄 자막 기본색/외곽선
CAPTION_FILL = (255, 255, 255)
CAPTION_OUTLINE = (10, 10, 10)

# ---------------------------------------------------------------------------
# 초기 2초 '구독·알림·좋아요' 배지 (2026-11-20 승태 님 요청)
# 영상 시작 0.0s ~ 2.0s 동안만 중단 영상 상단 중앙에 표시되고, 2.0s에 맞춰 사라진다.
# ---------------------------------------------------------------------------
SUBSCRIBE_BADGE_TEXT = "구독·알림·좋아요는 힘이 됩니다"
SUBSCRIBE_BADGE_TOP = 565                  # 중단 경계(540) 바로 아래, 가로 중앙 정렬
SUBSCRIBE_BADGE_FONT = 36
SUBSCRIBE_BADGE_PAD_X = 34
SUBSCRIBE_BADGE_PAD_Y = 15
SUBSCRIBE_BADGE_FILL = (238, 108, 22, 235)   # #EE6C1E 반투명
SUBSCRIBE_BADGE_EDGE = (255, 255, 255, 215)
SUBSCRIBE_BADGE_WINDOW = (0.0, 2.0)          # 노출 구간(초)
SUBSCRIBE_BADGE_FADE_IN = 0.0                # 첫 프레임(썸네일)부터 선명하게 — 페이드 인 없음
SUBSCRIBE_BADGE_FADE_OUT = 0.45              # 2.0s 직전 페이드 아웃

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

def _fit_font_width(text, max_w, start_size, min_size=24):
    """텍스트가 max_w를 넘지 않는 가장 큰 폰트 크기를 찾는다."""
    size = start_size
    while size > min_size:
        font = ImageFont.truetype(FONT_BOLD, size)
        bbox = font.getbbox(text)
        if bbox[2] - bbox[0] <= max_w:
            return font, bbox
        size -= 2
    font = ImageFont.truetype(FONT_BOLD, size)
    return font, font.getbbox(text)


def _outlined_text(draw, center, text, font, fill=CAPTION_FILL, outline=CAPTION_OUTLINE, width=4):
    x, y = center
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx * dx + dy * dy <= width * width + 2 and (dx or dy):
                draw.text((x + dx, y + dy), text, font=font, fill=outline, anchor="mm")
    draw.text((x, y), text, font=font, fill=fill, anchor="mm")


def subscribe_badge_geometry(width: int = 1080):
    """초기 2초 배지의 (폰트, 박스 좌표(x1,y1,x2,y2), 글자 높이). 박스는 가로 중앙·y=565 시작."""
    font, bb = _fit_font_width(SUBSCRIBE_BADGE_TEXT, width - 120, SUBSCRIBE_BADGE_FONT, 26)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    box_w = tw + SUBSCRIBE_BADGE_PAD_X * 2
    box_h = th + SUBSCRIBE_BADGE_PAD_Y * 2
    x1 = (width - box_w) // 2
    y1 = SUBSCRIBE_BADGE_TOP
    return font, (x1, y1, x1 + box_w, y1 + box_h), th


def draw_subscribe_badge(layer: Image.Image, width: int = 1080):
    """투명 RGBA 레이어에 '구독·알림·좋아요는 힘이 됩니다' 알약 배지를 그린다(박스 좌표 반환)."""
    font, box, _ = subscribe_badge_geometry(width)
    x1, y1, x2, y2 = box
    d = ImageDraw.Draw(layer)
    radius = (y2 - y1) // 2
    d.rounded_rectangle([x1 + 3, y1 + 6, x2 + 3, y2 + 6], radius=radius, fill=(0, 0, 0, 95))
    d.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=SUBSCRIBE_BADGE_FILL,
                        outline=SUBSCRIBE_BADGE_EDGE, width=3)
    d.text((width // 2, (y1 + y2) // 2 - 1), SUBSCRIBE_BADGE_TEXT, font=font,
           fill=(255, 255, 255, 255), anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255, 255))
    return box


def create_subscribe_badge_png(out_png: str, width: int = 1080, height: int = 1920) -> str:
    """ffmpeg 오버레이용 투명 배지 PNG(1080x1920, 배지 이외는 완전 투명)를 만든다."""
    layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw_subscribe_badge(layer, width)
    layer.save(out_png)
    return out_png


def _cover_crop(src: Image.Image, target_w: int, target_h: int, bias: float = 0.5) -> Image.Image:
    """비율을 유지한 채 영역을 가득 채우고 남는 쪽을 잘라낸다(bias: 위쪽 0.0 ~ 아래쪽 1.0)."""
    ratio = src.width / src.height
    target = target_w / target_h
    if ratio > target:
        new_h = target_h
        new_w = int(round(new_h * ratio))
    else:
        new_w = target_w
        new_h = int(round(new_w / ratio))
    resized = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
    extra_x, extra_y = new_w - target_w, new_h - target_h
    cx = int(round(extra_x * 0.5))
    cy = int(round(extra_y * bias))
    return resized.crop((cx, cy, cx + target_w, cy + target_h))


def create_jaljab_scene_frame(
    *,
    chalk_img_path: str,
    out_img: str,
    top_line: str = JALJAB_TITLE,
    topic_keyword: str = "",
    caption: str = "",
    footer: str = JALJAB_FOOTER,
    brand: str = JALJAB_BRAND,
    width: int = 1080,
    height: int = 1920,
    crop_bias: float = 0.5,
    scene_idx: int = 1,
    show_subscribe_badge: bool = False,
):
    """잘.의.정.바 3단 레이아웃 한 씬 프레임.

    상단(0~540 흰색): 1줄 굵은 검정 훅 + 2줄 주황 박스(흰 굵은 글씨)
    중단(540~1400): 칠판 아트 1080x860 좌우 꽉 차게 + 하단 중앙 흰 자막(검정 외곽선)
    하단(1400~1920 흰색): y1422 회색 안내문, 그 아래는 쇼츠 UI 여백으로 비움
    실명은 넣지 않는다.
    show_subscribe_badge=True: 영상 첫 2초(t<2.0s)에 보이는 '구독·알림·좋아요는 힘이 됩니다'
    배지를 정지 프레임·프리뷰에서 미리 확인하기 위한 옵션(실제 영상은 ffmpeg 오버레이로 2초만 노출).
    """
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # ---- 1. 상단 1/3: 흰 배경 + 굵은 검정 훅 + 주황 포인트 박스 ----
    top_line = (top_line or JALJAB_TITLE).strip()
    f_top, bb = _fit_font_width(top_line, width - 100, 62, 38)
    top_h = bb[3] - bb[1]
    line1_y = 244
    line1_cy = line1_y + top_h // 2
    draw.text((width // 2, line1_cy), top_line, font=f_top, fill=JALJAB_TEXT,
              anchor="mm", stroke_width=2, stroke_fill=JALJAB_TEXT)

    box_line = brand if not topic_keyword else f"{brand} · {topic_keyword}"
    box_line = box_line.strip()
    f_box, bb2 = _fit_font_width(box_line, width - 140, 64, 36)
    tw2, th2 = bb2[2] - bb2[0], bb2[3] - bb2[1]
    pad_x, pad_y = 32, 16
    box_y1 = max(line1_cy + top_h // 2 + 24, 366)
    box_y2 = box_y1 + th2 + pad_y * 2 + 12
    box_x1 = (width - tw2) // 2 - pad_x
    box_x2 = (width + tw2) // 2 + pad_x
    draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill=JALJAB_POINT)
    draw.text((width // 2, (box_y1 + box_y2) // 2), box_line, font=f_box, fill=(255, 255, 255),
              anchor="mm", stroke_width=2, stroke_fill=(255, 255, 255))

    # ---- 2. 중단: 칠판 아트 1080x860 (좌우 꽉 차게, 비율 유지 크롭) ----
    vid_y1, vid_y2 = JALJAB_VIDEO_BAND
    vid_h = vid_y2 - vid_y1
    if chalk_img_path and os.path.exists(chalk_img_path):
        raw = Image.open(chalk_img_path).convert("RGB")
        art = _cover_crop(raw, width, vid_h, bias=crop_bias)
        img.paste(art, (0, vid_y1))
    else:
        draw.rectangle([0, vid_y1, width, vid_y2], fill=(22, 38, 30))

    # 초기 2초 배지 (정지 프레임·프리뷰 확인용 — 영상은 이 PNG를 0~2초만 오버레이)
    if show_subscribe_badge:
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_subscribe_badge(layer, width)
        img.paste(layer, (0, 0), layer)

    # 하단 중앙 한 줄 자막 (검정 외곽선 + 굵은 흰색)
    cap = (caption or "").strip()
    if cap:
        f_cap, bb_cap = _fit_font_width(cap, width - 80, 52, 34)
        cap_c = (bb_cap[2] - bb_cap[0], bb_cap[3] - bb_cap[1])
        if cap_c[0] > width - 80 and " · " in cap:
            # 너무 길면 '·' 기준 두 줄로 나눠 폰트를 지킨다
            head, tail = cap.split(" · ", 1)
            f_cap = ImageFont.truetype(FONT_BOLD, 44)
            _outlined_text(draw, (width // 2, vid_y1 + vid_h - 128), head, f_cap, width=4)
            _outlined_text(draw, (width // 2, vid_y1 + vid_h - 62), tail, f_cap, width=4)
        else:
            _outlined_text(draw, (width // 2, vid_y1 + vid_h - 96), cap, f_cap, width=4)

    # ---- 3. 하단 여백: 회색 안내문만, 그 아래는 쇼츠 UI 여백 ----
    if footer:
        f_foot, bb_f = _fit_font_width(footer, width - 80, 28, 22)
        draw.text(((width - (bb_f[2] - bb_f[0])) // 2, JALJAB_FOOTER_Y), footer, font=f_foot, fill=JALJAB_FOOTER_GRAY)

    img.save(out_img, quality=95)
    return out_img


def scene_caption(scene: dict) -> str:
    """씬 dict에서 한 줄 자막 문구를 만든다(caption 우선, 없으면 main_text 두 줄을 '·'로 연결)."""
    cap = (scene.get("caption") or "").strip()
    if cap:
        return cap
    lines = [l.strip() for l in (scene.get("main_text") or "").split("\n") if l.strip()]
    return " · ".join(lines)


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

def render_scene_video(
    img_path: str,
    audio_path: str,
    out_mp4: str,
    duration: float,
    overlay_png: str = None,
    overlay_window: tuple = SUBSCRIBE_BADGE_WINDOW,
    fade_in: float = SUBSCRIBE_BADGE_FADE_IN,
    fade_out: float = SUBSCRIBE_BADGE_FADE_OUT,
):
    """한 씬 MP4를 만든다.

    overlay_png를 주면 투명 배지 PNG를 영상 위에 얹고 ``overlay_window`` 구간(기본 0.0~2.0초)에만
    보이게 한다 — 페이드 인으로 나타나 2초 직전에 페이드 아웃해 자막과 겹치지 않는다.
    """
    if overlay_png and os.path.exists(overlay_png):
        start, end = overlay_window
        end = min(end, max(duration, 0.1))           # 씬이 2초보다 짧으면 씬 끝까지만
        fade_out_start = max(start, end - fade_out)
        fade_out_len = max(end - fade_out_start, 0.05)
        fade_chain = "[1:v]format=rgba"
        if fade_in > 0:
            fade_chain += f",fade=t=in:st={start:.2f}:d={fade_in:.2f}:alpha=1"
        fade_chain += f",fade=t=out:st={fade_out_start:.2f}:d={fade_out_len:.2f}:alpha=1[badge];"
        graph = (
            fade_chain
            + f"[0:v][badge]overlay=0:0:enable='between(t,{start:.2f},{end:.2f})',fps=25[v]"
        )
        cmd = [
            FFMPEG_PATH, "-y",
            "-loop", "1",
            "-i", img_path,
            "-loop", "1",
            "-i", overlay_png,
            "-i", audio_path,
            "-filter_complex", graph,
            "-map", "[v]",
            "-map", "2:a",
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-preset", "veryfast",
            "-threads", "1",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", str(duration + 0.3),
            "-shortest",
            out_mp4
        ]
    else:
        cmd = [
            FFMPEG_PATH, "-y",
            "-loop", "1",
            "-i", img_path,
            "-i", audio_path,
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-preset", "veryfast",
            "-threads", "1",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-t", str(duration + 0.3),
            "-shortest",
            out_mp4
        ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def render_chalkboard_shorts(
    scenes: list,
    output_mp4: str,
    temp_dir: str = "/tmp/chalk_shorts_build",
    layout: str = DEFAULT_SHORTS_LAYOUT,
    top_line: str = JALJAB_TITLE,
    subscribe_badge: bool = True,
):
    """칠판 드로잉 의학 쇼츠 렌더링.

    layout="jaljab" (기본): 잘.의.정.바 3단 레이아웃
    layout="chalkboard": 기존 전면 칠판 프레임
    subscribe_badge=True (기본, jaljab 전용): 첫 씬 위에 '구독·알림·좋아요는 힘이 됩니다'
    배지를 영상 시작 0.0s~2.0s에만 표시한다.
    """
    os.makedirs(temp_dir, exist_ok=True)
    scene_videos = []

    print(f"\n[Chalkboard Video Engine] 칠판 분필 드로잉 스타일 쇼츠 렌더링 시작... (레이아웃: {layout})")
    
    for idx, sc in enumerate(scenes):
        scene_idx = idx + 1
        audio_file = os.path.join(temp_dir, f"audio_{scene_idx}.mp3")
        img_file = os.path.join(temp_dir, f"frame_{scene_idx}.jpg")
        scene_mp4 = os.path.join(temp_dir, f"scene_{scene_idx}.mp4")
        
        asyncio.run(generate_speech(sc["voice"], audio_file))
        duration = get_audio_duration(audio_file)
        
        if layout == LAYOUT_CLASSIC:
            create_chalkboard_scene_frame(
                scene_idx=scene_idx,
                badge=sc.get("badge", ""),
                chalk_keyword=sc.get("keyword", ""),
                main_text=sc.get("main_text", ""),
                sub_text=sc.get("sub_text", ""),
                chalk_img_path=sc.get("chalk_img", ""),
                out_img=img_file
            )
        else:
            create_jaljab_scene_frame(
                scene_idx=scene_idx,
                chalk_img_path=sc.get("chalk_img", ""),
                out_img=img_file,
                top_line=sc.get("top_line") or top_line,
                topic_keyword=sc.get("brand_keyword") or sc.get("keyword", ""),
                caption=scene_caption(sc),
                footer=sc.get("footer") or JALJAB_FOOTER,
            )

        # 첫 씬에만 초기 2초 배지 오버레이(레이아웃이 jaljab일 때)
        badge_png = None
        if subscribe_badge and layout != LAYOUT_CLASSIC and scene_idx == 1:
            badge_png = create_subscribe_badge_png(os.path.join(temp_dir, "subscribe_badge.png"))

        render_scene_video(img_file, audio_file, scene_mp4, duration, overlay_png=badge_png)
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

def render_jaljab_previews(
    scenes: list,
    out_dir: str,
    prefix: str = "jaljab_scene",
    top_line: str = JALJAB_TITLE,
    show_subscribe_badge: bool = True,
):
    """음성 없이 잘.의.정.바 3단 레이아웃 씬 프레임 PNG만 뽑는다.

    "1장 스크린샷" 요청이나 사전 시안 확인용. 첫 씬에는 영상 0~2초에 실제로 보이는
    '구독·알림·좋아요' 배지를 함께 넣어 확인할 수 있다(show_subscribe_badge).
    렌더된 파일 경로 목록을 돌려준다.
    """
    os.makedirs(out_dir, exist_ok=True)
    outs = []
    for idx, sc in enumerate(scenes, 1):
        out = os.path.join(out_dir, f"{prefix}_{idx}.png")
        create_jaljab_scene_frame(
            scene_idx=idx,
            chalk_img_path=sc.get("chalk_img", ""),
            out_img=out,
            top_line=sc.get("top_line") or top_line,
            topic_keyword=sc.get("brand_keyword") or sc.get("keyword", ""),
            caption=scene_caption(sc),
            footer=sc.get("footer") or JALJAB_FOOTER,
            show_subscribe_badge=bool(show_subscribe_badge and idx == 1),
        )
        outs.append(out)
        print(f"  - 프리뷰 {idx}/{len(scenes)}: {out}")
    return outs


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

def build_day6_chalkboard_shorts():
    scenes = [
        {
            "badge": "⚠️ 기온 급강하 경고",
            "keyword": "39도 고열·오한",
            "chalk_img": "/workspace/assets/chalkboard/day6/scene1_sudden_high_fever_chills.png",
            "main_text": "기온 뚝 떨어지자마자\n39도 고열과 온몸 근육통?",
            "sub_text": "단순 감기 아닌 인플루엔자 독감의 시작",
            "voice": "날씨가 갑자기 추워지며 38도 이상의 고열과 두들겨 맞은 듯한 온몸 근육통이 찾아왔다면 단순 감기가 아닙니다."
        },
        {
            "badge": "🏥 독감 vs 감기 감별",
            "keyword": "갑작스러운 폭격",
            "chalk_img": "/workspace/assets/chalkboard/day6/scene2_doctor_flu_cold_diagram.png",
            "main_text": "감기는 미열과 콧물 서서히\n독감은 몇 시간 만에 고열 폭탄!",
            "sub_text": "인플루엔자 바이러스의 급성 전신 침투",
            "voice": "감기는 콧물과 미열로 서서히 오지만, 독감은 몇 시간 만에 고열과 오한이 한꺼번에 덮치는 것이 결정적 차이입니다."
        },
        {
            "badge": "💡 치료의 골든타임",
            "keyword": "48시간 사수!",
            "chalk_img": "/workspace/assets/chalkboard/day6/scene3_antiviral_golden_time_clock.png",
            "main_text": "증상 시작 후 이틀 안에!\n타미플루·페라미플루 48시간",
            "sub_text": "바이러스 증식 차단하는 치료 골든타임",
            "voice": "증상이 시작되고 사십팔시간 안에 항바이러스제를 투약해야 바이러스 증식을 막고 합병증을 피할 수 있습니다."
        },
        {
            "badge": "🚨 치명적 합병증 경고",
            "keyword": "폐렴 신호 주의",
            "chalk_img": "/workspace/assets/chalkboard/day6/scene4_pneumonia_warning_signs.png",
            "main_text": "호흡곤란과 누런 가래\n2차 세균성 폐렴 위험 신호!",
            "sub_text": "어르신·당뇨 환자 쇼크 주의, 즉시 응급실",
            "voice": "숨이 차거나 누런 가래가 나오면 2차 세균성 폐렴 신호입니다. 어르신과 만성질환자는 즉시 병원에 가셔야 합니다."
        },
        {
            "badge": "👨‍👩‍👧 가족 건강 지키기",
            "keyword": "초기 검사 필수",
            "chalk_img": "/workspace/assets/chalkboard/day6/scene5_family_recovery_care.png",
            "main_text": "열나면 참지 말고 검사받고\n수분 섭취와 충분한 휴식!",
            "sub_text": "우리 가족의 건강한 겨울, 지금 꼭 공유해 주세요",
            "voice": "열나면 참지 마시고 신속항원 검사를 받으세요. 소중한 우리 가족을 위해 이 정보를 지금 꼭 공유해 주세요."
        }
    ]
    
    out_file = "/workspace/downloads/Day6_겨울철_독감_감기감별_칠판드로잉_쇼츠.mp4"
    render_chalkboard_shorts(scenes, out_file, temp_dir="/tmp/day6_chalk_shorts_build")
    
    dest_dir = "/workspace/work/content-automation-engine/content/2026-11-13-01/chalkboard"
    os.makedirs(dest_dir, exist_ok=True)
    subprocess.run(["cp", out_file, os.path.join(dest_dir, "chalkboard_shorts_video.mp4")])
    print(f"✅ Day 6 칠판 쇼츠 깃허브 아카이브 완료: chalkboard_shorts_video.mp4")
    return out_file

def build_day7_chalkboard_shorts():
    scenes = [
        {
            "badge": "⚠️ 겨울철 난방 경고",
            "keyword": "정면 바람 금지!",
            "chalk_img": "/workspace/assets/chalkboard/day7/scene1_heater_dry_eyes.png",
            "main_text": "히터 바람 정면으로 쐬면\n눈이 뻑뻑해집니다",
            "sub_text": "난방으로 실내 습도가 떨어지면 눈물이 빨리 마릅니다",
            "voice": "겨울철에 히터 바람을 얼굴로 직접 쐬면 눈이 뻑뻑해지고 침침해집니다. 실내 공기가 건조해지기 때문입니다."
        },
        {
            "badge": "🏥 눈물막의 비밀",
            "keyword": "눈물막 증발",
            "chalk_img": "/workspace/assets/chalkboard/day7/scene2_tear_film_breakup.png",
            "main_text": "눈물막이 마르면\n각막에 미세한 상처!",
            "sub_text": "기름막이 부족하면 물을 채워도 금세 마릅니다",
            "voice": "난방으로 실내 습도가 떨어지면 눈물막이 빠르게 증발하고, 각막 표면에 미세한 상처가 생깁니다."
        },
        {
            "badge": "💡 의사의 점안법",
            "keyword": "첫 방울은 버리기",
            "chalk_img": "/workspace/assets/chalkboard/day7/scene3_eyedrop_technique.png",
            "main_text": "무방부제 일회용 인공눈물\n첫 방울은 버리세요",
            "sub_text": "결막낭에 한 방울, 개봉 후 재사용 금지",
            "voice": "인공눈물은 무방부제 일회용으로 고르시고, 첫 방울은 버린 뒤 결막낭에 한 방울만 넣으세요. 개봉한 제품은 다시 쓰지 마세요."
        },
        {
            "badge": "🏠 실내 환경 관리",
            "keyword": "습도 사십에서 육십",
            "chalk_img": "/workspace/assets/chalkboard/day7/scene4_humidity_guard.png",
            "main_text": "실내 적정 습도\n사십에서 육십 퍼센트",
            "sub_text": "가습기 물은 매일 교체, 히터 방향 돌리기",
            "voice": "실내 습도는 사십에서 육십 퍼센트로 유지하고, 가습기 물은 매일 갈아 주셔야 합니다. 히터 방향도 얼굴에서 돌려 주세요."
        },
        {
            "badge": "🚨 응급 위험 신호",
            "keyword": "각막 손상 신호",
            "chalk_img": "/workspace/assets/chalkboard/day7/scene5_red_flag_eye.png",
            "main_text": "갑작스러운 시력 저하\n심한 안통은 응급 신호!",
            "sub_text": "각막 손상 의심, 즉시 안과 진료",
            "voice": "갑자기 시력이 떨어지거나 눈이 심하게 아프면 각막 손상 신호입니다. 지금 꼭 공유해 주세요."
        }
    ]

    out_file = "/workspace/downloads/Day7_겨울철_안구건조증_인공눈물_칠판드로잉_쇼츠.mp4"
    render_chalkboard_shorts(scenes, out_file, temp_dir="/tmp/day7_chalk_shorts_build")

    dest_dir = "/workspace/work/content-automation-engine/content/2026-11-14-01/chalkboard"
    os.makedirs(dest_dir, exist_ok=True)
    subprocess.run(["cp", out_file, os.path.join(dest_dir, "chalkboard_shorts_video.mp4")])
    print(f"✅ Day 7 칠판 쇼츠 깃허브 아카이브 완료: chalkboard_shorts_video.mp4")
    return out_file

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--day" and sys.argv[2] == "7":
        build_day7_chalkboard_shorts()
    elif len(sys.argv) > 1 and sys.argv[1] == "--day" and sys.argv[2] == "6":
        build_day6_chalkboard_shorts()
    elif len(sys.argv) > 1 and sys.argv[1] == "--day" and sys.argv[2] == "5":
        build_day5_chalkboard_shorts()
    elif len(sys.argv) > 1 and sys.argv[1] == "--day" and sys.argv[2] == "4":
        build_day4_chalkboard_shorts()
    else:
        build_day6_chalkboard_shorts()
