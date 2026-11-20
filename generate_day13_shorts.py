#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 13 유튜브 쇼츠 생성기 (칠판 분필 드로잉 특강 스타일)
주제: 겨울철 안전한 운동 가이드 (실내 맨몸 홈트 vs 야외 걷기 안전 수칙)
키워드: 겨울철 실내 운동, 한파 야외 걷기, 심혈관 운동 주의점
"""

import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.chalkboard_video_engine import render_chalkboard_shorts, FFMPEG_PATH

DAY_DIR = BASE_DIR / "content" / "2026-11-20-01"
CHALK_DIR = DAY_DIR / "chalkboard"
PREVIEW_DIR = CHALK_DIR / "preview"
CHALK_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

ART_DIR = Path("/workspace/assets/chalkboard/day13")
DOWNLOADS = Path("/workspace/downloads")

OUT_MP4 = DOWNLOADS / "Day13_겨울운동_오후운동_칠판드로잉_쇼츠.mp4"
GIF_OUT = DOWNLOADS / "Day13_겨울운동_미리보기.gif"

SCENES = [
    {
        "badge": "겨울 아침 경고",
        "keyword": "아침 혈압",
        "chalk_img": str(ART_DIR / "scene1_dawn_walk_chest.png"),
        "main_text": "새벽 운동은\n가장 힘든 시간입니다",
        "sub_text": "혈압은 가장 높고 체온은 가장 낮습니다",
        "voice": "겨울 새벽 다섯 시는 하루 중 혈압이 가장 높고 체온이 가장 낮은 시간입니다. 운동을 시작하기에 가장 불리한 조합입니다.",
    },
    {
        "badge": "심장이 받는 부담",
        "keyword": "혈관 수축",
        "chalk_img": str(ART_DIR / "scene2_cold_heart_load.png"),
        "main_text": "혈관이 좁아지면\n심장은 더 세게 밉니다",
        "sub_text": "같은 속도에 산소는 더 많이 듭니다",
        "voice": "추위에 혈관이 좁아지면 심장은 같은 양을 내보내기 위해 더 세게 밀어야 합니다. 같은 속도로 걸어도 심장이 쓰는 산소는 십 퍼센트 더 늘어납니다.",
    },
    {
        "badge": "운동 적기",
        "keyword": "오후 두 시에서 네 시",
        "chalk_img": str(ART_DIR / "scene3_afternoon_sun_walk.png"),
        "main_text": "체온이 오르는\n오후 두 시에서 네 시",
        "sub_text": "해가 지기 전에 끝내십시오",
        "voice": "체온은 늦은 오후에 정점을 찍습니다. 그래서 운동은 오후 두 시에서 네 시 사이가 좋고, 해가 지기 전에 끝내십시오.",
    },
    {
        "badge": "실내 이십 분",
        "keyword": "의자 홈트",
        "chalk_img": str(ART_DIR / "scene4_indoor_chair_workout.png"),
        "main_text": "의자 하나로\n이십 분이면 충분합니다",
        "sub_text": "준비 오 분, 본운동 십이 분, 정리 삼 분",
        "voice": "집에서는 의자 하나로 이십 분이면 충분합니다. 준비운동 오 분, 본운동 십이 분, 정리운동 삼 분이면 됩니다.",
    },
    {
        "badge": "응급 호출 신호",
        "keyword": "일일구",
        "chalk_img": str(ART_DIR / "scene5_chest_pain_call_119.png"),
        "main_text": "가슴 통증이 오 분\n지나면 일일구",
        "sub_text": "직접 운전하지 마시고 꼭 공유해 주세요",
        "voice": "운동 중 가슴이 조이고 오 분이 지나도 낫지 않으면 일일구를 부르십시오. 직접 운전하지 마시고 꼭 공유해 주세요.",
    },
]


def write_screenplay():
    total_chars = sum(len(s["voice"]) for s in SCENES)
    lines = [
        "# Day 13 유튜브 쇼츠 대본 - 겨울철 안전한 운동 가이드",
        "",
        "- 주제: 겨울철 안전한 운동 가이드: 실내 맨몸 홈트 vs 야외 걷기 안전 수칙",
        "- 키워드: 겨울철 실내 운동 / 한파 야외 걷기 / 심혈관 운동 주의점",
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
        "- 1씬은 새벽 아파트 단지의 눈 덮인 보도를 걷는 장면으로, 가슴에 손을 얹은 자세와 입김으로 시간대의 위험을 한 컷에 전달한다.",
        "- 2씬은 심장 단면과 관상동맥 도해에 찬 바람 화살표와 빨간 분필 표시를 넣어 혈관 수축과 부하 증가를 보여준다.",
        "- 3씬은 겨울 오후의 해와 걸어가는 사람으로 시간대 권고를 시각화한다. 해가 지기 전이라는 조건을 자막으로 닫는다.",
        "- 4씬은 거실에서 의자에 앉았다 일어서는 동작과 벽 밀기 삽화로 실내 루틴을 전달한다. 시계에는 숫자를 넣지 않았다.",
        "- 5씬은 길에 주저앉아 가슴을 누르는 사람, 응급 호출 화면, 구급차로 마무리하고 공유로 닫는다.",
        "- 숫자는 대본에서 한글 발음으로 적었다(다섯 시, 십 퍼센트, 두 시, 네 시, 오 분, 십이 분, 삼 분, 일일구). TTS 오독을 막기 위한 표기다.",
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
        cap = DOWNLOADS / f"Day13_scene_{idx}.png"
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

    render_chalkboard_shorts(SCENES, str(OUT_MP4), temp_dir="/tmp/day13_chalk_shorts_build")
    shutil.copy(OUT_MP4, CHALK_DIR / "chalkboard_shorts_video.mp4")

    total, caps = make_preview(OUT_MP4)

    print("\n✅ Day 13 쇼츠 완성")
    print(f"   - 영상: {OUT_MP4} ({total:.2f}초)")
    print(f"   - 아카이브: {CHALK_DIR / 'chalkboard_shorts_video.mp4'}")
    print(f"   - GIF: {GIF_OUT} ({GIF_OUT.stat().st_size / 1024 / 1024:.2f}MB)")
    for c in caps:
        print(f"   - 캡처: {c}")


if __name__ == "__main__":
    main()
