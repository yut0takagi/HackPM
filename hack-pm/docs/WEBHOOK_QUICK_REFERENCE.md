# GitHub Webhook クイックリファレンス

Hack PM の GitHub Webhook 機能を素早く使い始めるための簡易リファレンスです。

## 🚀 最速セットアップ (3ステップ)

### 1. 環境変数を設定

```bash
cd hack-pm
cp .env.example .env
```

`.env` を編集：
```env
GITHUB_WEBHOOK_SECRET=your_secret_here
GITHUB_TOKEN=ghp_your_token_here
ALLOWED_REPOS=your-org/your-repo
```

### 2. サーバーを起動

```bash
docker-compose up -d
# または
./start-docker.sh
```

### 3. GitHubでWebhookを設定

1. リポジトリの **Settings** → **Webhooks** → **Add webhook**
2. Payload URL: `https://your-domain.com/api/github/webhook`
3. Content type: `application/json`
4. Secret: `.env` と同じ値
5. Events: Pushes, Pull requests, Issues, Branch creation/deletion, Workflow runs

完了！ 🎉

## 📋 API エンドポイント

### Webhook エンドポイント
```
POST /api/github/webhook
```

### イベント取得
```bash
# 最新20件のイベントを取得
curl http://localhost:8000/api/events?limit=20

# 特定リポジトリのイベント
curl http://localhost:8000/api/events?repo=owner/repo

# 特定イベントタイプのみ
curl http://localhost:8000/api/events?event_type=push
```

### リポジトリ情報
```bash
# リポジトリ一覧
curl http://localhost:8000/api/repos

# リポジトリ詳細
curl http://localhost:8000/api/repos/1

# ブランチ一覧
curl http://localhost:8000/api/repos/1/branches

# PR一覧
curl http://localhost:8000/api/repos/1/pulls

# Issue一覧
curl http://localhost:8000/api/repos/1/issues

# CI実行履歴
curl http://localhost:8000/api/repos/1/ci-runs
```

### 統計
```bash
# 全体統計
curl http://localhost:8000/api/stats
```

### 手動同期
```bash
# GitHubから手動でデータを同期
curl -X POST http://localhost:8000/api/sync/github
```

## 🧪 ローカルテスト

### curlでテスト

```bash
# Push イベント
curl -X POST http://localhost:8000/api/github/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-GitHub-Delivery: test-delivery-001" \
  -d '{
    "ref": "refs/heads/main",
    "repository": {
      "full_name": "testuser/test-repo",
      "name": "test-repo",
      "owner": {"login": "testuser"}
    },
    "head_commit": {
      "message": "Test commit"
    },
    "sender": {"login": "testuser"}
  }'
```

### ngrokでローカル環境を公開

```bash
# インストール
brew install ngrok  # macOS

# 起動
ngrok http 8000

# 表示されたURLをGitHubのWebhook設定に使用
# 例: https://abc123.ngrok.io/api/github/webhook
```

### pytestでテスト

```bash
cd backend-python

# 全テスト実行
pytest tests/test_github_webhook.py -v

# 特定のテストのみ
pytest tests/test_github_webhook.py::TestWebhookSignatureVerification -v
```

## 🔍 トラブルシューティング

### Webhook配信が失敗する

**401 Unauthorized**
```bash
# Secretが間違っている可能性
# .envとGitHubの設定を確認
cat .env | grep GITHUB_WEBHOOK_SECRET
```

**403 Repository not allowed**
```bash
# ALLOWED_REPOSにリポジトリを追加
echo "ALLOWED_REPOS=owner1/repo1,owner2/repo2" >> .env
docker-compose restart backend-python
```

**404 Not Found**
```bash
# サーバーが起動しているか確認
curl http://localhost:8000/health
```

### ログを確認

```bash
# リアルタイムでログを表示
docker-compose logs -f backend-python

# 最近のログを表示
docker-compose logs --tail=50 backend-python

# webhookでフィルター
docker-compose logs backend-python | grep webhook
```

### データベースを確認

```bash
# SQLiteに接続
docker-compose exec backend-python sqlite3 hack_pm.db

# イベント一覧
SELECT * FROM events ORDER BY created_at DESC LIMIT 10;

# リポジトリ一覧
SELECT * FROM repositories;

# 終了
.quit
```

## 📊 サポートされるイベント

| イベント | 説明 | 保存データ |
|---------|------|-----------|
| `push` | コミットのプッシュ | ブランチ、コミット情報 |
| `pull_request` | PRの作成/更新 | PR番号、タイトル、状態 |
| `issues` | Issueの作成/更新 | Issue番号、タイトル、ラベル |
| `create` | ブランチ作成 | ブランチ名 |
| `delete` | ブランチ削除 | ブランチ名 |
| `workflow_run` | GitHub Actions実行 | ワークフロー名、結果 |

## 🔐 セキュリティチェックリスト

- [ ] `GITHUB_WEBHOOK_SECRET` を設定している
- [ ] `ALLOWED_REPOS` を設定している（本番環境）
- [ ] HTTPSを使用している
- [ ] GitHub Tokenの権限を最小限にしている
- [ ] ログを定期的に監視している

## 📚 詳細ドキュメント

より詳しい情報は以下を参照：
- [完全なセットアップガイド](WEBHOOK_SETUP.md)
- [テストサンプル](../test/webhook-samples.md)
- [API ドキュメント](http://localhost:8000/docs)

## 💡 よく使うコマンド

```bash
# サービス起動
docker-compose up -d

# ログ確認
docker-compose logs -f backend-python

# サービス再起動
docker-compose restart backend-python

# サービス停止
docker-compose down

# データベースリセット
docker-compose down -v
docker-compose up -d

# テスト実行
docker-compose exec backend-python pytest tests/test_github_webhook.py -v
```

---

質問やフィードバックは [Issues](https://github.com/yut0takagi/keel/issues) へ！
