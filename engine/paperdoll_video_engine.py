#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""잘.의.정.바 종이인형 쇼츠 엔진 (2026-11-25 신규 레이아웃).

레이아웃 (1080x1920)
- 상단 1/5 (y=0~380, 흰색): '잘못된 의료 정보 바로잡기' + 주황 박스 '잘.의.정.바 · 주제'
- 하단 4/5 (y=380~1920): clinic_bg_9x16.png 꽉 채움 + 검은 테두리 2D 종이인형 캐릭터가
  대사에 맞춰 까딱까딱 흔들리고 톡톡 튀어 오른다. 하단 안전 영역 위 한 줄 자막과 얇은 안내문.
- 대사는 캐릭터별 Edge-TTS 음성(voices.json)으로 생성하고, 발화 구간에 맞춰 씬을 이어 붙인다.

사용:
    from engine.paperdoll_video_engine import render_paperdoll_shorts
    render_paperdoll_shorts(BEATS, out_mp4, topic_keyword="감기·독감·RSV", temp_dir=...)
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from engine.chalkboard_video_engine import FFMPEG_PATH  # noqa: F401

BASE = Path(__file__).resolve().parents[1]
ASSETS = BASE / "assets"
CHARS = ASSETS / "characters"
BG_9X16 = ASSETS / "backgrounds" / "clinic_bg_9x16.png"
VOICES_JSON = CHARS / "voices.json"
FONT_REG = "/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf"

W, H = 1080, 1920
FPS = 24
HEADER_H = 380
CHAR_BASELINE = 1470
CAPTION_CY = 1550
FOOTER_Y = 1648

ORANGE = (238, 108, 22)
INK = (20, 20, 20)
GREY = (105, 105, 105)

BRAND = "잘.의.정.바"
TITLE = "잘못된 의료 정보 바로잡기"
FOOTER = "잘.의.정.바 · 자세한 칼럼은 프로필 링크"
SUBSCRIBE_TEXT = "구독·알림·좋아요는 힘이 됩니다"

# 캐릭터별 입 좌표(원본 투명 PNG 픽셀 기준): (x, y, 입 너비, 입 높이)
MOUTH_ANCHORS = {
    # (중심 x, 중심 y, 원래 입 전체를 덮는 폭, 높이)
    "doctor": (351, 554, 100, 70),
    "adult_woman": (281, 413, 88, 54),
    "boy": (387, 578, 98, 78),
    "girl": (339, 505, 90, 62),
    "grandpa": (300, 470, 76, 26),
    "grandma": (302, 470, 78, 28),
    "adult_man": (345, 558, 84, 52),
}
MOUTH_INK = (150, 62, 56)
MOUTH_TONGUE = (219, 116, 106)
LIP_LINE = (108, 58, 50)
MOUTH_SKIN = {"doctor": (253, 224, 197), "adult_woman": (253, 219, 193), "boy": (253, 224, 198),
              "girl": (253, 220, 196), "grandpa": (250, 208, 172), "grandma": (250, 210, 176),
              "adult_man": (253, 221, 194)}
_LEVELS = (0.0, 0.15, 0.3, 0.45, 0.6, 0.78, 1.0)


# --------------------------------------------------------------------------- 유틸
def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_REG, size)


def bold_text(draw, xy, text, f, fill, anchor=None, weight=1):
    x, y = xy
    for dx in range(-weight, weight + 1):
        for dy in range(-weight, weight + 1):
            draw.text((x + dx, y + dy), text, font=f, fill=fill, anchor=anchor)


def fit_font(text, max_w, start, minimum=24):
    size = start
    while size > minimum:
        f = font(size)
        bb = f.getbbox(text)
        if bb[2] - bb[0] <= max_w:
            return f, bb
        size -= 2
    f = font(size)
    return f, f.getbbox(text)


def cover_crop(src: Image.Image, tw: int, th: int, bias: float = 0.5) -> Image.Image:
    ratio = src.width / src.height
    target = tw / th
    if ratio > target:
        nh = th
        nw = int(round(nh * ratio))
    else:
        nw = tw
        nh = int(round(nw / ratio))
    im = src.resize((nw, nh), Image.LANCZOS)
    ex, ey = nw - tw, nh - th
    cx, cy = int(ex * 0.5), int(ey * bias)
    return im.crop((cx, cy, cx + tw, cy + th))


def rounded_panel(size, radius, fill, outline=None, width=0):
    panel = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(panel)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=fill,
                        outline=outline, width=width)
    return panel


TYPECAST_ENV = BASE / ".env.typecast"
TYPECAST_URL = "https://api.typecast.ai/v1/text-to-speech"


def load_voice_config() -> dict:
    return json.loads(VOICES_JSON.read_text(encoding="utf-8"))["characters"]


def typecast_key() -> str:
    for line in TYPECAST_ENV.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("TYPECAST_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("TYPECAST_API_KEY를 찾지 못했습니다")


def typecast_tts(text: str, out_path: Path, cfg: dict):
    import urllib.request
    body = {
        "voice_id": cfg["voice_id"],
        "text": text,
        "model": cfg.get("model", "ssfm-v31"),
        "language": "kor",
        "emotion_preset": cfg.get("emotion_preset", "normal"),
        "emotion_intensity": cfg.get("emotion_intensity", 1.0),
        "audio_tempo": cfg.get("audio_tempo", 1.0),
        "audio_pitch": cfg.get("audio_pitch", 0),
        "audio_format": "mp3",
    }
    req = urllib.request.Request(TYPECAST_URL, data=json.dumps(body).encode("utf-8"),
                                 headers={"X-API-KEY": typecast_key(),
                                          "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        out_path.write_bytes(r.read())


# --------------------------------------------------------------------------- 음성
async def _tts(text: str, out_mp3: Path, voice: str, rate: str, pitch: str):
    import edge_tts
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await comm.save(str(out_mp3))


def audio_envelope(mp3: str, fps: int = FPS) -> list[float]:
    """mp3를 16kHz 모노로 풀어 1/fps 초 창의 RMS를 0~1 입 벌림 값으로 만든다."""
    import array
    import wave
    wav = str(Path(mp3).with_suffix(".env.wav"))
    subprocess.run([FFMPEG_PATH, "-y", "-i", mp3, "-ac", "1", "-ar", "16000", wav],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(wav, "rb") as wf:
        sr = wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    data = array.array("h")
    data.frombytes(raw)
    win = max(1, sr // fps)
    rms = []
    for i in range(0, len(data) - win + 1, win):
        chunk = data[i:i + win]
        rms.append(math.sqrt(sum(v * v for v in chunk) / len(chunk)) / 32768.0)
    if not rms:
        return [0.0]
    loud = sorted(r for r in rms if r > 0.004)
    ref = loud[int(len(loud) * 0.9)] if loud else 0.05
    env = [min(1.0, (r / max(ref, 1e-4)) ** 0.8) for r in rms]
    # 짧은 끊김 메우기 + 부드럽게
    out = []
    for i, v in enumerate(env):
        prev = out[-1] if out else 0.0
        v = max(v, prev * 0.55) if v < prev else v
        out.append(v)
    return out


def synthesize(beats: list[dict], temp_dir: Path, voices: dict, engine: str = "typecast") -> list[dict]:
    temp_dir.mkdir(parents=True, exist_ok=True)
    if engine == "typecast":
        for i, b in enumerate(beats, 1):
            cfg = voices[b["speaker"]]["typecast"]
            typecast_tts(b["text"], temp_dir / f"beat_{i:02d}.wav", cfg)
            print(f"  typecast {i:02d} {b['speaker']} ok")
    else:
        async def run():
            for i, b in enumerate(beats, 1):
                cfg = voices[b["speaker"]]
                await _tts(b["text"], temp_dir / f"beat_{i:02d}.mp3", cfg["voice"], cfg["rate"],
                           cfg.get("pitch", "+0Hz"))
        asyncio.run(run())
    ext = "wav" if engine == "typecast" else "mp3"
    for i, b in enumerate(beats, 1):
        b["audio"] = str(temp_dir / f"beat_{i:02d}.{ext}")
        b["dur"] = probe_duration(Path(b["audio"]))
        b["env"] = audio_envelope(b["audio"])
    return beats


def probe_duration(path: Path) -> float:
    p = subprocess.run([FFMPEG_PATH, "-i", str(path)], capture_output=True, text=True)
    for line in p.stderr.split("\n"):
        if "Duration:" in line:
            h, m, sec = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return float(h) * 3600 + float(m) * 60 + float(sec)
    return 0.0


# --------------------------------------------------------------------------- 정지 레이어
_BG_CACHE = {}


def body_background() -> Image.Image:
    if "bg" not in _BG_CACHE:
        raw = Image.open(BG_9X16).convert("RGB")
        _BG_CACHE["bg"] = cover_crop(raw, W, H - HEADER_H, bias=0.45)
    return _BG_CACHE["bg"]


def char_sprite(name: str, height: int, crop: float | None = None) -> Image.Image:
    """crop=0.6 이면 상반신만 잘라 클로즈업으로 쓴다."""
    key = (name, height, crop)
    if key not in _BG_CACHE:
        im = Image.open(CHARS / f"{name}_transparent.png").convert("RGBA")
        if crop:
            im = im.crop((0, 0, im.width, int(im.height * crop)))
        ratio = height / im.height
        _BG_CACHE[key] = im.resize((max(1, int(im.width * ratio)), height), Image.LANCZOS)
    return _BG_CACHE[key]


def shadow_sprite(width: int, height: int = 44) -> Image.Image:
    key = ("shadow", width)
    if key not in _BG_CACHE:
        sh = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([0, 0, width - 1, height - 1], fill=(40, 30, 18, 70))
        _BG_CACHE[key] = sh.filter(ImageFilter.GaussianBlur(7))
    return _BG_CACHE[key]


def draw_header(img: Image.Image, topic_keyword: str):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, HEADER_H], fill=(255, 255, 255))
    f_title, bb = fit_font(TITLE, W - 120, 54, 36)
    bold_text(d, (W // 2, 74), TITLE, f_title, INK, anchor="mm", weight=2)

    box_line = f"{BRAND} · {topic_keyword}" if topic_keyword else BRAND
    f_box, bb2 = fit_font(box_line, W - 180, 46, 30)
    tw, th = bb2[2] - bb2[0], bb2[3] - bb2[1]
    pad_x, pad_y = 34, 16
    x1 = (W - tw) // 2 - pad_x
    x2 = (W + tw) // 2 + pad_x
    y1, y2 = 150, 150 + th + pad_y * 2
    d.rounded_rectangle([x1, y1, x2, y2], radius=14, fill=ORANGE)
    bold_text(d, (W // 2, (y1 + y2) // 2), box_line, f_box, (255, 255, 255), anchor="mm", weight=2)

    d.line([(60, HEADER_H - 6), (W - 60, HEADER_H - 6)], fill=(232, 232, 232), width=2)


def draw_chapter_pill(img: Image.Image, chapter: str):
    f, bb = fit_font(chapter, 520, 34, 24)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = 18
    panel = rounded_panel((tw + pad * 2, th + pad), 18, (20, 20, 20, 150))
    img.alpha_composite(panel, (44, HEADER_H + 30))
    d = ImageDraw.Draw(img)
    d.text((44 + pad, HEADER_H + 30 + pad // 2), chapter, font=f, fill=(255, 255, 255, 245))


def memo_chip(text: str, size=38) -> Image.Image:
    f, bb = fit_font(text, 460, size, 24)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    w, h = tw + 52, th + 34
    chip = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(chip)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=12, fill=(255, 238, 138, 246),
                        outline=(214, 176, 44, 220), width=3)
    d.polygon([(w - 26, h - 1), (w - 1, h - 26), (w - 1, h - 1)], fill=(246, 205, 84, 255))
    bold_text(d, (w // 2, h // 2 - 1), text, f, (58, 38, 8, 255), anchor="mm", weight=1)
    return chip.rotate(-3, expand=True, resample=Image.BICUBIC)


def draw_caption(img: Image.Image, text: str):
    text = text.strip()
    if not text:
        return
    f, bb = fit_font(text, W - 120, 52, 34)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    if tw > W - 120:  # 아주 길면 두 줄
        words, line1, line2 = text.split(), "", ""
        for w_ in words:
            trial = (line1 + " " + w_).strip()
            if f.getbbox(trial)[2] - f.getbbox(trial)[0] <= W - 140 and not line2:
                line1 = trial
            else:
                line2 = (line2 + " " + w_).strip()
        panel = rounded_panel((W - 100, th * 2 + 62), 20, (12, 12, 12, 170))
        img.alpha_composite(panel, (50, CAPTION_CY - panel.height // 2))
        d = ImageDraw.Draw(img)
        d.text((W // 2, CAPTION_CY - th // 2 - 4), line1, font=f, fill=(255, 255, 255), anchor="mm")
        d.text((W // 2, CAPTION_CY + th // 2 + 8), line2, font=f, fill=(255, 255, 255), anchor="mm")
        return
    pad_x, pad_y = 34, 18
    panel = rounded_panel((tw + pad_x * 2, th + pad_y * 2), 18, (12, 12, 12, 172))
    img.alpha_composite(panel, ((W - panel.width) // 2, CAPTION_CY - panel.height // 2))
    d = ImageDraw.Draw(img)
    bold_text(d, (W // 2, CAPTION_CY), text, f, (255, 255, 255), anchor="mm", weight=2)


def draw_footer(img: Image.Image):
    f = font(26)
    text = FOOTER
    tw = f.getbbox(text)[2] - f.getbbox(text)[0]
    panel = rounded_panel((tw + 44, 54), 14, (255, 255, 255, 150))
    img.alpha_composite(panel, ((W - panel.width) // 2, FOOTER_Y))
    d = ImageDraw.Draw(img)
    d.text((W // 2, FOOTER_Y + 27), text, font=f, fill=(60, 60, 60, 255), anchor="mm")


def draw_subscribe(img: Image.Image):
    f, bb = fit_font(SUBSCRIBE_TEXT, W - 160, 34, 24)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    panel = rounded_panel((tw + 60, th + 28), (th + 28) // 2, (238, 108, 22, 235),
                          outline=(255, 255, 255, 215), width=3)
    x = (W - panel.width) // 2
    img.alpha_composite(panel, (x, HEADER_H + 84))
    d = ImageDraw.Draw(img)
    d.text((W // 2, HEADER_H + 84 + panel.height // 2), SUBSCRIBE_TEXT, font=f,
           fill=(255, 255, 255), anchor="mm", stroke_width=1, stroke_fill=(255, 255, 255))


def draw_memo(lines: list[str], width: int = 386, x: int = 34, y: int = 496):
    """닥터 온 설명에 붙는 노란 인포그래픽 메모지(첫 줄은 굵게)."""
    head_f, body_f = font(34), font(28)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    wrapped = []
    for i, ln in enumerate(lines):
        f = head_f if i == 0 else body_f
        cur = ""
        for word in ln.split(" "):
            trial = (cur + " " + word).strip()
            if tmp.textlength(trial, font=f) <= width - 76 or not cur:
                cur = trial
            else:
                wrapped.append((i == 0, cur))
                cur = word
        if cur:
            wrapped.append((i == 0, cur))
    line_h = 52 if True else 46
    height = 40 + sum(54 if h else 44 for h, _ in wrapped) + 20
    note = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    grad = Image.new("RGBA", (width, height))
    gd = ImageDraw.Draw(grad)
    from_top, to_bottom = (255, 238, 138), (253, 216, 96)
    for yy in range(height):
        t = yy / max(1, height - 1)
        c = tuple(int(from_top[k] + (to_bottom[k] - from_top[k]) * t) for k in range(3))
        gd.line([(0, yy), (width, yy)], fill=c + (255,))
    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1, height - 1], radius=16, fill=248)
    note.paste(grad, (0, 0), mask)
    d = ImageDraw.Draw(note)
    d.rounded_rectangle([1, 1, width - 2, height - 2], radius=16, outline=(214, 176, 44, 220), width=3)
    d.polygon([(width - 46, height - 1), (width - 1, height - 46), (width - 1, height - 1)],
              fill=(246, 205, 84, 255))
    cy = 28
    for is_head, txt in wrapped:
        if is_head:
            bold_text(d, (38, cy), txt, head_f, (58, 38, 8, 255), weight=1)
            cy += 54
        else:
            d.ellipse([42, cy + 15, 50, cy + 23], fill=(120, 84, 20, 255))
            d.text((62, cy), txt, font=body_f, fill=(46, 38, 26, 255))
            cy += 44
    # 마스킹 테이프
    tape_w, tape_h = 120, 40
    tape = Image.new("RGBA", (tape_w, tape_h), (255, 252, 235, 130))
    note.alpha_composite(tape.rotate(-8, expand=True, resample=Image.BICUBIC), (28, -16))
    return note.rotate(-2, expand=True, resample=Image.BICUBIC)


def draw_teaser_badge(img: Image.Image, text: str):
    f, bb = fit_font(text, W - 200, 32, 22)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    panel = rounded_panel((tw + 48, th + 26), 16, (238, 108, 22, 240))
    img.alpha_composite(panel, ((W - panel.width) // 2, HEADER_H + 96))
    d = ImageDraw.Draw(img)
    d.text((W // 2, HEADER_H + 96 + panel.height // 2), text, font=f, fill=(255, 255, 255), anchor="mm")


def build_base(beat: dict, keyword: str, topic_keyword: str) -> Image.Image:
    base = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    draw_header(base, topic_keyword)
    base.paste(body_background(), (0, HEADER_H))
    draw_chapter_pill(base, beat["chapter"])
    if beat.get("memo"):
        memo = draw_memo(beat["memo"])
        base.alpha_composite(memo, (34, 500))
    elif keyword and not beat.get("closeup"):
        chip = memo_chip(keyword)
        base.alpha_composite(chip, (W - chip.width - 44, HEADER_H + 26))
    if beat.get("badge"):
        draw_teaser_badge(base, beat["badge"])
    draw_caption(base, beat["caption"])
    draw_footer(base)
    return base


def _skin_at(src: Image.Image, x: float, y: float, r: int = 7):
    x, y = int(x), int(y)
    box = src.crop((max(0, x - r), max(0, y - r), min(src.width, x + r), min(src.height, y + r)))
    px = [p for p in box.getdata() if p[3] > 200]
    if not px:
        return (253, 222, 196)
    px.sort(key=lambda p: p[0] + p[1] + p[2])
    return px[len(px) // 2][:3]


def face_color(name: str):
    """입 둘레 고리에서 붉은 기가 강한 화장·턱선을 뺀 피부색 중앙값(캐릭터당 1회 계산)."""
    key = ("facecolor", name)
    if key in _BG_CACHE:
        return _BG_CACHE[key]
    import numpy as np
    cx, cy, cw, ch = MOUTH_ANCHORS[name]
    arr = np.array(Image.open(CHARS / f"{name}_transparent.png").convert("RGB")).astype(int)
    H, W = arr.shape[:2]
    ys, xs = np.mgrid[0:H, 0:W]
    e = ((xs - cx) / (cw * 0.5)) ** 2 + ((ys - cy) / (ch * 0.5)) ** 2
    ring = (e >= 1.15 ** 2) & (e <= 1.9 ** 2)
    px = arr[ring]
    R, G, B = px[:, 0], px[:, 1], px[:, 2]
    keep = (R > 230) & (G > 180) & (B > 160) & ((R - G) < 45)
    col = tuple(int(v) for v in np.median(px[keep], axis=0)) if keep.any() else (253, 222, 196)
    _BG_CACHE[key] = col
    return col


def mouth_sprite(name: str, level: float) -> Image.Image:
    """원래 입 전체를 같은 피부색으로 덮고, 그 중심에 카툰 입을 그린 조각."""
    level = min(_LEVELS, key=lambda v: abs(v - level))
    key = ("mouth", name, level)
    if key in _BG_CACHE:
        return _BG_CACHE[key]
    cx, cy, cw, ch = MOUTH_ANCHORS[name]
    skin = face_color(name)
    cw2, ch2 = int(cw * 1.06), int(ch * 1.18)          # 원래 입 윗니까지 확실히 덮는다
    cy2 = cy - int(ch * 0.06)
    pad = int(min(cw2, ch2) * 0.28)
    w, h = cw2 + pad * 2, ch2 + pad * 2
    im = Image.new("RGBA", (w, h), skin + (0,))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([pad, pad, pad + cw2 - 1, pad + ch2 - 1],
                                           radius=int(ch2 * 0.40), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(max(4, int(pad * 0.55))))
    im.putalpha(mask)
    mouth_center = (w / 2, h / 2 + (cy - cy2) * 0)
    d = ImageDraw.Draw(im)
    mw, mh = cw * 0.78, ch * 0.70
    cxm = w / 2
    cym = h / 2 + (cy - cy2) * 0
    lip = max(2, int(mh * 0.11))
    if level <= 0.16:
        # 다문 입: 살짝 올라간 미소 선 하나만 남긴다
        d.line([(cxm - mw * 0.40, cym + mh * 0.04), (cxm - mw * 0.12, cym + mh * 0.14),
                (cxm + mw * 0.16, cym + mh * 0.14), (cxm + mw * 0.40, cym + mh * 0.02)],
               fill=LIP_LINE, width=lip, joint="curve")
    else:
        ow, oh = mw * (0.62 + 0.28 * level), mh * level
        box = [cxm - ow / 2, cym - oh * 0.45, cxm + ow / 2, cym + oh * 0.55]
        d.ellipse(box, fill=MOUTH_INK, outline=LIP_LINE, width=lip)
        if level >= 0.55:
            d.ellipse([box[0] + ow * 0.16, box[1] + oh * 0.05,
                       box[2] - ow * 0.16, box[1] + oh * 0.30], fill=(250, 246, 240))
        if level >= 0.4:
            d.ellipse([box[0] + ow * 0.22, box[3] - oh * 0.40,
                       box[2] - ow * 0.22, box[3] - oh * 0.05], fill=MOUTH_TONGUE)
    _BG_CACHE[key] = im
    return im


def draw_mouth(frame: Image.Image, name: str, height: int, crop: float | None, sprite_left: int,
               sprite_top: int, openness: float):
    """말하는 캐릭터의 입만 여닫는다(원본 좌표를 렌더 배율로 환산)."""
    if name not in MOUTH_ANCHORS:
        return
    mx, my, mw, mh = MOUTH_ANCHORS[name]
    key_h = ("srch", name)
    if key_h not in _BG_CACHE:
        _BG_CACHE[key_h] = Image.open(CHARS / f"{name}_transparent.png").height
    used_h = _BG_CACHE[key_h] * (crop if crop else 1.0)
    scale = height / used_h
    m = mouth_sprite(name, openness)
    tw, th = max(1, int(m.width * scale)), max(1, int(m.height * scale))
    m = m.resize((tw, th), Image.LANCZOS)
    frame.alpha_composite(m, (int(sprite_left + mx * scale - tw / 2),
                              int(sprite_top + my * scale - th / 2)))


def render_frames(beats: list[dict], timeline: list[dict], out_raw, keyword_by_beat: list[str],
                  topic_keyword: str):
    base_cache = [build_base(b, keyword_by_beat[i], topic_keyword) for i, b in enumerate(beats)]
    total = timeline[-1]["end"]
    n_frames = int(math.ceil(total * FPS))
    idx = 0
    for f_i in range(n_frames):
        t = f_i / FPS
        while idx < len(beats) - 1 and t >= timeline[idx]["end"]:
            idx += 1
        beat = beats[idx]
        local = t - timeline[idx]["start"]
        frame = base_cache[idx].copy()

        if t < 2.0:
            draw_subscribe(frame)

        for slot in beat["cast"]:
            name, height, cx = slot["name"], slot["height"], slot["cx"]
            speaking = name == beat["speaker"]
            # 아주 느리고 부드러운 호흡 모션만 남긴다(상하 2~3px, 주기 3~4초, 회전 없음)
            phase = 0.0 if speaking else (cx % 360) / 57.3
            bob = 2.4 * math.sin(2 * math.pi * local / 3.8 + phase)
            sway = 0.7 * math.sin(2 * math.pi * local / 4.6 + phase)
            if beat.get("nod"):
                bob += 1.6 * max(0.0, math.sin(2 * math.pi * local / 2.2))
            sprite = char_sprite(name, height, slot.get("crop"))
            x = int(cx - sprite.width / 2 + sway)
            y = int(CHAR_BASELINE - sprite.height + bob)
            if not slot.get("crop"):
                sh = shadow_sprite(int(sprite.width * 0.72))
                frame.alpha_composite(sh, (int(cx - sh.width / 2), CHAR_BASELINE - 16))
            frame.alpha_composite(sprite, (x, y))
            if speaking and local < beat.get("dur", 0):
                fi = int(round(local * FPS))
                env = beat.get("env") or []
                openness = env[fi] if 0 <= fi < len(env) else 0.0
                draw_mouth(frame, name, height, slot.get("crop"), x, y, openness)

        if keyword_by_beat[idx] and not beat.get("memo") and not beat.get("closeup"):
            chip = memo_chip(keyword_by_beat[idx])
            slide = 1.0
            if local < 0.4:
                slide = local / 0.4
            easing = 1 - (1 - slide) ** 3
            x = int((W - chip.width - 44) + (1 - easing) * 160)
            frame.alpha_composite(chip, (x, HEADER_H + 26))

        out_raw.write(frame.convert("RGB").tobytes())


# --------------------------------------------------------------------------- 오디오
def build_audio(beats: list[dict], timeline: list[dict], out_mp3: Path):
    inputs, filters, labels = [], [], []
    for i, (b, tl) in enumerate(zip(beats, timeline)):
        inputs += ["-i", b["audio"]]
        delay = int(round(tl["start"] * 1000))
        filters.append(f"[{i}:a]adelay={delay}|{delay},apad=whole_dur={timeline[-1]['end']:.3f}[a{i}]")
        labels.append(f"[a{i}]")
    fc = ";".join(filters) + ";" + "".join(labels) + f"amix=inputs={len(beats)}:normalize=0[aout]"
    subprocess.run([FFMPEG_PATH, "-y", *inputs, "-filter_complex", fc, "-map", "[aout]",
                    "-ac", "2", "-ar", "44100", "-b:a", "192k", str(out_mp3)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# --------------------------------------------------------------------------- 메인
def render_paperdoll_shorts(beats: list[dict], out_path: str, topic_keyword: str,
                            temp_dir: str, keyword_by_beat: list[str] | None = None,
                            gap: float = 0.35):
    temp = Path(temp_dir)
    temp.mkdir(parents=True, exist_ok=True)
    voices = load_voice_config()
    beats = synthesize(beats, temp, voices)
    keyword_by_beat = keyword_by_beat or ["" for _ in beats]

    timeline, acc = [], 0.0
    for b in beats:
        dur = max(1.6, b["dur"] + gap)
        timeline.append({"start": round(acc, 3), "end": round(acc + dur, 3), "dur": round(dur, 3)})
        acc += dur
    audio = temp / "voice_track.mp3"
    build_audio(beats, timeline, audio)

    total = timeline[-1]["end"]
    cmd = [FFMPEG_PATH, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", str(audio),
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE)
    render_frames(beats, timeline, proc.stdin, keyword_by_beat, topic_keyword)
    proc.stdin.close()
    err = proc.stderr.read().decode("utf-8", "ignore")
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg 실패 rc={rc}\n{err[-1500:]}")
    return {"out": out_path, "total_sec": round(total, 2), "beats": timeline,
            "frames": int(math.ceil(total * FPS))}


if __name__ == "__main__":
    print("library module")
