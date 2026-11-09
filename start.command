#!/bin/bash
# 맥: 더블클릭하면 작업 허브를 켭니다 (처음 한 번은 깃허브 연결도 같이 해요)
cd "$(dirname "$0")" || exit 1
REPO_URL="https://github.com/kst104/github.com-new.git"

if ! command -v git >/dev/null 2>&1; then
  echo "git 이 없어요. 설치 창이 뜨면 '설치'를 눌러 주세요. 끝나면 이 파일을 다시 더블클릭하세요."
  xcode-select --install
  read -r -p "엔터를 누르면 닫혀요" _; exit 1
fi

if [ ! -d .git ]; then
  echo "▶ 이 폴더를 깃허브 저장소와 연결하는 중…"
  git init -q -b main
  git remote add origin "$REPO_URL"
  git fetch -q origin main && git reset -q origin/main && git branch -q -u origin/main
  echo "  연결 완료"
fi

if [ -z "$(git config user.name)" ]; then
  git config user.name "$(scutil --get ComputerName 2>/dev/null || hostname)"
  git config user.email "kst104@users.noreply.github.com"
fi

# 깃허브에 올리기(push) 권한 확인
if command -v gh >/dev/null 2>&1; then
  if ! gh auth status >/dev/null 2>&1; then
    echo "▶ 깃허브 로그인이 필요해요. 브라우저가 열리면 승인해 주세요."
    gh auth login -h github.com -p https -w && gh auth setup-git
  fi
else
  if ! git ls-remote --exit-code -q origin >/dev/null 2>&1; then
    echo "⚠ 깃허브에 접속하지 못했어요. 인터넷 연결을 확인해 주세요."
  fi
  echo "ℹ 올리기(push)가 안 되면 터미널에서:  brew install gh && gh auth login && gh auth setup-git"
fi

echo "▶ 작업 허브를 켜는 중… (이 창을 닫으면 허브도 꺼져요)"
exec python3 hub/server.py --open
