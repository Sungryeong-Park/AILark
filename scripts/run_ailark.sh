#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

DAY=$(date +%u)   # 1=Mon ... 7=Sun
HOUR=$(date +%H)  # 00-23
TODAY=$(date +%Y-%m-%d)

WEEKDAY=$((DAY - 1))
MONDAY=$(date -v -${WEEKDAY}d +%m%d)
SUNDAY=$(date -v +$((6 - WEEKDAY))d +%m%d)
REPORT_PATH="$PROJECT_DIR/reports/${MONDAY}-${SUNDAY}/${TODAY}_AILark_Brief.md"

# 평일 + 오전 8시 이후 + 오늘 리포트 미존재 시에만 실행
if [ "$DAY" -le 5 ] && [ "$HOUR" -ge 9 ] && [ ! -f "$REPORT_PATH" ]; then
    "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/src/main.py"
fi
