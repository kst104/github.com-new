#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Day 18 블로그 삽화 3장: 3D 진료실 배경 + 검은 테두리 2D 종이인형 + 노란 메모지."""
import sys
from pathlib import Path

ROOT = Path("/workspace/work/content-automation-engine")
sys.path.insert(0, str(ROOT / "scripts"))
import make_paperdoll_illustration as doll  # noqa: E402

DAY = ROOT / "content" / "2026-11-25-01" / "images_v2"
doll.IMG_DIR = DAY
DAY.mkdir(parents=True, exist_ok=True)


def scene(out_name, characters, note_lines, note_pos, tag_txt, char_baseline=846, note_width=500,
          note_rot=-3):
    return doll.blog_scene(out_name, characters, note_lines, note_pos, tag_txt,
                           char_baseline=char_baseline, note_width=note_width, note_rot=note_rot)


if __name__ == "__main__":
    s1 = scene(
        "day18_v2_scene1_숨쉬는모습.png",
        characters=[("boy", 340, 250), ("doctor", 555, 545)],
        note_lines=[("head", "숨쉴 때 갈비뼈 밑이\n들어가나요?"),
                    ("body", "그렇다면 감기약이 아니라"),
                    ("body", "응급실 신호입니다"),
                    ("bullet", "빠른 호흡: 2개월 미만 60회"),
                    ("bullet", "2~12개월 50회, 1~5세 40회"),
                    ("bullet", "물도 못 마시고 소변 8시간 없음")],
        note_pos=(636, 118), tag_txt="RSV · 영아 호흡곤란 신호",
    )
    s2 = scene(
        "day18_v2_scene2_네가지감별.png",
        characters=[("adult_woman", 470, 190), ("girl", 350, 350), ("doctor", 540, 548)],
        note_lines=[("head", "시작이 다르면\n병도 다릅니다"),
                    ("body", "감기: 서서히, 열 낮음"),
                    ("body", "독감: 몇 시간 만에 고열·몸살"),
                    ("body", "RSV: 콧물 → 사흘째 쌕쌕"),
                    ("body", "마이코플라스마: 5~7일 마른기침")],
        note_pos=(664, 128), tag_txt="감기·독감·RSV·마이코플라스마",
    )
    s3 = scene(
        "day18_v2_scene3_어르신.png",
        characters=[("grandpa", 500, 250), ("doctor", 550, 530)],
        note_lines=[("head", "열이 없어도\n위중할 수 있습니다"),
                    ("body", "이틀 사이 밥을 못 먹고"),
                    ("body", "자리에서 못 일어나면"),
                    ("body", "폐렴을 먼저 의심합니다"),
                    ("body", "산소포화도 90% 아래 = 응급")],
        note_pos=(672, 140), tag_txt="어르신 호흡기 감염",
    )
    for p in (s1, s2, s3):
        print(p)
