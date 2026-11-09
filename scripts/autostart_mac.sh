#!/bin/bash
# 맥에 로그인할 때마다 작업 허브를 백그라운드로 자동 실행 (선택)
#   켜기:  bash scripts/autostart_mac.sh
#   끄기:  bash scripts/autostart_mac.sh off
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.seungtae.content-hub.plist"
if [ "$1" = "off" ]; then
  launchctl unload "$PLIST" 2>/dev/null || true
  rm -f "$PLIST"; echo "자동 실행을 껐어요"; exit 0
fi
PY="$(command -v python3)"
mkdir -p "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.seungtae.content-hub</string>
  <key>ProgramArguments</key><array><string>$PY</string><string>$DIR/hub/server.py</string></array>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>EnvironmentVariables</key><dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
  <key>StandardOutPath</key><string>$HOME/Library/Logs/content-hub.log</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/content-hub.log</string>
</dict></plist>
PL
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "자동 실행을 켰어요 → http://localhost:8787  (로그: ~/Library/Logs/content-hub.log)"
