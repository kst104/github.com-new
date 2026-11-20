# -*- coding: utf-8 -*-
"""
잘.의.정.바 3단 레이아웃 규격 검증 테스트 (1080x1920)
- 상단 1/3(0~540) 흰색 배경 + 검정 훅 + 주황 포인트 박스
- 중단(540~1400) 칠판 아트 1080x860 좌우 꽉 참
- 하단(1400~1920) 흰색 여백 + y1422 회색 안내문
- 실명 미포함

실행: python3 engine/test_jaljab_layout.py [--render]
  --render 를 주면 Day 13 씬 5장을 content/2026-11-20-01/chalkboard/jaljab_preview/ 에 PNG 로 뽑는다.
"""

import os
import sys
from pathlib import Path

from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from engine.chalkboard_video_engine import (  # noqa: E402
    JALJAB_TOP_BAND,
    JALJAB_VIDEO_BAND,
    JALJAB_FOOTER_Y,
    JALJAB_FOOTER,
    JALJAB_POINT,
    create_jaljab_scene_frame,
    render_jaljab_previews,
    scene_caption,
)

ART = Path("/workspace/assets/chalkboard/day13")
OUT_DIR = Path("/workspace/tool-results/jaljab")

SCENES = [
    {"keyword": "겨울 새벽 운동?!", "caption": "새벽엔 혈 최고 · 체온 최저!",
     "chalk_img": str(ART / "scene1_dawn_walk_chest.png")},
    {"keyword": "혈관 수축", "caption": "좁아진 혈관, 심장은 더 세게",
     "chalk_img": str(ART / "scene2_cold_heart_load.png")},
    {"keyword": "오후 두 시에서 네 시", "caption": "해 지기 전, 오후 두 시에서 네 시",
     "chalk_img": str(ART / "scene3_afternoon_sun_walk.png")},
    {"keyword": "의자 홈트", "caption": "의자 하나로 이십 분",
     "chalk_img": str(ART / "scene4_indoor_chair_workout.png")},
    {"keyword": "일일구", "caption": "가슴 통증 오 분이면 일일구",
     "chalk_img": str(ART / "scene5_chest_pain_call_119.png")},
]


def _is_near(px, target, tol=6):
    return all(abs(px[i] - target[i]) <= tol for i in range(3))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = OUT_DIR / "jaljab_layout_check.png"
    create_jaljab_scene_frame(
        chalk_img_path=SCENES[0]["chalk_img"],
        out_img=str(frame),
        topic_keyword=SCENES[0]["keyword"],
        caption=SCENES[0]["caption"],
    )
    img = Image.open(frame).convert("RGB")
    assert img.size == (1080, 1920), img.size

    top_y1, top_y2 = JALJAB_TOP_BAND
    vid_y1, vid_y2 = JALJAB_VIDEO_BAND
    px = img.load()

    # 상단 경계: y=0, y=530 은 흰색(문구 없는 좌우 여백 기준)
    for y in (5, 120, 520):
        assert _is_near(px[20, y], (255, 255, 255)), f"상단 흰색 아님: y={y} {px[20, y]}"
    # 주황 박스가 상단 밴드 안에 존재
    orange_rows = [y for y in range(0, top_y2) if _is_near(px[540, y], JALJAB_POINT)]
    assert orange_rows, "주황 포인트 박스 없음"
    assert min(orange_rows) > 300 and max(orange_rows) < top_y2, (min(orange_rows), max(orange_rows))

    # 중단: y=540 첫 행부터 칠판 아트(어두운 색), y=1399 마지막 행까지 어두움
    assert not _is_near(px[540, vid_y1], (255, 255, 255), tol=20), "영상 영역 시작이 흰색"
    assert not _is_near(px[540, vid_y2 - 1], (255, 255, 255), tol=20), "영상 영역 끝이 흰색"
    # 좌우 꽉 참 (x=0, x=1079)
    assert not _is_near(px[0, 1000], (255, 255, 255), tol=20), "영상이 좌측 끝까지 차지 않음"
    assert not _is_near(px[1079, 1000], (255, 255, 255), tol=20), "영상이 우측 끝까지 차지 않음"

    # 하단: y=1410 흰색, y=1500 흰색, y=1900 흰색 / 안내문은 y1422 근처에 회색 글씨
    for y in (1410, 1500, 1900):
        assert _is_near(px[20, y], (255, 255, 255)), f"하단 흰색 아님: y={y} {px[20, y]}"
    footer_band = [px[x, JALJAB_FOOTER_Y + 20] for x in range(0, 1080)]
    assert any(p[0] < 200 for p in footer_band), "하단 안내문 글씨 없음"

    # 자막: 영상 하단 중앙에 흰색 픽셀 존재
    caption_band = [px[x, vid_y2 - 96] for x in range(300, 780)]
    assert any(_is_near(p, (255, 255, 255), tol=10) for p in caption_band), "자막 흰색 글씨 없음"

    # 씬 dict → 자막 문구 도출
    assert scene_caption({"main_text": "a\nb"}) == "a · b"
    assert scene_caption({"caption": "x", "main_text": "a\nb"}) == "x"

    print("✅ 잘.의.정.바 3단 레이아웃 규격 검증 통과 (1080x1920, 3단 경계·자막·안내문)")

    if "--render" in sys.argv:
        outs = render_jaljab_previews(SCENES, "/workspace/downloads/jaljab_preview", prefix="day13_jaljab")
        print("프리뷰:", *outs, sep="\n  ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
