# Walkthrough - Refactor Image Editor Structure

このドキュメントでは、画像エディタのディレクトリ再構成の履歴を記録します。

## Changes

### Directory Move

- **New Location**: `apps/image/`
- **Old Location**: `app/`
- **Action**: Renamed/Moved contents to align with project structure.

### Detailed Updates

#### `apps/image/ui/main.py`

- `APP_ROOT`: Updated path traversal depth to account for new directory level.
- Imports: Updated internal references.

#### `launcher/main.py`

- Import Path: Updated `app.ui.main` to `apps.image.ui.main`.

#### `tools/verify_suite.py`

- Import Path: Updated test target.

## Verification Results

### Automated Tests

- [x] Run `tools/verify_suite.py` and confirm all checks pass.
  - Result: **ALL CHECKS PASSED**
  - Confirmed `app/` no longer exists.
  - Confirmed ImageEditor instantiation from `apps.image`.

### Manual Verification

- [ ] Confirm `Photo & Paint` runs from launcher.
- [ ] Confirm plugins are still loaded (check log output).
