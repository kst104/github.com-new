#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Day 18 쇼츠 한·영·일 자막 — 렌더된 MP4 오디오의 무음 구간 실측(silencedetect) 기준."""
import json
import re
import subprocess
from pathlib import Path

FFMPEG = "/usr/local/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"
VIDEO = Path("/workspace/downloads/Day18_겨울고열기침_감기독감RSV마이코플라스마_쇼츠.mp4")
DAY = Path("/workspace/work/content-automation-engine/content/2026-11-25-01")
OUT_DIRS = [Path("/workspace/work"), DAY / "subtitles"]

CUES = [
    ("아이가 열이 나고 기침을 하는데,\n감기약부터 먹일까요?",
     "My child has a fever and a cough.\nShould I give cold medicine first?",
     "子どもが熱と咳があります。\n風邪薬を先に飲ませてもいいですか？"),
    ("감기약보다 먼저,\n숨쉬는 모습을 보세요.",
     "Before cold medicine,\nlook at how your child is breathing.",
     "風邪薬より先に、\n息の仕方を見てください。"),
    ("갈비뼈 아래가 쑥 들어가면\n응급실 신호입니다.",
     "If the skin under the ribs pulls in,\nthat's an emergency sign.",
     "肋骨の下がへこむなら、\n救急外来のサインです。"),
    ("감기는 서서히, 독감은 몇 시간 만에\n고열과 몸살로 옵니다.",
     "A cold builds slowly. Flu brings high fever\nand body aches within hours.",
     "風邪はゆっくり、インフルエンザは\n数時間で高熱と筋肉痛が来ます。"),
    ("두 살 미만 쌕쌕거림은 RSV,\n빠른 호흡도 신호입니다.",
     "Under age two, wheezing means RSV.\nFast breathing is a sign too.",
     "2歳未満のゼーゼーはRSV。\n速い呼吸もサインです。"),
    ("보름 넘는 마른기침은\n마이코플라스마일 수 있습니다.",
     "A dry cough lasting over two weeks\nmay be mycoplasma.",
     "2週間以上続く乾いた咳は\nマイコプラズマかもしれません。"),
    ("두 살 미만은 종합감기약을\n임의로 먹이지 마세요.",
     "For children under two, don't give\ncombination cold medicine on your own.",
     "2歳未満には、総合風邪薬を\n自己判断で飲ませないでください。"),
    ("어르신은 열이 없어도, 밥 못 먹고\n기운 없으면 폐렴일 수 있습니다.",
     "In older adults, poor appetite and weakness\nwithout fever can be pneumonia.",
     "高齢者は熱がなくても、食事がとれず\n元気がなければ肺炎のことがあります。"),
    ("그럼 오늘은 뭘 먼저 볼까요?",
     "So what should we check first today?",
     "では今日は何を先に見ればいいですか？"),
    ("숨쉬는 모습과 소변,\n밥 먹는 양입니다.",
     "Breathing, urine output,\nand how much they eat.",
     "息の仕方、おしっこ、\n食事の量です。"),
    ("삼 주 넘는 기침의 원인은\n다음 편에서 봅니다.",
     "Next episode: what causes a cough\nlasting over three weeks.",
     "3週間以上続く咳の原因は、\n次の回で見ていきます。"),
]


def speech_spans():
    p = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", str(VIDEO),
                        "-af", "silencedetect=noise=-35dB:d=0.20", "-f", "null", "-"],
                       capture_output=True, text=True)
    spans, cur_start = [], 0.0
    for line in p.stderr.splitlines():
        m = re.search(r"silence_start: ([\d.]+)", line)
        if m:
            start = float(m.group(1))
            if start - cur_start >= 0.12:
                spans.append((cur_start, start))
            cur_start = None
            continue
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m:
            cur_start = float(m.group(1))
    return spans


def fmt(t: float) -> str:
    h, rem = divmod(max(0.0, t), 3600)
    m, s = divmod(rem, 60)
    ms = int(round((s - int(s)) * 1000))
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{ms:03d}"


def build():
    times = json.loads((DAY / "video" / "scene_times.json").read_text(encoding="utf-8"))["beats"]
    spans = speech_spans()
    out = {"ko": [], "en": [], "ja": []}
    for i, (beat, cue) in enumerate(zip(times, CUES), 1):
        lo, hi = beat["start_sec"], beat["start_sec"] + beat["duration"]
        inside = [(max(s, lo), min(e, hi)) for s, e in spans if e > lo + 0.05 and s < hi - 0.05]
        if inside:
            start, end = inside[0][0], inside[-1][1]
        else:
            start, end = lo, min(hi, lo + 3.0)
        end = min(end, hi - 0.02)
        for lang, txt in zip(("ko", "en", "ja"), cue):
            out[lang].append(f"{len(out[lang]) + 1}\n{fmt(start)} --> {fmt(end)}\n{txt}\n")
    return ({k: "\n".join(v) for k, v in out.items()}, len(spans))


def main():
    srts, n_spans = build()
    print(f"silencedetect 스팬 {n_spans}개")
    for lang, body in srts.items():
        for d in OUT_DIRS:
            d.mkdir(parents=True, exist_ok=True)
            (d / f"day18_{lang}.srt").write_text(body, encoding="utf-8")
        cues = body.strip().split("\n\n")
        print(f"[{lang}] {len(cues)}큐")
        for c in cues:
            print("   ", c.splitlines()[1], "|", c.splitlines()[2].replace("\n", " / "))
    return srts


if __name__ == "__main__":
    main()
