# Mouse Control Skill

## Trigger
デスクトップアプリのスクショと手順から、マウス自動操作・録画・再現を求められたときに使用します。

## Workflow
1. `get_screen_info` で画面情報を取得する。
2. スクショ上の座標を推定し、`screen_x = round(shot_x * screen_w / shot_w)` で実画面にスケーリングする。
3. 手順を `move / wait / click / drag / type / key / scroll` に変換し、安定化のため `wait` を挟む。
4. 実行前にユーザー承認を取り、必要なら `execute(dry_run=True)` で確認する。
5. `enqueue_actions` → `execute(record=True, name=...)` を実行する。
6. 結果の `html_path` / `video_path` を案内する。

## Safety
- 実行前承認を必須にする。
- 破壊的操作（削除・送信）を明示警告する。
- FAILSAFE（左上隅）と `abort` の中断手段を案内する。
