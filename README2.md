CreativeStudioは、プラグインアーキテクチャを採用した拡張可能な画像編集アプリケーションのプロトタイプです。
PySide6ベースのGUIアプリケーション、FastAPIによるプラグインストアサーバー、そしてセキュアなプラグイン実行環境を提供します。

## 📋 目次

- [主な機能](#主な機能)
- [プロジェクト構成](#プロジェクト構成)
- [環境要件](#環境要件)
- [セットアップ](#セットアップ)
- [使い方](#使い方)
  - [GUIアプリケーションの起動](#guiアプリケーションの起動)
  - [プラグインストアサーバーの起動](#プラグインストアサーバーの起動)
  - [プラグインの開発](#プラグインの開発)
- [API仕様](#api仕様)
- [セキュリティ](#セキュリティ)
- [ライセンス](#ライセンス)

## 主な機能

### 🎨 GUIアプリケーション
- **PySide6ベースのモダンUI**: 直感的な操作画面
- **プラグインシステム**: 動的なプラグイン読み込みと管理
- **セキュアな実行環境**: サンドボックス化されたプラグイン実行
- **ログ管理**: 詳細なデバッグログ（app.log）

### 🏪 プラグインストア
- **FastAPIベースのRESTful API**: 高速で信頼性の高いバックエンド
- **プラグイン管理**: アップロード、承認、配布の一元管理
- **電子署名**: cryptographyによる安全な署名検証
- **認証システム**: OAuth2 + APIキーによる二重認証
- **セキュリティスキャン**: アップロード時の自動静的解析

### 🔌 プラグインシステム
- **簡単な開発**: シンプルなJSON設定とPythonコード
- **リソース制限**: メモリ、CPU、ネットワークの制御
- **タイムアウト管理**: 無限ループやハングアップの防止
- **サンプルプラグイン同梱**: すぐに始められる開発テンプレート

## プロジェクト構成

```
creative-suite/
├── app/                      # メインアプリケーション
│   ├── core/                 # コア機能
│   │   ├── plugin_host.py    # プラグインホスト（サブプロセス実行）
│   │   ├── plugin_loader.py  # プラグイン読み込み
│   │   ├── policy_manager.py # セキュリティポリシー管理
│   │   └── canvas.py         # キャンバス描画エンジン
│   ├── ui/                   # UIコンポーネント
│   │   ├── main.py           # アプリケーションエントリーポイント
│   │   └── main_window.py    # メインウィンドウ
│   └── ipc/                  # プロセス間通信
│
├── server/                   # プラグインストアサーバー
│   └── app/
│       ├── main.py           # FastAPIアプリケーション
│       ├── auth.py           # 認証機能
│       ├── signing_utils.py  # 電子署名ユーティリティ
│       └── security_scan.py  # セキュリティスキャナー
│
├── plugins/                  # プラグインディレクトリ
│   ├── sample_plugin/        # サンプルプラグイン
│   │   ├── plugin.json       # マニフェストファイル
│   │   └── plugin.py         # プラグインコード
│   └── sample_plugin_ai/     # AI機能サンプル
│
├── cli/                      # コマンドラインツール
│   └── sign.py               # マニフェスト署名CLI
│
├── config/                   # 設定ファイル
│   └── policies.json         # プラグインセキュリティポリシー
│
├── docs/                     # ドキュメント
│   └── plugin_api_openapi.yaml  # OpenAPI仕様
│
├── data/                     # データストレージ（自動生成）
│   └── plugins.json          # プラグインメタデータ
│
├── pyproject.toml            # Poetryプロジェクト設定
├── requirements.txt          # pip依存関係
└── README.md                 # このファイル
```

## 環境要件

- **Python**: 3.12以上（3.13未満）
- **OS**: Windows / macOS / Linux
- **メモリ**: 最低4GB推奨
- **依存関係**:
  - PySide6 (>6.5)
  - FastAPI (^0.119.1)
  - Pillow, NumPy
  - cryptography, pydantic
  - その他（pyproject.toml参照）

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd creative-suite
```

### 2. 依存関係のインストール

#### pipを使用する場合

```bash
python -m pip install -r requirements.txt
```

#### Poetryを使用する場合（推奨）

```bash
poetry install
poetry shell
```

### 3. ディレクトリ構造の確認

初回起動時に以下のディレクトリが自動生成されます：
- `data/` - プラグインメタデータ保存先
- `server/app/keys/` - 署名鍵と APIキー保存先

## 使い方

### GUIアプリケーションの起動

```bash
# 直接起動
python -m app.ui.main

# または Poetry経由
poetry run python -m app.ui.main
```

起動すると：
1. メインウィンドウが表示されます
2. `plugins/`ディレクトリ内のプラグインが自動検出されます
3. プラグイン登録結果が`app.log`に記録されます

### プラグインストアサーバーの起動

#### 開発環境

```bash
uvicorn server.app.main:app --reload --port 8001
```

#### 本番環境

```bash
uvicorn server.app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

サーバー起動後、以下のエンドポイントにアクセスできます：
- `http://localhost:8001/plugins` - プラグイン一覧
- `http://localhost:8001/docs` - Swagger UI（API仕様書）

### プラグインの開発

#### 1. プラグインディレクトリの作成

```bash
mkdir -p plugins/my_plugin
cd plugins/my_plugin
```

#### 2. plugin.jsonの作成

```json
{
  \"name\": \"my_plugin\",
  \"entry\": \"plugins.my_plugin.plugin:register\",
  \"version\": \"1.0.0\",
  \"description\": \"私のカスタムプラグイン\"
}
```

#### 3. plugin.pyの実装

```python
def register(app_api=None):
    \"\"\"
    プラグイン登録関数
    
    Args:
        app_api: ホストアプリケーションのAPI辞書
    \"\"\"
    print(f\"[my_plugin] 登録完了: {app_api}\")
    
    # ここにプラグインの初期化コードを記述
    # 例: UIコンポーネントの追加、メニュー項目の登録など
```

#### 4. セキュリティポリシーの設定

`config/policies.json`に設定を追加：

```json
{
  \"my_plugin\": {
    \"network\": false,          # ネットワークアクセス許可
    \"gpu\": false,              # GPU使用許可
    \"memory_mb\": 512,          # メモリ上限（MB）
    \"cpus\": 1.0,               # CPU使用率上限
    \"pids_limit\": 64,          # プロセス数上限
    \"timeout_sec\": 30,         # タイムアウト（秒）
    \"allowed_paths\": [],       # 読み取り許可パス
    \"write_paths\": []          # 書き込み許可パス
  }
}
```

### プラグインのアップロード

#### curlを使用

```bash
# 1. プラグインのパッケージ化
tar -czf my_plugin.tar.gz -C plugins/my_plugin .

# 2. ストアサーバーへアップロード
curl -X POST \"http://localhost:8001/plugins/upload\" \\
  -F \"manifest=@plugins/my_plugin/plugin.json\" \\
  -F \"package=@my_plugin.tar.gz\"

# 3. 承認（管理者のみ）
curl -X POST \"http://localhost:8001/plugins/my_plugin/1.0.0/approve\" \\
  -H \"X-API-Key: YOUR_API_KEY\"

# 4. ダウンロード
curl -O \"http://localhost:8001/plugins/my_plugin/1.0.0/download\"
```

### マニフェストへの署名（管理者用）

```bash
python cli/sign.py plugins/my_plugin/plugin.json
```

署名後、plugin.jsonに`signature`フィールドが追加されます。

## API仕様

### 認証

#### OAuth2 トークン取得

```bash
curl -X POST \"http://localhost:8001/token\" \\
  -d \"username=admin&password=password\"
```

レスポンス：
```json
{
  \"access_token\": \"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...\",
  \"token_type\": \"bearer\"
}
```

#### APIキー認証

```bash
# server/app/keys/api_key.txt からキーを取得
curl -H \"X-API-Key: YOUR_API_KEY\" \\
  \"http://localhost:8001/plugins\"
```

### プラグインエンドポイント

| メソッド | エンドポイント | 説明 | 認証 |
|---------|---------------|------|------|
| GET | `/plugins` | プラグイン一覧取得 | 不要 |
| POST | `/plugins/upload` | プラグインアップロード | 必要 |
| POST | `/plugins/{name}/{version}/approve` | プラグイン承認 | 必要 |
| GET | `/plugins/{name}/{version}/download` | プラグインダウンロード | 不要 |

詳細は`docs/plugin_api_openapi.yaml`を参照してください。

## セキュリティ

### 実装済みのセキュリティ機能

✅ **サンドボックス実行**: プラグインは隔離されたサブプロセスで実行  
✅ **リソース制限**: メモリ、CPU、タイムアウトの制御  
✅ **電子署名**: cryptographyによる署名検証  
✅ **静的解析**: アップロード時のセキュリティスキャン  
✅ **認証**: OAuth2とAPIキーの二重認証  
✅ **入力検証**: Pydanticによる厳密なバリデーション  

### 本番環境での推奨事項

⚠️ **このプロトタイプを本番環境で使用する際の注意**

1. **HTTPS必須**: リバースプロキシ（Nginx/Caddy）でTLS終端
2. **鍵管理**: HSM（Hardware Security Module）または AWS KMS使用
3. **認証強化**: 
   - デフォルトパスワード（admin/password）の変更
   - JWT秘密鍵の再生成
   - レート制限の実装
4. **ネットワーク**: 
   - ファイアウォール設定
   - `/plugins/approve`へのアクセス制限
5. **監視**: 
   - ログ集約（ELK/Splunk）
   - 異常検知アラート

### セキュリティスキャン

アップロード時に以下をチェック：
- 危険な関数呼び出し（`eval`, `exec`, `__import__`）
- システムコマンド実行（`os.system`, `subprocess`）
- ファイルシステム操作
- ネットワークアクセス

結果は`app.log`に記録されます。

## トラブルシューティング

### プラグインが読み込まれない

1. **ログを確認**: `app.log`でエラーメッセージをチェック
2. **マニフェスト検証**: `plugin.json`の構文エラーを確認
3. **エントリーポイント**: `entry`フィールドのパスが正しいか確認

```bash
# ログの確認
tail -f app.log
```

### サーバーが起動しない

```bash
# ポート競合の確認
netstat -ano | findstr 8001  # Windows
lsof -i :8001                # macOS/Linux

# 依存関係の再インストール
pip install --upgrade -r requirements.txt
```

### 認証エラー

```bash
# APIキーの再生成
rm server/app/keys/api_key.txt
# サーバー再起動で自動生成

# トークンの再取得
curl -X POST \"http://localhost:8001/token\" \\
  -d \"username=admin&password=password\"
```

## 開発ロードマップ

### v0.2.0（予定）
- [ ] レイヤーシステムの実装
- [ ] 画像フィルタープラグインテンプレート
- [ ] プラグインマーケットプレイスUI

### v0.3.0（予定）
- [ ] AI画像処理プラグインSDK
- [ ] ブラシエンジン統合
- [ ] リアルタイムプレビュー

### v1.0.0（予定）
- [ ] マルチプラットフォームバイナリ配布
- [ ] エンタープライズサポート
- [ ] クラウド連携機能

## コントリビューション

プルリクエスト歓迎です！以下をお願いします：

1. **コードスタイル**: Black + Ruffで整形
2. **テスト**: `pytest`で全テスト通過
3. **コミット**: Conventional Commits形式
4. **ドキュメント**: 機能追加時は必ずREADME更新

```bash
# テスト実行
pytest tests/

# コードフォーマット
black app/ server/ cli/
ruff check --fix .
```

## ライセンス

このプロジェクトは複数のライセンスを含みます。詳細は`LICENSES/`ディレクトリを参照してください。

- コアコード: MIT License
- サードパーティ: 各ライセンスに従う（`LICENSE`ファイル参照）

## サポート

- **Issues**: [GitHub Issues](https://github.com/your-org/creative-suite/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/creative-suite/discussions)
- **Email**: support@example.com

---

**注意**: これはプロトタイプ版です。本番環境での使用は推奨されません。セキュリティ要件を満たすには追加の実装が必要です。

**最終更新**: 2025年10月
`
}