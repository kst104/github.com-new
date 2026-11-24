#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 17 유튜브 쇼츠 생성기 (칠판 분필 드로잉 특강 스타일)
주제: 밤마다 긁는 겨울 가려움증, 건조성 피부염 vs 아토피, 스테로이드 연고 오해
키워드: 겨울철 가려움증 원인, 건조성 피부염 증상, 아토피 연고 스테로이드
"""

import json
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.chalkboard_video_engine import render_chalkboard_shorts, FFMPEG_PATH  # 기본 레이아웃: 잘.의.정.바 3단(jaljab)

DAY_DIR = BASE_DIR / "content" / "2026-11-24-01"
CHALK_DIR = DAY_DIR / "chalkboard"
PREVIEW_DIR = CHALK_DIR / "preview"
CHALK_DIR.mkdir(parents=True, exist_ok=True)
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

ART_DIR = Path("/workspace/assets/chalkboard/day17")
DOWNLOADS = Path("/workspace/downloads")
TEMP_DIR = "/tmp/day17_chalk_shorts_build"

OUT_MP4 = DOWNLOADS / "Day17_겨울밤가려움_건조피부염아토피_칠판드로잉_쇼츠.mp4"
GIF_OUT = DOWNLOADS / "Day17_겨울밤가려움_미리보기.gif"

SCENES = [
    {
        "keyword": "밤 가려움",
        "caption": "밤에는 가려움이 더 심해질 수 있습니다",
        "chalk_img": str(ART_DIR / "scene1_night_scratch.png"),
        "main_text": "밤마다 다리를 긁는 이유는\n크림만이 아닐 수 있습니다",
        "sub_text": "피부 온도 상승과 코르티솔 저하가 요인으로 꼽힙니다",
        "chapter": "밤에 더 가려운 이유",
        "voice": "밤마다 다리를 긁는다면, 크림을 안 발라서만은 아닐 수 있습니다. 밤에는 피부 온도가 오르고 코르티솔이 낮아지는 것이 가려움을 심하게 하는 요인으로 꼽힙니다.",
    },
    {
        "keyword": "건조성 피부염",
        "caption": "정강이가 하얗게 갈라지면 건조성 피부염을 의심합니다",
        "chalk_img": str(ART_DIR / "scene2_shin_cracks.png"),
        "main_text": "정강이 앞쪽이 하얗게 갈라지면\n건조성 피부염을 의심합니다",
        "sub_text": "난방과 잦은 목욕이 악화 요인으로 꼽힙니다",
        "chapter": "건조성 피부염 증상",
        "voice": "정강이 앞쪽이 하얗게 갈라지면 건조성 피부염을 의심해 볼 수 있습니다. 난방으로 마른 실내와 잦은 목욕이 악화 요인으로 꼽힙니다.",
    },
    {
        "keyword": "아토피 피부염",
        "caption": "팔꿈치와 무릎 안쪽이 반복되면 아토피를 의심합니다",
        "chalk_img": str(ART_DIR / "scene3_atopic_elbow.png"),
        "main_text": "팔꿈치와 무릎 안쪽이 반복되면\n아토피 피부염을 의심합니다",
        "sub_text": "가려움이 먼저 오는 경우가 많습니다",
        "chapter": "아토피 피부염 감별",
        "voice": "팔꿈치와 무릎 안쪽이 반복해서 붉어지면 아토피 피부염을 의심해 볼 수 있습니다. 가려움이 먼저 오고 발진이 따라오는 경우가 많습니다.",
    },
    {
        "keyword": "연고 사용법",
        "caption": "처방받은 연고는 안내받은 부위에, 안내받은 양과 기간대로",
        "chalk_img": str(ART_DIR / "scene4_fingertip_ointment.png"),
        "main_text": "처방받은 연고는\n안내받은 대로 바릅니다",
        "sub_text": "바르는 양은 손가락 한 마디가 기준입니다",
        "chapter": "스테로이드 연고 사용법",
        "voice": "바르는 스테로이드는 먹는 약과 다릅니다. 처방받은 연고는 안내받은 부위에, 안내받은 양과 기간대로 바르는 것이 원칙입니다.",
    },
    {
        "keyword": "취침 전 보습",
        "caption": "잠들기 전 건조한 부위를 보습하고, 땀이 날 정도로 덥게 덮지 않기",
        "chalk_img": str(ART_DIR / "scene5_bedtime_moisturize.png"),
        "main_text": "잠들기 전\n건조한 부위를 보습합니다",
        "sub_text": "땀이 날 정도로 덥게 덮지 않습니다",
        "chapter": "취침 전 보습과 환경",
        "voice": "잠들기 전에 건조한 부위를 보습하고, 땀이 날 정도로 덥게 덮지 마십시오.",
    },
]


def write_screenplay():
    total_chars = sum(len(s["voice"]) for s in SCENES)
    lines = [
        "# Day 17 유튜브 쇼츠 대본 - 겨울밤 가려움증, 건조성 피부염과 아토피",
        "",
        "- 주제: 밤마다 긁는 겨울 가려움증, 건조성 피부염 vs 아토피, 스테로이드 연고 오해",
        "- 키워드: 겨울철 가려움증 원인 / 건조성 피부염 증상 / 아토피 연고 스테로이드",
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
        "- 1씬은 달빛이 드는 침실과 이불 밖으로 나온 다리, 정강이를 긁는 손을 한 화면에 두어 '밤'의 조건을 먼저 보여준다.",
        "- 2씬은 정강이의 그물 모양 균열과 들뜬 각질을 클로즈업했다. 손가락이 갈라진 자리를 가리키게 그렸다.",
        "- 3씬은 아이의 팔꿈치 안쪽을 오렌지 분필로 강조해 아토피의 굴측 분포를 보여준다.",
        "- 4씬은 연고 튜브와 손가락 한 마디 양을 대비시켜 '손가락 단위'를 시각화했다. 글자와 눈금은 넣지 않았다.",
        "- 5씬은 침대 끝에 앉아 정강이에 크림을 바르는 장면과 가습기 안개, 따뜻한 조명을 오렌지 분필로 처리했다.",
        "- 숫자는 대본에서 한글 발음으로 적었다. TTS 오독을 막기 위한 표기다.",
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


def probe_duration(path: Path) -> float:
    p = subprocess.run([FFMPEG_PATH, "-i", str(path)], capture_output=True, text=True)
    for line in p.stderr.split("\n"):
        if "Duration:" in line:
            h, m, sec = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return float(h) * 3600 + float(m) * 60 + float(sec)
    return 0.0


def make_preview(video: Path):
    total = probe_duration(video)

    subprocess.run([
        FFMPEG_PATH, "-y", "-i", str(video),
        "-vf", "fps=1.6,scale=420:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=192[p];[s1][p]paletteuse=dither=bayer",
        "-loop", "0", str(GIF_OUT)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    shutil.copy(GIF_OUT, PREVIEW_DIR / "moving_preview.gif")

    caps = []
    for idx, frac in enumerate([0.10, 0.42, 0.74], 1):
        cap = DOWNLOADS / f"Day17_scene_{idx}.png"
        subprocess.run([
            FFMPEG_PATH, "-y", "-ss", f"{total * frac:.2f}", "-i", str(video),
            "-frames:v", "1", str(cap)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.copy(cap, PREVIEW_DIR / f"scene{idx}_preview.png")
        caps.append(cap)
    return total, caps


def write_scene_times():
    """렌더된 씬 파일에서 실제 재생 시간을 읽어 시작 시각(MM:SS) 목차를 만든다."""
    times = []
    acc = 0.0
    for i, s in enumerate(SCENES, 1):
        dur = probe_duration(Path(TEMP_DIR) / f"scene_{i}.mp4")
        mm, ss = divmod(int(round(acc)), 60)
        times.append({"scene": i, "start": f"{mm:02d}:{ss:02d}", "start_sec": round(acc, 2),
                      "duration": round(dur, 2), "chapter": s["chapter"], "caption": s["caption"]})
        acc += dur
    data = {"scenes": times, "total_sec": round(acc, 2)}
    (CHALK_DIR / "scene_times.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n씬별 시작 시각")
    for t in times:
        print(f"  {t['start']}  {t['chapter']}  ({t['duration']}초)")
    return data


def main():
    write_screenplay()
    archive_art()

    render_chalkboard_shorts(SCENES, str(OUT_MP4), temp_dir=TEMP_DIR)
    shutil.copy(OUT_MP4, CHALK_DIR / "chalkboard_shorts_video.mp4")

    total, caps = make_preview(OUT_MP4)
    times = write_scene_times()

    print("\n✅ Day 17 쇼츠 완성")
    print(f"   - 영상: {OUT_MP4} ({total:.2f}초)")
    print(f"   - 아카이브: {CHALK_DIR / 'chalkboard_shorts_video.mp4'}")
    print(f"   - GIF: {GIF_OUT} ({GIF_OUT.stat().st_size / 1024 / 1024:.2f}MB)")
    for c in caps:
        print(f"   - 캡처: {c}")
    print(f"   - 씬 타임스탬프: {CHALK_DIR / 'scene_times.json'} (총 {times['total_sec']}초)")


if __name__ == "__main__":
    main()
