FROM node:18-alpine

WORKDIR /app

# package.jsonをコピー
COPY package.json ./

# 依存関係をインストール
RUN npm install

# ソースコードをコピー
COPY . .

# 環境変数を設定
ENV SKIP_PREFLIGHT_CHECK=true

EXPOSE 3000

CMD ["npm", "start"]