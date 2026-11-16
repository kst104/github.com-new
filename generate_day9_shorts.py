#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 9 유튜브 쇼츠 생성기 (칠판 분필 드로잉 특강 스타일)
주제: 건조한 겨울 피부 가려움증(피부건조증)과 온수 샤워 시 치명적 실수
키워드: 겨울철 피부건조증, 가려움증 보습제, 피부 장벽 크림
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.chalkboard_video_engine import render_chalkboard_shorts, FFMPEG_PATH

DAY_DIR = BASE_DIR / "content" / "2026-11-16-02"
CHALK_DIR = DAY_DIR / "chalkboard"
CHALK_DIR.mkdir(parents=True, exist_ok=True)

ART_DIR = Path("/workspace/assets/chalkboard/day9")
DOWNLOADS = Path("/workspace/downloads")

OUT_MP4 = DOWNLOADS / "Day9_겨울철_피부건조증_온수샤워_칠판드로잉_쇼츠.mp4"
GIF_OUT = DOWNLOADS / "Day9_칠판쇼츠_움직이는미리보기.gif"

SCENES = [
    {
        "badge": "겨울철 목욕 경고",
        "keyword": "뜨거운 물의 배신",
        "chalk_img": str(ART_DIR / "scene1_hot_shower_itchy_legs.png"),
        "main_text": "뜨거운 물로 샤워하고 나면\n다리가 근질근질하신가요",
        "sub_text": "씻어서가 아니라 지질이 녹아서입니다",
        "voice": "겨울에 뜨거운 물로 샤워하고 나면 다리가 근질근질 가려우신 적 있으신가요? 그 뜨거운 물이 피부에는 부담이 됩니다.",
    },
    {
        "badge": "피부 장벽의 비밀",
        "keyword": "세라마이드 유출",
        "chalk_img": str(ART_DIR / "scene2_lipid_barrier_washed_away.png"),
        "main_text": "사십 도가 넘는 물이\n피부 기름막을 녹여 씻어냅니다",
        "sub_text": "지질 장벽이 무너지면 수분이 새어 나갑니다",
        "voice": "피부 장벽은 세라마이드라는 지질이 벽돌 사이를 메우고 있는데, 사십 도가 넘는 뜨거운 물이 이 기름막을 녹여 씻어냅니다.",
    },
    {
        "badge": "치명적 실수",
        "keyword": "열탕 목욕 금지",
        "chalk_img": str(ART_DIR / "scene3_shower_rules_thermometer_clock.png"),
        "main_text": "뜨거운 물에 오래 쪼이면\n가려움은 더 심해집니다",
        "sub_text": "삼십팔에서 사십 도, 십 분 이내가 정답",
        "voice": "뜨거운 물에 오래 쪼이면 가려움은 오히려 심해집니다. 물온도는 삼십팔에서 사십 도, 십 분 이내가 좋습니다.",
    },
    {
        "badge": "의사의 삼 분 법칙",
        "keyword": "샤워 후 삼 분",
        "chalk_img": str(ART_DIR / "scene4_moisturize_within_3min.png"),
        "main_text": "물기를 살짝 남긴 채\n삼 분 안에 보습제를 바르세요",
        "sub_text": "세라마이드 크림이 장벽 회복을 돕습니다",
        "voice": "샤워 후 물기를 살짝 남긴 삼 분 안에 세라마이드 보습제를 바르세요. 이게 보습 골든타임입니다.",
    },
    {
        "badge": "가족 건강 지키기",
        "keyword": "진물은 진료",
        "chalk_img": str(ART_DIR / "scene5_scratched_skin_see_doctor.png"),
        "main_text": "긁어서 진물이 나거나\n밤마다 가려우면 진료받으세요",
        "sub_text": "우리 가족의 겨울 피부, 지금 꼭 공유해 주세요",
        "voice": "긁어서 진물이 나거나 밤마다 가려움에 깨신다면 피부과 진료를 받으세요. 우리 가족의 겨울 피부, 지금 꼭 공유해 주세요.",
    },
]


def write_screenplay():
    total_chars = sum(len(s["voice"]) for s in SCENES)
    lines = [
        "# Day 9 유튜브 쇼츠 대본 - 겨울철 피부건조증과 온수 샤워",
        "",
        "- 주제: 건조한 겨울 피부 가려움증과 온수 샤워 시 치명적 실수",
        "- 키워드: 겨울철 피부건조증 / 가려움증 보습제 / 피부 장벽 크림",
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
        "- 2씬은 벽돌(각질세포)과 모르타르(세라마이드 지질) 비유로 장벽 붕괴를 설명한다.",
        "- 숫자는 대본에서 한글 발음으로 적었다(사십 도, 삼십팔, 십 분, 삼 분).",
        "- 그림에는 글자와 일본어 가나를 넣지 않았다. 한글 자막은 엔진이 그린다.",
        "- 마지막 씬은 진료 기준과 공유 유도로 닫는다.",
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

    caps = []
    for idx, frac in enumerate([0.10, 0.42, 0.74], 1):
        cap = DOWNLOADS / f"Day9_씬{idx}_미리보기.png"
        subprocess.run([
            FFMPEG_PATH, "-y", "-ss", f"{total * frac:.2f}", "-i", str(video),
            "-frames:v", "1", str(cap)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        caps.append(cap)
    return total, caps


def main():
    write_screenplay()
    archive_art()

    render_chalkboard_shorts(SCENES, str(OUT_MP4), temp_dir="/tmp/day9_chalk_shorts_build")
    shutil.copy(OUT_MP4, CHALK_DIR / "chalkboard_shorts_video.mp4")

    total, caps = make_preview(OUT_MP4)

    print(f"\n✅ Day 9 쇼츠 완성")
    print(f"   - 영상: {OUT_MP4} ({total:.2f}초)")
    print(f"   - 아카이브: {CHALK_DIR / 'chalkboard_shorts_video.mp4'}")
    print(f"   - GIF: {GIF_OUT} ({GIF_OUT.stat().st_size / 1024 / 1024:.2f}MB)")
    for c in caps:
        print(f"   - 캡처: {c}")


if __name__ == "__main__":
    main()
