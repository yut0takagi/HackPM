# GitHub Webhook アーキテクチャ

Hack PM の GitHub Webhook 連携のアーキテクチャと動作フローを解説します。

## 📊 システムアーキテクチャ

```
┌─────────────────────────────────────────────────────────────────┐
│                         GitHub                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Push       │  │     PR       │  │   Issues     │         │
│  │   Events     │  │   Events     │  │   Events     │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                 │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │ HTTPS POST
                             │ (署名付きペイロード)
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Hack PM Backend                             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  POST /api/github/webhook                                  │ │
│  │  (GitHubWebhookHandler)                                    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                             │                                     │
│                             ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. 署名検証 (HMAC-SHA256)                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                             │                                     │
│                             ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  2. リポジトリ許可リスト確認                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                             │                                     │
│                             ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  3. リポジトリ情報の保存/更新                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                             │                                     │
│                             ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  4. イベントの保存                                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                             │                                     │
│                             ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  5. イベント種別に応じた処理                               │ │
│  │     • push → Branch 更新                                   │ │
│  │     • pull_request → PR 作成/更新                          │ │
│  │     • issues → Issue 作成/更新                             │ │
│  │     • create/delete → Branch 作成/削除                     │ │
│  │     • workflow_run → CI 実行記録                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                             │                                     │
│                             ↓                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  6. Discord 通知（オプション）                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                             │                                     │
└─────────────────────────────┼─────────────────────────────────────┘
                              │
                              ↓
                    ┌──────────────────┐
                    │   SQLite DB      │
                    │                  │
                    │  • repositories  │
                    │  • branches      │
                    │  • pull_requests │
                    │  • issues        │
                    │  • ci_runs       │
                    │  • events        │
                    └──────────────────┘
```

## 🔄 イベント処理フロー

### Push Event の処理

```
GitHub Push Event
      ↓
Webhook Handler
      ↓
Repository 確認/作成
      ↓
Branch テーブルに保存/更新
  • branch_name
  • head_sha
  • last_commit_message
  • last_commit_author
  • pushed_at
      ↓
Event テーブルに記録
      ↓
Response 200 OK
```

### Pull Request Event の処理

```
GitHub PR Event (opened/closed/synchronized)
      ↓
Webhook Handler
      ↓
Repository 確認/作成
      ↓
PullRequest テーブルに保存/更新
  • number
  • title, body
  • state (open/closed)
  • head_ref, base_ref
  • mergeable
  • merged_at (if merged)
      ↓
Event テーブルに記録
      ↓
Discord 通知 (opened/merged の場合)
      ↓
Response 200 OK
```

### Issues Event の処理

```
GitHub Issue Event (opened/closed/edited)
      ↓
Webhook Handler
      ↓
Repository 確認/作成
      ↓
Issue テーブルに保存/更新
  • number
  • title, body
  • state
  • labels (JSON)
  • assignees (JSON)
  • milestone
  • closed_at (if closed)
      ↓
Event テーブルに記録
      ↓
Response 200 OK
```

## 🔒 セキュリティレイヤー

### 1. 署名検証

```python
# GitHubから送信される署名を検証
HMAC-SHA256(payload, GITHUB_WEBHOOK_SECRET) == X-Hub-Signature-256

✅ 一致 → 処理続行
❌ 不一致 → 401 Unauthorized
```

### 2. リポジトリ許可リスト

```python
if repo_full_name in ALLOWED_REPOS:
    ✅ 処理続行
else:
    ❌ "Repository not allowed" レスポンス
```

### 3. HTTPS通信

```
GitHub → [HTTPS] → Hack PM Backend
         (暗号化)
```

## 📦 データモデル

### Repository (リポジトリ)
```python
{
    "id": 1,
    "full_name": "owner/repo",
    "name": "repo",
    "owner": "owner",
    "default_branch": "main",
    "visibility": "public",
    "description": "...",
    "html_url": "https://github.com/owner/repo",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
}
```

### Branch (ブランチ)
```python
{
    "id": 1,
    "repo_id": 1,
    "name": "main",
    "head_sha": "abc123...",
    "is_default": true,
    "last_commit_message": "Initial commit",
    "last_commit_author": "developer",
    "last_commit_date": "2024-01-01T00:00:00",
    "pushed_at": "2024-01-01T00:00:00"
}
```

### PullRequest (プルリクエスト)
```python
{
    "id": 1,
    "repo_id": 1,
    "number": 42,
    "title": "Add new feature",
    "body": "Description...",
    "state": "open",
    "author": "developer",
    "head_ref": "feature/awesome",
    "base_ref": "main",
    "mergeable": true,
    "merged_at": null,
    "created_at": "2024-01-01T00:00:00"
}
```

### Issue
```python
{
    "id": 1,
    "repo_id": 1,
    "number": 123,
    "title": "Bug report",
    "body": "Description...",
    "state": "open",
    "labels_json": "[\"bug\", \"priority:high\"]",
    "assignees_json": "[\"dev1\", \"dev2\"]",
    "milestone": "v1.0",
    "closed_at": null,
    "created_at": "2024-01-01T00:00:00"
}
```

### Event (イベント履歴)
```python
{
    "id": 1,
    "repo_id": 1,
    "event_type": "push",
    "action": null,
    "payload_json": "{...}",  # 完全なペイロード
    "delivery_id": "abc-123",
    "actor": "developer",
    "created_at": "2024-01-01T00:00:00"
}
```

## 🎯 処理の特徴

### 冪等性 (Idempotency)

同じイベントが複数回配信されても安全に処理できます：

```python
# リポジトリ: full_name で一意性を保証
# Branch: repo_id + name で一意性を保証
# PullRequest: repo_id + number で一意性を保証
# Issue: repo_id + number で一意性を保証

# 既存レコードがあれば更新、なければ作成 (Upsert)
```

### 非同期処理

```python
# Webhookハンドラーは非同期関数
async def handle_webhook(request: Request, db: Session):
    # 高速にレスポンスを返す
    # GitHubは10秒以内のレスポンスを期待
```

### エラーハンドリング

```python
try:
    # 処理
    db.commit()
    return success_response
except HTTPException:
    raise  # HTTPエラーはそのまま返す
except Exception as e:
    logger.error(f"Error: {e}")
    db.rollback()  # ロールバック
    raise HTTPException(500, detail=str(e))
```

## 📈 スケーラビリティ

### 現在の構成
- 単一のFastAPIサーバー
- SQLiteデータベース
- 小〜中規模のリポジトリに最適

### スケーリングオプション

1. **水平スケーリング**
   - 複数のサーバーインスタンス
   - ロードバランサーで分散

2. **データベース移行**
   - SQLite → PostgreSQL/MySQL
   - より多くの同時接続に対応

3. **非同期処理の強化**
   - Celery/RQ などのタスクキュー導入
   - Webhook受信とデータ処理を分離

4. **キャッシング**
   - Redis でよくアクセスされるデータをキャッシュ
   - API レスポンス高速化

## 🔍 モニタリング

### ログレベル

```
INFO: 通常の処理フロー
WARNING: 軽微な問題（署名未設定など）
ERROR: 処理エラー（ロールバック発生）
```

### 主要メトリクス

- Webhook 受信数
- 処理成功率
- 平均処理時間
- エラー発生率
- リポジトリ別イベント数

## 🚀 パフォーマンス

### レスポンスタイム目標

- Webhook 処理: < 1秒
- API レスポンス: < 200ms
- データベースクエリ: < 100ms

### 最適化ポイント

1. **データベースインデックス**
   - Repository.full_name
   - Branch(repo_id, name)
   - PullRequest(repo_id, number)
   - Issue(repo_id, number)
   - Event.created_at

2. **バッチ処理**
   - 複数のコミットを一度に処理
   - N+1 クエリの回避

3. **ペイロードの選択的保存**
   - 必要な情報のみを抽出
   - payload_json は完全なペイロードを保存（監査用）

## 🔧 トラブルシューティング

### よくある問題と解決方法

| 問題 | 原因 | 解決方法 |
|------|------|----------|
| 401 Error | 署名検証失敗 | SECRET確認 |
| 403 Error | リポジトリ未許可 | ALLOWED_REPOS追加 |
| 404 Error | エンドポイント間違い | URL確認 |
| 500 Error | サーバー内部エラー | ログ確認 |
| Timeout | 処理時間超過 | パフォーマンス確認 |

## 📚 参考資料

- [GitHub Webhooks Documentation](https://docs.github.com/webhooks)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [HMAC-SHA256 Signature](https://docs.github.com/webhooks/using-webhooks/validating-webhook-deliveries)

---

このアーキテクチャにより、GitHub イベントをリアルタイムに取得し、効率的にデータベースに保存できます。
