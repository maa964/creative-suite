# Creative Suite v0.50

Creative Suiteは、OSSベースのクリエイティブツール統合環境です。
Adobe Creative Cloudのような統合体験を、オープンソース技術（Python, Qt, MLT, SVG）を用いて提供することを目指しています。

v0.50では、以下の3つの主要ツールへアクセスできる**統合ランチャー**が導入されました。

## 🌟 主な機能

### 🚀 統合ランチャー (Unified Launcher)
- すべてのツールへのアクセスを提供するダッシュボード
- モダンなダークモードUI (PySide6)

### 🖼️ Photo & Paint (画像編集)
旧「CreativeStudio」プロトタイプを統合。
- レイヤーベースの編集
- Pythonによるプラグイン拡張
- 豊富な画像処理フィルター

### 🎬 Video Editor (動画編集) - *Preview*
- タイムライン型ノンリニア編集UI
- MLT Framework (予定) をバックエンドとした動画処理
- *v0.50現在はUIスカフォールド（プロトタイプ）段階です*

### ✒️ Vector Draw (ベクター編集) - *Preview*
- SVGベースのドローイングツール
- パス操作、シェイプ作成
- *v0.50現在はUIスカフォールド（プロトタイプ）段階です*

## 🛠️ インストールと起動

このプロジェクトは `poetry` を使用して依存関係を管理しています。

### 必要条件
- Python 3.12+
- Poetry

### セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/your-org/creative-suite.git
cd creative-suite

# 依存関係のインストール
poetry install
```

### 起動方法

統合ランチャーを起動します：

```bash
poetry run python launcher/main.py
```

## 🗺️ ロードマップ

- **v0.6.0**: Video/Vectorエディタの基本機能実装 (MLT/svgバックエンドの本格統合)
- **v0.7.0**: AI機能の統合 (Stable Diffusion, Whisper等のローカル実行)
- **v1.0.0**: マルチプラットフォームバイナリ配布

## 🤝 コントリビューション

Pull Requestは歓迎します！
新しい機能の提案やバグ報告は Issues にてお願いします。

## 📄 ライセンス

MIT License
