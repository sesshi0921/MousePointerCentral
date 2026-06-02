# MousePointerCentral

マウスポインタ操作用 MCP サーバー + 画面知覚 MCP サーバーの実装です。
録画入力は macOS / Windows / Linux の各 OS をサポートしています。

## アーキテクチャ

```
┌──────────────────────┐     ┌──────────────────────┐
│  MCP-A: mouse-control │     │ MCP-B: screen-percept │
│  (アクチュエータ)      │     │ (ウィンドウ/要素検出)  │
└──────────┬───────────┘     └──────────┬───────────┘
           │                            │
┌──────────┴──────────┐  ┌──────────────┴────────────┐
│ Skill-1: mouse-ctrl  │  │ Skill-2: screen-perception │
└──────────┬──────────┘  └──────────────┬────────────┘
           └───────────┬────────────────┘
              ┌────────┴─────────┐
              │ Skill-3: ui-auto  │
              └──────────────────┘
```

## セットアップ

### 1. 依存インストール

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

# CV 機能（OCR / 輪郭検出等）を使う場合
pip install -e ".[cv]"

# macOS アクセシビリティを使う場合
pip install -e ".[macos]"

# Windows アクセシビリティを使う場合
pip install -e ".[windows]"
```

### 2. ffmpeg のインストール

- macOS: `brew install ffmpeg`
- Windows: `choco install ffmpeg` または公式配布をPATHに追加
- Linux(Ubuntu): `sudo apt-get install ffmpeg`

### 3. Tesseract のインストール（OCR を使う場合）

- macOS: `brew install tesseract tesseract-lang`
- Windows: [UB-Mannheim installer](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux(Ubuntu): `sudo apt-get install tesseract-ocr tesseract-ocr-jpn`

### 4. OSの画面収録・アクセシビリティ権限

- macOS: システム設定 > プライバシーとセキュリティ > 画面収録 で Python/ターミナルを許可。
  アクセシビリティツリー取得のためにアクセシビリティ権限も付与してください。
- Windows: 設定 > プライバシー > 画面キャプチャ関連の権限を許可
- Linux: X11 セッションで実行、必要なら DISPLAY を設定

### 5. MCP クライアント登録

`.mcp.json` に `mouse` (MCP-A) と `screen-percept` (MCP-B) の2サーバーが定義されています。

## 主要ツール

### MCP-A: mouse-control

- `get_screen_info`
- `enqueue_actions`
- `peek_queue`
- `clear_queue`
- `start_recording`
- `stop_recording`
- `execute`
- `abort`
- `get_status`

### MCP-B: screen-percept

- `capture_screen` – フルスクリーンショット取得
- `get_active_window` – アクティブウィンドウの領域取得
- `focus_window` – 指定ウィンドウを前面化
- `get_region` – 任意矩形の画像取得
- `get_accessibility_tree` – OS アクセシビリティツリー取得（最優先）
- `preprocess_region` – 画像前処理（拡大・ノイズ除去）
- `detect_candidates` – 4 検出器のアンサンブルによる UI 要素候補検出
- `refine_point` – クリック座標の補正

## 環境変数

- `MOUSE_MCP_OUTPUT_DIR` (default: `./output`)
- `MOUSE_MCP_FFMPEG` (default: `ffmpeg`)
- `MOUSE_MCP_FPS` (default: `15`)
- `MOUSE_MCP_FAILSAFE` (default: `true`)
- `MOUSE_MCP_PAUSE` (default: `0.1`)
- `MOUSE_MCP_MAX_QUEUE` (default: `500`)

## 評価 (§10)

```bash
python -m fixtures.evaluate
```

`fixtures/screenshots/` にスクショ、`fixtures/labels/` に正解ラベルを配置し、
再現率 ≥ 95%、クリック成功率 ≥ 90% を目標とします。

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
