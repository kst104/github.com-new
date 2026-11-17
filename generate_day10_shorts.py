#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 10 유튜브 쇼츠 생성기 (칠판 분필 드로잉 특강 스타일)
주제: 겨울철 음주 후 귀가 시 저체온증의 치명적 위험 (응급실 단골 사고)
키워드: 겨울철 음주 저체온증, 저체온증 증상 체온, 동상 응급처치
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.chalkboard_video_engine import render_chalkboard_shorts, FFMPEG_PATH

DAY_DIR = BASE_DIR / "content" / "2026-11-17-01"
CHALK_DIR = DAY_DIR / "chalkboard"
PREVIEW_DIR = CHALK_DIR / "preview"
CHALK_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

ART_DIR = Path("/workspace/assets/chalkboard/day10")
DOWNLOADS = Path("/workspace/downloads")

OUT_MP4 = DOWNLOADS / "Day10_겨울철_음주_저체온증_칠판드로잉_쇼츠.mp4"
GIF_OUT = DOWNLOADS / "Day10_겨울철_음주_저체온증_미리보기.gif"

SCENES = [
    {
        "badge": "⚠️ 겨울철 음주 경고",
        "keyword": "술의 착각",
        "chalk_img": str(ART_DIR / "scene1_drunk_walk_home_undressed.png"),
        "main_text": "술 마시고 몸이 덥다고\n코트를 벗으시나요",
        "sub_text": "따뜻한 것은 피부뿐, 심부체온은 내려갑니다",
        "voice": "겨울 회식 후에 몸이 덥다며 코트를 벗고 걷는 분들이 많습니다. 그런데 그 따뜻함은 피부에서만 느껴지는 감각입니다.",
    },
    {
        "badge": "🏥 피부 혈관의 반전",
        "keyword": "혈관 확장",
        "chalk_img": str(ART_DIR / "scene2_skin_vessels_heat_loss.png"),
        "main_text": "알코올이 피부 혈관을 열어\n열을 밖으로 내보냅니다",
        "sub_text": "떨림 반사까지 함께 꺼집니다",
        "voice": "술은 피부 혈관을 열어 열을 밖으로 빼내고, 추울 때 몸을 떨게 하는 반사까지 꺼버립니다.",
    },
    {
        "badge": "💡 체온 단계",
        "keyword": "삼십이 도 경계",
        "chalk_img": str(ART_DIR / "scene3_thermometer_stages_drowsy.png"),
        "main_text": "삼십오 도 아래는 저체온증\n삼십이 도 이하면 말이 어눌해집니다",
        "sub_text": "떨림이 멈추면 더 위험한 신호입니다",
        "voice": "체온이 삼십오 도 아래로 떨어지면 저체온증입니다. 삼십이 도 이하에서는 말이 어눌해지고, 떨림이 멈추면 더 위험한 신호입니다.",
    },
    {
        "badge": "🚨 동상 응급처치",
        "keyword": "문지르지 마세요",
        "chalk_img": str(ART_DIR / "scene4_no_rubbing_warm_water.png"),
        "main_text": "얼어붙은 손은 문지르지 말고\n삼십칠에서 삼십구 도 미온수에",
        "sub_text": "십오 분에서 삼십 분, 재동결은 금지입니다",
        "voice": "얼어붙은 손과 발은 절대로 문지르지 마십시오. 삼십칠에서 삼십구 도 미온수에 십오 분에서 삼십 분간 담그십시오.",
    },
    {
        "badge": "👨‍👩‍👧 가족 안전",
        "keyword": "일일구 신고",
        "chalk_img": str(ART_DIR / "scene5_call_emergency_at_door.png"),
        "main_text": "의식이 흐리거나 떨림이 멈추면\n바로 일일구에 신고하세요",
        "sub_text": "우리 가족의 겨울 귀가, 지금 꼭 공유해 주세요",
        "voice": "의식이 흐려지거나 떨림이 멈추면 바로 일일구에 신고하십시오. 우리 가족의 겨울 귀가, 지금 꼭 공유해 주세요.",
    },
]


def write_screenplay():
    total_chars = sum(len(s["voice"]) for s in SCENES)
    lines = [
        "# Day 10 유튜브 쇼츠 대본 - 겨울철 음주 후 귀가와 저체온증",
        "",
        "- 주제: 겨울철 음주 후 귀가 시 저체온증의 치명적 위험과 동상 응급처치",
        "- 키워드: 겨울철 음주 저체온증 / 저체온증 증상 체온 / 동상 응급처치",
        "- 규격: 1080x1920 세로형 9:16, 칠판 분필 드로잉 특강 스타일, 5개 씬",
        "- 음성: Edge-TTS ko-KR-InJoonNeural, 속도 +5%",
        f"- 대본 분량: {total_chars}자",
        "",
        "| 씬 | 배지 | 노란 키워드 | 화면 문구 | 내레이션 |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for i, s in enumerate(SCENES, 1):
        main = s["main_text"].replace("\n", " / ")
        lines.append(f"| {i} | {s['badge']} | {s['keyword']} | {main} | {s['voice']} |")
    lines += [
        "",
        "## 연출 메모",
        "- 1씬은 술자리 뒤 홀로 눈길을 걷는 모습으로 시작하고, 코트를 벗는 행동이 위험 신호임을 화면 문구로 못 박는다.",
        "- 2씬은 피부 단면에서 혈관이 확장되고 열이 화살표로 빠져나가는 도해를 쓴다.",
        "- 3씬은 낮아진 체온계와 떨리는 사람, 처진 사람을 나란히 두어 단계 변화를 보여준다.",
        "- 4씬은 문지르기에 금지 표시를, 미온수 침수에는 김나는 대야를 그려 O/X를 그림으로 전달한다.",
        "- 숫자는 대본에서 한글 발음으로 적었다(삼십오 도, 삼십이 도, 삼십칠에서 삼십구 도, 십오 분). 119는 일일구로 읽는다.",
        "- 그림에는 글자와 일본어 가나를 넣지 않았다. 한글 자막은 엔진이 그린다.",
        "- 마지막 씬은 신고 기준과 공유 유도로 닫는다.",
        "",
    ]
    (CHALK_DIR / "shorts_script.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ 대본 저장: {CHALK_DIR / 'shorts_script.md'}")


def archive_art():
    for s in SCENES:
        src = Path(s["chalk_img"])
        if src.exists():
            shutil.copy(src, CHALK_DIR / src.name)


def make_preview(video: Path):
    p = subprocess.run([FFMPEG_PATH, "-i", str(video)], capture_output=True, text=True)
    total = 0.0
    for line in p.stderr.split("\n"):
        if "Duration:" in line:
            h, m, sec = line.split("Duration:")[1].split(",")[0].strip().split(":")
            total = float(h) * 3600 + float(m) * 60 + float(sec)
            break

    subprocess.run([
        FFMPEG_PATH, "-y", "-i", str(video),
        "-vf", "fps=1.6,scale=420:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=192[p];[s1][p]paletteuse=dither=bayer",
        "-loop", "0", str(GIF_OUT)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    shutil.copy(GIF_OUT, PREVIEW_DIR / "moving_preview.gif")

    caps = []
    for idx, frac in enumerate([0.10, 0.42, 0.74], 1):
        cap = DOWNLOADS / f"Day10_scene_{idx}.png"
        subprocess.run([
            FFMPEG_PATH, "-y", "-ss", f"{total * frac:.2f}", "-i", str(video),
            "-frames:v", "1", str(cap)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.copy(cap, PREVIEW_DIR / f"scene{idx}_preview.png")
        caps.append(cap)
    return total, caps


def main():
    write_screenplay()
    archive_art()

    render_chalkboard_shorts(SCENES, str(OUT_MP4), temp_dir="/tmp/day10_chalk_shorts_build")
    shutil.copy(OUT_MP4, CHALK_DIR / "chalkboard_shorts_video.mp4")

    total, caps = make_preview(OUT_MP4)

    print("\n✅ Day 10 쇼츠 완성")
    print(f"   - 영상: {OUT_MP4} ({total:.2f}초)")
    print(f"   - 아카이브: {CHALK_DIR / 'chalkboard_shorts_video.mp4'}")
    print(f"   - GIF: {GIF_OUT} ({GIF_OUT.stat().st_size / 1024 / 1024:.2f}MB)")
    for c in caps:
        print(f"   - 캡처: {c}")


if __name__ == "__main__":
    main()
