# Hack PM (React + TS + Vite)

Hack PM is a lightweight hackathon project management app.

Features

- Ideation: add ideas, tag, and rank by Impact vs Effort
- Requirements: features with priority, status, and user stories
- Gantt: simple timeline with progress tracking (no external libs)
- ER Diagram: define entities, attributes, and relations; auto SVG diagram
- Prompt Builder: generate PoC prompts for Google AI Studio Build
- Persistence: auto-save to localStorage; JSON export/import

Getting Started

- Install deps: `npm install`
- Dev server: `npm run dev`
- Build: `npm run build` (output in `dist/`)

Notes

- No backend required; all data stays in the browser.
- Gantt and ERD are minimal and dependency-free for hackathon speed.

OpenAI 連携

- ブラウザで Settings → OpenAI API に APIキー（sk-...）を保存すると、ホームの「AI自動生成」でアイデアから機能要件/ガント/ER図(Mermaid)を生成できます。
- セキュリティ注意: APIキーはブラウザの localStorage に保存され、クライアントからOpenAI APIへ直接リクエストします。チーム共有や公開環境ではサーバ経由のプロキシ実装を推奨します。
