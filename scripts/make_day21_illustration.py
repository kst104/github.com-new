#!/usr/bin/env python3
"""Day 21(2026-11-28) 블로그 삽화 3장: 3D 병원 배경 + 종이인형 캐릭터 + 노란 메모지."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_paperdoll_illustration as m

m.IMG_DIR = Path(__file__).resolve().parents[1] / "content" / "2026-11-28-01" / "images_v2"

s1 = m.blog_scene(
    "day21_v2_scene1_겨울자외선.png",
    characters=[("adult_woman", 475, 225), ("doctor", 550, 505)],
    note_lines=[("head", "겨울 자외선,"), ("body", "여름과 거의 같습니다"),
                ("body", "눈은 80%를 반사"), ("body", "스키장은 2~4배"),
                ("body", "SPF 30 · 외출 15분 전")],
    note_pos=(668, 145), tag_txt="겨울 광노출 · 현장 리포트",
)
s2 = m.blog_scene(
    "day21_v2_scene2_입술.png",
    characters=[("adult_man", 480, 235), ("doctor", 545, 505)],
    note_lines=[("head", "입술은"), ("body", "피지선이 없습니다"),
                ("body", "침으로 축이면 더 마름"), ("body", "뜯지 말고"),
                ("body", "바셀린으로 덮기")],
    note_pos=(672, 150), tag_txt="갈라진 입술 · 구순 건조",
)
s3 = m.blog_scene(
    "day21_v2_scene3_손등.png",
    characters=[("grandma", 455, 205), ("doctor", 545, 505)],
    note_lines=[("head", "손등이 붉게 붓고"), ("body", "가렵다가 트면"),
                ("body", "동창 vs 손습진"), ("body", "젖은 손 + 찬 바람")],
    note_pos=(676, 140), tag_txt="말초 피부 손상 · 감별",
)
print(s1, s2, s3, sep="\n")
