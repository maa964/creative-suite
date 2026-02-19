# Creative Suite v0.7.0

Creative Suiteは、OSSベースのクリエイティブツール統合環境です。
Adobe Creative Cloudのような統合体験を、オープンソース技術（Python, Qt, SVG）を用いて提供することを目指しています。

v0.7.0では、**AI Studio** が追加されました。Text-to-Image生成、音声文字起こし（Whisper）、背景除去をHugging Face API / ローカル実行の両方で利用できます。

## 主な機能

### 統合ランチャー (Unified Launcher)

- すべてのツールへのアクセスを提供するダッシュボード
- モダンなダークモードUI (PySide6)

### Photo & Paint (画像編集)

- レイヤーベースの編集
- Pythonによるプラグイン拡張（プラグインホスト / セキュリティポリシー管理）
- 豊富な画像処理フィルター
- セキュリティ: サブプロセス分離、Docker サンドボックスポリシー

### Video Editor (動画編集)

- PySide6 QtMultimedia バックエンドによる動画プレビュー再生
- インタラクティブなタイムライン（クリップ表示・ドラッグ&ドロップ・トリム）
- プロジェクトビン（メディアファイルのインポート・管理）
- トランスポートコントロール（Play/Pause/Stop・シークバー・タイムコード表示）
- マルチトラック対応（ビデオ2トラック + オーディオ2トラック）
- タイムラインズーム

### Vector Draw (ベクター編集)

- SVGベースのドローイングツール（矩形・楕円・線・ペン）
- インタラクティブな選択・移動・リサイズ
- プロパティパネル（塗り・線色・線幅・位置・サイズ）
- SVGファイルの読み込み/書き出し
- Undo/Redo対応
- ズーム（マウスホイール / メニュー）

### AI Studio (AI機能)

- **Text-to-Image**: Stable Diffusion系モデルによるテキストからの画像生成
  - プロンプト / ネガティブプロンプト / サイズ / ステップ数 / CFG / シード指定
  - 生成画像のプレビューとPNG保存
- **Speech-to-Text**: Whisperによる音声ファイルの文字起こし
  - モデルサイズ選択（tiny〜large）
  - 言語自動検出 / 手動指定
  - テキスト出力とクリップボードコピー
- **Background Removal**: 画像の背景自動除去
  - Alpha Mattingオプション（高品質モード）
  - Before/After プレビュー
- **バックエンド切り替え**: Hugging Face Inference API / ローカル実行を設定で切替可能
- **設定パネル**: APIキー管理、ローカル依存ライブラリの状況表示

## インストールと起動

このプロジェクトは `poetry` を使用して依存関係を管理しています。

### 必要条件

- Python 3.12+
- Poetry
- PySide6, Pillow, NumPy, defusedxml, huggingface-hub

### セットアップ

```bash
# リポジトリのクローン
git clone https://github.com/your-org/creative-suite.git
cd creative-suite

# 依存関係のインストール（API モードのみ）
poetry install

# ローカルAI実行も利用する場合（GPU推奨）
pip install .[ai-local]
```

### 起動方法

統合ランチャーを起動します：

```bash
poetry run python launcher/main.py
```

### ビルド (Windows)

PowerShellスクリプトでテスト・Lint・パッケージングを実行します：

```powershell
.\build.ps1
```

## ロードマップ

- ~~**v0.6.0**: Video/Vectorエディタの基本機能実装~~ **完了**
- ~~**v0.7.0**: AI機能の統合 (Stable Diffusion, Whisper等)~~ **完了**
- **v1.0.0**: マルチプラットフォームバイナリ配布
- **v1.1.0**: エフェクト＆トランジション — Videoエディタにトランジション/フィルター、Vectorエディタにグラデーション/パターン塗り
- **v1.2.0**: プロジェクト連携 — アプリ間データ受け渡し（画像→ベクター→動画タイムライン等）
- **v1.3.0**: プラグインマーケットプレイス — サーバー連携プラグインストアの本番化
- **v2.0.0**: コラボレーション＆クラウド同期 — リアルタイム共同編集、クラウドプロジェクト保存

## コントリビューション

Pull Requestは歓迎します！
新しい機能の提案やバグ報告は Issues にてお願いします。

## ライセンス

MIT License
