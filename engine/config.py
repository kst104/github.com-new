import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

DEFAULT_MODEL_PROVIDER = os.getenv("DEFAULT_MODEL_PROVIDER", "claude") # "claude" or "openai"
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# 쇼츠 기본 비주얼 스타일 설정 (11-11 승태 님 지시: 칠판 분필 드로잉 특강 스타일을 기본으로 적용)
DEFAULT_SHORTS_STYLE = "chalkboard" # "chalkboard", "anime", "standard"

# 칠판 쇼츠의 프레임 레이아웃 (11-20 승태 님 확정: 잘.의.정.바 3단 레이아웃을 기본으로 적용)
# "jaljab" = 상단 흰색 헤더 + 중단 1080x860 영상 + 하단 여백 / "chalkboard" = 기존 전면 칠판 프레임
# 실제 기본값은 engine/chalkboard_video_engine.py의 DEFAULT_SHORTS_LAYOUT(jaljab)이다.
DEFAULT_SHORTS_LAYOUT = "jaljab" # "jaljab", "chalkboard"
