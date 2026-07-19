#!/bin/bash
cd "$(dirname "$0")"
python3 generate.py || exit 1
cd clipboard_generated
python3 -m http.server 8000 &
sleep 1
open http://localhost:8000
wait
