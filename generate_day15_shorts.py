#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 15 유튜브 쇼츠 생성기 (칠판 분필 드로잉 특강 스타일)
주제: 겨울철 피부 건조와 보습의 정석, 세라마이드 보습제 3분 법칙
키워드: 겨울철 피부 건조 원인, 보습제 바르는 법, 세라마이드 크림 효과
"""

import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.chalkboard_video_engine import render_chalkboard_shorts, FFMPEG_PATH  # 기본 레이아웃: 잘.의.정.바 3단(jaljab)

DAY_DIR = BASE_DIR / "content" / "2026-11-22-01"
CHALK_DIR = DAY_DIR / "chalkboard"
PREVIEW_DIR = CHALK_DIR / "preview"
CHALK_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

ART_DIR = Path("/workspace/assets/chalkboard/day15")
DOWNLOADS = Path("/workspace/downloads")

OUT_MP4 = DOWNLOADS / "Day15_겨울피부건조_보습3분법칙_칠판드로잉_쇼츠.mp4"
GIF_OUT = DOWNLOADS / "Day15_겨울피부건조_미리보기.gif"

SCENES = [
    {
        "badge": "겨울 피부의 시작",
        "keyword": "겨울철 실내 건조",
        "caption": "난방 켜면 습도는 20퍼센트까지",
        "chalk_img": str(ART_DIR / "scene1_dry_winter_room.png"),
        "main_text": "난방을 켜면\n습도가 이십 퍼센트까지 떨어집니다",
        "sub_text": "피부 수분이 빠져나가는 속도가 빨라집니다",
        "voice": "겨울에 난방을 켜면 실내 습도는 이십 퍼센트까지 떨어집니다. 공기가 건조하면 피부의 수분이 빠져나가는 속도가 빨라집니다.",
    },
    {
        "badge": "샤워 뒤 삼 분",
        "keyword": "샤워 후 삼분 법칙",
        "caption": "닦지 말고, 물기 남은 채로 3분",
        "chalk_img": str(ART_DIR / "scene2_three_minute_cream.png"),
        "main_text": "수건으로 닦으면\n각질층 물기를 빼앗습니다",
        "sub_text": "물기를 살짝 남긴 채로 삼 분 안에",
        "voice": "샤워 뒤 수건으로 박박 닦으면 각질층의 물기를 다 빼앗습니다. 물기를 살짝 남긴 채로 삼 분 안에 보습제를 바르십시오.",
    },
    {
        "badge": "장벽의 절반",
        "keyword": "세라마이드 장벽",
        "caption": "각질층 지질의 절반이 세라마이드",
        "chalk_img": str(ART_DIR / "scene3_ceramide_mortar.png"),
        "main_text": "각질세포 사이를 채우는\n지질의 절반이 세라마이드",
        "sub_text": "이 기름이 빠지면 물이 새어 나갑니다",
        "voice": "각질세포 사이를 채우는 지질의 절반이 세라마이드입니다. 이 기름이 빠지면 벽에 금이 간 것처럼 수분이 새어 나갑니다.",
    },
    {
        "badge": "제형 고르기",
        "keyword": "크림과 연고 고르기",
        "caption": "겨울 몸에는 로션보다 크림, 연고",
        "chalk_img": str(ART_DIR / "scene4_lotion_cream_ointment.png"),
        "main_text": "겨울 몸에는\n로션보다 크림과 연고",
        "sub_text": "전신에 이십 그램, 아끼지 말고",
        "voice": "겨울철 몸에는 물 비중이 높은 로션보다 크림이나 연고가 맞습니다. 성인은 전신에 이십 그램, 아끼지 말고 바르십시오.",
    },
    {
        "badge": "진료가 필요한 때",
        "keyword": "진료가 필요한 신호",
        "caption": "진물과 열감, 번지면 크림이 아니라 진료",
        "chalk_img": str(ART_DIR / "scene5_infection_see_doctor.png"),
        "main_text": "진물이 나고\n붉은 부위가 번지면 진료",
        "sub_text": "긁은 상처에 균이 들어간 상태일 수 있습니다",
        "voice": "진물이 나거나 노란 딱지가 앉고, 붉은 부위가 번지며 열이 나면 크림으로 해결할 단계가 아닙니다. 지체 없이 진료를 받으십시오.",
    },
]


def write_screenplay():
    total_chars = sum(len(s["voice"]) for s in SCENES)
    lines = [
        "# Day 15 유튜브 쇼츠 대본 - 겨울철 피부 건조와 보습의 정석",
        "",
        "- 주제: 겨울철 피부 건조와 보습의 정석, 세라마이드 보습제 3분 법칙",
        "- 키워드: 겨울철 피부 건조 원인 / 보습제 바르는 법 / 세라마이드 크림 효과",
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
        "- 1씬은 난방기와 낮게 떨어진 습도계, 창밖 눈과 갈라진 정강이를 한 화면에 두어 '겨울 건조'의 출발점을 보여준다.",
        "- 2씬은 샤워 직후 물방울이 남은 몸, 수건으로 누르는 동작, 튜브에서 짜낸 크림을 물기 있는 팔에 바르는 장면, 짧은 시간을 가리키는 시계로 삼 분 법칙을 시각화했다.",
        "- 3씬은 각질층을 벽돌벽 단면으로 그려 세라마이드 모르타르와 새어 나가는 물방울을 대비시켰다.",
        "- 4씬은 로션·크림·연고 용기를 나란히 두고 손등에 크림을 바르는 장면으로 제형 차이를 보여준다.",
        "- 5씬은 붉게 부은 정강이와 진물, 보호자와 의료진, 병원 표시로 진료가 필요한 신호를 전달한다.",
        "- 숫자는 대본에서 한글 발음으로 적었다(이십 퍼센트, 삼 분, 이십 그램). TTS 오독을 막기 위한 표기다.",
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
        cap = DOWNLOADS / f"Day15_scene_{idx}.png"
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

    render_chalkboard_shorts(SCENES, str(OUT_MP4), temp_dir="/tmp/day15_chalk_shorts_build")
    shutil.copy(OUT_MP4, CHALK_DIR / "chalkboard_shorts_video.mp4")

    total, caps = make_preview(OUT_MP4)

    print("\n✅ Day 15 쇼츠 완성")
    print(f"   - 영상: {OUT_MP4} ({total:.2f}초)")
    print(f"   - 아카이브: {CHALK_DIR / 'chalkboard_shorts_video.mp4'}")
    print(f"   - GIF: {GIF_OUT} ({GIF_OUT.stat().st_size / 1024 / 1024:.2f}MB)")
    for c in caps:
        print(f"   - 캡처: {c}")


if __name__ == "__main__":
    main()
