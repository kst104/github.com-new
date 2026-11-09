#!/bin/bash
# 리눅스/기타: ./start.sh
cd "$(dirname "$0")" || exit 1
exec python3 hub/server.py --open "$@"
