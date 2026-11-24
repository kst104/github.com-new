#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 18 유튜브 쇼츠 (종이인형 레이아웃)
주제: 겨울 고열·기침, 감기인가 독감인가. RSV·마이코플라스마까지 아이와 어르신 감별법
연출(승태 님 2026-11-25 확정): 환자 질문 → 닥터 온 클로즈업 설명 → 환자 2~3명 엔딩 대화 → Day 19 예고
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from engine.paperdoll_video_engine import render_paperdoll_shorts, probe_duration, FFMPEG_PATH  # noqa: E402

DAY_DIR = BASE_DIR / "content" / "2026-11-25-01"
VID_DIR = DAY_DIR / "video"
PREVIEW = VID_DIR / "preview"
TEMP = "/tmp/day18_paperdoll_build"
DOWNLOADS = Path("/workspace/downloads")
for d in (VID_DIR, PREVIEW):
    d.mkdir(parents=True, exist_ok=True)

OUT_MP4 = DOWNLOADS / "Day18_겨울고열기침_감기독감RSV마이코플라스마_쇼츠.mp4"
GIF_OUT = DOWNLOADS / "Day18_겨울고열기침_미리보기.gif"
TOPIC_KEYWORD = "감기·독감·RSV"

DOCTOR_CU = {"name": "doctor", "height": 1000, "cx": 830, "crop": 0.60}
GROUP = [
    {"name": "adult_woman", "height": 700, "cx": 190},
    {"name": "doctor", "height": 790, "cx": 540},
    {"name": "boy", "height": 530, "cx": 872},
]

BEATS = [
    {
        "chapter": "오늘의 질문",
        "caption": "아이 기침에 열까지, 감기약 먼저?",
        "speaker": "adult_woman",
        "text": "아이가 열이 나고 기침을 하는데, 감기약부터 먹일까요?",
        "cast": [
            {"name": "adult_woman", "height": 640, "cx": 320},
            {"name": "doctor", "height": 720, "cx": 760},
        ],
        "keyword": "감기약 먼저?",
    },
    {
        "chapter": "먼저 볼 것",
        "caption": "감기약보다 숨쉬는 모습 먼저",
        "speaker": "doctor",
        "text": "감기약보다 먼저, 숨쉬는 모습을 보세요.",
        "cast": [DOCTOR_CU],
        "closeup": True,
        "memo": ["먼저 볼 세 가지", "숨쉬는 모습", "소변 양", "밥 먹는 양"],
    },
    {
        "chapter": "응급실 신호",
        "caption": "갈비뼈 밑이 들어가면 응급실",
        "speaker": "doctor",
        "text": "갈비뼈 아래가 쑥 들어가면 응급실 신호입니다.",
        "cast": [DOCTOR_CU],
        "closeup": True,
        "memo": ["응급실 신호", "갈비뼈 아래 함몰", "입술이 파래짐", "물도 못 마심"],
    },
    {
        "chapter": "감기와 독감",
        "caption": "감기는 서서히, 독감은 갑자기",
        "speaker": "doctor",
        "text": "감기는 서서히, 독감은 몇 시간 만에 고열과 몸살로 옵니다.",
        "cast": [DOCTOR_CU],
        "closeup": True,
        "memo": ["시작이 다릅니다", "감기: 서서히, 열 낮음", "독감: 갑자기 고열"],
    },
    {
        "chapter": "RSV",
        "caption": "두 살 미만 쌕쌕거림은 RSV",
        "speaker": "doctor",
        "text": "두 살 미만 쌕쌕거림은 알에스브이, 빠른 호흡도 신호입니다.",
        "cast": [DOCTOR_CU],
        "closeup": True,
        "memo": ["빠른 호흡 기준", "두 달 미만 예순 번", "열두 달까지 쉰 번", "다섯 살까지 마흔 번"],
    },
    {
        "chapter": "마이코플라스마",
        "caption": "보름째 마른기침은 다릅니다",
        "speaker": "doctor",
        "text": "보름 넘는 마른기침은 마이코플라스마일 수 있습니다.",
        "cast": [DOCTOR_CU],
        "closeup": True,
        "memo": ["마이코플라스마", "보름 넘는 마른기침", "항생제가 필요"],
    },
    {
        "chapter": "감기약 주의",
        "caption": "두 살 미만은 감기약 임의 복용 금지",
        "speaker": "doctor",
        "text": "두 살 미만은 종합감기약을 임의로 먹이지 마세요.",
        "cast": [DOCTOR_CU],
        "closeup": True,
        "memo": ["집에서 주의할 것", "두 살 미만 종합감기약", "임의 복용 금지"],
    },
    {
        "chapter": "어르신",
        "caption": "열이 없어도 폐렴일 수 있습니다",
        "speaker": "doctor",
        "text": "어르신은 열이 없어도, 밥 못 먹고 기운 없으면 폐렴일 수 있습니다.",
        "cast": [DOCTOR_CU],
        "closeup": True,
        "memo": ["어르신은 다릅니다", "열이 없어도", "밥 못 먹고 기운 없으면"],
    },
    {
        "chapter": "오늘 확인할 것",
        "caption": "그럼 오늘은 뭘 먼저 볼까요?",
        "speaker": "adult_woman",
        "text": "그럼 오늘은 뭘 먼저 볼까요?",
        "cast": GROUP,
        "nod": True,
    },
    {
        "chapter": "오늘 확인할 것",
        "caption": "숨쉬는 모습, 소변, 밥 먹는 양",
        "speaker": "doctor",
        "text": "숨쉬는 모습과 소변, 밥 먹는 양입니다.",
        "cast": GROUP,
        "nod": True,
    },
    {
        "chapter": "다음 편 예고",
        "caption": "다음 편: 3주 넘는 기침의 원인",
        "speaker": "doctor",
        "text": "삼 주 넘는 기침의 원인은 다음 편에서 봅니다.",
        "cast": GROUP,
        "nod": True,
        "badge": "다음 편 예고 · 3주 넘는 마른기침",
    },
]


def write_script():
    total = sum(len(b["text"]) for b in BEATS)
    lines = [
        "# Day 18 유튜브 쇼츠 대본 - 겨울 고열·기침, 감기인가 독감인가",
        "",
        "- 주제: 겨울 고열·기침, 감기인가 독감인가. RSV·마이코플라스마까지 아이와 어르신 감별법",
        "- 키워드: RSV 증상 아이 / 마이코플라스마 폐렴 기침 / 독감 감기 차이",
        "- 규격: 1080x1920 세로형, 상단 1/5 흰색 헤더 + 하단 4/5 종이인형 애니메이션, 11개 비트",
        "- 음성: 캐릭터별 Edge-TTS (닥터 온 인준 / 가온·몽이 선희 계열), voices.json",
        f"- 대본 분량: {total}자",
        "",
        "| # | 화자 | 챕터 | 화면 자막 | 대사 |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    names = {"doctor": "닥터 온", "adult_woman": "가온", "boy": "몽이", "girl": "콩이", "grandpa": "느티"}
    for i, b in enumerate(BEATS, 1):
        lines.append(f"| {i} | {names[b['speaker']]} | {b['chapter']} | {b['caption']} | {b['text']} |")
    lines += [
        "",
        "## 연출 메모",
        "- 1비트: 가온이 닥터 온에게 질문하며 시작한다(환자 목소리).",
        "- 2~8비트: 닥터 온 상반신 클로즈업 + 노란 인포그래픽 메모지로 핵심을 설명한다.",
        "- 9~11비트: 닥터 온·가온·몽이가 나란히 서서 대화하고, 마지막에 닥터 온이 Day 19 마른기침을 예고한다.",
        "- 캐릭터는 검은 테두리 2D 종이인형 컷아웃이며, 발화자만 크게 흔들리고 듣는 쪽은 작게 끄덕인다.",
        "- 숫자는 대본에서 한글 발음으로 적었다. TTS 오독을 막기 위한 표기다.",
        "",
    ]
    (VID_DIR / "shorts_script.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ 대본: {VID_DIR / 'shorts_script.md'} ({total}자)")


def write_times(timeline):
    names = {"doctor": "닥터 온", "adult_woman": "가온", "boy": "몽이", "girl": "콩이", "grandpa": "느티"}
    rows = []
    for i, (b, tl) in enumerate(zip(BEATS, timeline), 1):
        mm, ss = divmod(int(round(tl["start"])), 60)
        rows.append({"beat": i, "start": f"{mm:02d}:{ss:02d}", "start_sec": tl["start"],
                     "duration": tl["dur"], "chapter": b["chapter"], "caption": b["caption"],
                     "speaker": names[b["speaker"]]})
    data = {"beats": rows, "total_sec": timeline[-1]["end"]}
    (VID_DIR / "scene_times.json").write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                              encoding="utf-8")
    print("\n비트별 시작 시각")
    for r in rows:
        print(f"  {r['start']}  {r['chapter']}  ({r['duration']}초)")


def make_preview(video: Path, total: float):
    subprocess.run([FFMPEG_PATH, "-y", "-i", str(video), "-vf",
                    "fps=1.6,scale=420:-1:flags=lanczos,split[s0][s1];"
                    "[s0]palettegen=max_colors=192[p];[s1][p]paletteuse=dither=bayer",
                    "-loop", "0", str(GIF_OUT)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.copy(GIF_OUT, PREVIEW / "moving_preview.gif")
    caps = []
    for idx, frac in enumerate([0.06, 0.22, 0.45, 0.68, 0.9], 1):
        cap = DOWNLOADS / f"Day18_scene_{idx}.png"
        subprocess.run([FFMPEG_PATH, "-y", "-ss", f"{total * frac:.2f}", "-i", str(video),
                        "-frames:v", "1", str(cap)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.copy(cap, PREVIEW / f"scene{idx}_preview.png")
        caps.append(cap)
    return caps


def main():
    write_script()
    res = render_paperdoll_shorts(BEATS, str(OUT_MP4), TOPIC_KEYWORD, TEMP,
                                  keyword_by_beat=[b.get("keyword", "") for b in BEATS], gap=0.3)
    print(f"\n✅ 렌더 완료: {OUT_MP4} ({res['total_sec']}초, {res['frames']}프레임)")
    shutil.copy(OUT_MP4, VID_DIR / "paperdoll_shorts_video.mp4")
    write_times(res["beats"])
    total = probe_duration(OUT_MP4)
    caps = make_preview(OUT_MP4, total)
    print(f"   - 실측 길이 {total:.2f}초")
    print(f"   - GIF {GIF_OUT} ({GIF_OUT.stat().st_size/1024/1024:.2f}MB)")
    for c in caps:
        print("   - 캡처", c)


if __name__ == "__main__":
    main()
