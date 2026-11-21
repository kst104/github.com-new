#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 14 유튜브 쇼츠 생성기 (칠판 분필 드로잉 특강 스타일)
주제: 체온을 1도 올리는 겨울철 온열 영양 식단과 면역 강화 푸드
키워드: 겨울철 면역력 음식, 온열 식품 식단, 생강차 대추차 효능
"""

import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.chalkboard_video_engine import render_chalkboard_shorts, FFMPEG_PATH  # 기본 레이아웃: 잘.의.정.바 3단(jaljab)

DAY_DIR = BASE_DIR / "content" / "2026-11-21-01"
CHALK_DIR = DAY_DIR / "chalkboard"
PREVIEW_DIR = CHALK_DIR / "preview"
CHALK_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

ART_DIR = Path("/workspace/assets/chalkboard/day14")
DOWNLOADS = Path("/workspace/downloads")

OUT_MP4 = DOWNLOADS / "Day14_겨울면역음식_온열식단_칠판드로잉_쇼츠.mp4"
GIF_OUT = DOWNLOADS / "Day14_겨울면역음식_미리보기.gif"

SCENES = [
    {
        "badge": "겨울 식탁의 오해",
        "keyword": "국물과 체온",
        "caption": "뜨거운 국물, 체온은 그대로",
        "chalk_img": str(ART_DIR / "scene1_winter_table_pot.png"),
        "main_text": "뜨거운 국물은\n체온을 올리지 않습니다",
        "sub_text": "열은 음식이 아니라 몸이 만듭니다",
        "voice": "뜨거운 국물 한 그릇은 몸을 편하게 하지만 체온을 일 도 올려 주지는 않습니다. 열은 음식이 아니라 몸이 만듭니다.",
    },
    {
        "badge": "열을 만드는 영양소",
        "keyword": "단백질 식사",
        "caption": "소화할 때 가장 뜨거운 영양소는 단백질",
        "chalk_img": str(ART_DIR / "scene2_digestion_heat.png"),
        "main_text": "단백질은 소화할 때\n열을 가장 많이 씁니다",
        "sub_text": "먹은 열량의 이십에서 삼십 퍼센트",
        "voice": "단백질은 소화할 때 먹은 열량의 이십에서 삼십 퍼센트를 열로 씁니다. 탄수화물의 네 배가 넘습니다.",
    },
    {
        "badge": "근거 있는 면역 영양",
        "keyword": "비타민 디",
        "caption": "겨울 면역, 가장 흔한 결핍은 비타민 디",
        "chalk_img": str(ART_DIR / "scene3_winter_sun_vitamin_d.png"),
        "main_text": "겨울에 가장 흔한\n결핍은 비타민 디",
        "sub_text": "부족한 사람에게 보충하면 감기가 줄어듭니다",
        "voice": "겨울에 가장 흔히 부족해지는 것은 비타민 디입니다. 부족한 사람에게 보충하면 호흡기 감염이 줄었다는 분석이 있습니다.",
    },
    {
        "badge": "생강차 대추차",
        "keyword": "설탕과 온도",
        "caption": "차보다 먼저 볼 것은 설탕과 온도",
        "chalk_img": str(ART_DIR / "scene4_ginger_jujube_tea.png"),
        "main_text": "대추차 한 잔에\n설탕 스푼 두세 개",
        "sub_text": "육십 도가 넘으면 식도에 좋지 않습니다",
        "voice": "생강차와 대추차는 따뜻한 수분을 채우는 데 좋습니다. 다만 시판 대추차 한 잔에는 설탕이 스푼 두세 개 들어 있습니다.",
    },
    {
        "badge": "겨울 영양 사고",
        "keyword": "저혈당과 저체온",
        "caption": "밥 거르고 인슐린, 겨울에 특히 위험",
        "chalk_img": str(ART_DIR / "scene5_elderly_cold_hypoglycemia.png"),
        "main_text": "밥을 거르고\n인슐린을 맞으면 위험합니다",
        "sub_text": "손이 차갑고 말이 느려지면 일일구",
        "voice": "겨울에는 식사를 거르기 쉽습니다. 밥을 거르고 인슐린을 맞으면 저혈당이 옵니다. 손이 차갑고 말이 느려지면 일일구를 부르십시오.",
    },
]


def write_screenplay():
    total_chars = sum(len(s["voice"]) for s in SCENES)
    lines = [
        "# Day 14 유튜브 쇼츠 대본 - 겨울철 온열 영양 식단과 면역 강화 푸드",
        "",
        "- 주제: 체온을 1도 올리는 겨울철 온열 영양 식단과 면역 강화 푸드",
        "- 키워드: 겨울철 면역력 음식 / 온열 식품 식단 / 생강차 대추차 효능",
        "- 규격: 1080x1920 세로형 9:16, 칠판 분필 드로잉 특강 스타일, 5개 씬, 잘.의.정.바 3단 레이아웃",
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
        "- 1씬은 겨울 식탁의 뚝배기와 뿌리채소(생강·대추·마늘·무·우엉)를 한 화면에 놓아 '온열 식품'의 실제 모습을 보여주고, 김이 오르는 국물과 체온이 별개라는 점을 자막으로 닫는다.",
        "- 2씬은 인체 단면과 위·장관, 옆에 크기가 다른 세 개의 불꽃으로 영양소별 식사성 발열 차이를 시각화했다. 불꽃에 글자나 숫자는 넣지 않았다.",
        "- 3씬은 겨울 창가의 낮은 해와 두꺼운 옷, 피부에 닿는 빛줄기, 그리고 노란 분필의 분자 도해로 비타민 디 합성을 표현했다.",
        "- 4씬은 유리 찻주전자와 찻잔(생강·대추), 온도계, 그리고 설탕과 꿀에 빨간 금지 표시를 넣어 당류와 온도 경고를 한 컷에 담았다.",
        "- 5씬은 난방이 약한 방에서 담요를 쓴 노인과 체온계를 든 보호자, 식지 않은 밥그릇, 혈당계로 저혈당·저체온의 두 갈래 위험을 보여준다.",
        "- 숫자는 대본에서 한글 발음으로 적었다(일 도, 이십, 삼십, 네 배, 육십 도, 두세 개, 일일구). TTS 오독을 막기 위한 표기다.",
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
        cap = DOWNLOADS / f"Day14_scene_{idx}.png"
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

    render_chalkboard_shorts(SCENES, str(OUT_MP4), temp_dir="/tmp/day14_chalk_shorts_build")
    shutil.copy(OUT_MP4, CHALK_DIR / "chalkboard_shorts_video.mp4")

    total, caps = make_preview(OUT_MP4)

    print("\n✅ Day 14 쇼츠 완성")
    print(f"   - 영상: {OUT_MP4} ({total:.2f}초)")
    print(f"   - 아카이브: {CHALK_DIR / 'chalkboard_shorts_video.mp4'}")
    print(f"   - GIF: {GIF_OUT} ({GIF_OUT.stat().st_size / 1024 / 1024:.2f}MB)")
    for c in caps:
        print(f"   - 캡처: {c}")


if __name__ == "__main__":
    main()
