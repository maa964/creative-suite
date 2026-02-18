# Walkthrough - Extract Common Components

このドキュメントでは、UI部品や設定管理の共通化の履歴を記録します。

## Changes

### 1. Common Theme Management (`apps/common`)

#### `apps/common/theme.py`

- 新規作成: アプリケーション全体のダークテーマを一元管理するモジュール。
- `apply_dark_theme`: `QAppliction` にスタイルを適用するヘルパー関数。

### 2. Core Utilities (`apps/core`)

#### `apps/core/logging.py`

- 新規作成: アプリケーション名に応じたログファイルを設定するモジュール。

#### `apps/core/config.py`

- 新規作成: 設定値をJSONファイルで管理するクラス。

### 3. Integration Changes

#### `launcher/main.py`

- テーマ適用とロギング設定を共通モジュールに置き換え。

#### `apps/common/base_window.py`

- テーマ設定を削除し、`QApplication` 全体への適用を前提とするように変更（または呼び出し）。

#### `apps/image/ui/main.py`

- ロギング設定を共通化。

## Verification Results

### Manual Test

- [x] ランチャー起動時にテーマが適用されているか。
  - ランチャーおよび各アプリ起動時のダーク系テーマを確認。
- [x] 各アプリのログが生成されているか。
  - `launcher.log` が生成されることを確認。
  - `image_editor.log` が生成されることを確認。
- [x] `tools/verify_suite.py` のパスを確認。
