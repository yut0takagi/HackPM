<div id="top"></div>

<p align="center">
  <img src="./public/logo.svg" width="360" alt="Hack PM logo"/>
</p>

# Hack PM — Hackathon Project Manager (React + TS + Vite)

ハッカソンの「最短でつくる」に全振りしたローカルファーストなPJT管理テンプレート。要件 → ガント（日/時間）→ ER 図 → AIプロンプト → Git までワンストップ。LPも同梱（GSAP）。

デモLP: `/lp`（開発サーバで `http://localhost:5173/lp`）

---

使用技術一覧

<p style="display:inline-block">
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=61DAFB&labelColor=0B0C10&color=0B0C10&style=for-the-badge"/>
  <img src="https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=3178C6&labelColor=0B0C10&color=0B0C10&style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Vite-^5-646CFF?logo=vite&logoColor=646CFF&labelColor=0B0C10&color=0B0C10&style=for-the-badge"/>
  <img src="https://img.shields.io/badge/GSAP-ScrollTrigger-88CE02?logo=greensock&logoColor=88CE02&labelColor=0B0C10&color=0B0C10&style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Mermaid-ER%20Diagram-1f6feb?logo=mermaid&logoColor=1f6feb&labelColor=0B0C10&color=0B0C10&style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Express-API-ffffff?logo=express&logoColor=ffffff&labelColor=0B0C10&color=0B0C10&style=for-the-badge"/>
  <img src="https://img.shields.io/badge/simple--git-Git%20Ops-00ADD8?labelColor=0B0C10&color=0B0C10&style=for-the-badge"/>
  <img src="https://img.shields.io/badge/ws-Presence-25A162?labelColor=0B0C10&color=0B0C10&style=for-the-badge"/>
</p>

---

目次

- プロダクト概要
- 主な機能
- スクリーンショット/LP
- クイックスタート
- スクリプト一覧
- 環境変数（任意）
- ディレクトリ構成
- Tips / 注意事項
- ライセンス

---

プロダクト概要

- ローカル完結で爆速に進めるハッカソン用PJT管理。
- 依存ミニマム。ガント/ERは純CSS/SVG＋Mermaidで軽快。
- AIを使った要件/タスク/ERの自動生成（OpenAI API）。
- リポジトリ操作（ブランチ/コミット/Push/Fetch）とプレゼンス表示（WS）。

主な機能

- 機能要件: 優先度（P0/P1/P2）、ステータス、ユーザーストーリー。
- ガント: 日/時間スケール、業務時間（例: 7:00〜20:00）設定、バーのドラッグ移動/リサイズ、現在時刻ライン、左列固定。
- ER 図: エンティティ/属性/リレーションの定義、Mermaid記法プレビュー/保存/自動生成。
- プロンプト生成: Google AI Studio Build向けPoCプロンプトをワンクリック生成。
- Git: ブランチ切替・作成、Add/Commit/Push、Auto-Fetch、プレゼンス表示。
- 設定: JSON入出力、データリセット、OpenAI APIキーの保存（localStorage）。

スクリーンショット/LP

- LP（GSAP/ネオン）: `http://localhost:5173/lp`
- アプリ: `http://localhost:5173/`

クイックスタート

前提: Node.js 18+ / npm

1) 依存のインストール

```
cd hack-pm
npm install
```

2) 開発起動（アプリ + Git APIサーバ）

```
npm run dev:all
```

3) ブラウザでアクセス

- アプリ: http://localhost:5173
- LP: http://localhost:5173/lp
- Git API: http://localhost:8787

4) OpenAI 連携（任意）

- 画面右の「設定」→ OpenAI API で `sk-...` を保存
- ホーム「AI自動生成」でアイデアから要件/ガント/ER(Mermaid)を生成

スクリプト一覧

| コマンド            | 説明                                   |
| ------------------- | -------------------------------------- |
| `npm run dev`       | Vite 開発サーバ（アプリのみ）          |
| `npm run dev:server`| ローカルGit APIサーバのみ起動          |
| `npm run dev:all`   | アプリ + APIサーバ同時起動              |
| `npm run build`     | 本番ビルド（`dist/`）                  |
| `npm run preview`   | 本番ビルドのプレビュー                 |

環境変数（任意）

- `VITE_OPENAI_API_KEY`: クライアントに埋め込む場合のみ。推奨は設定画面からの保存（localStorage）。

ディレクトリ構成（抜粋）

```
hack-pm/
├─ src/
│  ├─ pages/
│  │  ├─ HomePage.tsx          # 概要 + 自動生成
│  │  ├─ RequirementsPage.tsx  # 機能要件
│  │  ├─ GanttPage.tsx         # ガント（日/時間, ドラッグ/リサイズ）
│  │  ├─ ERDiagramPage.tsx     # ER定義 + Mermaidプレビュー
│  │  ├─ PromptBuilderPage.tsx # PoCプロンプト生成
│  │  ├─ GitPage.tsx           # Git操作 + プレゼンス
│  │  └─ LandingPage.tsx       # LP（GSAP/ネオン）
│  ├─ components/
│  │  └─ Modal.tsx
│  ├─ state/
│  │  └─ store.tsx             # アプリ状態（localStorage保存）
│  ├─ ai/openai.ts             # OpenAI呼び出し（client）
│  ├─ auto/planner.ts          # ローカルヒューリスティック生成
│  ├─ App.tsx / App.css        # ルータ/レイアウト（サイドバー折りたたみ）
│  └─ lp.css                   # LPスタイル（ネオン）
├─ server/
│  └─ index.js                 # Git API (Express + simple-git) / WSプレゼンス
└─ README.md
```

Tips / 注意事項

- OpenAIキーはlocalStorage保存 + クライアントから直接APIへ送信します。共有/公開環境ではプロキシ導入を推奨。
- Git API はローカルのリポジトリに対して動作します。Push には SSH/HTTPS 設定が必要です。
- データはブラウザの localStorage に自動保存（設定からエクスポート/インポート可）。
- ガントの時間スケールは業務時間外を圧縮表示します（実時間と列幅は一致しません）。

ライセンス

本テンプレートの著作権/ライセンス方針に合わせて記載してください（未定の場合は社内利用/個人利用の範囲を明記）。

― Enjoy hacking! 🚀

OpenAI 連携

- ブラウザで Settings → OpenAI API に APIキー（sk-...）を保存すると、ホームの「AI自動生成」でアイデアから機能要件/ガント/ER図(Mermaid)を生成できます。
- セキュリティ注意: APIキーはブラウザの localStorage に保存され、クライアントからOpenAI APIへ直接リクエストします。チーム共有や公開環境ではサーバ経由のプロキシ実装を推奨します。
