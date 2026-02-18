# Implementation Plan - Extract Common Components

各アプリケーションで重複しているUIスタイル定義やロギング設定、構成管理機能を `apps/common` および新規作成する `apps/core` パッケージに集約し、保守性を向上させます。

## User Requirements

- 共通のUI部品や設定管理を `core/` や `common/` にまとめる。
- コードの重複を排除し、統一感を強化する。

## Proposed Changes

### 1. Common Theme Management (`apps/common`)

各アプリ（Launcher, Image, Video, Vector）で個別に定義されているダークモードのパレット設定を一元管理します。

#### [NEW] `apps/common/theme.py`

- `apply_dark_theme(app: QApplication)` 関数を定義。
- 統一されたカラーパレット（`QPalette`）とスタイルシート（`QSS`）を提供。

### 2. Core Utilities (`apps/core`)

アプリケーションの基盤となる設定管理とロギング機能を実装します。

#### [NEW] `apps/core/__init__.py`

- パッケージ初期化。

#### [NEW] `apps/core/logging.py`

- アプリケーションごとのログファイルを適切に設定する `setup_logging(app_name: str)` 関数を提供。
- 標準出力とファイル出力のフォーマットを統一。

#### [NEW] `apps/core/config.py`

- 設定情報の読み込み・保存を行う `ConfigManager` クラス。
- JSONファイルベースの簡易設定管理（例：ウィンドウサイズ、前回開いたファイルなど）。

### 3. Integration

各アプリケーションの初期化プロセスを修正し、共通コンポーネントを使用するように変更します。

#### `launcher/main.py`

- `theme.apply_dark_theme` を使用。
- `setup_logging("launcher")` を使用。

#### `apps/common/base_window.py`

- `BaseMainWindow` 内でのテーマ設定ロジックを `theme.apply_dark_theme` に置き換え（またはコンストラクタで自動適用される仕組みに依存）。
- ウィンドウサイズや位置の保存・復元に `ConfigManager` を利用（Optional）。

#### `apps/image/ui/main.py`

- 独自のロギング設定を `apps.core.logging` に置き換え。

## Verification Plan

### Automated Tests

- 新規モジュール (`apps.common.theme`, `apps.core.logging`, `apps.core.config`) のインポートテスト。
- `verify_suite.py` の実行によるリグレッションテスト。

### Manual Verification

1. **Launcher**: 起動し、ダークテーマが適用されているか確認。ログファイルが生成されているか確認。
2. **Video/Vector**: 各アプリを起動し、同様にテーマとログを確認。
3. **Image**: 既存の画像エディタが正常に起動し、ログが出力されるか確認。

## Directory Structure Strategy

- `apps/common/`: UI関連（テーマ、ウィジェット、基底ウィンドウ）
- `apps/core/`: ロジック・インフラ関連（設定、ログ、プラグイン機構）
