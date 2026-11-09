---
name: anime-shorts
description: >-
  90s Retro Japanese Anime & Manga style shorts/reels video generator. Produces
  1080x1920 vertical videos with vintage 1990s cel animation aesthetics, CRT scanlines,
  manga sound effects (SFX) badges, retro VHS title overlays, and classic yellow subtitles.
  Supports dual-mode selectable generation (Standard Dr. GeongTae 3D vs 90s Retro Anime).
  Use whenever creating or switching shorts style to 90s Japanese anime/manga ("90년대 애니 스타일 쇼츠 만들어줘",
  "만화 스타일 쇼츠로 바꿔줘", "일반과 애니 버전 2개로 만들어줘").
---

# anime-shorts

Generates and renders nostalgic 90s Japanese Retro Anime & Manga style 9:16 vertical videos (1080×1920) for Instagram Reels and YouTube Shorts.

## Features

1. **90s Cel Animation Aesthetic**:
   - Vintage 1990s hand-drawn cel look (reminiscent of Black Jack, City Hunter, Evangelion, Sailor Moon medical/city scenes).
   - Warm retro color grading, subtle CRT scanlines, and VHS tape broadcast overlay (`🔴 REC SP 0:00:24`, `1995.11.09 HI-FI`).
2. **Manga Comic Badges & SFX**:
   - Dramatic comic sound effects in Japanese manga style (`쿵!!`, `위잉!!`, `반짝✨`, `콰앙!!`, `훈훈~`).
   - High-contrast comic speech and warning frames.
3. **90s Fansub Subtitle Styling**:
   - Classic retro yellow text (`#FEF08A`) with solid black outline for maximum readability on mobile screens.
4. **Dual Selectable Mode**:
   - `--style standard`: Dr. GeongTae 3D mascot + Infographic situation cards
   - `--style anime`: 90s Retro Japanese Anime & Manga style
   - `--style both`: Generates both versions simultaneously so the creator can compare or A/B test on Instagram and YouTube!

## Usage

### 1. Python CLI
```bash
# 90s 애니 스타일 쇼츠 단독 렌더링
python3 engine/video_engine.py --style anime

# 일반 버전 단독 렌더링
python3 engine/video_engine.py --style standard

# 일반 + 애니 2개 버전 동시 렌더링 (추천)
python3 engine/video_engine.py --style both
```

### 2. Scene Image Generation Prompt Formula (90s Retro Anime)
When generating scene illustrations with AI image tools (`images` CLI or DALL-E / Midjourney):

```
90s retro anime style, [scene subject / medical action], vintage 1990s cel animation screencap, detailed line art, muted retro color palette, dramatic lighting, 1995 anime OVA screenshot, cel shaded
```

#### Example Prompts:
- **Morning Danger**: `90s retro anime style, a person waking up in shock in a cold winter bedroom, frost on window, vintage 1990s cel animation screencap, dramatic lighting, clean lineart`
- **Emergency Room Rush**: `90s retro anime style, intense hospital emergency room hallway with anime doctor and staff rushing, dramatic red emergency lights, vintage 1995 anime OVA screenshot`
- **Doctor Consultation**: `90s retro anime style, a calm handsome anime doctor in white coat and stethoscope explaining with gentle smile and pointing finger, bright retro clinic office, vintage cel shaded`
- **Winter Jogging Warning**: `90s retro anime style, a runner jogging in freezing dark winter morning mist with frost and heavy breath, warning danger atmosphere, manga action speedlines`
- **Cozy Family Ending**: `90s retro anime style, cozy warm living room with smiling family drinking steaming tea together, sunset golden hour glow, peaceful heartwarming 1990s anime ending scene`

## File Structure

- `engine/anime_video_engine.py`: Dedicated 90s anime frame synthesis & video compiler
- `engine/video_engine.py`: Integrated controller with `--style {standard, anime, both}`
- `assets/anime/`: Generated retro cel art per topic
- `downloads/`: Exported MP4 videos
