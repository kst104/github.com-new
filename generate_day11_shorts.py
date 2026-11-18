#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 11 유튜브 쇼츠 생성기 (칠판 분필 드로잉 특강 스타일)
주제: 무릎 관절염·오십견 환자를 위한 초겨울 관절 보온과 온찜질 스트레칭
키워드: 겨울철 무릎 관절염, 오십견 스트레칭, 관절 통증 온찜질
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.chalkboard_video_engine import render_chalkboard_shorts, FFMPEG_PATH

DAY_DIR = BASE_DIR / "content" / "2026-11-18-01"
CHALK_DIR = DAY_DIR / "chalkboard"
PREVIEW_DIR = CHALK_DIR / "preview"
CHALK_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

ART_DIR = Path("/workspace/assets/chalkboard/day11")
DOWNLOADS = Path("/workspace/downloads")

OUT_MP4 = DOWNLOADS / "Day11_무릎관절염_오십견_칠판드로잉_쇼츠.mp4"
GIF_OUT = DOWNLOADS / "Day11_무릎관절염_오십견_미리보기.gif"

SCENES = [
    {
        "badge": "⚠️ 겨울철 무릎 경고",
        "keyword": "아침 첫 계단",
        "chalk_img": str(ART_DIR / "scene1_morning_stairs_stiff_knee.png"),
        "main_text": "겨울 아침 무릎이 굳어\n계단이 무섭다면",
        "sub_text": "밤새 움직이지 않은 관절이 가장 뻣뻣합니다",
        "voice": "겨울 아침에 무릎이 굳어 첫 계단이 무섭다는 분들이 많습니다. 밤새 움직이지 않은 관절이 가장 뻣뻣한 상태이기 때문입니다.",
    },
    {
        "badge": "🏥 관절 속 액체의 변화",
        "keyword": "활액 점도",
        "chalk_img": str(ART_DIR / "scene2_knee_fluid_viscosity_diagram.png"),
        "main_text": "기온이 떨어지면\n활액이 걸쭉해집니다",
        "sub_text": "미끄러짐이 줄어 첫 움직임이 시큰합니다",
        "voice": "기온이 떨어지면 무릎을 채운 활액의 점도가 올라갑니다. 미끄러짐이 줄어 첫 움직임이 뻣뻣하고 시큰해집니다.",
    },
    {
        "badge": "💡 온찜질의 기준",
        "keyword": "붓으면 냉, 굳으면 온",
        "chalk_img": str(ART_DIR / "scene3_warm_compress_towel_wrapped.png"),
        "main_text": "뻣뻣하면 온찜질\n붓고 뜨거우면 냉찜질",
        "sub_text": "사십오 도 이하, 수건 두어 겹, 십오 분",
        "voice": "기준은 하나입니다. 뻣뻣하면 온찜질, 붓고 뜨거우면 냉찜질입니다. 사십오 도 이하로 수건을 두어 겹 감싸고 십오 분에서 이십 분까지만 하십시오.",
    },
    {
        "badge": "🏠 온찜질 다음 십 분",
        "keyword": "대퇴사두근 운동",
        "chalk_img": str(ART_DIR / "scene4_seated_knee_extension_exercise.png"),
        "main_text": "열로 풀고 나서 움직여야\n관절이 부드러워집니다",
        "sub_text": "허벅지에 힘 주어 무릎 누르기부터",
        "voice": "온찜질로 근육을 푼 뒤 십 분간 스트레칭을 하십시오. 허벅지에 힘을 주어 무릎 뒤를 바닥으로 누르는 동작부터 시작하십시오.",
    },
    {
        "badge": "🚨 밤에 아픈 어깨",
        "keyword": "오십견 신호",
        "chalk_img": str(ART_DIR / "scene5_night_shoulder_pain_towel.png"),
        "main_text": "등 뒤로 손이 안 가고\n밤에 아프다면 오십견",
        "sub_text": "통증기에는 펴지 말고, 가라앉힌 뒤 늘리세요",
        "voice": "등 뒤로 손이 가지 않고 밤에 어깨가 아프면 오십견을 의심해야 합니다. 통증기에는 무리하게 펴지 말고 가라앉힌 뒤에 늘리십시오. 부모님께 꼭 공유해 주세요.",
    },
]


def write_screenplay():
    total_chars = sum(len(s["voice"]) for s in SCENES)
    lines = [
        "# Day 11 유튜브 쇼츠 대본 - 겨울철 무릎 관절염과 오십견 온찜질 스트레칭",
        "",
        "- 주제: 무릎 관절염·오십견 환자를 위한 초겨울 관절 보온과 온찜질 스트레칭",
        "- 키워드: 겨울철 무릎 관절염 / 오십견 스트레칭 / 관절 통증 온찜질",
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
        "- 1씬은 아파트 계단참에서 첫 발을 내딛지 못하는 등 뒤 모습으로 시작해, 겨울 아침 강직을 한 장면으로 전달한다.",
        "- 2씬은 무릎 관절 단면 도해로 연골과 활액 주머니, 좌우 화살표로 제한된 미끄러짐을 보여준다.",
        "- 3씬은 수건으로 감싼 온수팩을 무릎에 얹은 모습으로 온도와 겹 수 규칙을 화면 문구로 못 박는다.",
        "- 4씬은 의자에 앉아 다리를 펴는 동작으로 온찜질 뒤 스트레칭 순서를 몸으로 보여준다.",
        "- 5씬은 밤 침대에서 어깨를 붙잡은 모습과 등 뒤 수건으로 오십견 신호를 전달하고 공유로 닫는다.",
        "- 숫자는 대본에서 한글 발음으로 적었다(사십오 도, 십오 분, 이십 분, 십 분). TTS 오독을 막기 위한 표기다.",
        "- 그림에는 글자와 일본어 가나를 넣지 않았다. 한글 자막은 엔진이 그린다.",
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
        cap = DOWNLOADS / f"Day11_scene_{idx}.png"
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

    render_chalkboard_shorts(SCENES, str(OUT_MP4), temp_dir="/tmp/day11_chalk_shorts_build")
    shutil.copy(OUT_MP4, CHALK_DIR / "chalkboard_shorts_video.mp4")

    total, caps = make_preview(OUT_MP4)

    print("\n✅ Day 11 쇼츠 완성")
    print(f"   - 영상: {OUT_MP4} ({total:.2f}초)")
    print(f"   - 아카이브: {CHALK_DIR / 'chalkboard_shorts_video.mp4'}")
    print(f"   - GIF: {GIF_OUT} ({GIF_OUT.stat().st_size / 1024 / 1024:.2f}MB)")
    for c in caps:
        print(f"   - 캡처: {c}")


if __name__ == "__main__":
    main()
