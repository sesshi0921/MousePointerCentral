# Screen Perception Skill

## Trigger
画面上の UI 要素の座標を取得したいとき、またはスクショから操作対象を特定したいときに使用します。

## Workflow
1. `capture_screen` でフルスクリーンショットを取得する。
2. 対象が特定ウィンドウなら `focus_window(title)` で前面化し領域を取得、そうでなければ `get_active_window` を使う。
3. `get_region` で操作領域を確定する（`is_fullscreen` なら全画面をそのまま使用）。
4. **`get_accessibility_tree` を最優先で試す。**取得できた場合は正確な座標が得られるため、ステップ 5〜7 をスキップして座標確定。
5. `preprocess_region` で前処理画像を取得し、Claude が目視確認して対象要素を特定・粗座標を推定する。
6. `detect_candidates` の候補リストと突き合わせ、`refine_point` で最終座標を補正する。
7. `to_vision=true` や `snapped=false` の要素は **確信度を添えてユーザー確認** を促す。
8. 返す座標は必ず `coord_space:"screen"` に変換する。

## Coordinate Spaces
- `screen`: 仮想デスクトップ左上が原点（MCP-A が消費する最終座標）
- `crop`: クロップ画像内の座標
- `upscaled`: 前処理後の拡大画像座標

## Safety
- スクショには機微情報が含まれうるため、画像・OCR テキストを外部に送信しない。
- アクセシビリティ権限が必要。権限付与手順は README を参照。
