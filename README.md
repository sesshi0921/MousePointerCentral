# MousePointerCentral

マウスポインタ操作用 MCP サーバー実装です。
録画入力は macOS / Windows / Linux の各 OS をサポートしています。

## セットアップ

### 1. 依存インストール

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. ffmpeg のインストール

- macOS: `brew install ffmpeg`
- Windows: `choco install ffmpeg` または公式配布をPATHに追加
- Linux(Ubuntu): `sudo apt-get install ffmpeg`

### 3. OSの画面収録権限

- macOS: システム設定 > プライバシーとセキュリティ > 画面収録 で Python/ターミナルを許可
- Windows: 設定 > プライバシー > 画面キャプチャ関連の権限を許可
- Linux: X11 セッションで実行、必要なら DISPLAY を設定

### 4. MCP クライアント登録

MCP クライアントから `mouse_mcp.server:mcp` をサーバーエントリとして登録します。

## 主要ツール

- `get_screen_info`
- `enqueue_actions`
- `peek_queue`
- `clear_queue`
- `start_recording`
- `stop_recording`
- `execute`
- `abort`
- `get_status`

## 環境変数

- `MOUSE_MCP_OUTPUT_DIR` (default: `./output`)
- `MOUSE_MCP_FFMPEG` (default: `ffmpeg`)
- `MOUSE_MCP_FPS` (default: `15`)
- `MOUSE_MCP_FAILSAFE` (default: `true`)
- `MOUSE_MCP_PAUSE` (default: `0.1`)
- `MOUSE_MCP_MAX_QUEUE` (default: `500`)

## スモークテスト（dry run）

```python
from mouse_mcp.server import enqueue_actions, execute

enqueue_actions([
    {"type": "move", "to": [100, 200]},
    {"type": "wait", "seconds": 0.2},
    {"type": "click", "at": [100, 200]},
])
print(execute(record=False, dry_run=True))
```
