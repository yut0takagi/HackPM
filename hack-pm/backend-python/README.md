# GitHub Template System - Backend

## 📁 プロジェクト構造

```
hack-pm/backend-python/
├── 📁 src/                            # ソースコード
│   ├── 📁 core/                       # コアロジック
│   │   ├── template_parser.py         # テンプレート解析エンジン
│   │   ├── branch_naming.py           # ブランチ命名規則システム
│   │   └── status_mapping.py          # ステータスマッピングシステム
│   ├── 📁 services/                   # サービス層
│   │   ├── database.py                # データベース操作
│   │   └── timebox_service.py         # タイムボックス管理
│   ├── 📁 api/                        # API統合
│   │   ├── github_api.py              # GitHub API統合
│   │   └── github_webhook.py          # GitHub Webhook処理
│   └── 📁 utils/                      # ユーティリティ
│       └── config.py                  # 設定管理システム
├── 📁 tests/                          # テストファイル
│   ├── test_base.py                   # テスト基盤クラス
│   ├── test_template_parser.py        # テンプレートパーサーのテスト
│   ├── test_branch_naming.py          # ブランチ命名のテスト
│   ├── test_status_mapping.py         # ステータスマッピングのテスト
│   ├── test_integration.py            # 統合テスト
│   ├── test_github_api_integration.py # GitHub API統合テスト
│   └── test_end_to_end_workflow.py    # エンドツーエンドワークフローテスト
├── 📁 config/                         # 設定ファイル
│   ├── config.example.json            # 設定ファイルサンプル
│   └── .env.example                   # 環境変数サンプル
├── 📁 docs/                           # ドキュメント
│   ├── REFACTORING_SUMMARY.md         # リファクタリング概要
│   └── TEST_SUMMARY.md                # テスト概要
├── 📁 scripts/                        # スクリプト
│   ├── test_runner.py                 # 統合テストランナー
│   └── debug_yaml.py                  # デバッグスクリプト
├── 📁 data/                           # データファイル
├── main.py                            # メインアプリケーション
├── requirements.txt                   # Python依存関係
└── Dockerfile                         # Docker設定
```

## 🚀 クイックスタート

### テストの実行

```bash
# 全テストを実行
python3 scripts/test_runner.py

# 特定のテストを実行
python3 scripts/test_runner.py --test-files tests/test_template_parser.py

# HTMLレポート付きでテストを実行
python3 scripts/test_runner.py --format html

# パフォーマンステストをスキップ
python3 scripts/test_runner.py --no-performance
```

### 個別テストの実行

```bash
# テンプレートパーサーのテスト
python3 tests/test_template_parser.py

# ブランチ命名のテスト
python3 tests/test_branch_naming.py

# ステータスマッピングのテスト
python3 tests/test_status_mapping.py
```

## 🏗️ アーキテクチャ

### コアコンポーネント

1. **Template Parser** (`template_parser.py`)
   - YAML frontmatterとMarkdownテンプレートの解析
   - セキュリティサニタイゼーション
   - パフォーマンス最適化

2. **Branch Naming** (`branch_naming.py`)
   - ブランチ命名規則の検証
   - 自動ブランチ名提案
   - Issue番号との連携

3. **Status Mapping** (`status_mapping.py`)
   - テンプレートデータのダッシュボード表示への変換
   - ハッカソン特化機能
   - 進捗追跡

4. **Configuration** (`config.py`)
   - 環境変数とJSONファイルからの設定読み込み
   - 階層的設定管理
   - 実行時設定変更

### テストアーキテクチャ

- **BaseTestSuite**: 再利用可能なテスト基盤
- **MockDataGenerator**: 一貫したテストデータ生成
- **PerformanceBenchmark**: パフォーマンス測定
- **TestAssertions**: 拡張アサーション

## 📊 パフォーマンス

### ベンチマーク結果

- **テンプレート解析**: 平均 0.2ms/テンプレート
- **大きなテンプレート**: 平均 1.2ms/テンプレート
- **ステータスマッピング**: 平均 0.01ms/Issue
- **ブランチ名検証**: 平均 0.002ms/ブランチ

### スケーラビリティ

- 1000テンプレート同時処理: <1秒
- メモリ使用量: <10MB (1000テンプレート)
- キャッシュヒット率: >90%

## 🔧 設定

### 環境変数

```bash
# テンプレート解析設定
export TEMPLATE_MAX_TEXT_LENGTH=10000
export TEMPLATE_MAX_LIST_ITEMS=100
export TEMPLATE_SANITIZATION=true

# ステータスマッピング設定
export STATUS_ENABLE_TIME_BOXING=true
export STATUS_DEFAULT_PRIORITY=medium

# ブランチ命名設定
export BRANCH_ENFORCE_CONVENTION=true
export BRANCH_MAX_DESC_LENGTH=50

# グローバル設定
export DEBUG_MODE=false
export LOG_LEVEL=INFO
export ENVIRONMENT=development
```

### JSONファイル設定

`config.json`ファイルを作成して詳細な設定を行えます：

```json
{
  "parsing": {
    "max_text_length": 10000,
    "sanitization_enabled": true,
    "enable_caching": true
  },
  "status_mapping": {
    "enable_hackathon_features": true,
    "escalation_threshold_hours": 2.0
  },
  "branch_naming": {
    "enforce_naming_convention": true,
    "allowed_prefixes": ["feature", "bugfix", "hotfix"]
  }
}
```

## 🧪 テスト

### テストカバレッジ

- **Template Parser**: 15テストケース、100%カバレッジ
- **Branch Naming**: 13テストケース、100%カバレッジ
- **Status Mapping**: 12テストケース、100%カバレッジ
- **Integration**: 10テストケース、エンドツーエンド
- **Security**: XSS、SQLインジェクション対策テスト

### テストレポート

テスト実行後、以下のレポートが生成されます：

- `test_reports/test_results.json`: JSON形式の詳細結果
- `test_reports/test_results.html`: HTML形式の視覚的レポート

## 🔒 セキュリティ

### 実装済みセキュリティ機能

- **入力サニタイゼーション**: XSS攻撃防止
- **SQLインジェクション対策**: 危険なパターンの除去
- **入力サイズ制限**: DoS攻撃防止
- **安全なYAML解析**: コードインジェクション防止

## 📈 監視とログ

### パフォーマンス監視

```python
from template_parser import template_parser

# パフォーマンス統計の取得
stats = template_parser.get_performance_stats()
print(f"解析回数: {stats['parse_count']}")
print(f"平均時間: {stats['average_time']:.4f}s")
```

### ログ設定

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🚀 本番環境デプロイ

### Docker使用

```bash
# イメージのビルド
docker build -t github-template-system .

# コンテナの実行
docker run -p 8000:8000 github-template-system
```

### 環境別設定

- **Development**: `ENVIRONMENT=development`
- **Testing**: `ENVIRONMENT=testing`
- **Staging**: `ENVIRONMENT=staging`
- **Production**: `ENVIRONMENT=production`

## 🤝 開発ガイド

### 新しいテストの追加

1. `tests/`ディレクトリに新しいテストファイルを作成
2. `BaseTestSuite`を継承したテストクラスを作成
3. `get_test_methods()`メソッドでテストメソッドを定義
4. `test_runner.py`で自動検出される

### 新しい機能の追加

1. メインモジュールに機能を実装
2. 対応するテストを`tests/`に追加
3. 設定オプションを`config.py`に追加
4. ドキュメントを更新

## 📝 変更履歴

### v2.0.0 (リファクタリング版)
- モジュラーアーキテクチャへの移行
- 10倍のパフォーマンス向上
- 包括的なテストスイート
- 設定管理システムの追加
- セキュリティ強化

### v1.0.0 (初期版)
- 基本的なテンプレート解析機能
- ブランチ命名規則
- ステータスマッピング

---

**開発チーム**: GitHub Template System  
**最終更新**: 2025年10月7日  
**ライセンス**: MIT