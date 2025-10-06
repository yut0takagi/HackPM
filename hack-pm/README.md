# Hack PM - ハッカソンプロジェクト管理システム

Hack PMは、ハッカソンイベントでのプロジェクト管理を効率化するWebアプリケーションです。プロジェクトの作成、管理、そしてKeelテンプレートリポジトリからの自動リポジトリ生成機能を提供します。

## 🏗️ アーキテクチャ

- **フロントエンド**: React (TypeScript)
- **バックエンド**: 
  - Go (Gin) - プロジェクト管理API
  - Python (FastAPI) - 統計分析・リポジトリ管理API
- **データベース**: PostgreSQL
- **コンテナ化**: Docker & Docker Compose

## 🚀 クイックスタート

### 前提条件

- Docker
- Docker Compose

### 起動方法

1. リポジトリをクローン
```bash
git clone <repository-url>
cd hack-pm
```

2. Docker Composeでサービスを起動
```bash
docker-compose up --build
```

3. ブラウザでアクセス
- フロントエンド: http://localhost:3000
- Go API: http://localhost:8080
- Python API: http://localhost:8000

### 初回起動時

初回起動時には、サンプルプロジェクトが自動的に作成されます：
- AIチャットボット
- IoTセンサーダッシュボード  
- ブロックチェーン投票システム

## 📱 機能

### 主要機能

1. **ダッシュボード**
   - プロジェクト統計の表示
   - 最新プロジェクトの一覧

2. **プロジェクト管理**
   - プロジェクトの作成・編集・削除
   - プロジェクト詳細の表示
   - ステータス管理（進行中/完了）

3. **アイデアジェネレーター** 🆕
   - テーマ・技術・難易度に基づくアイデア自動生成
   - 生成されたアイデアから直接プロジェクト作成
   - 推奨技術スタックと機能の提案

4. **サービスビルダー** 🆕
   - Webアプリ、API、モバイルアプリなど多様なサービステンプレート
   - 機能選択による自動コード生成
   - Docker、Vercel、AWSなど複数のデプロイオプション

5. **チーム管理** 🆕
   - チームメンバーの追加・管理
   - スキルとロールの管理
   - GitHub・Discord連携

6. **Discord連携** 🆕
   - Webhook通知の自動送信
   - チーム活動の自動通知
   - プロジェクト進捗の共有

7. **GitHub連携** 🆕
   - CI/CDパイプラインの自動生成
   - GitHub Workflowの作成
   - リポジトリ管理の自動化

8. **リポジトリ管理**
   - Keelテンプレートからの自動リポジトリ作成
   - プロジェクト用リポジトリの管理

9. **分析機能**
   - プロジェクト統計の生成
   - プロジェクト分析と推奨事項の提供

### API エンドポイント

#### Go API (ポート 8080)
- `GET /api/projects` - プロジェクト一覧取得
- `GET /api/projects/:id` - プロジェクト詳細取得
- `POST /api/projects` - プロジェクト作成
- `PUT /api/projects/:id` - プロジェクト更新
- `DELETE /api/projects/:id` - プロジェクト削除
- `GET /api/projects/:id/team` - チームメンバー一覧取得 🆕
- `POST /api/projects/:id/team` - チームメンバー追加 🆕
- `DELETE /api/projects/:id/team/:member_id` - チームメンバー削除 🆕

#### Python API (ポート 8000)
- `GET /api/stats` - プロジェクト統計取得
- `POST /api/projects/:id/repository` - リポジトリ作成
- `GET /api/templates` - テンプレート一覧取得
- `POST /api/analyze/project` - プロジェクト分析
- `POST /api/ideas/generate` - アイデア生成 🆕
- `GET /api/templates/service` - サービステンプレート取得 🆕
- `POST /api/services/generate` - サービス生成 🆕
- `POST /api/discord/notify` - Discord通知送信 🆕
- `POST /api/projects/:id/github/workflow` - GitHub Workflow作成 🆕

## 🛠️ 開発

### ローカル開発環境

各サービスは独立して開発できます：

#### フロントエンド開発
```bash
cd frontend
npm install
npm start
```

#### Go バックエンド開発
```bash
cd backend-go
go mod tidy
go run main.go
```

#### Python バックエンド開発
```bash
cd backend-python
pip install -r requirements.txt
uvicorn main:app --reload
```

### データベース

PostgreSQLが自動的にセットアップされます：
- ホスト: localhost:5432
- データベース: hackpm
- ユーザー: hackpm
- パスワード: hackpm123

### 環境変数

各サービスで使用される主な環境変数：

#### フロントエンド
- `REACT_APP_API_URL`: Go APIのURL (デフォルト: http://localhost:8080)
- `REACT_APP_PYTHON_API_URL`: Python APIのURL (デフォルト: http://localhost:8000)

#### Go バックエンド
- `PORT`: サーバーポート (デフォルト: 8080)
- `PYTHON_API_URL`: Python APIのURL

#### Python バックエンド
- `PORT`: サーバーポート (デフォルト: 8000)

## 🔧 Keelテンプレートとの連携

Hack PMは `/keel` ディレクトリにあるテンプレートリポジトリと連携します。新しいプロジェクトを作成する際、以下の流れでリポジトリが生成されます：

1. プロジェクト詳細画面で「Keelテンプレートからリポジトリを作成」をクリック
2. Python APIがKeelテンプレートを基にリポジトリを作成
3. 作成されたリポジトリURLがプロジェクトに関連付けられる

### テンプレートの種類

- **keel**: 基本的なハッカソンテンプレート
- **keel-python**: Python/FastAPI版
- **keel-go**: Go版

## 📝 使用例

### 新しいプロジェクトの作成

1. ダッシュボードまたはプロジェクト一覧から「新規プロジェクト作成」をクリック
2. プロジェクト名と説明を入力
3. プロジェクトが作成され、詳細画面に移動
4. 「Keelテンプレートからリポジトリを作成」でリポジトリを生成

### プロジェクトの管理

- プロジェクト一覧でステータスや進捗を確認
- プロジェクト詳細でリポジトリURLや詳細情報を管理
- ダッシュボードで全体の統計を把握

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🆘 トラブルシューティング

### よくある問題

1. **ポートが既に使用されている**
   ```bash
   # 使用中のポートを確認
   lsof -i :3000
   lsof -i :8080
   lsof -i :8000
   ```

2. **データベース接続エラー**
   ```bash
   # PostgreSQLコンテナの状態を確認
   docker-compose logs postgres
   ```

3. **フロントエンドでAPIに接続できない**
   - 環境変数 `REACT_APP_API_URL` と `REACT_APP_PYTHON_API_URL` を確認
   - バックエンドサービスが起動しているか確認

### ログの確認

```bash
# 全サービスのログを表示
docker-compose logs

# 特定のサービスのログを表示
docker-compose logs frontend
docker-compose logs backend-go
docker-compose logs backend-python
```

### 完全リセット

```bash
# 全コンテナとボリュームを削除
docker-compose down -v
docker-compose up --build
```