# UI Automation Skill (統合)

## Trigger
スクショと手順書から、画面上の UI 要素を特定してマウス操作を自動実行したいときに使用します。

## Workflow
**ロジックを持たない薄いオーケストレータ。**

1. **Skill-2 (screen-perception)** で各操作対象の `screen` 座標を確定する。
2. 手順書を MCP-A のアクション列（`move` / `wait` / `click` / `drag` / `type` / `key`）に翻訳する。
3. **実行前にアクション列をユーザーに提示して承認を取る。** 破壊的操作（削除・送信等）は明示的に警告する。
4. MCP-A の `enqueue_actions` → `execute(record=true)` を実行する。
5. 生成された動画 + HTML レポートをユーザーに案内する。

## Safety
- **実行前承認を必須にする。**
- 破壊的操作（削除・送信）を明示警告する。
- FAILSAFE（左上隅移動で中断）と `abort` の中断手段を案内する。
- スクショには機微情報が含まれうるため外部送信しない。
