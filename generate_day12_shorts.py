#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 12 유튜브 쇼츠 생성기 (칠판 분필 드로잉 특강 스타일)
주제: 만성 호흡기 질환자(천식·COPD)의 찬 공기 기관지 수축 방어법
키워드: 찬 공기 천식 기침, 겨울철 호흡기 관리, 방한 마스크 효과
"""

import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.chalkboard_video_engine import render_chalkboard_shorts, FFMPEG_PATH

DAY_DIR = BASE_DIR / "content" / "2026-11-19-01"
CHALK_DIR = DAY_DIR / "chalkboard"
PREVIEW_DIR = CHALK_DIR / "preview"
CHALK_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

ART_DIR = Path("/workspace/assets/chalkboard/day12")
DOWNLOADS = Path("/workspace/downloads")

OUT_MP4 = DOWNLOADS / "Day12_만성호흡기_찬공기_칠판드로잉_쇼츠.mp4"
GIF_OUT = DOWNLOADS / "Day12_만성호흡기_찬공기_미리보기.gif"

SCENES = [
    {
        "badge": "겨울 아침 경고",
        "keyword": "찬 공기 자극",
        "chalk_img": str(ART_DIR / "scene1_cold_morning_doorway_breath.png"),
        "main_text": "문을 열자마자\n숨이 조여 옵니다",
        "sub_text": "영하의 공기가 점막의 열과 물을 빼앗습니다",
        "voice": "겨울 아침 문을 열자마자 숨이 조여 오는 분들이 있습니다. 영하의 공기가 기도 점막의 열을 빼앗고, 습도까지 함께 빼앗기 때문입니다.",
    },
    {
        "badge": "기도가 좁아지는 이유",
        "keyword": "부종과 수축",
        "chalk_img": str(ART_DIR / "scene2_bronchoconstriction_diagram.png"),
        "main_text": "점막이 부으면\n기도가 좁아집니다",
        "sub_text": "차갑고 건조한 자극이 근육까지 조입니다",
        "voice": "찬 공기가 닿으면 점막의 혈관이 부어 기도 벽이 두꺼워집니다. 차갑고 건조한 자극은 기도를 둘러싼 근육까지 수축시킵니다. 그래서 마른기침이 먼저 시작됩니다.",
    },
    {
        "badge": "마스크의 진짜 효과",
        "keyword": "작은 온실",
        "chalk_img": str(ART_DIR / "scene3_winter_mask_warm_air.png"),
        "main_text": "마스크와 목도리는\n공기를 데우고 적십니다",
        "sub_text": "안쪽 공기층이 완충재가 됩니다",
        "voice": "마스크와 목도리의 효과는 필터가 아니라 안쪽에 생기는 공기층입니다. 체온으로 데워진 공기가 다음 숨을 덥고 촉촉하게 만들어 줍니다.",
    },
    {
        "badge": "외출 전 십오 분",
        "keyword": "준비운동과 코 호흡",
        "chalk_img": str(ART_DIR / "scene4_scarf_nose_breathing.png"),
        "main_text": "외출 전에 몸을 데우고\n첫 십 분은 천천히",
        "sub_text": "코로 숨쉬면 공기가 데워집니다",
        "voice": "외출 전에 몸을 데우고 코와 입을 덮은 뒤, 첫 십 분은 천천히 거르십시오. 코로 숨쉬는 것이 가장 값싼 보호 장치입니다.",
    },
    {
        "badge": "응급 호출 신호",
        "keyword": "일일구",
        "chalk_img": str(ART_DIR / "scene5_inhaler_rescue_call.png"),
        "main_text": "흡입제를 써도 이십 분\n숨이 차면 일일구",
        "sub_text": "직접 운전하지 마시고 꼭 공유해 주세요",
        "voice": "구조 흡입제를 써도 이십 분이 지나도록 숨이 차면 일일구를 부르십시오. 직접 운전하지 마시고 꼭 공유해 주세요.",
    },
]


def write_screenplay():
    total_chars = sum(len(s["voice"]) for s in SCENES)
    lines = [
        "# Day 12 유튜브 쇼츠 대본 - 만성 호흡기 질환자의 찬 공기 방어법",
        "",
        "- 주제: 만성 호흡기 질환자(천식·COPD)의 찬 공기 기관지 수축 방어법",
        "- 키워드: 찬 공기 천식 기침 / 겨울철 호흡기 관리 / 방한 마스크 효과",
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
        "- 1씬은 새벽 아파트 현관을 나서며 가슴을 누르고 입김을 내뿜는 장면으로, 첫 숨의 자극을 한 컷에 전달한다.",
        "- 2씬은 기관과 기관지 단면 도해로 정상 기도와 좁아진 기도를 비교하고, 빨간 분필로 근육층 수축을 표시한다.",
        "- 3씬은 방한 마스크를 쓴 옆얼굴에 따뜻한 공기 화살표를 그려 가온·가습 원리를 보여준다.",
        "- 4씬은 목도리로 입을 가리고 코로 숨쉬는 모습과 비강에서 폐로 이어지는 점선 화살표로 순서를 전달한다.",
        "- 5씬은 스페이서를 끼운 흡입기와 구급차, 응급 표시가 있는 휴대전화로 마무리하고 공유로 닫는다.",
        "- 숫자는 대본에서 한글 발음으로 적었다(십오 분, 십 분, 이십 분, 일일구). TTS 오독을 막기 위한 표기다.",
        "- 그림에는 글자와 일본어 가나를 넣지 않았다. 한글 자막은 엔진이 그린다.",
        "",
    ]
    (CHALK_DIR / "shorts_script.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ 대본 저장: {CHALK_DIR / 'shorts_script.md'} ({total_chars}자)")


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
        cap = DOWNLOADS / f"Day12_scene_{idx}.png"
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

    render_chalkboard_shorts(SCENES, str(OUT_MP4), temp_dir="/tmp/day12_chalk_shorts_build")
    shutil.copy(OUT_MP4, CHALK_DIR / "chalkboard_shorts_video.mp4")

    total, caps = make_preview(OUT_MP4)

    print("\n✅ Day 12 쇼츠 완성")
    print(f"   - 영상: {OUT_MP4} ({total:.2f}초)")
    print(f"   - 아카이브: {CHALK_DIR / 'chalkboard_shorts_video.mp4'}")
    print(f"   - GIF: {GIF_OUT} ({GIF_OUT.stat().st_size / 1024 / 1024:.2f}MB)")
    for c in caps:
        print(f"   - 캡처: {c}")


if __name__ == "__main__":
    main()
