#!/data/data/com.termux/files/usr/bin/sh
set -eu
cd "$(dirname "$0")/../control-plane"
python -m unittest -v
