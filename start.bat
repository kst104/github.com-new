@echo off
rem 윈도우: 더블클릭하면 작업 허브를 켭니다
chcp 65001 >nul
cd /d "%~dp0"
where git >nul 2>nul || (echo git 이 없어요. https://git-scm.com 에서 설치해 주세요. & pause & exit /b 1)
if not exist .git (
  git init -q -b main
  git remote add origin https://github.com/kst104/github.com-new.git
  git fetch -q origin main && git reset -q origin/main && git branch -q -u origin/main
)
where py >nul 2>nul && (py hub\server.py --open) || (python hub\server.py --open)
pause
