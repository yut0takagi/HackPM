# GitHub Webhook セットアップガイド

このガイドでは、Hack PMでGitHub Webhookを設定し、リアルタイムでリポジトリのイベントを取得する方法を説明します。

## 📋 目次

1. [概要](#概要)
2. [前提条件](#前提条件)
3. [Webhook設定手順](#webhook設定手順)
4. [環境変数の設定](#環境変数の設定)
5. [動作確認](#動作確認)
6. [トラブルシューティング](#トラブルシューティング)
7. [サポートされるイベント](#サポートされるイベント)

## 概要

GitHub Webhookを利用することで、以下のイベントをリアルタイムで取得できます：

- 🔄 **Push**: コミットのプッシュ
- 🔀 **Pull Request**: PRの作成、更新、マージ
- 🐛 **Issues**: Issueの作成、更新、クローズ
- 🌿 **Branch**: ブランチの作成、削除
- ⚙️ **Workflow Run**: GitHub Actionsの実行結果

## 前提条件

- GitHub リポジトリへの管理者権限
- Hack PM バックエンドが稼働中（パブリックにアクセス可能なURL）
- Webhook シークレットトークン（セキュリティのため推奨）

## Webhook設定手順

### 1. GitHubリポジトリの設定ページを開く

1. 監視したいGitHubリポジトリにアクセス
2. **Settings** タブをクリック
3. 左サイドバーの **Webhooks** をクリック
4. **Add webhook** ボタンをクリック

### 2. Webhookの設定

#### Payload URL
```
https://your-domain.com/api/github/webhook
```

または開発環境の場合（ngrokなどを使用）：
```
https://your-ngrok-url.ngrok.io/api/github/webhook
```

#### Content type
- **application/json** を選択

#### Secret
セキュリティのため、シークレットトークンを設定することを強く推奨します：

```bash
# ランダムな文字列を生成（例）
openssl rand -hex 20
```

生成された文字列をSecretフィールドに入力し、`.env`ファイルにも設定します。

#### イベントの選択

**"Let me select individual events"** を選択し、以下のイベントにチェックを入れます：

- ✅ **Pushes** - コミットのプッシュ
- ✅ **Pull requests** - PRの作成・更新
- ✅ **Issues** - Issueの作成・更新
- ✅ **Branch or tag creation** - ブランチ作成
- ✅ **Branch or tag deletion** - ブランチ削除
- ✅ **Workflow runs** - GitHub Actions実行

#### Active
- ✅ **Active** にチェックを入れる

### 3. 保存

**Add webhook** ボタンをクリックして保存します。

## 環境変数の設定

### `.env` ファイルの設定

`hack-pm/.env` ファイルに以下を設定：

```env
# GitHub Webhook設定
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
GITHUB_TOKEN=ghp_your_personal_access_token_here
ALLOWED_REPOS=owner1/repo1,owner2/repo2

# Discord通知（オプション）
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your/webhook/url
```

### 設定項目の説明

#### `GITHUB_WEBHOOK_SECRET`
- GitHubで設定したWebhook Secret
- ペイロードの署名検証に使用
- セキュリティのため必ず設定することを推奨

#### `GITHUB_TOKEN`
- GitHub Personal Access Token
- 手動同期やAPI呼び出しに使用
- 必要な権限: `repo`, `read:org`

トークンの作成方法：
1. GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **Generate new token** をクリック
3. 必要な権限を選択して生成

#### `ALLOWED_REPOS`
- 監視を許可するリポジトリのリスト（カンマ区切り）
- 形式: `owner/repo`
- 例: `myorg/repo1,myorg/repo2,user/personal-repo`
- 空の場合は全てのリポジトリを許可（本番環境では非推奨）

#### `DISCORD_WEBHOOK_URL` (オプション)
- Discord通知用のWebhook URL
- 重要なイベント（Force push、PR merge、CI失敗など）を通知

## 動作確認

### 1. Webhookの配信履歴を確認

GitHubのWebhook設定ページで、**Recent Deliveries** タブを確認：

- 緑色のチェックマーク: 成功
- 赤色のエラーマーク: 失敗

失敗の場合、Response bodyでエラー内容を確認できます。

### 2. テストペイロードの送信

Webhook設定画面で **Redeliver** ボタンをクリックして、テストペイロードを再送信できます。

### 3. ローカルでテスト

`hack-pm/test/webhook-samples.md` にあるサンプルcurlコマンドを使用：

```bash
# Push イベントのテスト
curl -X POST http://localhost:8000/api/github/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-GitHub-Delivery: test-123" \
  -d @sample_push_payload.json
```

### 4. APIでイベントを確認

```bash
# 最近のイベントを取得
curl http://localhost:8000/api/events?limit=10

# 統計を確認
curl http://localhost:8000/api/stats
```

## トラブルシューティング

### Webhook配信が失敗する

#### 症状: 401 Unauthorized
- **原因**: Webhook Secretが間違っている
- **解決方法**: 
  1. GitHubのSecret設定を確認
  2. `.env`ファイルの`GITHUB_WEBHOOK_SECRET`を確認
  3. 両方が一致していることを確認

#### 症状: 403 Repository not allowed
- **原因**: リポジトリが`ALLOWED_REPOS`に含まれていない
- **解決方法**: `.env`ファイルに対象リポジトリを追加

```env
ALLOWED_REPOS=myorg/existing-repo,myorg/new-repo
```

#### 症状: 404 Not Found
- **原因**: エンドポイントURLが間違っている
- **解決方法**: 
  1. Payload URLが正しいか確認: `/api/github/webhook`
  2. サーバーが起動しているか確認
  3. ファイアウォールやプロキシの設定を確認

#### 症状: Timeout
- **原因**: サーバーが応答していない、またはネットワークの問題
- **解決方法**:
  1. サーバーのログを確認
  2. ネットワーク接続を確認
  3. ngrok等のトンネルが稼働しているか確認

### ローカル開発でWebhookをテスト

パブリックURLがない場合、ngrokを使用：

```bash
# ngrokをインストール
brew install ngrok  # macOS
# または https://ngrok.com/ からダウンロード

# ポート8000をトンネル
ngrok http 8000

# 表示されたURLをGitHubのWebhook設定に使用
# 例: https://abc123.ngrok.io/api/github/webhook
```

### ログの確認

```bash
# Dockerログを確認
docker-compose logs backend-python

# 特定のイベントをフィルター
docker-compose logs backend-python | grep "webhook"

# リアルタイムでログを監視
docker-compose logs -f backend-python
```

### データベースの確認

```bash
# SQLiteデータベースに接続
sqlite3 hack_pm.db

# イベントを確認
SELECT * FROM events ORDER BY created_at DESC LIMIT 10;

# リポジトリを確認
SELECT * FROM repositories;

# 終了
.quit
```

## サポートされるイベント

### Push Events
```json
{
  "event_type": "push",
  "stored_data": {
    "branch": "ブランチ名",
    "commits": "コミット一覧",
    "head_sha": "最新コミットSHA"
  }
}
```

### Pull Request Events
```json
{
  "event_type": "pull_request",
  "actions": ["opened", "closed", "reopened", "synchronize"],
  "stored_data": {
    "number": "PR番号",
    "title": "PRタイトル",
    "state": "状態",
    "mergeable": "マージ可能か"
  }
}
```

### Issues Events
```json
{
  "event_type": "issues",
  "actions": ["opened", "closed", "reopened", "edited"],
  "stored_data": {
    "number": "Issue番号",
    "title": "Issueタイトル",
    "labels": "ラベル一覧",
    "assignees": "担当者一覧"
  }
}
```

### Branch Events
```json
{
  "event_type": "create" | "delete",
  "ref_type": "branch",
  "stored_data": {
    "branch_name": "ブランチ名"
  }
}
```

### Workflow Run Events
```json
{
  "event_type": "workflow_run",
  "stored_data": {
    "workflow_name": "ワークフロー名",
    "status": "completed",
    "conclusion": "success | failure",
    "run_id": "実行ID"
  }
}
```

## セキュリティのベストプラクティス

1. **必ずWebhook Secretを設定する**
   - ペイロードの改ざんを防ぐ
   - HMAC-SHA256署名で検証

2. **ALLOWED_REPOSを設定する**
   - 意図しないリポジトリからのイベントを防ぐ
   - 本番環境では必須

3. **HTTPSを使用する**
   - 通信を暗号化
   - Let's Encryptなどで証明書を取得

4. **GitHub Tokenの権限を最小限に**
   - 必要な権限のみを付与
   - 定期的にトークンをローテーション

5. **ログを監視する**
   - 異常なアクセスがないか確認
   - エラーを早期に検出

## 参考リンク

- [GitHub Webhooks Documentation](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
- [Securing your webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks/securing-your-webhooks)
- [Webhook events and payloads](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads)

## サポート

問題が解決しない場合：
1. GitHubのIssueを確認
2. 新しいIssueを作成
3. ログファイルを添付

---

✨ Hack PMでリアルタイムなプロジェクト管理を楽しんでください！
