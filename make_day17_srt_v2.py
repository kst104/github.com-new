#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Day 17 쇼츠(2판) 한·영·일 자막 생성 — 렌더된 MP4 오디오의 무음 구간 실측 타임코드 기준.

- `silencedetect=noise=-32dB:d=0.15` 로 발화 덩어리(스팬)를 뽑고, 각 스팬에 대사를 1:1로 매핑한다.
- 한 스팬이 너무 길어 두 줄로도 넘치는 경우(0:05.9 문장)는 글자 수 비율로 스팬을 둘로 나눈다.
- 출력: work/day17_{ko,en,ja}.srt, content/2026-11-24-01/subtitles/day17_{ko,en,ja}.srt
"""
import re
import subprocess
from pathlib import Path

FFMPEG = "/usr/local/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
VIDEO = Path("/workspace/downloads/Day17_겨울밤가려움_건조피부염아토피_칠판드로잉_쇼츠.mp4")
OUT_DIRS = [Path("/workspace/work"), Path("/workspace/work/content-automation-engine/content/2026-11-24-01/subtitles")]

# (스팬 인덱스, 스팬 안에서 나눌 비율 또는 None, 한국어, 영어, 일본어)
CUES = [
    (0, None, "밤마다 다리를 긁는다면,",
     "If you scratch your legs every night,",
     "毎晩脚をかいているなら、"),
    (1, None, "크림을 안 발라서만은 아닐 수 있습니다.",
     "it may not be only because you skip moisturizer.",
     "クリームを塗っていないからだけではない\nかもしれません。"),
    (2, 0.527, "밤에는 피부 온도가 오르고\n코르티솔이 낮아지는 것이",
     "At night, skin temperature rises\nand cortisol falls,",
     "夜は皮膚温が上がり\nコルチゾールが下がることが、"),
    (2, 0.527, "가려움을 심하게 하는 요인으로 꼽힙니다.",
     "and that is often cited as a reason\nthe itch gets worse.",
     "かゆみを強くする要因として\n挙げられています。"),
    (3, None, "정강이 앞쪽이 하얗게 갈라지면,",
     "If the front of your shins cracks\nand turns white,",
     "すねの前面が白くひび割れたら、"),
    (4, None, "건조성 피부염을 의심해 볼 수 있습니다.",
     "dry-skin eczema is one possibility\nto consider.",
     "乾燥性皮膚炎の可能性を\n考えてみてください。"),
    (5, None, "난방으로 마른 실내와 잦은 목욕이\n악화 요인으로 꼽힙니다.",
     "Dry indoor air from heating and frequent\nbathing can make it worse.",
     "暖房で乾燥した室内と頻繁な入浴が\n悪化要因として挙げられます。"),
    (6, None, "팔꿈치와 무릎 안쪽이 반복해서 붉어지면,",
     "If the insides of your elbows and knees\nkeep turning red,",
     "ひじやひざの内側が\n繰り返し赤くなるなら、"),
    (7, None, "아토피 피부염을 의심해 볼 수 있습니다.",
     "atopic dermatitis is one possibility\nto consider.",
     "アトピー性皮膚炎の可能性を\n考えてみてください。"),
    (8, None, "가려움이 먼저 오고 발진이 따라오는\n경우가 많습니다.",
     "The itch often comes first,\nand the rash follows.",
     "かゆみが先に来て、湿疹が後から\n現れることが多いです。"),
    (9, None, "바르는 스테로이드는 먹는 약과 다릅니다.",
     "Topical steroids are not\nthe same as steroid pills.",
     "塗るステロイドは\n飲み薬とは違います。"),
    (10, None, "처방받은 연고는 안내받은 부위에,",
     "Apply the ointment you were prescribed\nto the area you were told,",
     "処方された軟膏は、\n説明された部位に、"),
    (11, None, "안내받은 양과 기간대로 바르는 것이\n원칙입니다.",
     "in the amount and for the period you were told.",
     "説明された量と期間どおりに\n塗るのが原則です。"),
    (12, None, "잠들기 전에 건조한 부위를 보습하고,",
     "Before bed, moisturize the dry areas,",
     "寝る前に乾燥した部位を保湿し、"),
    (13, None, "땀이 날 정도로 덥게 덮지 마십시오.",
     "and don't cover up so warmly\nthat you sweat.",
     "汗ばむほど厚く\n布団をかけないでください。"),
]


def speech_spans() -> list[tuple[float, float]]:
    p = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", str(VIDEO),
                        "-af", "silencedetect=noise=-32dB:d=0.15", "-f", "null", "-"],
                       capture_output=True, text=True)
    lines = p.stderr.splitlines()
    spans, cur_start = [], 0.0
    starts = {}
    for line in lines:
        m = re.search(r"silence_start: ([\d.]+)", line)
        if m:
            starts["s"] = float(m.group(1))
            if m.group(1) not in ("0", "0.0"):
                spans.append((cur_start, float(m.group(1))))
            cur_start = None
            continue
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m:
            cur_start = float(m.group(1))
    # 마지막 스팬은 마지막 무음 시작에서 끝난다(silence_end 는 영상 끝)
    return [s for s in spans if s[1] - s[0] >= 0.15]


def fmt(t: float) -> str:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    ms = int(round((s - int(s)) * 1000))
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{ms:03d}"


def build() -> dict[str, str]:
    spans = speech_spans()
    assert len(spans) == 14, f"발화 스팬 수가 예상과 다릅니다: {len(spans)}"
    used = {}
    out = {"ko": [], "en": [], "ja": []}
    idx = {"ko": 0, "en": 0, "ja": 0}
    for span_i, ratio, ko, en, ja in CUES:
        s, e = spans[span_i]
        if ratio is not None:
            key = (span_i, ratio)
            used[key] = used.get(key, 0) + 1
            if used[key] == 1:
                e = s + (e - s) * ratio
            else:
                s, _ = spans[span_i]
                s = s + (_ - s) * ratio
        for lang, text in (("ko", ko), ("en", en), ("ja", ja)):
            idx[lang] += 1
            out[lang].append(f"{idx[lang]}\n{fmt(s)} --> {fmt(e - 0.03)}\n{text}\n")
    return {lang: "\n".join(blocks) for lang, blocks in out.items()}


def main():
    srts = build()
    for lang, body in srts.items():
        for d in OUT_DIRS:
            d.mkdir(parents=True, exist_ok=True)
            (d / f"day17_{lang}.srt").write_text(body, encoding="utf-8")
        cues = body.strip().split("\n\n")
        print(f"[{lang}] {len(cues)}큐, {len(body)}자")
        first = cues[0].splitlines()
        last = cues[-1].splitlines()
        print(f"   첫 큐 {first[1]}  |  끝 큐 {last[1]}")


if __name__ == "__main__":
    main()
