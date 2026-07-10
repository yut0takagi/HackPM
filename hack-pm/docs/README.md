# Hack PM Documentation

GitHub Webhook連携機能のドキュメント集です。

## 📚 ドキュメント一覧

### 🚀 [Webhook セットアップガイド](WEBHOOK_SETUP.md)
**初めての方はこちらから！**

GitHub Webhookを設定してHack PMでリアルタイムイベント取得を開始するための完全ガイド。

**含まれる内容:**
- GitHubでのWebhook設定手順（画像付き説明）
- 環境変数の詳細な設定方法
- 動作確認とテスト方法
- トラブルシューティングガイド
- セキュリティのベストプラクティス
- サポートされるイベント一覧

**所要時間:** 15-20分  
**難易度:** ⭐⭐☆☆☆ (初級)

---

### ⚡ [Webhook クイックリファレンス](WEBHOOK_QUICK_REFERENCE.md)
**素早く使い始めたい方向け！**

最速3ステップでWebhookを設定し、よく使うコマンドをすぐに見つけられるチートシート。

**含まれる内容:**
- 3ステップクイックセットアップ
- API エンドポイント一覧
- ローカルテスト用curlコマンド集
- トラブルシューティング早見表
- よく使うコマンド集

**所要時間:** 5分  
**難易度:** ⭐☆☆☆☆ (入門)

---

### 🏗️ [Webhook アーキテクチャ](WEBHOOK_ARCHITECTURE.md)
**システムを理解したい開発者向け！**

Hack PMのGitHub Webhook連携システムの内部構造と動作原理を詳しく解説。

**含まれる内容:**
- システムアーキテクチャ図
- イベント処理フロー
- セキュリティレイヤーの詳細
- データモデル定義
- スケーラビリティ設計
- パフォーマンス最適化
- モニタリング方法

**所要時間:** 30分  
**難易度:** ⭐⭐⭐⭐☆ (上級)

---

## 🎯 目的別ガイド

### 新規ユーザー
1. [セットアップガイド](WEBHOOK_SETUP.md) を読む
2. 環境変数を設定する
3. GitHubでWebhookを設定する
4. [クイックリファレンス](WEBHOOK_QUICK_REFERENCE.md) をブックマーク

### 既存ユーザー
- トラブルが起きたら → [セットアップガイド](WEBHOOK_SETUP.md) のトラブルシューティング
- コマンドを忘れたら → [クイックリファレンス](WEBHOOK_QUICK_REFERENCE.md)

### 開発者
1. [アーキテクチャ](WEBHOOK_ARCHITECTURE.md) でシステムを理解
2. `tests/test_github_webhook.py` でテストを確認
3. `src/api/github_webhook.py` でコードを確認

---

## 📊 統計

| ファイル | 行数 | サイズ | 内容 |
|---------|------|--------|------|
| WEBHOOK_SETUP.md | 345行 | 9.2KB | 完全セットアップガイド |
| WEBHOOK_QUICK_REFERENCE.md | 244行 | 5.4KB | クイックリファレンス |
| WEBHOOK_ARCHITECTURE.md | 387行 | 15KB | システムアーキテクチャ |
| **合計** | **976行** | **29.6KB** | **3つのドキュメント** |

## 🧪 テストカバレッジ

Webhook機能は **21個のテスト** で完全にカバーされています：

```bash
# テスト実行
cd backend-python
pytest tests/test_github_webhook.py -v

# 結果
======================= 21 passed ========================
```

**テストカテゴリ:**
- 署名検証: 4テスト
- リポジトリ許可リスト: 3テスト
- リポジトリ作成/更新: 2テスト
- Pushイベント処理: 2テスト
- PRイベント処理: 2テスト
- Issueイベント処理: 2テスト
- イベント保存: 1テスト
- Discord通知: 2テスト
- 日時パース: 3テスト

---

## 🔗 関連リンク

### 内部リソース
- [メインREADME](../README.md)
- [テストサンプル](../test/webhook-samples.md)
- [ソースコード](../backend-python/src/api/github_webhook.py)

### 外部リソース
- [GitHub Webhooks 公式ドキュメント](https://docs.github.com/webhooks)
- [FastAPI 公式ドキュメント](https://fastapi.tiangolo.com/)
- [Webhook署名検証](https://docs.github.com/webhooks/using-webhooks/validating-webhook-deliveries)

---

## 💡 Tips

### ドキュメントの読み方

**急いでいる場合:**
```
クイックリファレンス (5分)
  ↓
セットアップ実行 (10分)
  ↓
完了！
```

**じっくり理解したい場合:**
```
セットアップガイド (20分)
  ↓
アーキテクチャ (30分)
  ↓
ソースコード確認
  ↓
カスタマイズ
```

### よくある質問

**Q: どのドキュメントから読めばいい？**  
A: [クイックリファレンス](WEBHOOK_QUICK_REFERENCE.md) で概要を掴んでから、[セットアップガイド](WEBHOOK_SETUP.md) で詳細設定を行うのがおすすめです。

**Q: テストの書き方を知りたい**  
A: `tests/test_github_webhook.py` を参照してください。21個の実装例があります。

**Q: セキュリティは大丈夫？**  
A: [セットアップガイド](WEBHOOK_SETUP.md#セキュリティのベストプラクティス) のセキュリティセクションを確認してください。

**Q: スケールするか心配**  
A: [アーキテクチャ](WEBHOOK_ARCHITECTURE.md#スケーラビリティ) のスケーラビリティセクションで詳しく解説しています。

---

## 🤝 コントリビューション

ドキュメントの改善提案は [Issues](https://github.com/yut0takagi/keel/issues) へ！

---

**最終更新:** 2024年10月  
**バージョン:** 1.0.0  
**ステータス:** ✅ Production Ready
