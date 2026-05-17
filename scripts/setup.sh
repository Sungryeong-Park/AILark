#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_PATH="$HOME/Library/LaunchAgents/com.ailark.run.plist"

echo "=== AILark 설정 시작 ==="

# 1. 가상환경 생성
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "[1/4] 가상환경 생성 중..."
    python3 -m venv "$PROJECT_DIR/.venv"
else
    echo "[1/4] 가상환경 이미 존재, 건너뜀"
fi

# 2. 패키지 설치
echo "[2/4] 패키지 설치 중..."
"$PROJECT_DIR/.venv/bin/pip" install -q -r "$PROJECT_DIR/requirements.txt"

# 3. .env 생성
echo "[3/4] API 키 설정"
if [ -f "$PROJECT_DIR/.env" ]; then
    echo "      .env 파일이 이미 존재합니다. 덮어쓰시겠습니까? (y/N)"
    read -r overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "      건너뜀"
    else
        printf "GEMINI_API_KEY 입력: "
        read -r api_key
        echo "GEMINI_API_KEY=$api_key" > "$PROJECT_DIR/.env"
        echo "      .env 저장 완료"
    fi
else
    printf "GEMINI_API_KEY 입력: "
    read -r api_key
    echo "GEMINI_API_KEY=$api_key" > "$PROJECT_DIR/.env"
    echo "      .env 저장 완료"
fi

# 4. launchd 등록
echo "[4/4] 자동 실행 등록 중..."
chmod +x "$PROJECT_DIR/scripts/run_ailark.sh"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ailark.run</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$PROJECT_DIR/scripts/run_ailark.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <array>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
    </array>
</dict>
</plist>
EOF

launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

echo ""
echo "=== 설정 완료 ==="
echo "매주 월~금 오전 8시에 자동 실행됩니다."
echo "리포트 저장 위치: $PROJECT_DIR/reports/"
