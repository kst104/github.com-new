---
name: ig-video
description: >-
  Automatically renders a complete 9:16 vertical 1080x1920 MP4 Reel/Shorts video
  from an Instagram Reel script or raw medical topic. Integrates Edge-TTS Korean
  voice narration (Dr. Seung-tae tone), Dr. GeongTae mascot branding, and high-impact
  yellow/white subtitles. Use whenever the user asks to generate, render, or produce
  a video, reel, or shorts ("쇼츠 만들어줘", "릴스 영상 만들어줘", "비디오 렌더링해줘").
---

# ig-video

Generates a complete, ready-to-upload 9:16 (1080x1920) vertical video for Instagram Reels and YouTube Shorts.

## Tools in this skill

- `engine/video_engine.py`: Takes scenes and beats, produces Edge-TTS audio, builds graphic frames with mascot avatar, and exports MP4.

```bash
# Day 1 샘플 쇼츠 즉시 렌더링
python3 engine/video_engine.py --sample

# 특정 릴스 대본을 비디오로 렌더링
python3 engine/video_engine.py --script content/2026-11-09-05/instagram/reel_script.md --output downloads/my_reel.mp4
```

## Features

1. **Edge-TTS Korean Narration**: Uses `ko-KR-InJoonNeural` (warm, authoritative male doctor tone) or `ko-KR-SunHiNeural`.
2. **Visual Layout (1080×1920)**:
   - Header badge: "닥터 김승태의 1분 응급실 클립"
   - Scene alert badge: "⚠️ 긴급 주의보", "🏥 응급실 현장 리포트", "💡 의사의 3분 처방"
   - Mascot character: Dr. GeongTae avatar with stethoscope
   - Large mobile-optimized subtitle box: Yellow main emphasis font (68pt) + White subtext (48pt)
3. **Timed Audio Sync**: Measures audio length per beat and renders seamless video.
4. **Format**: H.264 / AAC 1080x1920 MP4, 100% compliant with Instagram Reels and YouTube Shorts.
