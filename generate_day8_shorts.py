#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 8 유튜브 쇼츠 생성기 (칠판 분필 드로잉 특강 스타일)
주제: 면역력의 핵심 - 겨울철 비타민D 결핍 극복과 계절성 우울증 예방
키워드: 겨울철 비타민D, 비타민D 영양제 주사, 계절성 우울증 극복
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.chalkboard_video_engine import render_chalkboard_shorts, FFMPEG_PATH

DAY_DIR = BASE_DIR / "content" / "2026-11-16-01"
CHALK_DIR = DAY_DIR / "chalkboard"
CHALK_DIR.mkdir(parents=True, exist_ok=True)

ART_DIR = Path("/workspace/assets/chalkboard/day8")
DOWNLOADS = Path("/workspace/downloads")

OUT_MP4 = DOWNLOADS / "Day8_겨울철_비타민D_계절성우울증_칠판드로잉_쇼츠.mp4"
GIF_OUT = DOWNLOADS / "Day8_칠판쇼츠_움직이는미리보기.gif"

SCENES = [
    {
        "badge": "겨울철 면역 경고",
        "keyword": "햇빛 부족",
        "chalk_img": str(ART_DIR / "scene1_winter_low_sun_fatigue.png"),
        "main_text": "겨울만 되면 기운이 없고\n감기까지 자주 걸린다면",
        "sub_text": "햇빛이 줄면 면역의 연료도 같이 줄어듭니다",
        "voice": "겨울만 되면 이유 없이 기운이 없고 감기에 자주 걸리시나요? 그건 추위 때문만은 아닙니다.",
    },
    {
        "badge": "응급실 현장 진실",
        "keyword": "자외선 비 흡수",
        "chalk_img": str(ART_DIR / "scene2_uvb_blocked_atmosphere.png"),
        "main_text": "겨울 자외선 비는\n대기에서 거의 흡수됩니다",
        "sub_text": "피부가 비타민디를 만들 시간이 부족해집니다",
        "voice": "피부는 자외선 비를 받아 비타민 디를 만드는데, 겨울에는 그 자외선 비가 대기에서 거의 흡수돼 버립니다.",
    },
    {
        "badge": "의사의 병태 설명",
        "keyword": "세로토닌 불균형",
        "chalk_img": str(ART_DIR / "scene3_serotonin_melatonin_imbalance.png"),
        "main_text": "햇빛이 줄면 세로토닌은 줄고\n멜라토닌 리듬은 흐트러집니다",
        "sub_text": "계절성 우울증이 시작되는 지점",
        "voice": "햇빛이 줄면 기분을 올려 주는 세로토닌이 줄고, 수면을 조절하는 멜라토닌 리듬이 흐트러지면서 계절성 우울증이 찾아옵니다.",
    },
    {
        "badge": "아침 햇빛 루틴",
        "keyword": "아침 삼십 분",
        "chalk_img": str(ART_DIR / "scene4_morning_sunlight_routine.png"),
        "main_text": "기상 후 삼십 분 안에\n창문 말고 밖으로 나가세요",
        "sub_text": "혈중 비타민디 농도는 이십에서 삼십을 목표로",
        "voice": "가능하면 아침에 일어나 삼십 분 안에 창문이 아니라 밖으로 나가 햇빛을 쬐세요. 비타민 디 혈중 농도는 이십에서 삼십 사이를 목표로 합니다.",
    },
    {
        "badge": "과잉 복용 주의",
        "keyword": "검사 먼저",
        "chalk_img": str(ART_DIR / "scene5_injection_vs_blood_test_caution.png"),
        "main_text": "고용량 주사부터 찾지 말고\n혈중 농도부터 확인하세요",
        "sub_text": "과잉은 오히려 해롭습니다, 지금 꼭 공유해 주세요",
        "voice": "고용량 비타민 디 주사부터 찾지 마시고, 혈중 농도를 먼저 확인하세요. 지나친 과잉은 오히려 해롭습니다. 지금 꼭 공유해 주세요.",
    },
]


def write_screenplay():
    total_chars = sum(len(s["voice"]) for s in SCENES)
    lines = [
        "# Day 8 유튜브 쇼츠 대본 - 겨울철 비타민D와 계절성 우울증",
        "",
        "- 주제: 면역력의 핵심, 겨울철 비타민D 결핍 극복과 계절성 우울증 예방",
        "- 키워드: 겨울철 비타민D / 비타민D 영양제 주사 / 계절성 우울증 극복",
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
        "- 각 씬의 하단 자막 박스는 화면 문구(노랑)와 보조 설명(흰색) 두 단으로 나뉜다.",
        "- 숫자는 대본에서 한글 발음으로 적었다(삼십 분, 이십에서 삼십, 사십 도, 삼 분).",
        "- 그림에는 글자와 일본어 가나를 넣지 않았다. 한글 자막은 엔진이 그린다.",
        "- 마지막 씬은 저장과 공유를 유도하는 마무리 문장으로 끝난다.",
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
    """전체 흐름이 보이는 움직이는 GIF 미리보기 + 씬 캡처 3장"""
    dur_cmd = [FFMPEG_PATH, "-i", str(video)]
    p = subprocess.run(dur_cmd, capture_output=True, text=True)
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
        cap = DOWNLOADS / f"Day8_씬{idx}_미리보기.png"
        subprocess.run([
            FFMPEG_PATH, "-y", "-ss", f"{total * frac:.2f}", "-i", str(video),
            "-frames:v", "1", str(cap)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        caps.append(cap)
    return total, caps


def main():
    write_screenplay()
    archive_art()

    render_chalkboard_shorts(SCENES, str(OUT_MP4), temp_dir="/tmp/day8_chalk_shorts_build")
    shutil.copy(OUT_MP4, CHALK_DIR / "chalkboard_shorts_video.mp4")

    total, caps = make_preview(OUT_MP4)

    print(f"\n✅ Day 8 쇼츠 완성")
    print(f"   - 영상: {OUT_MP4} ({total:.2f}초)")
    print(f"   - 아카이브: {CHALK_DIR / 'chalkboard_shorts_video.mp4'}")
    print(f"   - GIF: {GIF_OUT} ({GIF_OUT.stat().st_size / 1024 / 1024:.2f}MB)")
    for c in caps:
        print(f"   - 캡처: {c}")


if __name__ == "__main__":
    main()
