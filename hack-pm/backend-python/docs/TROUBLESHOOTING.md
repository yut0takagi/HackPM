# API接続トラブルシューティングガイド

## 🔍 フロントエンドからAPIにアクセスできない場合

### 1. サーバーが起動しているか確認

```bash
# サーバーを起動
cd hack-pm/backend-python
python3 main.py

# または起動スクリプトを使用
./start.sh

# または専用スクリプトを使用
python3 scripts/start_server.py
```

### 2. ポートが使用可能か確認

```bash
# ポート8000が使用されているか確認
lsof -i :8000

# 他のプロセスが使用している場合は終了
kill -9 <PID>
```

### 3. API接続テストを実行

```bash
# API接続テストスクリプトを実行
python3 scripts/test_api_connection.py
```

### 4. 手動でAPIをテスト

```bash
# ヘルスチェック
curl http://localhost:8000/health

# API テストエンドポイント
curl http://localhost:8000/api/test

# リポジトリ一覧
curl http://localhost:8000/api/repos
```

### 5. ブラウザでテスト

以下のURLをブラウザで開いて確認：

- http://localhost:8000 (ルートエンドポイント)
- http://localhost:8000/health (ヘルスチェック)
- http://localhost:8000/docs (API ドキュメント)
- http://localhost:8000/api/test (API テスト)

## 🔧 よくある問題と解決方法

### 問題1: Connection Refused

**症状**: `Connection refused` エラー

**解決方法**:
1. サーバーが起動していることを確認
2. 正しいポート（8000）を使用していることを確認
3. ファイアウォール設定を確認

### 問題2: CORS エラー

**症状**: `CORS policy` エラー

**解決方法**:
1. `main.py`のCORS設定を確認
2. フロントエンドのURLが許可リストに含まれているか確認
3. ブラウザのキャッシュをクリア

### 問題3: Import エラー

**症状**: `ModuleNotFoundError`

**解決方法**:
1. 依存関係をインストール: `pip3 install -r requirements.txt`
2. Pythonパスが正しく設定されているか確認
3. 仮想環境を使用している場合は有効化

### 問題4: Database エラー

**症状**: Database関連のエラー

**解決方法**:
1. データベースファイルの権限を確認
2. SQLiteが利用可能か確認
3. データベースファイルを削除して再作成

## 🛠️ デバッグ手順

### 1. ログを確認

```bash
# サーバーログを確認
tail -f server.log

# リアルタイムでログを監視
python3 main.py | tee server.log
```

### 2. 詳細なエラー情報を取得

```bash
# デバッグモードで起動
DEBUG_MODE=true python3 main.py

# より詳細なログレベル
LOG_LEVEL=DEBUG python3 main.py
```

### 3. ネットワーク接続を確認

```bash
# ローカルホストでの接続テスト
telnet localhost 8000

# ネットワークインターフェースを確認
netstat -an | grep 8000
```

## 🔄 フロントエンド側の設定

### React/Vite設定例

```javascript
// vite.config.js
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  }
}
```

### Fetch API使用例

```javascript
// API呼び出し例
const apiCall = async (endpoint) => {
  try {
    const response = await fetch(`http://localhost:8000${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

// 使用例
apiCall('/api/test').then(data => console.log(data));
```

## 📞 サポート

問題が解決しない場合は、以下の情報を含めて報告してください：

1. エラーメッセージの全文
2. ブラウザのコンソールログ
3. サーバーログ（server.log）
4. 使用しているOS・ブラウザ
5. フロントエンドのURL
6. 実行したコマンド

## 🎯 クイックフィックス

最も一般的な問題の即座の解決方法：

```bash
# 1. サーバーを強制終了して再起動
pkill -f "python3 main.py"
python3 main.py

# 2. ポートを変更して起動
PORT=8001 python3 main.py

# 3. 依存関係を再インストール
pip3 install --upgrade -r requirements.txt

# 4. データベースをリセット
rm -f hackathon.db
python3 main.py
```