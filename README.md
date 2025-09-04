<p align="center">
  <img src="hack-pm/public/logo.svg" width="360" alt="Hack PM logo"/>
</p>

# Hackathon Project Template — Hack PM

このリポジトリは、ハッカソンで「最短でデモまで持っていく」ためのプロジェクトテンプレートです。要件作成 → ガント（日/時間）→ ER 図 → AI プロンプト → Git の基本動線を、1つの React アプリで完結できます。ネオン調のLP（GSAPアニメ）も同梱しているので、そのまま配布/募集用のページとして使えます。

主な中身（ディレクトリ）

- `hack-pm/`: ハッカソン用PJT管理アプリ（React + TypeScript + Vite）
  - `/lp`: GSAPで作ったネオンLP
  - ガント（日/時間）・ER図（Mermaid）・要件・AI自動生成・Git操作（ローカルAPI）を実装

特徴（Why this template）

- ローカルファースト: ブラウザの localStorage に自動保存、すぐ始められる
- 依存ミニマム: Gantt/ERは純CSS/SVG＋Mermaidで軽快に動作
- ハッカソン動線最適化: 要件→計画→データ設計→PoC準備までを最短で
- Git連携: ブランチ/コミット/Push/Fetch とメンバープレゼンスを画面から操作
- LP同梱: `GSAP + ScrollTrigger` を使った印象的なLPを `/lp` で提供

クイックスタート（各PJTでの使い方）

1) このテンプレートを自分のリポジトリへ（例: GitHub「Use this template」 or 手動でコピー）
2) アプリ起動

```
cd hack-pm
npm install
npm run dev:all   # アプリ + Git APIサーバを同時起動
```

- アプリ: http://localhost:5173
- LP: http://localhost:5173/lp
- Git API（ローカル）: http://localhost:8787

GitHub Pages でLPを公開する

1) GitHubの対象リポジトリ → Settings → Pages
2) Source を「Deploy from a branch」/ Branch を「main」/ フォルダを「/docs」へ設定 → Save
3) 数分待つと `https://<your-account>.github.io/<repo>/` で公開されます

LPの編集は `docs/` 配下（`index.html`, `styles.css`, `app.js`）を更新してください。

3) OpenAI 連携（任意）

- 画面右の「設定」→ OpenAI API で `sk-...` を保存
- ホーム「AI自動生成」で要件/ガント/ER(Mermaid)をまとめて生成

アプリでできること（要点）

- 機能要件: 優先度（P0/P1/P2）、ステータス、ユーザーストーリー
- ガント: 日/時間スケール、業務時間（例: 7:00〜20:00）設定、バーのドラッグ移動/リサイズ、現在時刻ライン、タスク列固定
- ER 図: エンティティ/属性/リレーション定義、Mermaid記法プレビュー/保存/自動生成
- プロンプト生成: Google AI Studio Build向けPoCプロンプトをワンクリックで生成
- Git: ブランチ切替/作成、Add/Commit/Push、Auto-Fetch（30s）、メンバーのプレゼンス表示（WS）
- 設定: JSON入出力、データリセット、OpenAI APIキーの保存（localStorage）

よくある使い方（チームでの流れ）

1. PJT名・説明を入れる（ホーム）
2. 必須機能を要件に落とす（Requirements）
3. ガントでスケジュール感を掴む（時間スケール/業務時間を活用）
4. ER のたたきを作る → Mermaidで共有（ER Diagram）
5. プロンプトを出して PoC 素案を加速（Prompt）
6. Git ページでブランチ切替/コミット/Push、プレゼンスでメンバー可視化

注意事項 / Tips

- OpenAIキーはlocalStorageに保存し、クライアントから直接APIへ送信します。公開環境や共有端末では必ずサーバープロキシの導入を検討してください。
- Git API はローカルのリポジトリに対して動作します。PushにはSSH/HTTPSの認証設定が必要です。
- データはブラウザに自動保存（設定からエクスポート/インポート可能）。
- ガントの時間スケールは“業務時間外を圧縮”して表示します（実時間の長さとは一致しません）。

ライセンス

プロジェクト方針に合わせて記載してください（未定の場合は社内/個人利用範囲などを明記）。

— Enjoy hacking! 🚀
