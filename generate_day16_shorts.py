#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 16 유튜브 쇼츠 생성기 (칠판 분필 드로잉 특강 스타일)
주제: 겨울 샤워·세안 습관이 피부를 망친다, 뜨거운 물·비누·각질 제거의 함정
키워드: 겨울철 샤워 습관, 뜨거운 물 피부 자극, 약산성 클렌저 고르는 법
"""

import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.chalkboard_video_engine import render_chalkboard_shorts, FFMPEG_PATH  # 기본 레이아웃: 잘.의.정.바 3단(jaljab)

DAY_DIR = BASE_DIR / "content" / "2026-11-23-01"
CHALK_DIR = DAY_DIR / "chalkboard"
PREVIEW_DIR = CHALK_DIR / "preview"
CHALK_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

ART_DIR = Path("/workspace/assets/chalkboard/day16")
DOWNLOADS = Path("/workspace/downloads")

OUT_MP4 = DOWNLOADS / "Day16_겨울샤워습관_피부장벽_칠판드로잉_쇼츠.mp4"
GIF_OUT = DOWNLOADS / "Day16_겨울샤워습관_미리보기.gif"

SCENES = [
    {
        "keyword": "42도 샤워의 함정",
        "caption": "42도 물이 피부 기름을 씻어냅니다",
        "chalk_img": str(ART_DIR / "scene1_hot_shower.png"),
        "main_text": "뜨거운 물은\n피부 기름을 녹여 씻어냅니다",
        "sub_text": "그 기름이 수분을 막는 방수막입니다",
        "voice": "겨울 목욕 후 개운함은 잠깐입니다. 사십이 도가 넘는 물은 피부 표면 기름을 녹여 씻어냅니다. 그 기름이 수분을 막는 방수막입니다.",
    },
    {
        "keyword": "씻을수록 당기는 이유",
        "caption": "씻은 직후보다 30분 뒤가 더 당깁니다",
        "chalk_img": str(ART_DIR / "scene2_towel_rub.png"),
        "main_text": "수건으로 박박 닦으면\n장벽이 더 얇아집니다",
        "sub_text": "물이 증발하며 각질층 수분까지 끌고 갑니다",
        "voice": "씻은 직후보다 삼십 분 뒤가 더 당깁니다. 물이 증발하며 각질층 수분까지 끌고 가기 때문입니다. 수건으로 박박 닦으면 손실이 더 큽니다.",
    },
    {
        "keyword": "비누 칠할 부위",
        "caption": "세정제는 겨드랑이와 사타구니에만",
        "chalk_img": str(ART_DIR / "scene3_soap_local.png"),
        "main_text": "겨울 비누는\n겨드랑이에만 칠하십시오",
        "sub_text": "등과 팔다리는 물로 헹구면 충분합니다",
        "voice": "정상 피부는 약산성인데 흔한 비누는 강한 알칼리성입니다. 겨울에는 세정제를 겨드랑이와 사타구니에만 쓰고, 등과 팔다리는 물로 헹구십시오.",
    },
    {
        "keyword": "때밀이 주 1회",
        "caption": "겨울 각질은 벗길 대상이 아닙니다",
        "chalk_img": str(ART_DIR / "scene4_scrub_mitt_back.png"),
        "main_text": "때밀이는 주 1회 이하\n필링은 2주에 한 번",
        "sub_text": "겨울 각질은 물을 잃은 장벽이 들뜬 것입니다",
        "voice": "겨울에 보이는 하얀 각질은 물을 잃은 장벽이 들뜬 것입니다. 때밀이는 주 일회 이하, 필링은 이 주에 한 번, 붉어진 날에는 하지 마십시오.",
    },
    {
        "keyword": "촉촉할 때 보습",
        "caption": "물기를 다 닦기 전에 바로 바릅니다",
        "chalk_img": str(ART_DIR / "scene5_damp_face_cream.png"),
        "main_text": "물기를 다 닦기 전에\n보습제를 바르십시오",
        "sub_text": "삼 분을 재지 않아도 괜찮습니다",
        "voice": "씻고 나오면 수건으로 문지르지 말고 물기를 가볍게 눌러 닦으십시오. 피부가 아직 촉촉할 때 보습제를 바로 바르면 됩니다.",
    },
]


def write_screenplay():
    total_chars = sum(len(s["voice"]) for s in SCENES)
    lines = [
        "# Day 16 유튜브 쇼츠 대본 - 겨울 샤워·세안 습관이 피부를 망친다",
        "",
        "- 주제: 겨울 샤워·세안 습관이 피부를 망친다, 뜨거운 물·비누·각질 제거의 함정",
        "- 키워드: 겨울철 샤워 습관 / 뜨거운 물 피부 자극 / 약산성 클렌저 고르는 법",
        "- 규격: 1080x1920 세로형 9:16, 칠판 분필 드로잉 특강 스타일, 5개 씬, 잘.의.정.바 3단 레이아웃",
        "- 음성: Edge-TTS ko-KR-InJoonNeural, 속도 +5%",
        f"- 대본 분량: {total_chars}자",
        "",
        "| 씬 | 노란 키워드 | 화면 문구 | 자막 | 내레이션 |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for i, s in enumerate(SCENES, 1):
        main = s["main_text"].replace("\n", " / ")
        lines.append(f"| {i} | {s['keyword']} | {main} | {s['caption']} | {s['voice']} |")
    lines += [
        "",
        "## 연출 메모",
        "- 1씬은 김이 가득한 욕실과 뜨거운 물, 게이지의 붉은 눈금을 한 화면에 두어 '42도'의 출발점을 보여준다.",
        "- 2씬은 샤워 직후 수건으로 팔을 박박 미는 장면과 벌겋게 된 피부를 오렌지 분필로 강조했다.",
        "- 3씬은 한쪽 팔을 들어 겨드랑이에만 비누를 칠하는 장면. 나머지 몸에는 거품 없이 물만 흐르게 그렸다.",
        "- 4씬은 때밀이 타월로 등을 미는 손과 벌겋게 부은 등, 떨어지는 각질을 대비시켰다.",
        "- 5씬은 물기가 남은 얼굴에 크림을 바르는 장면으로 '촉촉할 때 보습'을 시각화했다. 지피티 겅태 11-22 검수 의견(3분 강박 대신 물기 남았을 때)을 반영했다.",
        "- 숫자는 대본에서 한글 발음으로 적었다(사십이 도, 삼십 분, 이 주). TTS 오독을 막기 위한 표기다.",
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
        cap = DOWNLOADS / f"Day16_scene_{idx}.png"
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

    render_chalkboard_shorts(SCENES, str(OUT_MP4), temp_dir="/tmp/day16_chalk_shorts_build")
    shutil.copy(OUT_MP4, CHALK_DIR / "chalkboard_shorts_video.mp4")

    total, caps = make_preview(OUT_MP4)

    print("\n✅ Day 16 쇼츠 완성")
    print(f"   - 영상: {OUT_MP4} ({total:.2f}초)")
    print(f"   - 아카이브: {CHALK_DIR / 'chalkboard_shorts_video.mp4'}")
    print(f"   - GIF: {GIF_OUT} ({GIF_OUT.stat().st_size / 1024 / 1024:.2f}MB)")
    for c in caps:
        print(f"   - 캡처: {c}")


if __name__ == "__main__":
    main()
