#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="$HOME/.claude/mcp-servers/mouse-mcp"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SETTINGS="$HOME/.claude/settings.json"
OUTPUT_DIR="$HOME/Documents/mouse-mcp"

echo "[1/4] ソースをコピー中: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR/src"
cp -r "$SCRIPT_DIR/src/mouse_mcp" "$INSTALL_DIR/src/"
cp "$SCRIPT_DIR/pyproject.toml" "$INSTALL_DIR/"

echo "[2/4] Python 3.10+ を検索中"
PYTHON3=""
for cmd in python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$cmd" &>/dev/null; then
    ver=$("$cmd" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null || echo "False")
    if [ "$ver" = "True" ]; then
      PYTHON3="$cmd"
      break
    fi
  fi
done
# Homebrew fallback
if [ -z "$PYTHON3" ]; then
  for p in /opt/homebrew/bin/python3* /usr/local/bin/python3*; do
    [[ "$p" == *-config ]] && continue
    if [ -x "$p" ]; then
      ver=$("$p" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null || echo "False")
      if [ "$ver" = "True" ]; then PYTHON3="$p"; break; fi
    fi
  done
fi
if [ -z "$PYTHON3" ]; then
  echo "エラー: Python 3.10 以上が見つかりません" >&2; exit 1
fi
echo "  使用 Python: $PYTHON3 ($($PYTHON3 --version))"

echo "[3/5] venv作成・パッケージインストール中"
"$PYTHON3" -m venv --clear "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install --quiet "$INSTALL_DIR"

PYTHON="$INSTALL_DIR/.venv/bin/python"

echo "[4/5] ~/.claude/settings.json を更新中"
mkdir -p "$HOME/.claude"
"$PYTHON" - "$SETTINGS" "$PYTHON" "$OUTPUT_DIR" <<'PYEOF'
import json, sys, os

settings_path, python_path, output_dir = sys.argv[1], sys.argv[2], sys.argv[3]

if os.path.exists(settings_path):
    with open(settings_path, encoding="utf-8") as f:
        settings = json.load(f)
else:
    settings = {}

settings.setdefault("mcpServers", {})
settings["mcpServers"]["mouse"] = {
    "command": python_path,
    "args": ["-m", "mouse_mcp.server"],
    "env": {
        "MOUSE_MCP_OUTPUT_DIR": output_dir
    }
}

with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
    f.write("\n")
PYEOF

echo "[5/5] 完了"
echo "  インストール先: $INSTALL_DIR"
echo "  録画出力先:     $OUTPUT_DIR"
echo "  Claude Code を再起動すると mouse MCP サーバーが有効になります"
