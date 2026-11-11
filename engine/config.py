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
