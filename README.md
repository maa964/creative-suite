# CreativeStudio Prototype (Git-ready scaffold)

商用化を視野に入れた「Adobe Suite + CLIP STUDIO 互換 統合アプリ」の最小プロトタイプリポジトリ雛形です。

## 目的
- PySide6 ベースの最小ランチャー（UI）を提供。
- プラグインスキャンの仕組み・サンプルプラグインを含む。
- 商用配布前のライセンスチェックを行いやすい構成にしています。

## 使い方（ローカルで動かす）
```bash
python -m venv .venv
. .venv/bin/activate      # Windows: .\.venv\Scripts\activate
pip install -r requirements.txt || pip install PySide6
python -m app.ui.main
```

## 構成
- `app/ui/main.py` : 起動用の最小アプリ（エラーハンドリングあり）
- `plugins/sample_plugin` : サンプルプラグイン（plugin.json + register 関数）
- `pyproject.toml` : パッケージ設定
- `LICENSE` : MIT ライセンス（ひな形）

## ライセンスと商用メモ
このリポジトリは MIT ライセンスで配布しています。ただし実際に外部 OSS を組み込む際は、各ライブラリのライセンス条件（特に GPL / LGPL 等）を法務で確認してください。

## 備考
- この雛形には `use context7` を含めています（要望に基づくメモ）。

---
Generated for masahiro — enjoy building! 🎨
