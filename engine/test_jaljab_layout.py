# -*- coding: utf-8 -*-
"""
잘.의.정.바 3단 레이아웃 규격 검증 테스트 (1080x1920)
- 상단 1/3(0~540) 흰색 배경 + 검정 훅 + 주황 포인트 박스
- 중단(540~1400) 칠판 아트 1080x860 좌우 꽉 참
- 하단(1400~1920) 흰색 여백 + y1422 회색 안내문
- 초기 2초(t < 2.0s) '구독·알림·좋아요는 힘이 됩니다' 배지 — t >= 2.0s 프레임에는 없음
- 실명 미포함

실행: python3 engine/test_jaljab_layout.py [--render] [--no-video]
  --render   : Day 13 씬 5장을 content/2026-11-20-01/chalkboard/jaljab_preview/ 에 PNG 로 뽑는다.
  --no-video : 실제 2씬 MP4 렌더 검증(기본 실행)을 건너뛴다. TTS 네트워크가 없을 때만 사용.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from engine.chalkboard_video_engine import (  # noqa: E402
    FFMPEG_PATH,
    JALJAB_TOP_BAND,
    JALJAB_VIDEO_BAND,
    JALJAB_FOOTER_Y,
    JALJAB_FOOTER,
    JALJAB_POINT,
    SUBSCRIBE_BADGE_TEXT,
    SUBSCRIBE_BADGE_WINDOW,
    create_jaljab_scene_frame,
    get_audio_duration,
    render_chalkboard_shorts,
    render_jaljab_previews,
    scene_caption,
    subscribe_badge_geometry,
)

ART = Path("/workspace/assets/chalkboard/day13")
OUT_DIR = Path("/workspace/tool-results/jaljab")
VIDEO_TMP = Path("/tmp/jaljab_badge_video_test")

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


def _orange_count(img, box):
    """배지 영역의 주황(#EE6C1E) 픽셀 수 — 배지 유무 판별용."""
    x1, y1, x2, y2 = box
    px = img.load()
    n = 0
    for y in range(y1, y2):
        for x in range(x1, x2):
            r, g, b = px[x, y][:3]
            if r > 180 and 60 <= g <= 160 and b < 90:
                n += 1
    return n


def _badge_band(width=1080):
    _, box, _ = subscribe_badge_geometry(width)
    x1, y1, x2, y2 = box
    return (x1, y1, x2, y2)


def _grab_frame(mp4, t, png):
    cmd = [FFMPEG_PATH, "-y", "-ss", f"{t:.2f}", "-i", str(mp4),
           "-frames:v", "1", "-update", "1", str(png)]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return Image.open(png).convert("RGB")


def check_static_frames():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = OUT_DIR / "jaljab_layout_check.png"
    create_jaljab_scene_frame(
        chalk_img_path=SCENES[0]["chalk_img"],
        out_img=str(frame),
        topic_keyword=SCENES[0]["keyword"],
        caption=SCENES[0]["caption"],
    )
    create_jaljab_scene_frame(
        chalk_img_path=SCENES[0]["chalk_img"],
        out_img=str(OUT_DIR / "jaljab_layout_check_badge2s.png"),
        topic_keyword=SCENES[0]["keyword"],
        caption=SCENES[0]["caption"],
        show_subscribe_badge=True,
    )
    img = Image.open(frame).convert("RGB")
    assert img.size == (1080, 1920), img.size
    img_badge = Image.open(OUT_DIR / "jaljab_layout_check_badge2s.png").convert("RGB")

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

    # --- 초기 2초 배지: 정지 프레임에서 위치·색·문구 자리 검증 ---
    bx1, by1, bx2, by2 = _badge_band()
    assert by1 >= vid_y1, f"배지가 영상 영역 위로 벗어남: {by1}"
    assert by2 < vid_y2 and by2 < vid_y2 - 200, f"배지가 자막 영역과 겹침: {by2}"
    assert bx1 > 0 and bx2 < 1080, (bx1, bx2)
    orange_plain = _orange_count(img, (0, by1, 1080, by2))
    orange_badge = _orange_count(img_badge, (0, by1, 1080, by2))
    assert orange_plain < 300, f"배지 없는 프레임에 주황 영역이 이미 있음: {orange_plain}"
    assert orange_badge > 5000, f"배지 프레임에 주황 배지가 없음: {orange_badge}"
    # 배지 안에 굵은 흰 글씨
    white_in_badge = sum(1 for y in range(by1, by2) for x in range(bx1, bx2)
                         if _is_near(img_badge.getpixel((x, y)), (255, 255, 255), tol=16))
    assert white_in_badge > 1500, f"배지 흰 글씨 픽셀 부족: {white_in_badge}"
    # 2초 배지가 씬 자막·상단 헤더를 건드리지 않음
    for y in (520, vid_y2 - 96):
        assert img.getpixel((540, y)) == img_badge.getpixel((540, y)), f"배지가 y={y} 행을 덮음"

    # 씬 dict → 자막 문구 도출
    assert scene_caption({"main_text": "a\nb"}) == "a · b"
    assert scene_caption({"caption": "x", "main_text": "a\nb"}) == "x"

    print(f"✅ 정지 프레임 검증 통과 — 배지 없음 {orange_plain}px / 배지 있음 {orange_badge}px "
          f"({SUBSCRIBE_BADGE_TEXT}, y {by1}~{by2})")


def check_video_timing():
    """실제 2씬 MP4(3초 이상)를 렌더해 t<2.0s 배지 있음 / t>=2.0s 배지 없음 확인 후 테스트 MP4 삭제."""
    shutil.rmtree(VIDEO_TMP, ignore_errors=True)
    VIDEO_TMP.mkdir(parents=True)
    scenes = [
        {"keyword": "겨울 새벽 운동?!", "caption": "새벽엔 혈 최고 · 체온 최저!",
         "chalk_img": str(ART / "scene1_dawn_walk_chest.png"),
         "voice": "겨울 새벽 운동은 혈관에 부담이 됩니다."},
        {"keyword": "혈관 수축", "caption": "좁아진 혈관, 심장은 더 세게",
         "chalk_img": str(ART / "scene2_cold_heart_load.png"),
         "voice": "추위로 혈관이 좁아지면 심장은 더 세게 뜁니다."},
    ]
    out = VIDEO_TMP / "jaljab_badge_test.mp4"
    png = VIDEO_TMP / "frame.png"
    _, by1, _, by2 = _badge_band()
    band = (0, by1, 1080, by2)
    try:
        render_chalkboard_shorts(scenes, str(out), temp_dir=str(VIDEO_TMP / "build"))
        assert out.exists(), "테스트 MP4 가 만들어지지 않음"
        duration = get_audio_duration(str(out))
        assert duration >= 3.0, f"테스트 MP4 가 3초 미만: {duration:.2f}s"

        early = _orange_count(_grab_frame(out, 1.0, png), band)      # t < 2.0s
        late = _orange_count(_grab_frame(out, 2.6, png), band)      # t >= 2.0s
        assert early > 5000, f"t=1.0s 프레임에 2초 배지 없음: {early}px"
        assert late < 300, f"t=2.6s 프레임에도 배지가 남아 있음: {late}px"
        assert SUBSCRIBE_BADGE_WINDOW == (0.0, 2.0), SUBSCRIBE_BADGE_WINDOW
        print(f"✅ 2씬 MP4 검증 통과 — 총 {duration:.2f}s · t=1.0s 배지 {early}px / "
              f"t=2.6s 배지 {late}px (노출 구간 {SUBSCRIBE_BADGE_WINDOW[0]}~{SUBSCRIBE_BADGE_WINDOW[1]}s)")
    finally:
        # 테스트 MP4 와 임시 빌드 산출물은 남기지 않는다
        shutil.rmtree(VIDEO_TMP, ignore_errors=True)
        print("   테스트 MP4 삭제 완료:", not out.exists())


def main():
    check_static_frames()

    if "--no-video" not in sys.argv:
        check_video_timing()

    print("✅ 잘.의.정.바 3단 레이아웃 규격 검증 통과 (1080x1920, 3단 경계·자막·안내문·초기 2초 배지)")

    if "--render" in sys.argv:
        outs = render_jaljab_previews(SCENES, "/workspace/downloads/jaljab_preview", prefix="day13_jaljab")
        print("프리뷰:", *outs, sep="\n  ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
