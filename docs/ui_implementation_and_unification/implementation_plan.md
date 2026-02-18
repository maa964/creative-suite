# Implementation Plan - UI Implementation and Unification

統合ランチャーから起動される各アプリケーション（Video Editor, Vector Editor, Photo & Paint）について、統一された操作感と最低限の機能（ファイル操作のモックなど）を実装する計画です。

## User Requirements

- 各エディタ（Video, Vector）のメインウィンドウが表示され、最低限の操作（ファイルの開閉など）ができる状態にする。
- プロジェクト全体の統一感を出す。

## Proposed Changes

### 1. Common Infrastructure (`apps/common`)

各アプリケーションで共通して利用する基底クラスを作成し、統一されたルック＆フィールと基本機能を提供します。

#### [NEW] `apps/common/base_window.py`

- **Class `BaseMainWindow(QMainWindow)`**
  - 共通の初期化処理（ウィンドウサイズ、タイトル、アイコン設定）
  - **Menu Bar**:
    - `File`: New, Open, Save, Save As, Exit
    - `Help`: About
  - **Method Stubs**: `on_new_file`, `on_open_file`, `on_save_file` 等のオーバーライド用メソッド
  - **Theme**: ダークモードパレットの適用ロジックをここに集約

### 2. Vector Editor Enhancements (`apps/vector`)

#### [MODIFY] `apps/vector/main.py`

- `BaseMainWindow` を継承するように変更
- **Tool Logic**:
  - 列挙型 `EditorMode` (SELECT, PEN, RECT, CIRCLE) を導入
  - ツールバーのアクションがトリガーされた際にモードを切り替えるロジックを実装
  - ステータスバーに現在のモードを表示
- **File I/O**:
  - `on_open_file`: ファイルダイアログを表示し、SVGファイルのパスを取得（読み込みロジックはスタブ）
  - `on_save_file`: ファイルダイアログを表示（書き出しロジックはスタブ）

### 3. Video Editor Enhancements (`apps/video`)

#### [MODIFY] `apps/video/main.py`

- `BaseMainWindow` を継承するように変更
- **Layout Refinement**:
  - スプリッター（`QSplitter`）を導入し、パネルサイズを可変にする
- **Control Logic**:
  - 再生/一時停止ボタンのトグル動作（アイコン切り替え）
  - シークバー操作時のログ出力（プレビュー更新の準備）
- **File I/O**:
  - `on_open_file`: プロジェクトファイル（`.mlt` 等）またはメディアファイルのインポート動作のスタブ

### 4. Image Editor (Existing App) Integration (`app/ui`)

#### [MODIFY] `app/ui/main.py`

- 既存の `MainWindow` にメニューバーを追加
- `File -> Exit` でアプリケーションを閉じる（ランチャーは起動したままにするため、`sys.exit` ではなく `close()` で済むか確認）

## Verification Plan

### Automated Tests

- 新規作成する `apps/common` モジュールのインポートテスト
- 各 `main.py` がエラーなくインスタンス化できるかのスモークテスト

### Manual Verification

1. `launcher/main.py` を実行
2. **Video Editor** を起動
   - メニューバーが表示されているか確認
   - `File -> Open` でダイアログが出るか確認
   - スプリッターでレイアウト調整ができるか確認
3. **Vector Editor** を起動
   - ツールバーのボタンを押して、ステータスバーの表示が変わるか確認
4. **Photo & Paint** を起動
   - メニューバーが表示されているか確認

## Constraints & Risks

- **Image Editor**: 既存コードがプラグインホストとしての機能しかないため、実際の画像編集機能はまだない（今回のスコープ外）。
- **MLT/SVG Backend**: バックエンドロジックは全てモック/スタブとする。
