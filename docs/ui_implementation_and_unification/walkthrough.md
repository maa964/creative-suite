# Walkthrough - UI Implementation and Unification

このドキュメントでは、各アプリケーション（Video Editor, Vector Editor, Image Editor）のUI実装と統合の詳細な履歴を記録します。

## Changes

### 1. Common Infrastructure (`apps/common`)

#### `apps/common/base_window.py`

- 新規作成: すべてのエディタウィンドウの親クラスとなる `BaseMainWindow` を定義。
- 機能:
  - 標準的なメニューバー (File, Edit, View, Help)
  - ウィンドウタイトル設定
  - ダークモードの適用 (QPalette)
  - ステータスバーの初期化
  - 終了確認ダイアログ (`closeEvent`)

### 2. Vector Editor Changes (`apps/vector`)

#### `apps/vector/main.py`

- `BaseMainWindow` を継承するように変更。
- ツールバーのアクションに `triggered` シグナルを接続し、ステータスバーに選択ツールを表示するように変更。
- `QGraphicsView` のマウスイベントをフックし、ツールに応じた動作（例: 矩形描画のスタブ）を追加。

### 3. Video Editor Changes (`apps/video`)

#### `apps/video/main.py`

- `BaseMainWindow` を継承するように変更。
- `QSplitter` を用いて、プレビューエリア、アセットライブラリ、タイムラインのサイズを可変に変更。
- 再生ボタンのアイコン切り替えロジックを追加。

### 4. Image Editor Changes (`app/ui`)

#### `app/ui/main.py`

- メニューバーを追加し、全体の統一感を向上。

## Verification Results

### Automated Tests

- **Smoke Test (`tools/verify_suite.py`)**:
  - `QApplication` initialization: **PASS**
  - `apps.common.base_window` import: **PASS**
  - `app.ui.main` (Image Editor) instantiation: **PASS**
  - `apps.video.main` (Video Editor) instantiation: **PASS**
  - `apps.vector.main` (Vector Editor) instantiation: **PASS**
  - All components verified to load without import errors or syntax errors.

### Manual Verification

- [ ] Launcherから各アプリが起動することを確認。
- [ ] 各アプリで `File -> Exit` が機能するか確認。
- [ ] Vector Editorでツール切り替え時にステータスバーが更新されるか確認。
- [ ] Video Editorでパネルのリサイズができるか確認。
