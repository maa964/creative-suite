# Implementation Plan - Refactor Image Editor Structure

既存の `app/` ディレクトリ（画像エディタ）を `apps/image/` に移動し、プロジェクト全体のディレクトリ構成を統一します。

## User Requirements

- `app/` ディレクトリを `apps/image/` に移動する（コードベースのリファクタリング）。
- `launcher` やテストスクリプトが壊れないように修正する。

## Proposed Changes

### 1. Directory Restructuring

#### Move Operations

- Create `apps/image/`
- Move contents of `app/` to `apps/image/`
- Delete `app/` (after verification)

### 2. Code Updates

#### `apps/image/ui/main.py` (Moved file)

- **Path Resolution**: Update `APP_ROOT` logic to correctly find the project root from the new location.
  - Before: `Path(__file__).resolve().parents[2]`
  - After: `Path(__file__).resolve().parents[3]` (since it's now deeper: `apps/image/ui/main.py`)
- **Imports**: Update internal absolute imports.
  - `from app.core...` -> `from apps.image.core...`

#### `apps/image/core/plugin_host.py` (and other core files)

- Update any absolute imports starting with `app.` to `apps.image.`

#### `launcher/main.py`

- Update import paths for the image editor.
  - `from app.ui.main import ...` -> `from apps.image.ui.main import ...`

#### `tools/verify_suite.py`

- Update verification logic to import from the new package location.

#### `tests/test_plugin_host.py`

- Update import paths for testing.

## Verification Plan

### Automated Tests

- Run `tools/verify_suite.py` to ensure all components can still be instantiated.
- Run `pytest` if available/applicable for `tests/test_plugin_host.py`.

### Manual Verification

1. Launch `launcher/main.py`
2. Click "Photo & Paint"
3. Verify the window opens correctly and loads plugins (check logs).

## Risks

- **Plugin Loading**: If plugins assume a specific path relative to the executable, they might break. However, `APP_ROOT` adjustment should cover standard cases.
- **Git History**: Moving files might complicate git history tracking if not done carefully, but `git mv` is preferred (though we might simulate it via file operations if git command is restricted or complex via agent tools). We will purely use file system operations here.
